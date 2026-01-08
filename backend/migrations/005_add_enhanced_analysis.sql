-- Migration: Add Enhanced Analysis Features (Phase 1)
-- Date: 2026-01-05
-- Description: Adds new JSON columns for access patterns, advanced duplicates, 
--              directory analysis, data quality, and recommendations

-- Add new analysis columns to the results table
ALTER TABLE dbo.tpsm_analysis_results
ADD access_patterns NVARCHAR(MAX) NULL;

ALTER TABLE dbo.tpsm_analysis_results
ADD duplicates_advanced NVARCHAR(MAX) NULL;

ALTER TABLE dbo.tpsm_analysis_results
ADD directory_analysis NVARCHAR(MAX) NULL;

ALTER TABLE dbo.tpsm_analysis_results
ADD data_quality NVARCHAR(MAX) NULL;

ALTER TABLE dbo.tpsm_analysis_results
ADD recommendations NVARCHAR(MAX) NULL;

-- Add comments for documentation
EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Access frequency analysis: Hot/Warm/Cold/Frozen files based on accessed_date', 
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'tpsm_analysis_results',
    @level2type = N'COLUMN', @level2name = 'access_patterns';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Advanced duplicate detection with confidence scoring and version analysis', 
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'tpsm_analysis_results',
    @level2type = N'COLUMN', @level2name = 'duplicates_advanced';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Directory-level insights: largest dirs, abandoned dirs, archive candidates', 
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'tpsm_analysis_results',
    @level2type = N'COLUMN', @level2name = 'directory_analysis';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Data quality assessment: completeness, accuracy, anomalies', 
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'tpsm_analysis_results',
    @level2type = N'COLUMN', @level2name = 'data_quality';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Prioritized actionable recommendations with ROI and effort estimates', 
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'tpsm_analysis_results',
    @level2type = N'COLUMN', @level2name = 'recommendations';

PRINT 'Enhanced analysis columns added successfully';
