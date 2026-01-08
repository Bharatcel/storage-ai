-- Migration: Performance Indexes (Phase 1)
-- Date: 2026-01-05
-- Description: Adds indexes to improve query performance for analysis operations

-- Index for age distribution analysis (queries on modified_date)
CREATE NONCLUSTERED INDEX IX_FileMetadata_Project_ModifiedDate
ON dbo.tpsm_file_metadata (project_id, modified_date)
INCLUDE (size_gb, file_count);

-- Index for access pattern analysis (queries on accessed_date)
CREATE NONCLUSTERED INDEX IX_FileMetadata_Project_AccessedDate
ON dbo.tpsm_file_metadata (project_id, accessed_date)
INCLUDE (size_gb, file_name, directory_path);

-- Index for file type analysis (queries on extension)
CREATE NONCLUSTERED INDEX IX_FileMetadata_Project_Extension
ON dbo.tpsm_file_metadata (project_id, extension)
INCLUDE (size_gb);

-- Index for duplicate detection (queries on size, extension, file_name)
CREATE NONCLUSTERED INDEX IX_FileMetadata_Duplicates
ON dbo.tpsm_file_metadata (project_id, size_gb, extension, file_name)
INCLUDE (directory_path, server_name);

-- Index for directory analysis (queries on directory_path)
CREATE NONCLUSTERED INDEX IX_FileMetadata_Project_Directory
ON dbo.tpsm_file_metadata (project_id, directory_path)
INCLUDE (size_gb, file_count, modified_date);

-- Index for server-based queries
CREATE NONCLUSTERED INDEX IX_FileMetadata_Project_Server
ON dbo.tpsm_file_metadata (project_id, server_name)
INCLUDE (size_gb, file_count);

-- Statistics update for better query optimization
UPDATE STATISTICS dbo.tpsm_file_metadata WITH FULLSCAN;

PRINT 'Performance indexes created successfully';
