-- Migration: Add tpsm_script_results table
-- Date: 2025-12-16
-- Description: Store metadata for uploaded script result files

-- Create the script results table
CREATE TABLE dbo.tpsm_script_results (
    id INT PRIMARY KEY IDENTITY(1,1),
    project_id INT NOT NULL,
    original_filename NVARCHAR(500) NOT NULL,
    stored_filename NVARCHAR(500) NOT NULL,
    blob_url NVARCHAR(1000) NOT NULL,
    file_size INT NOT NULL,
    file_type NVARCHAR(100) NULL,
    uploaded_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    -- Foreign key constraint
    CONSTRAINT FK_script_results_project 
        FOREIGN KEY (project_id) 
        REFERENCES dbo.tpsm_projects(id)
        ON DELETE CASCADE
);

-- Create index on project_id for faster queries
CREATE INDEX IX_script_results_project_id 
    ON dbo.tpsm_script_results(project_id);

-- Create index on uploaded_at for sorting
CREATE INDEX IX_script_results_uploaded_at 
    ON dbo.tpsm_script_results(uploaded_at DESC);

PRINT 'Table dbo.tpsm_script_results created successfully';
