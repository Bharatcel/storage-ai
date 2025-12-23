# Simplified Storage Analysis Schema (3 Tables)

## Database Structure

### **Table 1: tpsm_file_metadata**
- **Purpose**: Store raw parsed CSV file data
- **Row Count**: Can grow to millions (one row per file or aggregated entry)
- **Columns**: 16 columns including server_name, drive_letter, directory_path, file_name, extension, sizes (bytes/MB/GB), dates (created/modified/accessed)
- **Foreign Keys**: project_id → tpsm_projects, result_file_id → tpsm_script_results

### **Table 2: tpsm_analysis_results**  
- **Purpose**: Store all 5 analysis types in JSON format
- **Row Count**: 1 row per project
- **Columns**:
  - `age_distribution` (JSON) - Array of 5 age buckets
  - `file_types` (JSON) - Array of file extensions (top 50)
  - `storage_tiers` (JSON) - Array of 4 tiers (Hot/Cool/Archive/Delete)
  - `cost_analysis` (JSON) - Single object with cost breakdown
  - `growth_projection` (JSON) - Single object with projections
- **Foreign Key**: project_id → tpsm_projects

### **Table 3: tpsm_analysis_summary**
- **Purpose**: Track analysis status and summary metrics
- **Row Count**: 1 row per project
- **Columns**: total_files, total_size_gb, analyzed_files_count, analysis_status, error_message, timestamps
- **Foreign Key**: project_id → tpsm_projects

## Migration SQL

Execute this in Azure SQL Database:

```sql
-- Table 1: File Metadata (Raw Data)
CREATE TABLE dbo.tpsm_file_metadata ( ... );

-- Table 2: Analysis Results (JSON)
CREATE TABLE dbo.tpsm_analysis_results (
    id INT PRIMARY KEY IDENTITY(1,1),
    project_id INT NOT NULL UNIQUE,
    age_distribution NVARCHAR(MAX) NULL,
    file_types NVARCHAR(MAX) NULL,
    storage_tiers NVARCHAR(MAX) NULL,
    cost_analysis NVARCHAR(MAX) NULL,
    growth_projection NVARCHAR(MAX) NULL,
    analyzed_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (project_id) REFERENCES dbo.tpsm_projects(id) ON DELETE CASCADE
);

-- Table 3: Analysis Summary (Status)
CREATE TABLE dbo.tpsm_analysis_summary ( ... );

-- Indexes
CREATE INDEX IX_file_metadata_project ON dbo.tpsm_file_metadata(project_id);
CREATE INDEX IX_analysis_results_project ON dbo.tpsm_analysis_results(project_id);
CREATE INDEX IX_analysis_summary_project ON dbo.tpsm_analysis_summary(project_id);
CREATE INDEX IX_analysis_summary_status ON dbo.tpsm_analysis_summary(analysis_status);
```

## JSON Data Structure

### Age Distribution Example
```json
[
  {"age_bucket": "<6m", "file_count": 50000, "total_size_gb": 250.5, "percentage": 30.2},
  {"age_bucket": "6m-1Y", "file_count": 30000, "total_size_gb": 180.3, "percentage": 21.7},
  {"age_bucket": "1-3Y", "file_count": 20000, "total_size_gb": 150.0, "percentage": 18.1},
  {"age_bucket": "3-5Y", "file_count": 15000, "total_size_gb": 125.2, "percentage": 15.1},
  {"age_bucket": ">5Y", "file_count": 10000, "total_size_gb": 124.0, "percentage": 14.9}
]
```

### File Types Example
```json
[
  {"extension": ".pdf", "file_count": 25000, "total_size_gb": 300.5, "percentage": 25.3},
  {"extension": ".docx", "file_count": 20000, "total_size_gb": 150.2, "percentage": 12.6},
  ...
]
```

### Storage Tiers Example
```json
[
  {"tier_name": "Hot", "file_count": 30000, "total_size_gb": 200.0, "percentage": 20.0, "monthly_cost": 3.68},
  {"tier_name": "Cool", "file_count": 25000, "total_size_gb": 250.0, "percentage": 25.0, "monthly_cost": 2.50},
  {"tier_name": "Archive", "file_count": 40000, "total_size_gb": 450.0, "percentage": 45.0, "monthly_cost": 0.45},
  {"tier_name": "Delete", "file_count": 10000, "total_size_gb": 100.0, "percentage": 10.0, "monthly_cost": 0.00}
]
```

### Cost Analysis Example
```json
{
  "current_monthly_cost": 18.40,
  "optimized_monthly_cost": 6.63,
  "monthly_savings": 11.77,
  "savings_percentage": 64.02,
  "annual_savings": 141.24
}
```

### Growth Projection Example
```json
{
  "current_size_gb": 1000.0,
  "projected_6m_gb": 1075.0,
  "projected_1y_gb": 1150.0,
  "projected_3y_gb": 1520.9,
  "annual_growth_rate_pct": 15.0,
  "confidence_level": "Medium"
}
```

## Benefits of Simplified Design

✅ **Reduced Complexity**: 3 tables instead of 7 (57% reduction)
✅ **Easier Management**: Fewer migrations, less schema management
✅ **Flexible**: Easy to add new analysis types without schema changes
✅ **Maintained Performance**: File metadata still separate and indexed
✅ **Same API Response**: Frontend receives identical JSON structure

## Files Updated

1. ✅ `backend/migrations/002_add_analysis_tables.sql` - New 3-table schema
2. ✅ `backend/app/models.py` - Removed 5 models, added AnalysisResults model
3. ✅ `backend/app/services/storage_analyzer.py` - Returns data instead of saving to separate tables
4. ✅ `backend/app/routes/analysis_routes.py` - Parses JSON from database

## Installation Steps

1. **Run Migration**:
   ```powershell
   # Execute in Azure SQL via Azure Portal Query Editor or Azure Data Studio
   ```

2. **Install Chart.js** (if not already done):
   ```powershell
   cd frontend
   npm install chart.js react-chartjs-2
   ```

3. **Start Application**:
   ```powershell
   # Backend
   cd backend
   uvicorn main:app --reload

   # Frontend
   cd frontend
   npm start
   ```

## Verification Query

After migration, verify tables:

```sql
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE 'tpsm_%analysis%' 
   OR TABLE_NAME LIKE 'tpsm_file_metadata'
ORDER BY TABLE_NAME;

-- Should return:
-- tpsm_analysis_results
-- tpsm_analysis_summary
-- tpsm_file_metadata
```

## Frontend - No Changes Required!

The frontend components work exactly the same because the API returns identical JSON structure. No changes needed to:
- ProjectsList.js
- AnalysisDashboard.js
- api.js

The refactoring is completely backend-only! 🎉
