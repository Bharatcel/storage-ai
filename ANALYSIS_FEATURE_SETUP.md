# Storage Analysis Feature - Setup Guide

## Overview
This document provides instructions for setting up and using the new storage analysis feature that has been added to the Assessment App.

## New Features Added

### 1. **Database Schema**
- 7 new tables for storing parsed CSV data and analysis results:
  - `tpsm_file_metadata` - Raw file data from uploaded CSVs
  - `tpsm_age_analysis` - Age distribution analysis
  - `tpsm_filetype_analysis` - File type analysis
  - `tpsm_tier_recommendations` - Storage tier recommendations
  - `tpsm_cost_analysis` - Cost optimization analysis
  - `tpsm_growth_projections` - Future growth projections
  - `tpsm_analysis_summary` - Overall analysis status tracking

### 2. **Backend Components**
- **Storage Analyzer Service** (`backend/app/services/storage_analyzer.py`)
  - Parses CSV files from Azure Blob Storage
  - Performs 5 types of analysis:
    * Age distribution (categorizes files by modified date)
    * File type analysis (groups by extension)
    * Storage tier recommendations (Hot/Cool/Archive/Delete)
    * Cost analysis (current vs optimized costs with savings)
    * Growth projections (6m/1y/3y forecasts)

- **Analysis API Routes** (`backend/app/routes/analysis_routes.py`)
  - `POST /api/analysis/trigger/{project_id}` - Start analysis
  - `GET /api/analysis/status/{project_id}` - Check analysis status
  - `GET /api/analysis/results/{project_id}` - Get analysis results
  - `DELETE /api/analysis/results/{project_id}` - Delete analysis to re-run

### 3. **Frontend Components**
- **Projects List** (`frontend/src/components/ProjectsList.js`)
  - View all your assessment projects
  - "Analyze" button for each project
  - Shows analysis status (processing/completed)
  - Real-time status polling during analysis
  - "View Analysis" button when completed

- **Analysis Dashboard** (`frontend/src/components/AnalysisDashboard.js`)
  - Interactive charts (Pie, Bar, Line charts using Chart.js)
  - Summary cards showing total files, storage size, potential savings
  - Age distribution visualization
  - Top file types bar chart
  - Storage tier recommendations with costs
  - Growth projection timeline
  - Cost comparison (current vs optimized)
  - Detailed data tables

## Installation Steps

### 1. Database Migration

Run the new migration script to create the analysis tables:

```powershell
# Navigate to backend directory
cd backend

# Run migration using your database connection
# Option 1: Using sqlcmd (if installed)
sqlcmd -S aznprd-neu-ghub-sql01-01.database.windows.net -d aznprd-neu-ghub-sqldb01 -i migrations/002_add_analysis_tables.sql

# Option 2: Using Azure Data Studio or SQL Server Management Studio
# Open migrations/002_add_analysis_tables.sql and execute it
```

### 2. Backend Setup

No new Python packages are required - all dependencies are already in your existing `requirements.txt`.

```powershell
# If you need to verify/reinstall dependencies
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup

Install Chart.js for data visualization:

```powershell
cd frontend
npm install chart.js react-chartjs-2
```

### 4. Start the Application

```powershell
# Terminal 1 - Start Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Start Frontend
cd frontend
npm start
```

## How to Use

### Workflow

1. **Create Assessment** (Existing flow)
   - Go to homepage
   - Fill in project details
   - Answer assessment questions
   - Upload script result CSV files

2. **View Projects**
   - Click "My Projects" in the header navigation
   - See all your assessment projects

3. **Run Analysis**
   - Click "Analyze" button on any project
   - Wait for analysis to complete (status updates automatically)
   - Analysis processes all uploaded CSV files for that project

4. **View Analysis Results**
   - Click "View Analysis →" button when analysis is completed
   - See interactive dashboard with:
     * Summary metrics (total files, storage, potential savings)
     * Age distribution pie chart
     * File type analysis bar chart
     * Storage tier recommendations
     * Cost analysis (current vs optimized)
     * Growth projections

### CSV File Requirements

The analysis expects CSV files with the following columns:
- `ServerName` - Name of the server
- `Drive` - Drive letter
- `Directory` - Directory path
- `FileName` - File name
- `Extension` - File extension
- `SizeBytes` - File size in bytes
- `SizeMB` - File size in MB
- `SizeGB` - File size in GB
- `CreatedDate` - File creation date
- `ModifiedDate` - File last modified date
- `AccessedDate` - File last accessed date
- `FileCount` (optional) - Count of files (for aggregated data)

## Analysis Details

### Age Distribution Buckets
- **<6 months** - Recently created/modified files
- **6 months - 1 year** - Semi-recent files
- **1-3 years** - Moderately old files
- **3-5 years** - Old files
- **>5 years** - Very old files

### Storage Tier Recommendations
- **Hot** - Files modified in last 30 days (frequent access)
- **Cool** - Files modified 30-90 days ago (infrequent access)
- **Archive** - Files modified 90-365 days ago (rare access)
- **Delete** - Files not modified in >365 days (consider deletion)

### Pricing (Azure Blob Storage - December 2025)
- Hot: $0.0184/GB/month
- Cool: $0.01/GB/month
- Archive: $0.00099/GB/month
- Delete: $0/GB/month

### Growth Projection
- Uses 15% annual growth rate (industry average)
- Projects 6 months, 1 year, and 3 years into future
- In Phase 2, this will use historical data for better accuracy

## API Endpoints

### Analysis Endpoints

**Trigger Analysis**
```http
POST /api/analysis/trigger/{project_id}
Response: { "message": "Analysis started", "project_id": 1, "status": "processing" }
```

**Check Status**
```http
GET /api/analysis/status/{project_id}
Response: {
  "project_id": 1,
  "status": "completed|processing|failed|not_started",
  "total_files": 1000000,
  "total_size_gb": 5000.50,
  "analyzed_files_count": 3,
  "started_at": "2025-01-15T10:30:00",
  "completed_at": "2025-01-15T10:35:00",
  "error_message": null
}
```

**Get Results**
```http
GET /api/analysis/results/{project_id}
Response: {
  "project_id": 1,
  "summary": { ... },
  "age_distribution": [ ... ],
  "file_types": [ ... ],
  "storage_tiers": [ ... ],
  "cost_analysis": { ... },
  "growth_projection": { ... }
}
```

**Delete Results** (to re-run analysis)
```http
DELETE /api/analysis/results/{project_id}
```

## Troubleshooting

### Analysis Fails
1. **Check CSV format** - Ensure all required columns are present
2. **Check blob storage** - Verify files were uploaded successfully
3. **Check logs** - Look for error messages in backend console
4. **Check database** - Verify migration ran successfully

### Charts Not Displaying
1. **Verify Chart.js installation** - `npm list chart.js react-chartjs-2`
2. **Check browser console** - Look for JavaScript errors
3. **Clear cache** - Hard refresh browser (Ctrl+Shift+R)

### Analysis Stuck in "Processing"
1. **Check backend console** - Look for errors
2. **Check database** - Query `tpsm_analysis_summary` table
3. **Re-trigger analysis** - Delete results and try again

## Testing

### Sample Test Data
Use the provided sample CSV file: `DC1IOPSUAT-20231227-2004-DriveFileDetails.csv`

### Manual Testing Steps
1. Create a new assessment
2. Upload the sample CSV file
3. Navigate to Projects list
4. Click "Analyze" on the new project
5. Wait for completion (should take 10-30 seconds for sample file)
6. Click "View Analysis"
7. Verify all charts and tables display correctly

## Performance Notes

- **CSV Parsing**: Processes in batches of 1000 rows for memory efficiency
- **Analysis**: Runs asynchronously in background
- **Polling**: Frontend polls status every 2 seconds during analysis
- **Large Files**: Files with >1 million rows may take several minutes

## Future Enhancements (Phase 2)

1. **Duplicate Detection**
   - Identify duplicate files based on name, size, or hash
   - Calculate wasted storage from duplicates

2. **Historical Growth Analysis**
   - Track storage growth over time
   - Use historical data for more accurate projections

3. **Advanced Recommendations**
   - Machine learning for access pattern prediction
   - Custom tier recommendations based on business rules
   - File archival suggestions

4. **Export Functionality**
   - Export analysis reports to PDF
   - Export data to Excel
   - Scheduled email reports

5. **Real-time Analysis**
   - Stream processing for large files
   - Progress bar during analysis
   - Partial results preview

## Support

For issues or questions:
1. Check backend logs in the terminal
2. Check browser console for frontend errors
3. Verify database connectivity
4. Ensure all migrations have been run
5. Verify Azure Blob Storage credentials

## File Structure

```
backend/
├── app/
│   ├── models.py (updated with 7 new models)
│   ├── routes/
│   │   └── analysis_routes.py (new)
│   ├── services/
│   │   └── storage_analyzer.py (new)
│   └── migrations/
│       └── 002_add_analysis_tables.sql (new)
└── main.py (updated to include analysis routes)

frontend/
├── src/
│   ├── components/
│   │   ├── ProjectsList.js (new)
│   │   ├── ProjectsList.css (new)
│   │   ├── AnalysisDashboard.js (new)
│   │   ├── AnalysisDashboard.css (new)
│   │   └── AssessmentForm.js (updated with navigation)
│   ├── services/
│   │   └── api.js (updated with analysis APIs)
│   ├── App.js (updated with new routes)
│   └── App.css (updated with navigation)
```

## Conclusion

The storage analysis feature is now fully integrated into your Assessment App. Users can:
1. Upload CSV files from their storage assessment scripts
2. Trigger analysis with one click
3. View comprehensive analysis dashboard
4. Make informed decisions about storage optimization
5. Estimate cost savings from tier optimization

The feature provides actionable insights to help reduce storage costs by recommending appropriate storage tiers based on file access patterns.
