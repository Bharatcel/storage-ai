-- Migration: Add Storage Analysis Tables (Simplified 3-Table Design)
-- Date: 2025-12-23
-- Description: Tables for storing file metadata and analysis results

-- Table 1: File Metadata from uploaded CSVs (Raw Data)
CREATE TABLE dbo.tpsm_file_metadata (
    id BIGINT PRIMARY KEY IDENTITY(1,1),
    project_id INT NOT NULL,
    result_file_id INT NOT NULL,  -- Link to uploaded CSV file
    server_name NVARCHAR(255) NULL,
    drive_letter NVARCHAR(10) NULL,
    directory_path NVARCHAR(4000) NULL,
    file_name NVARCHAR(500) NULL,
    extension NVARCHAR(50) NULL,
    size_bytes BIGINT NULL,
    size_mb DECIMAL(18,2) NULL,
    size_gb DECIMAL(18,2) NULL,
    created_date DATETIME2 NULL,
    modified_date DATETIME2 NULL,
    accessed_date DATETIME2 NULL,
    file_count INT NULL,  -- For aggregated entries
    uploaded_at DATETIME2 DEFAULT GETDATE(),
    
    CONSTRAINT FK_file_metadata_project 
        FOREIGN KEY (project_id) REFERENCES dbo.tpsm_projects(id) ON DELETE CASCADE,
    CONSTRAINT FK_file_metadata_result_file
        FOREIGN KEY (result_file_id) REFERENCES dbo.tpsm_script_results(id) ON DELETE CASCADE
);

-- Table 2: Analysis Results (All analysis types in JSON)
CREATE TABLE dbo.tpsm_analysis_results (
    id INT PRIMARY KEY IDENTITY(1,1),
    project_id INT NOT NULL UNIQUE,
    
    -- Age Distribution (JSON array)
    age_distribution NVARCHAR(MAX) NULL,
    
    -- File Type Analysis (JSON array)
    file_types NVARCHAR(MAX) NULL,
    
    -- Storage Tier Recommendations (JSON array)
    storage_tiers NVARCHAR(MAX) NULL,
    
    -- Cost Analysis (JSON object)
    cost_analysis NVARCHAR(MAX) NULL,
    
    -- Growth Projection (JSON object)
    growth_projection NVARCHAR(MAX) NULL,
    
    analyzed_at DATETIME2 DEFAULT GETDATE(),
    
    CONSTRAINT FK_analysis_results_project 
        FOREIGN KEY (project_id) REFERENCES dbo.tpsm_projects(id) ON DELETE CASCADE
);

-- Table 3: Analysis Summary (Status Tracking)
CREATE TABLE dbo.tpsm_analysis_summary (
    id INT PRIMARY KEY IDENTITY(1,1),
    project_id INT NOT NULL UNIQUE,
    total_files BIGINT NOT NULL DEFAULT 0,
    total_size_gb DECIMAL(18,2) NOT NULL DEFAULT 0,
    analyzed_files_count INT NOT NULL DEFAULT 0,  -- Number of CSV files processed
    analysis_status NVARCHAR(50) NOT NULL,  -- 'pending', 'processing', 'completed', 'failed'
    error_message NVARCHAR(MAX) NULL,
    started_at DATETIME2 NULL,
    completed_at DATETIME2 NULL,
    
    CONSTRAINT FK_analysis_summary_project 
        FOREIGN KEY (project_id) REFERENCES dbo.tpsm_projects(id) ON DELETE CASCADE
);

-- Indexes for Performance
CREATE INDEX IX_file_metadata_project ON dbo.tpsm_file_metadata(project_id);
CREATE INDEX IX_file_metadata_modified ON dbo.tpsm_file_metadata(modified_date) WHERE modified_date IS NOT NULL;
CREATE INDEX IX_file_metadata_extension ON dbo.tpsm_file_metadata(extension) WHERE extension IS NOT NULL;
CREATE INDEX IX_file_metadata_size ON dbo.tpsm_file_metadata(size_bytes DESC) WHERE size_bytes IS NOT NULL;

CREATE INDEX IX_analysis_results_project ON dbo.tpsm_analysis_results(project_id);
CREATE INDEX IX_analysis_summary_project ON dbo.tpsm_analysis_summary(project_id);
CREATE INDEX IX_analysis_summary_status ON dbo.tpsm_analysis_summary(analysis_status);

PRINT 'Storage Analysis Tables created successfully (3 tables)';
