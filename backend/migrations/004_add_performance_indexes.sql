-- Add indexes to improve query performance
-- Run this migration to speed up analysis queries

-- Index for file metadata queries by project
CREATE NONCLUSTERED INDEX idx_file_metadata_project 
ON dbo.tpsm_file_metadata(project_id) 
INCLUDE (size_gb, extension, modified_date);

-- Index for age-based queries
CREATE NONCLUSTERED INDEX idx_file_metadata_modified_date 
ON dbo.tpsm_file_metadata(project_id, modified_date) 
INCLUDE (size_gb);

-- Index for file type analysis
CREATE NONCLUSTERED INDEX idx_file_metadata_extension 
ON dbo.tpsm_file_metadata(project_id, extension) 
INCLUDE (size_gb);

-- Index for duplicate detection (composite on name, size, extension)
CREATE NONCLUSTERED INDEX idx_file_metadata_duplicates 
ON dbo.tpsm_file_metadata(project_id, file_name, size_gb, extension);

-- Index for script results by project
CREATE NONCLUSTERED INDEX idx_script_results_project 
ON dbo.tpsm_script_results(project_id) 
INCLUDE (original_filename, blob_url);

PRINT 'Performance indexes created successfully';
