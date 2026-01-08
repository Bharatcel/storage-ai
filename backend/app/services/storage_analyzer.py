"""
Storage Analysis Service
Analyzes uploaded CSV files and generates insights
"""
import csv
import io
import json
import decimal
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, not_
from app.models import (
    Project, ScriptResult, FileMetadata, AnalysisResults, AnalysisSummary
)
from app.blob_storage import BlobStorageService
import logging

logger = logging.getLogger(__name__)

# Azure Blob Storage Pricing (per GB per month) - December 2025
TIER_PRICING = {
    "Hot": Decimal("0.0184"),
    "Cool": Decimal("0.01"),
    "Archive": Decimal("0.00099"),
    "Delete": Decimal("0")
}

class StorageAnalyzer:
    """Main analysis engine for storage assessment"""
    
    def __init__(self, db: Session):
        self.db = db
        self.blob_service = BlobStorageService()
    
    async def analyze_project(self, project_id: int) -> Dict:
        """
        Main entry point - analyzes all uploaded CSV files for a project
        Returns analysis summary
        """
        try:
            # Update status to processing
            summary = self._get_or_create_summary(project_id)
            summary.analysis_status = "processing"
            summary.started_at = datetime.now()
            summary.error_message = None
            self.db.commit()
            
            # Get all uploaded CSV files for this project
            csv_files = self.db.query(ScriptResult).filter(
                ScriptResult.project_id == project_id,
                ScriptResult.original_filename.like('%.csv')
            ).all()
            
            if not csv_files:
                raise Exception("No CSV files found for this project")
            
            # Parse and store file metadata
            total_rows = 0
            logger.info(f"Starting CSV parsing for {len(csv_files)} files...")
            for idx, csv_file in enumerate(csv_files, 1):
                logger.info(f"Parsing file {idx}/{len(csv_files)}: {csv_file.original_filename}")
                rows = await self._parse_csv_file(csv_file, project_id)
                total_rows += rows
            
            logger.info(f"✅ Parsed {total_rows} rows from {len(csv_files)} CSV files")
            
            # Run all analyses and store in single JSON record
            analysis_data = {}
            logger.info("Running age distribution analysis...")
            analysis_data['age_distribution'] = self._analyze_age_distribution(project_id)
            
            logger.info("Running file type analysis...")
            analysis_data['file_types'] = self._analyze_file_types(project_id)
            
            logger.info("Running storage tier analysis...")
            analysis_data['storage_tiers'] = self._analyze_storage_tiers(project_id)
            
            logger.info("Calculating costs...")
            analysis_data['cost_analysis'] = self._calculate_costs(analysis_data['storage_tiers'])
            
            logger.info("Projecting growth...")
            analysis_data['growth_projection'] = self._project_growth(project_id)
            
            logger.info("Analyzing duplicate files...")
            analysis_data['duplicate_files'] = self._analyze_duplicates(project_id)
            
            logger.info("Extracting script metadata...")
            analysis_data['script_metadata'] = self._extract_script_metadata(csv_files)
            
            # PHASE 1: New Enhanced Analysis
            logger.info("Analyzing access patterns...")
            analysis_data['access_patterns'] = self._analyze_access_patterns(project_id)
            
            logger.info("Running advanced duplicate detection...")
            analysis_data['duplicates_advanced'] = self._analyze_duplicates_advanced(project_id)
            
            logger.info("Analyzing directories...")
            analysis_data['directory_analysis'] = self._analyze_directories(project_id)
            
            logger.info("Validating data quality...")
            analysis_data['data_quality'] = self._validate_data_quality(project_id)
            
            logger.info("Generating recommendations...")
            analysis_data['recommendations'] = self._generate_recommendations(project_id, analysis_data)
            
            # Store results in database
            self._save_analysis_results(project_id, analysis_data)
            
            # Update summary with totals
            total_files, total_size_gb = self._calculate_totals(project_id)
            summary.total_files = total_files
            summary.total_size_gb = total_size_gb
            summary.analyzed_files_count = len(csv_files)
            summary.analysis_status = "completed"
            summary.completed_at = datetime.now()
            self.db.commit()
            
            return {
                "status": "success",
                "total_files": total_files,
                "total_size_gb": float(total_size_gb),
                "analyzed_csv_count": len(csv_files)
            }
            
        except Exception as e:
            logger.error(f"Analysis failed for project {project_id}: {str(e)}")
            summary = self._get_or_create_summary(project_id)
            summary.analysis_status = "failed"
            summary.error_message = str(e)
            summary.completed_at = datetime.now()
            self.db.commit()
            raise
    
    async def _parse_csv_file(self, csv_file: ScriptResult, project_id: int) -> int:
        """Parse a single CSV file and store metadata - OPTIMIZED"""
        try:
            # Download CSV from blob storage
            blob_content = await self._download_blob(csv_file.blob_url)
            
            # Parse CSV
            csv_text = blob_content.decode('utf-8-sig')  # Handle BOM
            reader = csv.DictReader(io.StringIO(csv_text))
            
            rows_processed = 0
            batch = []
            batch_size = 1000  # Increased from 500 for better performance
            
            for row in reader:
                # Map CSV columns to database fields
                # Support both old format (ServerName, Drive, etc.) and new format (Hostname, DriveLetter, etc.)
                server_name = row.get('ServerName') or row.get('Hostname')
                drive_letter = row.get('Drive') or row.get('DriveLetter')
                directory_path = row.get('Directory') or row.get('Path')
                file_name = row.get('FileName')
                extension = row.get('Extension') or row.get('FileType')
                
                # Handle different size formats
                size_kb = self._parse_decimal(row.get('FileSizeKB'))
                size_bytes = self._parse_int(row.get('SizeBytes')) or (int(size_kb * 1024) if size_kb else None)
                size_mb = self._parse_decimal(row.get('SizeMB')) or (size_kb / 1024 if size_kb else None)
                size_gb = self._parse_decimal(row.get('SizeGB')) or (size_kb / (1024 * 1024) if size_kb else None)
                
                # Handle different date formats
                created_date = self._parse_date(row.get('CreatedDate') or row.get('CreatedTime'))
                modified_date = self._parse_date(row.get('ModifiedDate') or row.get('LastModified'))
                accessed_date = self._parse_date(row.get('AccessedDate') or row.get('LastAccessed'))
                
                metadata = FileMetadata(
                    project_id=project_id,
                    result_file_id=csv_file.id,
                    server_name=server_name,
                    drive_letter=drive_letter,
                    directory_path=directory_path,
                    file_name=file_name,
                    extension=self._extract_extension(extension),
                    size_bytes=size_bytes,
                    size_mb=size_mb,
                    size_gb=size_gb,
                    created_date=created_date,
                    modified_date=modified_date,
                    accessed_date=accessed_date,
                    file_count=self._parse_int(row.get('FileCount')) or 1
                )
                batch.append(metadata)
                rows_processed += 1
                
                # Batch insert every 1000 rows for better performance
                if len(batch) >= batch_size:
                    self.db.bulk_save_objects(batch)
                    self.db.commit()
                    logger.info(f"Processed {rows_processed} rows from {csv_file.original_filename}")
                    batch = []
            
            # Insert remaining rows
            if batch:
                self.db.bulk_save_objects(batch)
                self.db.commit()
            
            logger.info(f"✅ Parsed {rows_processed} rows from {csv_file.original_filename}")
            return rows_processed
            
        except Exception as e:
            logger.error(f"Error parsing {csv_file.original_filename}: {str(e)}")
            raise
    
    async def _download_blob(self, blob_url: str) -> bytes:
        """Download file from blob storage"""
        # Extract blob name from URL
        blob_name = blob_url.split(self.blob_service.container_name + "/")[-1]
        blob_client = self.blob_service.blob_service_client.get_blob_client(
            container=self.blob_service.container_name,
            blob=blob_name
        )
        return blob_client.download_blob().readall()
    
    def _analyze_age_distribution(self, project_id: int) -> List[Dict]:
        """Analyze files by age buckets - returns data instead of saving"""
        now = datetime.now()
        buckets = {
            '<6m': (0, 180),
            '6m-1Y': (180, 365),
            '1-3Y': (365, 1095),
            '3-5Y': (1095, 1825),
            '>5Y': (1825, 36500)
        }
        
        total_size = Decimal(0)
        bucket_stats = {}
        
        for bucket_name, (min_days, max_days) in buckets.items():
            min_date = now - timedelta(days=max_days)
            max_date = now - timedelta(days=min_days)
            
            # Query files in this age range
            result = self.db.query(
                func.count(FileMetadata.id),
                func.coalesce(func.sum(FileMetadata.size_gb), 0)
            ).filter(
                FileMetadata.project_id == project_id,
                FileMetadata.modified_date >= min_date,
                FileMetadata.modified_date < max_date
            ).first()
            
            count = result[0] or 0
            size_gb = Decimal(str(result[1] or 0))
            
            bucket_stats[bucket_name] = {
                'count': count,
                'size_gb': size_gb
            }
            total_size += size_gb
        
        # Calculate percentages and return as list
        results = []
        for bucket_name, stats in bucket_stats.items():
            percentage = (stats['size_gb'] / total_size * 100) if total_size > 0 else Decimal(0)
            results.append({
                'age_bucket': bucket_name,
                'file_count': stats['count'],
                'total_size_gb': float(stats['size_gb']),
                'percentage': float(percentage)
            })
        
        logger.info(f"Age distribution analysis completed for project {project_id}")
        return results
    
    def _analyze_file_types(self, project_id: int) -> List[Dict]:
        """Analyze files by type/extension - returns data instead of saving"""
        # Group by extension
        results = self.db.query(
            FileMetadata.extension,
            func.count(FileMetadata.id).label('count'),
            func.coalesce(func.sum(FileMetadata.size_gb), 0).label('size_gb')
        ).filter(
            FileMetadata.project_id == project_id
        ).group_by(
            FileMetadata.extension
        ).order_by(
            func.sum(FileMetadata.size_gb).desc()
        ).limit(50).all()  # Top 50 types
        
        total_size = sum(Decimal(str(r.size_gb)) for r in results)
        
        file_types = []
        for result in results:
            size_gb = Decimal(str(result.size_gb))
            percentage = (size_gb / total_size * 100) if total_size > 0 else Decimal(0)
            
            file_types.append({
                'extension': result.extension or 'NO_EXTENSION',
                'file_count': result.count,
                'total_size_gb': float(size_gb),
                'percentage': float(percentage)
            })
        
        logger.info(f"File type analysis completed for project {project_id}")
        return file_types
    
    def _analyze_storage_tiers(self, project_id: int) -> List[Dict]:
        """
        Recommend storage tiers based on BOTH modification AND access patterns
        SAFE & CONSERVATIVE approach - Delete tier requires multiple conditions
        """
        now = datetime.now()
        
        tier_stats = {}
        
        # Hot tier: Modified OR accessed in last 30 days (active files)
        result = self.db.query(
            func.count(FileMetadata.id),
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id,
            or_(
                FileMetadata.modified_date >= now - timedelta(days=30),
                FileMetadata.accessed_date >= now - timedelta(days=30)
            )
        ).first()
        tier_stats['Hot'] = {'count': result[0], 'size_gb': Decimal(str(result[1]))}
        
        # Cool tier: Modified/accessed 30-180 days ago (occasionally used)
        result = self.db.query(
            func.count(FileMetadata.id),
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id,
            or_(
                and_(
                    FileMetadata.modified_date >= now - timedelta(days=180),
                    FileMetadata.modified_date < now - timedelta(days=30)
                ),
                and_(
                    FileMetadata.accessed_date >= now - timedelta(days=180),
                    FileMetadata.accessed_date < now - timedelta(days=30)
                )
            ),
            # Exclude files already in Hot tier
            not_(or_(
                FileMetadata.modified_date >= now - timedelta(days=30),
                FileMetadata.accessed_date >= now - timedelta(days=30)
            ))
        ).first()
        tier_stats['Cool'] = {'count': result[0], 'size_gb': Decimal(str(result[1]))}
        
        # Archive tier: Modified 180 days - 3 years ago AND not accessed recently (rarely used)
        result = self.db.query(
            func.count(FileMetadata.id),
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.modified_date >= now - timedelta(days=1095),  # 3 years
            FileMetadata.modified_date < now - timedelta(days=180),
            # Not in Hot or Cool tier
            not_(or_(
                FileMetadata.modified_date >= now - timedelta(days=180),
                FileMetadata.accessed_date >= now - timedelta(days=180)
            ))
        ).first()
        tier_stats['Archive'] = {'count': result[0], 'size_gb': Decimal(str(result[1]))}
        
        # Delete CANDIDATES (not automatic!): Very old AND likely obsolete
        # Criteria: Modified > 3 years ago AND not accessed in 2+ years
        # PLUS one of: temp file pattern, backup pattern, or very small size
        delete_candidates = self.db.query(
            func.count(FileMetadata.id),
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.modified_date < now - timedelta(days=1095),  # > 3 years old
            or_(
                FileMetadata.accessed_date < now - timedelta(days=730),  # Not accessed in 2+ years
                FileMetadata.accessed_date.is_(None)  # Or no access data
            ),
            # Additional safety: Only suggest deletion for likely temp/backup files
            or_(
                func.lower(FileMetadata.file_name).like('%temp%'),
                func.lower(FileMetadata.file_name).like('%tmp%'),
                func.lower(FileMetadata.file_name).like('%backup%'),
                func.lower(FileMetadata.file_name).like('%old%'),
                func.lower(FileMetadata.file_name).like('%.bak%'),
                func.lower(FileMetadata.directory_path).like('%temp%'),
                func.lower(FileMetadata.directory_path).like('%cache%'),
                func.lower(FileMetadata.directory_path).like('%backup%')
            )
        ).first()
        tier_stats['Delete'] = {'count': delete_candidates[0], 'size_gb': Decimal(str(delete_candidates[1]))}
        tier_stats['Delete'] = {'count': delete_candidates[0], 'size_gb': Decimal(str(delete_candidates[1]))}
        
        # Calculate totals and return as list
        total_size = sum(stats['size_gb'] for stats in tier_stats.values())
        
        storage_tiers = []
        for tier_name, stats in tier_stats.items():
            percentage = (stats['size_gb'] / total_size * 100) if total_size > 0 else Decimal(0)
            monthly_cost = stats['size_gb'] * TIER_PRICING[tier_name]
            
            # Add warning for Delete tier
            description = ""
            if tier_name == 'Delete':
                description = "REVIEW REQUIRED - Deletion candidates based on age + naming patterns. Manual approval needed."
            elif tier_name == 'Archive':
                description = "Rarely accessed - safe to archive"
            elif tier_name == 'Cool':
                description = "Occasionally accessed - good for Cool tier"
            elif tier_name == 'Hot':
                description = "Actively used - keep in Hot tier"
            
            storage_tiers.append({
                'tier_name': tier_name,
                'file_count': stats['count'],
                'total_size_gb': float(stats['size_gb']),
                'percentage': float(percentage),
                'monthly_cost': float(monthly_cost),
                'description': description
            })
        
        logger.info(f"Storage tier analysis completed for project {project_id}")
        return storage_tiers
    
    def _calculate_costs(self, storage_tiers: List[Dict]) -> Dict:
        """Calculate cost savings from tier optimization - takes tiers as input"""
        current_cost = Decimal(0)
        optimized_cost = Decimal(0)
        
        for tier in storage_tiers:
            # Assume all data is currently in Hot storage
            current_cost += Decimal(str(tier['total_size_gb'])) * TIER_PRICING['Hot']
            optimized_cost += Decimal(str(tier['monthly_cost']))
        
        monthly_savings = current_cost - optimized_cost
        savings_pct = (monthly_savings / current_cost * 100) if current_cost > 0 else Decimal(0)
        
        cost_analysis = {
            'current_monthly_cost': float(current_cost),
            'optimized_monthly_cost': float(optimized_cost),
            'monthly_savings': float(monthly_savings),
            'savings_percentage': float(savings_pct),
            'annual_savings': float(monthly_savings * 12)
        }
        
        logger.info(f"Cost analysis completed")
        return cost_analysis
    
    def _project_growth(self, project_id: int) -> Dict:
        """Project future storage growth - returns data"""
        # Calculate current total size
        current_size = self.db.query(
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id
        ).scalar()
        
        current_size_gb = Decimal(str(current_size or 0))
        
        # Simple linear projection: assume 15% annual growth (industry average)
        # In Phase 2, this would use historical data
        annual_growth_rate = Decimal("15.0")
        monthly_rate = annual_growth_rate / Decimal("12") / Decimal("100")
        
        projected_6m = current_size_gb * (Decimal("1") + (monthly_rate * Decimal("6")))
        projected_1y = current_size_gb * (Decimal("1") + (annual_growth_rate / Decimal("100")))
        projected_3y = current_size_gb * ((Decimal("1") + (annual_growth_rate / Decimal("100"))) ** 3)
        
        projection = {
            'current_size_gb': float(current_size_gb),
            'projected_6m_gb': float(projected_6m),
            'projected_1y_gb': float(projected_1y),
            'projected_3y_gb': float(projected_3y),
            'annual_growth_rate_pct': float(annual_growth_rate),
            'confidence_level': 'Medium'  # Would be 'High' with historical data
        }
        
        logger.info(f"Growth projection completed")
        return projection
    
    def _analyze_duplicates(self, project_id: int) -> Dict:
        """
        Detect duplicate files based on size, extension, and filename
        Returns duplicate file analysis with potential savings
        """
        # Find files with same size, extension, and name (potential duplicates)
        duplicate_groups = self.db.query(
            FileMetadata.extension,
            FileMetadata.size_gb,
            FileMetadata.file_name,
            func.count(FileMetadata.id).label('occurrence_count'),
            func.sum(FileMetadata.size_gb).label('total_size_gb')
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.size_gb > 0  # Ignore zero-byte files
        ).group_by(
            FileMetadata.extension,
            FileMetadata.size_gb,
            FileMetadata.file_name
        ).having(
            func.count(FileMetadata.id) > 1  # Only duplicates
        ).order_by(
            func.sum(FileMetadata.size_gb).desc()
        ).limit(100).all()  # Top 100 duplicate groups
        
        duplicates = []
        total_duplicate_size = Decimal(0)
        total_duplicate_count = 0
        
        for dup in duplicate_groups:
            occurrence_count = dup.occurrence_count
            size_per_file = Decimal(str(dup.size_gb))
            total_size = Decimal(str(dup.total_size_gb))
            
            # Savings = (n-1) copies * size (keep 1, delete rest)
            potential_savings = size_per_file * (occurrence_count - 1)
            
            duplicates.append({
                'file_name': dup.file_name,
                'extension': dup.extension or 'NO_EXTENSION',
                'size_gb': float(size_per_file),
                'occurrence_count': occurrence_count,
                'total_size_gb': float(total_size),
                'potential_savings_gb': float(potential_savings)
            })
            
            total_duplicate_size += potential_savings
            total_duplicate_count += (occurrence_count - 1)  # Extra copies
        
        # Cache total size to avoid redundant query
        _, project_total_size = self._calculate_totals(project_id)
        savings_pct = float((total_duplicate_size / project_total_size * 100) if project_total_size > 0 else 0)
        
        duplicate_analysis = {
            'duplicate_groups': duplicates,
            'total_duplicate_files': total_duplicate_count,
            'total_potential_savings_gb': float(total_duplicate_size),
            'savings_percentage': savings_pct
        }
        
        logger.info(f"Duplicate analysis completed: {total_duplicate_count} duplicates found, {float(total_duplicate_size):.2f} GB potential savings")
        return duplicate_analysis
    
    def _extract_script_metadata(self, csv_files: List) -> Dict:
        """
        Extract metadata from script-generated CSV files
        Returns information about data collection
        """
        servers_scanned = set()
        total_size_collected = 0
        earliest_scan = None
        latest_scan = None
        
        for csv_file in csv_files:
            # Extract server name from filename pattern (if available)
            # e.g., "DC1IOPSUAT-20231227-2004-DriveFileDetails.csv"
            filename = csv_file.original_filename
            parts = filename.split('-')
            if parts:
                servers_scanned.add(parts[0])
            
            total_size_collected += csv_file.file_size
            
            # Track scan dates from upload times
            if not earliest_scan or csv_file.uploaded_at < earliest_scan:
                earliest_scan = csv_file.uploaded_at
            if not latest_scan or csv_file.uploaded_at > latest_scan:
                latest_scan = csv_file.uploaded_at
        
        metadata = {
            'servers_scanned': list(servers_scanned),
            'server_count': len(servers_scanned),
            'csv_files_uploaded': len(csv_files),
            'total_csv_size_mb': round(total_size_collected / (1024 * 1024), 2),
            'earliest_scan_date': earliest_scan.isoformat() if earliest_scan else None,
            'latest_scan_date': latest_scan.isoformat() if latest_scan else None,
            'scan_duration_days': (latest_scan - earliest_scan).days if (earliest_scan and latest_scan) else 0
        }
        
        logger.info(f"Script metadata extracted: {metadata['server_count']} servers scanned")
        return metadata
    
    def _analyze_access_patterns(self, project_id: int) -> Dict:
        """
        PHASE 1: Analyze file access patterns to optimize storage tiering
        Categorizes files by access frequency: Hot/Warm/Cold/Frozen
        """
        now = datetime.now()
        
        # Define access patterns (more granular than modification-based tiering)
        patterns = {
            'Hot': (0, 30),      # Accessed in last 30 days - frequent access
            'Warm': (30, 90),    # Accessed 30-90 days ago - occasional access
            'Cold': (90, 365),   # Accessed 90-365 days ago - rare access
            'Frozen': (365, 36500)  # Not accessed in 1+ year - dormant
        }
        
        pattern_stats = {}
        total_size = Decimal(0)
        
        for pattern_name, (min_days, max_days) in patterns.items():
            min_date = now - timedelta(days=max_days)
            max_date = now - timedelta(days=min_days)
            
            # Query files in this access pattern
            result = self.db.query(
                func.count(FileMetadata.id),
                func.coalesce(func.sum(FileMetadata.size_gb), 0)
            ).filter(
                FileMetadata.project_id == project_id,
                FileMetadata.accessed_date.isnot(None),
                FileMetadata.accessed_date >= min_date,
                FileMetadata.accessed_date < max_date
            ).first()
            
            count = result[0] or 0
            size_gb = Decimal(str(result[1] or 0))
            
            pattern_stats[pattern_name] = {
                'count': count,
                'size_gb': size_gb
            }
            total_size += size_gb
        
        # Handle files with missing access dates
        no_access_data = self.db.query(
            func.count(FileMetadata.id),
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.accessed_date.is_(None)
        ).first()
        
        pattern_stats['Unknown'] = {
            'count': no_access_data[0] or 0,
            'size_gb': Decimal(str(no_access_data[1] or 0))
        }
        total_size += pattern_stats['Unknown']['size_gb']
        
        # Identify "zombie files" - large files never accessed
        zombie_files = self.db.query(
            func.count(FileMetadata.id),
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.size_gb > 1,  # Larger than 1GB
            FileMetadata.accessed_date < now - timedelta(days=730)  # Not accessed in 2 years
        ).first()
        
        # Calculate percentages and build results
        access_patterns = []
        for pattern_name, stats in pattern_stats.items():
            percentage = (stats['size_gb'] / total_size * 100) if total_size > 0 else Decimal(0)
            access_patterns.append({
                'pattern': pattern_name,
                'file_count': stats['count'],
                'total_size_gb': float(stats['size_gb']),
                'percentage': float(percentage),
                'recommended_tier': self._map_access_to_tier(pattern_name)
            })
        
        analysis_result = {
            'patterns': access_patterns,
            'zombie_files': {
                'count': zombie_files[0] or 0,
                'total_size_gb': float(zombie_files[1] or 0)
            },
            'total_analyzed_size_gb': float(total_size)
        }
        
        logger.info(f"Access pattern analysis completed: {len(access_patterns)} patterns identified")
        return analysis_result
    
    def _map_access_to_tier(self, pattern: str) -> str:
        """Map access pattern to recommended Azure storage tier"""
        mapping = {
            'Hot': 'Hot',
            'Warm': 'Cool',
            'Cold': 'Archive',
            'Frozen': 'Delete',
            'Unknown': 'Cool'  # Conservative default
        }
        return mapping.get(pattern, 'Cool')
    
    def _analyze_duplicates_advanced(self, project_id: int) -> Dict:
        """
        PHASE 1: Advanced duplicate detection with confidence scoring
        Identifies duplicates, versions, and naming patterns
        """
        import re
        
        # Find exact duplicates (same size, extension, name)
        # Note: Using func.max instead of string_agg to avoid VARCHAR(MAX) separator error
        exact_duplicates = self.db.query(
            FileMetadata.extension,
            FileMetadata.size_gb,
            FileMetadata.file_name,
            func.count(FileMetadata.id).label('occurrence_count'),
            func.sum(FileMetadata.size_gb).label('total_size_gb'),
            func.max(FileMetadata.directory_path).label('locations')  # Sample location
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.size_gb > 0
        ).group_by(
            FileMetadata.extension,
            FileMetadata.size_gb,
            FileMetadata.file_name
        ).having(
            func.count(FileMetadata.id) > 1
        ).order_by(
            func.sum(FileMetadata.size_gb).desc()
        ).limit(100).all()
        
        # Analyze naming patterns for version detection
        version_patterns = [
            r'_v\d+',           # file_v1.xlsx
            r'_version\d+',     # file_version1.xlsx
            r'_\d{8}',          # file_20231227.xlsx
            r'[-_](copy|backup|old|archive|temp|final|draft)',  # file_copy.xlsx
            r'\(\d+\)'          # file (1).xlsx
        ]
        
        duplicates_data = []
        version_files = []
        total_exact_savings = Decimal(0)
        total_version_savings = Decimal(0)
        
        for dup in exact_duplicates:
            occurrence_count = dup.occurrence_count
            size_per_file = Decimal(str(dup.size_gb))
            potential_savings = size_per_file * (occurrence_count - 1)
            
            # Detect version files in the name
            is_version = any(re.search(pattern, dup.file_name, re.IGNORECASE) for pattern in version_patterns)
            confidence = 'Exact' if occurrence_count > 2 else 'High'
            
            dup_entry = {
                'file_name': dup.file_name,
                'extension': dup.extension or 'NO_EXTENSION',
                'size_gb': float(size_per_file),
                'occurrence_count': occurrence_count,
                'total_size_gb': float(dup.total_size_gb),
                'potential_savings_gb': float(potential_savings),
                'confidence': confidence,
                'is_version': is_version,
                'safe_to_delete': occurrence_count > 2  # More than 2 copies = definitely safe
            }
            
            duplicates_data.append(dup_entry)
            total_exact_savings += potential_savings
            
            if is_version:
                version_files.append(dup_entry)
                total_version_savings += potential_savings
        
        # Detect similar file names (fuzzy matching)
        similar_files = self._detect_similar_files(project_id)
        
        advanced_analysis = {
            'exact_duplicates': {
                'groups': duplicates_data[:50],  # Top 50
                'total_groups': len(duplicates_data),
                'total_files': sum(d['occurrence_count'] - 1 for d in duplicates_data),
                'total_savings_gb': float(total_exact_savings)
            },
            'version_files': {
                'groups': version_files[:20],  # Top 20
                'total_files': sum(v['occurrence_count'] - 1 for v in version_files),
                'total_savings_gb': float(total_version_savings)
            },
            'similar_files': similar_files,
            'summary': {
                'total_potential_savings_gb': float(total_exact_savings),
                'high_confidence_savings_gb': float(sum(
                    Decimal(str(d['potential_savings_gb'])) 
                    for d in duplicates_data 
                    if d['confidence'] == 'Exact'
                ))
            }
        }
        
        logger.info(f"Advanced duplicate analysis: {len(duplicates_data)} groups, {float(total_exact_savings):.2f} GB savings")
        return advanced_analysis
    
    def _detect_similar_files(self, project_id: int) -> Dict:
        """Detect files with similar names (potential versions/copies)"""
        # Query files grouped by base name patterns
        # This is a simplified version - full implementation would use Levenshtein distance
        
        similar_count = self.db.query(
            func.count(FileMetadata.id)
        ).filter(
            FileMetadata.project_id == project_id,
            func.lower(FileMetadata.file_name).like('%copy%')
            | func.lower(FileMetadata.file_name).like('%backup%')
            | func.lower(FileMetadata.file_name).like('%old%')
            | func.lower(FileMetadata.file_name).like('%temp%')
        ).scalar()
        
        similar_size = self.db.query(
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id,
            func.lower(FileMetadata.file_name).like('%copy%')
            | func.lower(FileMetadata.file_name).like('%backup%')
            | func.lower(FileMetadata.file_name).like('%old%')
            | func.lower(FileMetadata.file_name).like('%temp%')
        ).scalar()
        
        return {
            'suspected_count': similar_count or 0,
            'total_size_gb': float(similar_size or 0),
            'confidence': 'Medium',
            'note': 'Files with copy/backup/old/temp in filename'
        }
    
    def _analyze_directories(self, project_id: int) -> Dict:
        """
        PHASE 1: Directory-level analysis for storage optimization
        Identifies largest, deepest, and abandoned directories
        """
        # Top 20 largest directories by size
        largest_dirs = self.db.query(
            FileMetadata.directory_path,
            func.count(FileMetadata.id).label('file_count'),
            func.coalesce(func.sum(FileMetadata.size_gb), 0).label('total_size_gb'),
            func.max(FileMetadata.modified_date).label('last_modified'),
            func.max(FileMetadata.accessed_date).label('last_accessed')
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.directory_path.isnot(None)
        ).group_by(
            FileMetadata.directory_path
        ).order_by(
            func.sum(FileMetadata.size_gb).desc()
        ).limit(20).all()
        
        largest_directories = []
        for dir_info in largest_dirs:
            largest_directories.append({
                'path': dir_info.directory_path,
                'file_count': dir_info.file_count,
                'total_size_gb': float(dir_info.total_size_gb),
                'last_modified': dir_info.last_modified.isoformat() if dir_info.last_modified else None,
                'last_accessed': dir_info.last_accessed.isoformat() if dir_info.last_accessed else None
            })
        
        # Identify abandoned directories (not accessed in 1+ year)
        now = datetime.now()
        abandoned_dirs = self.db.query(
            FileMetadata.directory_path,
            func.count(FileMetadata.id).label('file_count'),
            func.coalesce(func.sum(FileMetadata.size_gb), 0).label('total_size_gb'),
            func.max(FileMetadata.accessed_date).label('last_accessed')
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.directory_path.isnot(None),
            FileMetadata.accessed_date < now - timedelta(days=365)
        ).group_by(
            FileMetadata.directory_path
        ).order_by(
            func.sum(FileMetadata.size_gb).desc()
        ).limit(20).all()
        
        abandoned_directories = []
        total_abandoned_size = Decimal(0)
        for dir_info in abandoned_dirs:
            size_gb = Decimal(str(dir_info.total_size_gb))
            abandoned_directories.append({
                'path': dir_info.directory_path,
                'file_count': dir_info.file_count,
                'total_size_gb': float(size_gb),
                'last_accessed': dir_info.last_accessed.isoformat() if dir_info.last_accessed else None,
                'archive_candidate': True
            })
            total_abandoned_size += size_gb
        
        # Detect temp/cache/backup directories by name patterns
        temp_patterns = ['temp', 'tmp', 'cache', 'backup', 'bak', 'old', 'archive']
        temp_dirs = self.db.query(
            func.count(FileMetadata.id).label('file_count'),
            func.coalesce(func.sum(FileMetadata.size_gb), 0).label('total_size_gb')
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.directory_path.isnot(None),
            or_(*[
                func.lower(FileMetadata.directory_path).like(f'%{pattern}%')
                for pattern in temp_patterns
            ])
        ).first()
        
        directory_analysis = {
            'largest_directories': largest_directories,
            'abandoned_directories': {
                'directories': abandoned_directories,
                'total_count': len(abandoned_directories),
                'total_size_gb': float(total_abandoned_size)
            },
            'temp_cache_directories': {
                'file_count': temp_dirs.file_count or 0,
                'total_size_gb': float(temp_dirs.total_size_gb or 0),
                'cleanup_potential': True
            },
            'total_directories_analyzed': len(largest_directories)
        }
        
        logger.info(f"Directory analysis: {len(largest_directories)} largest, {len(abandoned_directories)} abandoned")
        return directory_analysis
    
    def _validate_data_quality(self, project_id: int) -> Dict:
        """
        PHASE 1: Validate data quality and completeness
        Identifies missing fields, outliers, and anomalies
        """
        # Total files in project
        total_files = self.db.query(func.count(FileMetadata.id)).filter(
            FileMetadata.project_id == project_id
        ).scalar() or 0
        
        # Check for missing critical fields
        missing_size = self.db.query(func.count(FileMetadata.id)).filter(
            FileMetadata.project_id == project_id,
            or_(
                FileMetadata.size_gb.is_(None),
                FileMetadata.size_gb == 0
            )
        ).scalar() or 0
        
        missing_dates = self.db.query(func.count(FileMetadata.id)).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.modified_date.is_(None)
        ).scalar() or 0
        
        missing_accessed = self.db.query(func.count(FileMetadata.id)).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.accessed_date.is_(None)
        ).scalar() or 0
        
        missing_extension = self.db.query(func.count(FileMetadata.id)).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.extension.is_(None)
        ).scalar() or 0
        
        # Detect anomalies: files with future dates
        now = datetime.now()
        future_dates = self.db.query(func.count(FileMetadata.id)).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.modified_date > now
        ).scalar() or 0
        
        # Detect outliers: extremely large files (>100GB)
        large_files = self.db.query(
            func.count(FileMetadata.id),
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.size_gb > 100
        ).first()
        
        # Calculate completeness scores
        completeness = {
            'size': ((total_files - missing_size) / total_files * 100) if total_files > 0 else 0,
            'modified_date': ((total_files - missing_dates) / total_files * 100) if total_files > 0 else 0,
            'accessed_date': ((total_files - missing_accessed) / total_files * 100) if total_files > 0 else 0,
            'extension': ((total_files - missing_extension) / total_files * 100) if total_files > 0 else 0
        }
        
        overall_score = sum(completeness.values()) / len(completeness)
        
        quality_assessment = {
            'total_files': total_files,
            'completeness': {
                'size_data': float(completeness['size']),
                'modified_date': float(completeness['modified_date']),
                'accessed_date': float(completeness['accessed_date']),
                'extension': float(completeness['extension']),
                'overall_score': float(overall_score)
            },
            'missing_data': {
                'size_missing': missing_size,
                'dates_missing': missing_dates,
                'accessed_missing': missing_accessed,
                'extension_missing': missing_extension
            },
            'anomalies': {
                'future_dates': future_dates,
                'extremely_large_files': {
                    'count': large_files[0] or 0,
                    'total_size_gb': float(large_files[1] or 0)
                }
            },
            'quality_grade': self._calculate_quality_grade(overall_score)
        }
        
        logger.info(f"Data quality: {overall_score:.1f}% complete, Grade: {quality_assessment['quality_grade']}")
        return quality_assessment
    
    def _calculate_quality_grade(self, score: float) -> str:
        """Calculate quality grade based on completeness score"""
        if score >= 95:
            return 'Excellent'
        elif score >= 85:
            return 'Good'
        elif score >= 70:
            return 'Fair'
        elif score >= 50:
            return 'Poor'
        else:
            return 'Critical'
    
    def _generate_recommendations(self, project_id: int, analysis_data: Dict) -> List[Dict]:
        """
        PHASE 1: Generate prioritized, actionable recommendations
        Based on all analysis results with ROI calculations
        """
        recommendations = []
        
        # Recommendation 1: Archive old files
        storage_tiers = analysis_data.get('storage_tiers', [])
        archive_tier = next((t for t in storage_tiers if t['tier_name'] == 'Archive'), None)
        if archive_tier and archive_tier['total_size_gb'] > 10:
            archive_savings = archive_tier['total_size_gb'] * (float(TIER_PRICING['Hot']) - float(TIER_PRICING['Archive']))
            recommendations.append({
                'id': 'REC001',
                'priority': 'High',
                'category': 'Cost Optimization',
                'title': f"Archive {archive_tier['total_size_gb']:.1f}GB of rarely accessed files",
                'description': f"Move {archive_tier['file_count']:,} files (180 days - 3 years old, rarely accessed) to Archive tier",
                'impact': f"${archive_savings:.2f}/month savings (${archive_savings * 12:.2f}/year)",
                'effort': 'Medium',
                'roi_timeline': '1 month',
                'action_steps': [
                    'Review files in Archive tier recommendation',
                    'Verify files are truly inactive (check access logs)',
                    'Use Azure lifecycle policies to automate tiering',
                    'Monitor access patterns post-migration'
                ],
                'estimated_savings_monthly': float(archive_savings)
            })
        
        # Recommendation 2: Review deletion candidates (NOT auto-delete!)
        delete_tier = next((t for t in storage_tiers if t['tier_name'] == 'Delete'), None)
        if delete_tier and delete_tier['total_size_gb'] > 1:  # Only if > 1GB
            delete_savings = delete_tier['total_size_gb'] * float(TIER_PRICING['Hot'])
            recommendations.append({
                'id': 'REC002',
                'priority': 'Medium',  # Lowered from Critical
                'category': 'Data Hygiene',
                'title': f"Review {delete_tier['total_size_gb']:.1f}GB of potential deletion candidates",
                'description': f"Examine {delete_tier['file_count']:,} files (3+ years old, temp/backup patterns) for possible deletion. MANUAL REVIEW REQUIRED.",
                'impact': f"${delete_savings:.2f}/month potential savings (${delete_savings * 12:.2f}/year) if deleted",
                'effort': 'High',
                'roi_timeline': 'Requires stakeholder approval',
                'action_steps': [
                    '⚠️ DO NOT auto-delete - manual review required',
                    'Review file list with business owners',
                    'Identify truly obsolete temp/backup files',
                    'Get written approval before deletion',
                    'Backup files before deletion as safety measure',
                    'Implement formal retention policy going forward'
                ],
                'estimated_savings_monthly': float(delete_savings),
                'warning': 'Deletion requires careful review and stakeholder approval'
            })
        
        # Recommendation 3: Remove duplicates
        duplicates = analysis_data.get('duplicates_advanced', {})
        exact_dups = duplicates.get('exact_duplicates', {})
        if exact_dups.get('total_savings_gb', 0) > 1:
            dup_savings = exact_dups['total_savings_gb'] * float(TIER_PRICING['Hot'])
            recommendations.append({
                'id': 'REC003',
                'priority': 'High',
                'category': 'Data Hygiene',
                'title': f"Remove {exact_dups['total_files']:,} duplicate files",
                'description': f"Eliminate {exact_dups['total_savings_gb']:.1f}GB of duplicated data",
                'impact': f"${dup_savings:.2f}/month savings + improved data organization",
                'effort': 'Medium',
                'roi_timeline': '2 weeks',
                'action_steps': [
                    'Review duplicate file report',
                    'Keep one master copy, delete others',
                    'Implement version control for documents',
                    'Educate users on file management'
                ],
                'estimated_savings_monthly': float(dup_savings)
            })
        
        # Recommendation 4: Clean up abandoned directories
        dir_analysis = analysis_data.get('directory_analysis', {})
        abandoned = dir_analysis.get('abandoned_directories', {})
        if abandoned.get('total_size_gb', 0) > 10:
            abandoned_savings = abandoned['total_size_gb'] * float(TIER_PRICING['Hot'])
            recommendations.append({
                'id': 'REC004',
                'priority': 'Medium',
                'category': 'Data Hygiene',
                'title': f"Archive {abandoned['total_count']} abandoned directories",
                'description': f"Move {abandoned['total_size_gb']:.1f}GB from inactive directories",
                'impact': f"${abandoned_savings:.2f}/month potential savings",
                'effort': 'Low',
                'roi_timeline': '1 month',
                'action_steps': [
                    'Review abandoned directory list',
                    'Contact directory owners for confirmation',
                    'Archive or delete as appropriate',
                    'Set up monitoring for future abandonment'
                ],
                'estimated_savings_monthly': float(abandoned_savings)
            })
        
        # Recommendation 5: Data quality improvements
        data_quality = analysis_data.get('data_quality', {})
        quality_score = data_quality.get('completeness', {}).get('overall_score', 100)
        if quality_score < 85:
            recommendations.append({
                'id': 'REC005',
                'priority': 'Medium',
                'category': 'Data Quality',
                'title': f"Improve data quality (current score: {quality_score:.1f}%)",
                'description': 'Address missing metadata and data anomalies',
                'impact': 'Better analysis accuracy and decision-making',
                'effort': 'Low',
                'roi_timeline': 'Ongoing',
                'action_steps': [
                    'Re-run data collection scripts on affected servers',
                    'Update file metadata where missing',
                    'Fix date/time anomalies',
                    'Implement data validation in collection process'
                ],
                'estimated_savings_monthly': 0
            })
        
        # Recommendation 6: Access-based tiering
        access_patterns = analysis_data.get('access_patterns', {})
        zombie = access_patterns.get('zombie_files', {})
        if zombie.get('total_size_gb', 0) > 5:
            zombie_savings = zombie['total_size_gb'] * (float(TIER_PRICING['Hot']) - float(TIER_PRICING['Archive']))
            recommendations.append({
                'id': 'REC006',
                'priority': 'High',
                'category': 'Cost Optimization',
                'title': f"Archive {zombie['count']:,} zombie files",
                'description': f"Large files ({zombie['total_size_gb']:.1f}GB) not accessed in 2+ years",
                'impact': f"${zombie_savings:.2f}/month savings",
                'effort': 'Low',
                'roi_timeline': 'Immediate',
                'action_steps': [
                    'Review zombie file list',
                    'Confirm no business need',
                    'Move to Archive or Delete',
                    'Enable access-based lifecycle policies'
                ],
                'estimated_savings_monthly': float(zombie_savings)
            })
        
        # Sort by priority and estimated savings
        priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        recommendations.sort(key=lambda x: (
            priority_order.get(x['priority'], 4),
            -x.get('estimated_savings_monthly', 0)
        ))
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
    
    def _save_analysis_results(self, project_id: int, analysis_data: Dict):
        """Save all analysis results to database as JSON"""
        # Check if results already exist
        existing = self.db.query(AnalysisResults).filter(
            AnalysisResults.project_id == project_id
        ).first()
        
        if existing:
            # Update existing
            existing.age_distribution = json.dumps(analysis_data['age_distribution'])
            existing.file_types = json.dumps(analysis_data['file_types'])
            existing.storage_tiers = json.dumps(analysis_data['storage_tiers'])
            existing.cost_analysis = json.dumps(analysis_data['cost_analysis'])
            existing.growth_projection = json.dumps(analysis_data['growth_projection'])
            existing.duplicate_files = json.dumps(analysis_data.get('duplicate_files', {}))
            existing.script_metadata = json.dumps(analysis_data.get('script_metadata', {}))
            # PHASE 1: Save new enhanced analysis results
            existing.access_patterns = json.dumps(analysis_data.get('access_patterns', {}))
            existing.duplicates_advanced = json.dumps(analysis_data.get('duplicates_advanced', {}))
            existing.directory_analysis = json.dumps(analysis_data.get('directory_analysis', {}))
            existing.data_quality = json.dumps(analysis_data.get('data_quality', {}))
            existing.recommendations = json.dumps(analysis_data.get('recommendations', []))
            existing.analyzed_at = datetime.now()
        else:
            # Create new
            results = AnalysisResults(
                project_id=project_id,
                age_distribution=json.dumps(analysis_data['age_distribution']),
                file_types=json.dumps(analysis_data['file_types']),
                storage_tiers=json.dumps(analysis_data['storage_tiers']),
                cost_analysis=json.dumps(analysis_data['cost_analysis']),
                growth_projection=json.dumps(analysis_data['growth_projection']),
                duplicate_files=json.dumps(analysis_data.get('duplicate_files', {})),
                script_metadata=json.dumps(analysis_data.get('script_metadata', {})),
                # PHASE 1: Save new enhanced analysis results
                access_patterns=json.dumps(analysis_data.get('access_patterns', {})),
                duplicates_advanced=json.dumps(analysis_data.get('duplicates_advanced', {})),
                directory_analysis=json.dumps(analysis_data.get('directory_analysis', {})),
                data_quality=json.dumps(analysis_data.get('data_quality', {})),
                recommendations=json.dumps(analysis_data.get('recommendations', []))
            )
            self.db.add(results)
        
        self.db.commit()
        logger.info(f"Analysis results saved for project {project_id}")

    
    def _calculate_totals(self, project_id: int):
        """Calculate total files and size"""
        result = self.db.query(
            func.count(FileMetadata.id),
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id
        ).first()
        
        return result[0] or 0, Decimal(str(result[1] or 0))
    
    def _get_or_create_summary(self, project_id: int) -> AnalysisSummary:
        """Get or create analysis summary record"""
        summary = self.db.query(AnalysisSummary).filter(
            AnalysisSummary.project_id == project_id
        ).first()
        
        if not summary:
            summary = AnalysisSummary(
                project_id=project_id,
                total_files=0,
                total_size_gb=Decimal(0),
                analyzed_files_count=0,
                analysis_status='pending'
            )
            self.db.add(summary)
            self.db.commit()
        
        return summary
    
    # Helper functions
    def _extract_extension(self, ext: str) -> str:
        """Clean file extension"""
        if not ext:
            return None
        ext = ext.strip().lower()
        if not ext.startswith('.'):
            ext = '.' + ext
        return ext
    
    def _parse_int(self, value: str) -> int:
        """Parse integer from string, handling commas"""
        try:
            if not value:
                return None
            # Remove commas if present
            clean_value = str(value).replace(',', '').strip()
            return int(float(clean_value))
        except (ValueError, TypeError):
            return None
    
    def _parse_decimal(self, value: str) -> Decimal:
        """Parse decimal from string, handling commas"""
        try:
            if not value:
                return None
            # Remove commas if present
            clean_value = str(value).replace(',', '').strip()
            return Decimal(clean_value)
        except (ValueError, TypeError, decimal.InvalidOperation):
            return None
    
    def _parse_date(self, value: str) -> datetime:
        """Parse date from string"""
        if not value:
            return None
        try:
            # Try multiple date formats (most common first for performance)
            for fmt in [
                '%m/%d/%Y %I:%M:%S %p',  # 4/20/2018 5:38:48 PM (PowerShell default)
                '%m/%d/%Y %H:%M:%S',      # 4/20/2018 17:38:48 (24-hour)
                '%Y-%m-%d %H:%M:%S',      # 2018-04-20 17:38:48 (ISO-like)
                '%Y-%m-%d',               # 2018-04-20 (date only)
                '%m/%d/%Y'                # 4/20/2018 (date only)
            ]:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None
