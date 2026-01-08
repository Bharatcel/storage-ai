-- Migration: Add duplicate file and script metadata analysis columns
-- Date: 2025-12-30
-- Description: Extends AnalysisResults table with duplicate detection and script metadata

USE [aznprd-neu-ghub-sqldb01];
GO

-- Add new columns to store duplicate file analysis and script metadata
ALTER TABLE dbo.tpsm_analysis_results
ADD 
    duplicate_files NVARCHAR(MAX) NULL,  -- JSON: Duplicate file analysis
    script_metadata NVARCHAR(MAX) NULL;  -- JSON: Script generation metadata

GO

PRINT 'Migration 003 completed: Added duplicate_files and script_metadata columns';
GO
