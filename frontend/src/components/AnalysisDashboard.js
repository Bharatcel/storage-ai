import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getAnalysisResults, getProject } from '../services/api';
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';
import './AnalysisDashboard.css';

// Register ChartJS components
ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

function AnalysisDashboard() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalysisData();
  }, [projectId]);

  const fetchAnalysisData = async () => {
    try {
      setLoading(true);
      const [projectData, analysis] = await Promise.all([
        getProject(projectId),
        getAnalysisResults(projectId)
      ]);
      setProject(projectData);
      setAnalysisData(analysis);
      setError(null);
    } catch (err) {
      setError('Failed to load analysis results');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getAgeDistributionChart = () => {
    if (!analysisData?.age_distribution) return null;

    const colors = ['#4caf50', '#8bc34a', '#ffc107', '#ff9800', '#f44336'];
    
    return {
      labels: analysisData.age_distribution.map(item => item.age_bucket),
      datasets: [{
        label: 'Storage Size (GB)',
        data: analysisData.age_distribution.map(item => item.total_size_gb),
        backgroundColor: colors,
        borderColor: colors.map(c => c),
        borderWidth: 1
      }]
    };
  };

  const getFileTypesChart = () => {
    if (!analysisData?.file_types) return null;

    const top10 = analysisData.file_types.slice(0, 10);
    
    return {
      labels: top10.map(item => item.extension),
      datasets: [{
        label: 'Storage Size (GB)',
        data: top10.map(item => item.total_size_gb),
        backgroundColor: '#2196f3',
        borderColor: '#1976d2',
        borderWidth: 1
      }]
    };
  };

  const getStorageTiersChart = () => {
    if (!analysisData?.storage_tiers) return null;

    const colors = {
      'Hot': '#f44336',
      'Cool': '#2196f3',
      'Archive': '#9c27b0',
      'Delete': '#607d8b'
    };
    
    return {
      labels: analysisData.storage_tiers.map(item => item.tier_name),
      datasets: [{
        label: 'Storage Size (GB)',
        data: analysisData.storage_tiers.map(item => item.total_size_gb),
        backgroundColor: analysisData.storage_tiers.map(item => colors[item.tier_name]),
        borderWidth: 1
      }]
    };
  };

  const getGrowthProjectionChart = () => {
    if (!analysisData?.growth_projection) return null;

    const projection = analysisData.growth_projection;
    
    return {
      labels: ['Current', '6 Months', '1 Year', '3 Years'],
      datasets: [{
        label: 'Projected Storage (GB)',
        data: [
          projection.current_size_gb,
          projection.projected_6m_gb,
          projection.projected_1y_gb,
          projection.projected_3y_gb
        ],
        borderColor: '#4caf50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.4,
        fill: true
      }]
    };
  };

  const getAccessPatternsChart = () => {
    if (!analysisData?.access_patterns) return null;

    const patterns = analysisData.access_patterns.patterns;
    const colors = {
      'Hot': '#ff5722',
      'Warm': '#ff9800',
      'Cold': '#2196f3',
      'Frozen': '#9c27b0',
      'Unknown': '#757575'
    };
    
    return {
      labels: patterns.map(p => p.pattern),
      datasets: [{
        label: 'Storage Size (GB)',
        data: patterns.map(p => p.total_size_gb),
        backgroundColor: patterns.map(p => colors[p.pattern]),
        borderWidth: 1
      }]
    };
  };

  if (loading) {
    return (
      <div className="analysis-loading">
        <div className="spinner-large"></div>
        <p>Loading analysis...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analysis-error">
        <h2>⚠️ {error}</h2>
        <button onClick={() => navigate('/projects')} className="btn-back">
          Back to Projects
        </button>
      </div>
    );
  }

  if (!analysisData || !analysisData.summary) {
    return <div className="analysis-error">No analysis data available</div>;
  }

  const { summary, cost_analysis, growth_projection } = analysisData;

  return (
    <div className="analysis-dashboard">
      <div className="analysis-header">
        <button onClick={() => navigate('/projects')} className="btn-back-small">
          ← Back to Projects
        </button>
        <div>
          <h1>Storage Analysis Report</h1>
          <h2>{project?.project_name}</h2>
          <p className="analysis-date">
            Completed: {new Date(summary.completed_at).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-icon">📁</div>
          <div className="card-content">
            <h3>Total Files</h3>
            <p className="card-value">{summary?.total_files?.toLocaleString() || '0'}</p>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon">💾</div>
          <div className="card-content">
            <h3>Total Storage</h3>
            <p className="card-value">{summary?.total_size_gb?.toFixed(2) || '0.00'} GB</p>
          </div>
        </div>

        {cost_analysis && (
          <>
            <div className="summary-card highlight">
              <div className="card-icon">💰</div>
              <div className="card-content">
                <h3>Potential Monthly Savings</h3>
                <p className="card-value">${cost_analysis.monthly_savings?.toFixed(2) || '0.00'}</p>
                <p className="card-subtitle">{cost_analysis.savings_percentage?.toFixed(1) || '0.0'}% reduction</p>
              </div>
            </div>

            <div className="summary-card">
              <div className="card-icon">📈</div>
              <div className="card-content">
                <h3>Annual Savings</h3>
                <p className="card-value">${cost_analysis.annual_savings?.toFixed(2) || '0.00'}</p>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        {/* Age Distribution */}
        <div className="chart-container">
          <h3>Age Distribution</h3>
          <p className="chart-description">Files categorized by last modified date</p>
          {getAgeDistributionChart() && (
            <div className="chart-wrapper">
              <Pie 
                data={getAgeDistributionChart()} 
                options={{
                  responsive: true,
                  maintainAspectRatio: true,
                  plugins: {
                    legend: {
                      position: 'bottom'
                    }
                  }
                }}
              />
            </div>
          )}
          <div className="data-table">
            <table>
              <thead>
                <tr>
                  <th>Age Bucket</th>
                  <th>Files</th>
                  <th>Size (GB)</th>
                  <th>%</th>
                </tr>
              </thead>
              <tbody>
                {analysisData.age_distribution?.map(item => (
                  <tr key={item.age_bucket}>
                    <td>{item.age_bucket}</td>
                    <td>{item.file_count?.toLocaleString() || '0'}</td>
                    <td>{item.total_size_gb?.toFixed(2) || '0.00'}</td>
                    <td>{item.percentage?.toFixed(1) || '0.0'}%</td>
                  </tr>
                )) || []}
              </tbody>
            </table>
          </div>
        </div>

        {/* File Types */}
        <div className="chart-container">
          <h3>Top File Types</h3>
          <p className="chart-description">Storage usage by file extension</p>
          {getFileTypesChart() && (
            <div className="chart-wrapper">
              <Bar 
                data={getFileTypesChart()} 
                options={{
                  responsive: true,
                  maintainAspectRatio: true,
                  plugins: {
                    legend: {
                      display: false
                    }
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                      title: {
                        display: true,
                        text: 'Size (GB)'
                      }
                    }
                  }
                }}
              />
            </div>
          )}
        </div>

        {/* Storage Tiers */}
        <div className="chart-container">
          <h3>Storage Tier Recommendations</h3>
          <p className="chart-description">Optimize costs by moving data to appropriate tiers</p>
          {getStorageTiersChart() && (
            <div className="chart-wrapper">
              <Pie 
                data={getStorageTiersChart()} 
                options={{
                  responsive: true,
                  maintainAspectRatio: true,
                  plugins: {
                    legend: {
                      position: 'bottom'
                    }
                  }
                }}
              />
            </div>
          )}
          <div className="data-table">
            <table>
              <thead>
                <tr>
                  <th>Tier</th>
                  <th>Files</th>
                  <th>Size (GB)</th>
                  <th>Monthly Cost</th>
                </tr>
              </thead>
              <tbody>
                {analysisData.storage_tiers?.map(item => (
                  <tr key={item.tier_name}>
                    <td><strong>{item.tier_name}</strong></td>
                    <td>{item.file_count?.toLocaleString() || '0'}</td>
                    <td>{item.total_size_gb?.toFixed(2) || '0.00'}</td>
                    <td>${item.monthly_cost?.toFixed(2) || '0.00'}</td>
                  </tr>
                )) || []}
              </tbody>
            </table>
          </div>
        </div>

        {/* Growth Projection */}
        {growth_projection && (
          <div className="chart-container">
            <h3>Growth Projection</h3>
            <p className="chart-description">
              Projected at {growth_projection.annual_growth_rate_pct?.toFixed(1) || '0.0'}% annual growth
              ({growth_projection.confidence_level || 'Low'} confidence)
            </p>
            {getGrowthProjectionChart() && (
              <div className="chart-wrapper">
                <Line 
                  data={getGrowthProjectionChart()} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                      legend: {
                        display: false
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        title: {
                          display: true,
                          text: 'Size (GB)'
                        }
                      }
                    }
                  }}
                />
              </div>
            )}
          </div>
        )}
      </div>

      {/* PHASE 1: Access Patterns Analysis */}
      {analysisData.access_patterns && (
        <div className="chart-container full-width">
          <h3>🔥 Access Pattern Analysis</h3>
          <p className="chart-description">Files categorized by last access date for optimal tiering</p>
          <div className="charts-row">
            <div className="chart-wrapper-half">
              {getAccessPatternsChart() && (
                <Pie 
                  data={getAccessPatternsChart()} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                      legend: {
                        position: 'right'
                      }
                    }
                  }}
                />
              )}
            </div>
            <div className="data-table-half">
              <table>
                <thead>
                  <tr>
                    <th>Pattern</th>
                    <th>Files</th>
                    <th>Size (GB)</th>
                    <th>%</th>
                    <th>Recommended Tier</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisData.access_patterns.patterns?.map(pattern => (
                    <tr key={pattern.pattern}>
                      <td><strong>{pattern.pattern}</strong></td>
                      <td>{pattern.file_count?.toLocaleString() || '0'}</td>
                      <td>{pattern.total_size_gb?.toFixed(2) || '0.00'}</td>
                      <td>{pattern.percentage?.toFixed(1) || '0.0'}%</td>
                      <td><span className={`tier-badge ${pattern.recommended_tier?.toLowerCase() || 'cool'}`}>
                        {pattern.recommended_tier || 'N/A'}
                      </span></td>
                    </tr>
                  )) || []}
                </tbody>
              </table>
              {analysisData.access_patterns.zombie_files?.count > 0 && (
                <div className="zombie-alert">
                  ⚠️ <strong>Zombie Files Detected:</strong> {analysisData.access_patterns.zombie_files.count?.toLocaleString() || '0'} 
                  files ({analysisData.access_patterns.zombie_files.total_size_gb?.toFixed(2) || '0.00'} GB) 
                  larger than 1GB haven't been accessed in 2+ years
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* PHASE 1: Advanced Duplicate Analysis */}
      {analysisData.duplicates_advanced && (
        <div className="chart-container full-width">
          <h3>📋 Advanced Duplicate Detection</h3>
          <p className="chart-description">
            Exact duplicates identified. Potential savings: <strong>${analysisData.duplicates_advanced.total_exact_savings_gb?.toFixed(2) || '0.00'} GB</strong>
          </p>
          <div className="duplicate-summary">
            <div className="dup-stat">
              <span className="dup-label">Exact Duplicates:</span>
              <span className="dup-value">{analysisData.duplicates_advanced.exact_duplicate_sets || 0}</span>
            </div>
            <div className="dup-stat">
              <span className="dup-label">Version Files:</span>
              <span className="dup-value">{analysisData.duplicates_advanced.version_file_count || 0}</span>
            </div>
            <div className="dup-stat">
              <span className="dup-label">Fuzzy Matches:</span>
              <span className="dup-value">{analysisData.duplicates_advanced.fuzzy_match_count || 0}</span>
            </div>
          </div>
          <div className="data-table">
            <table>
              <thead>
                <tr>
                  <th>File Name</th>
                  <th>Extension</th>
                  <th>Size (GB)</th>
                  <th>Copies</th>
                  <th>Wasted Space (GB)</th>
                  <th>Has Versions</th>
                  <th>Sample Location</th>
                </tr>
              </thead>
              <tbody>
                {analysisData.duplicates_advanced.duplicates?.slice(0, 20).map((dup, idx) => (
                  <tr key={idx}>
                    <td className="file-name">{dup.file_name || 'Unknown'}</td>
                    <td>{dup.extension || 'N/A'}</td>
                    <td>{dup.size_per_file_gb?.toFixed(4) || '0.0000'}</td>
                    <td><strong>{dup.occurrence_count || 0}</strong></td>
                    <td className="savings-value">{dup.potential_savings_gb?.toFixed(2) || '0.00'}</td>
                    <td>{dup.has_version_pattern ? '✓ Yes' : '—'}</td>
                    <td className="location-cell" title={dup.sample_location || ''}>
                      {dup.sample_location?.substring(0, 50) || 'N/A'}...
                    </td>
                  </tr>
                )) || []}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* PHASE 1: Directory Analysis */}
      {analysisData.directory_analysis && (
        <div className="chart-container full-width">
          <h3>📂 Directory Analysis</h3>
          <p className="chart-description">Identify space-consuming and abandoned directories</p>
          <div className="directory-sections">
            <div className="dir-section">
              <h4>Largest Directories</h4>
              <div className="data-table">
                <table>
                  <thead>
                    <tr>
                      <th>Directory Path</th>
                      <th>Files</th>
                      <th>Size (GB)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analysisData.directory_analysis.largest_directories?.slice(0, 10).map((dir, idx) => (
                      <tr key={idx}>
                        <td className="dir-path" title={dir.directory_path || ''}>{dir.directory_path || 'N/A'}</td>
                        <td>{dir.file_count?.toLocaleString() || '0'}</td>
                        <td>{dir.total_size_gb?.toFixed(2) || '0.00'}</td>
                      </tr>
                    )) || []}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="dir-section">
              <h4>Abandoned Directories</h4>
              <p className="dir-subtitle">Not accessed in 1+ year</p>
              <div className="data-table">
                <table>
                  <thead>
                    <tr>
                      <th>Directory Path</th>
                      <th>Last Access</th>
                      <th>Size (GB)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analysisData.directory_analysis.abandoned_directories?.directories?.slice(0, 10).map((dir, idx) => (
                      <tr key={idx}>
                        <td className="dir-path" title={dir.directory_path || ''}>{dir.directory_path || 'N/A'}</td>
                        <td>{dir.last_access ? new Date(dir.last_access).toLocaleDateString() : 'N/A'}</td>
                        <td>{dir.total_size_gb?.toFixed(2) || '0.00'}</td>
                      </tr>
                    )) || []}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="dir-section">
              <h4>Temp/Cache Directories</h4>
              <div className="temp-stats">
                <div className="temp-stat">
                  <span className="temp-label">Files:</span>
                  <span className="temp-value">
                    {analysisData.directory_analysis.temp_cache_directories?.file_count?.toLocaleString() || '0'}
                  </span>
                </div>
                <div className="temp-stat">
                  <span className="temp-label">Total Size:</span>
                  <span className="temp-value">
                    {analysisData.directory_analysis.temp_cache_directories?.total_size_gb?.toFixed(2) || '0.00'} GB
                  </span>
                </div>
                {analysisData.directory_analysis.temp_cache_directories?.cleanup_potential && (
                  <div className="cleanup-alert">
                    ⚠️ High cleanup potential - review for safe deletion
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* PHASE 1: Data Quality */}
      {analysisData.data_quality && (
        <div className="chart-container full-width">
          <h3>✅ Data Quality Assessment</h3>
          <p className="chart-description">Completeness and anomaly detection</p>
          <div className="quality-score-section">
            <div className="quality-score-card">
              <div className="score-circle">
                <svg width="120" height="120">
                  <circle cx="60" cy="60" r="50" fill="none" stroke="#e0e0e0" strokeWidth="10"/>
                  <circle 
                    cx="60" 
                    cy="60" 
                    r="50" 
                    fill="none" 
                    stroke={(analysisData.data_quality.overall_quality_score || 0) >= 80 ? '#4caf50' : 
                            (analysisData.data_quality.overall_quality_score || 0) >= 60 ? '#ff9800' : '#f44336'}
                    strokeWidth="10"
                    strokeDasharray={`${(analysisData.data_quality.overall_quality_score || 0) * 3.14} 314`}
                    strokeDashoffset="78.5"
                    transform="rotate(-90 60 60)"
                  />
                </svg>
                <div className="score-text">
                  <span className="score-number">{analysisData.data_quality.overall_quality_score?.toFixed(0) || '0'}</span>
                  <span className="score-label">Score</span>
                </div>
              </div>
              <div className="quality-details">
                <div className="quality-metric">
                  <span className="metric-label">Completeness:</span>
                  <span className="metric-value">{analysisData.data_quality.completeness_score?.toFixed(1) || '0.0'}%</span>
                </div>
                <div className="quality-metric">
                  <span className="metric-label">Missing Size Data:</span>
                  <span className="metric-value">{analysisData.data_quality.missing_size_pct?.toFixed(1) || '0.0'}%</span>
                </div>
                <div className="quality-metric">
                  <span className="metric-label">Missing Dates:</span>
                  <span className="metric-value">{analysisData.data_quality.missing_dates_pct?.toFixed(1) || '0.0'}%</span>
                </div>
              </div>
            </div>
            {analysisData.data_quality.anomalies?.length > 0 && (
              <div className="anomalies-section">
                <h4>🔍 Anomalies Detected</h4>
                <ul className="anomaly-list">
                  {analysisData.data_quality.anomalies.map((anomaly, idx) => (
                    <li key={idx} className="anomaly-item">
                      <strong>{anomaly.type || 'Unknown'}:</strong> {anomaly.description || 'No description'}
                      {anomaly.affected_count && ` (${anomaly.affected_count?.toLocaleString() || '0'} files)`}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* PHASE 1: Recommendations */}
      {analysisData.recommendations && (
        <div className="chart-container full-width">
          <h3>💡 Optimization Recommendations</h3>
          <p className="chart-description">Prioritized by ROI and impact</p>
          <div className="recommendations-grid">
            {analysisData.recommendations.recommendations?.map((rec, idx) => (
              <div key={idx} className={`recommendation-card priority-${rec.priority?.toLowerCase() || 'low'}`}>
                <div className="rec-header">
                  <h4>{rec.action || 'No action'}</h4>
                  <span className={`priority-badge ${rec.priority?.toLowerCase() || 'low'}`}>
                    {rec.priority || 'Low'}
                  </span>
                </div>
                <p className="rec-description">{rec.description || 'No description'}</p>
                <div className="rec-impact">
                  <div className="impact-item">
                    <span className="impact-label">Potential Savings:</span>
                    <span className="impact-value">${rec.estimated_monthly_savings?.toFixed(2) || '0.00'}/mo</span>
                  </div>
                  <div className="impact-item">
                    <span className="impact-label">Space Freed:</span>
                    <span className="impact-value">{rec.space_freed_gb?.toFixed(2) || '0.00'} GB</span>
                  </div>
                  <div className="impact-item">
                    <span className="impact-label">Affected Files:</span>
                    <span className="impact-value">{rec.affected_file_count?.toLocaleString() || '0'}</span>
                  </div>
                </div>
                <div className="rec-footer">
                  <span className="roi-label">ROI Score:</span>
                  <div className="roi-bar">
                    <div 
                      className="roi-fill" 
                      style={{width: `${Math.min((rec.roi_score || 0) * 10, 100)}%`}}
                    ></div>
                  </div>
                  <span className="roi-value">{rec.roi_score?.toFixed(1) || '0.0'}</span>
                </div>
              </div>
            )) || []}
          </div>
        </div>
      )}

      {/* Cost Analysis */}
      {cost_analysis && (
        <div className="cost-analysis-section">
          <h3>Cost Analysis</h3>
          <div className="cost-comparison">
            <div className="cost-item">
              <span className="cost-label">Current Monthly Cost:</span>
              <span className="cost-value current">${cost_analysis.current_monthly_cost.toFixed(2)}</span>
            </div>
            <div className="cost-arrow">→</div>
            <div className="cost-item">
              <span className="cost-label">Optimized Monthly Cost:</span>
              <span className="cost-value optimized">${cost_analysis.optimized_monthly_cost.toFixed(2)}</span>
            </div>
            <div className="cost-savings">
              <span className="savings-badge">
                Save ${cost_analysis.monthly_savings.toFixed(2)}/month
                ({cost_analysis.savings_percentage.toFixed(1)}%)
              </span>
            </div>
          </div>
          <p className="cost-note">
            💡 <strong>Tip:</strong> Moving older files to Cool or Archive storage can significantly reduce costs
            while maintaining data accessibility.
          </p>
        </div>
      )}
    </div>
  );
}

export default AnalysisDashboard;
