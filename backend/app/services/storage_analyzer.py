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
from sqlalchemy import func
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
            for csv_file in csv_files:
                rows = await self._parse_csv_file(csv_file, project_id)
                total_rows += rows
            
            logger.info(f"Parsed {total_rows} rows from {len(csv_files)} CSV files")
            
            # Run all analyses and store in single JSON record
            analysis_data = {}
            analysis_data['age_distribution'] = self._analyze_age_distribution(project_id)
            analysis_data['file_types'] = self._analyze_file_types(project_id)
            analysis_data['storage_tiers'] = self._analyze_storage_tiers(project_id)
            analysis_data['cost_analysis'] = self._calculate_costs(analysis_data['storage_tiers'])
            analysis_data['growth_projection'] = self._project_growth(project_id)
            
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
        """Parse a single CSV file and store metadata"""
        try:
            # Download CSV from blob storage
            blob_content = await self._download_blob(csv_file.blob_url)
            
            # Parse CSV
            csv_text = blob_content.decode('utf-8-sig')  # Handle BOM
            reader = csv.DictReader(io.StringIO(csv_text))
            
            rows_processed = 0
            batch = []
            
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
                
                # Batch insert every 1000 rows
                if len(batch) >= 1000:
                    self.db.bulk_save_objects(batch)
                    self.db.commit()
                    batch = []
            
            # Insert remaining rows
            if batch:
                self.db.bulk_save_objects(batch)
                self.db.commit()
            
            logger.info(f"Parsed {rows_processed} rows from {csv_file.original_filename}")
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
        """Recommend storage tiers based on access patterns - returns data"""
        now = datetime.now()
        tiers = {
            'Hot': 30,      # Modified in last 30 days
            'Cool': 90,     # Modified 30-90 days ago
            'Archive': 365, # Modified 90-365 days ago
            'Delete': None  # Modified >365 days ago or temp files
        }
        
        tier_stats = {}
        
        # Hot tier: < 30 days
        result = self.db.query(
            func.count(FileMetadata.id),
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.modified_date >= now - timedelta(days=30)
        ).first()
        tier_stats['Hot'] = {'count': result[0], 'size_gb': Decimal(str(result[1]))}
        
        # Cool tier: 30-90 days
        result = self.db.query(
            func.count(FileMetadata.id),
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.modified_date >= now - timedelta(days=90),
            FileMetadata.modified_date < now - timedelta(days=30)
        ).first()
        tier_stats['Cool'] = {'count': result[0], 'size_gb': Decimal(str(result[1]))}
        
        # Archive tier: 90-365 days
        result = self.db.query(
            func.count(FileMetadata.id),
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.modified_date >= now - timedelta(days=365),
            FileMetadata.modified_date < now - timedelta(days=90)
        ).first()
        tier_stats['Archive'] = {'count': result[0], 'size_gb': Decimal(str(result[1]))}
        
        # Delete candidates: > 365 days
        result = self.db.query(
            func.count(FileMetadata.id),
            func.coalesce(func.sum(FileMetadata.size_gb), 0)
        ).filter(
            FileMetadata.project_id == project_id,
            FileMetadata.modified_date < now - timedelta(days=365)
        ).first()
        tier_stats['Delete'] = {'count': result[0], 'size_gb': Decimal(str(result[1]))}
        
        # Calculate totals and return as list
        total_size = sum(stats['size_gb'] for stats in tier_stats.values())
        
        storage_tiers = []
        for tier_name, stats in tier_stats.items():
            percentage = (stats['size_gb'] / total_size * 100) if total_size > 0 else Decimal(0)
            monthly_cost = stats['size_gb'] * TIER_PRICING[tier_name]
            
            storage_tiers.append({
                'tier_name': tier_name,
                'file_count': stats['count'],
                'total_size_gb': float(stats['size_gb']),
                'percentage': float(percentage),
                'monthly_cost': float(monthly_cost)
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
            existing.analyzed_at = datetime.now()
        else:
            # Create new
            results = AnalysisResults(
                project_id=project_id,
                age_distribution=json.dumps(analysis_data['age_distribution']),
                file_types=json.dumps(analysis_data['file_types']),
                storage_tiers=json.dumps(analysis_data['storage_tiers']),
                cost_analysis=json.dumps(analysis_data['cost_analysis']),
                growth_projection=json.dumps(analysis_data['growth_projection'])
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
        """Parse date from string, handling multiple formats"""
        if not value:
            return None
        
        try:
            # Try format: 12/27/2023 8:04:45 PM (US format with AM/PM)
            if '/' in value and ('AM' in value or 'PM' in value):
                return datetime.strptime(value, '%m/%d/%Y %I:%M:%S %p')
            # Try format: 2023-12-27 20:04:45
            elif '-' in value:
                return datetime.strptime(value.split('.')[0], '%Y-%m-%d %H:%M:%S')
            # Try format: 12/27/2023 20:04:45 (US format 24-hour)
            elif '/' in value:
                return datetime.strptime(value, '%m/%d/%Y %H:%M:%S')
            else:
                return None
        except (ValueError, TypeError):
            return None
        except (ValueError, TypeError):
            return None
    
    def _parse_date(self, value: str) -> datetime:
        """Parse date from string"""
        if not value:
            return None
        try:
            # Try multiple date formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y']:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None
