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

  if (!analysisData) {
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
            <p className="card-value">{summary.total_files.toLocaleString()}</p>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon">💾</div>
          <div className="card-content">
            <h3>Total Storage</h3>
            <p className="card-value">{summary.total_size_gb.toFixed(2)} GB</p>
          </div>
        </div>

        {cost_analysis && (
          <>
            <div className="summary-card highlight">
              <div className="card-icon">💰</div>
              <div className="card-content">
                <h3>Potential Monthly Savings</h3>
                <p className="card-value">${cost_analysis.monthly_savings.toFixed(2)}</p>
                <p className="card-subtitle">{cost_analysis.savings_percentage.toFixed(1)}% reduction</p>
              </div>
            </div>

            <div className="summary-card">
              <div className="card-icon">📈</div>
              <div className="card-content">
                <h3>Annual Savings</h3>
                <p className="card-value">${cost_analysis.annual_savings.toFixed(2)}</p>
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
                {analysisData.age_distribution.map(item => (
                  <tr key={item.age_bucket}>
                    <td>{item.age_bucket}</td>
                    <td>{item.file_count.toLocaleString()}</td>
                    <td>{item.total_size_gb.toFixed(2)}</td>
                    <td>{item.percentage.toFixed(1)}%</td>
                  </tr>
                ))}
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
                {analysisData.storage_tiers.map(item => (
                  <tr key={item.tier_name}>
                    <td><strong>{item.tier_name}</strong></td>
                    <td>{item.file_count.toLocaleString()}</td>
                    <td>{item.total_size_gb.toFixed(2)}</td>
                    <td>${item.monthly_cost.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Growth Projection */}
        {growth_projection && (
          <div className="chart-container">
            <h3>Growth Projection</h3>
            <p className="chart-description">
              Projected at {growth_projection.annual_growth_rate_pct.toFixed(1)}% annual growth
              ({growth_projection.confidence_level} confidence)
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
