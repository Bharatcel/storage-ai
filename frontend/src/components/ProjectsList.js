import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects, triggerAnalysis, getAnalysisStatus } from '../services/api';
import './ProjectsList.css';

function ProjectsList() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzingProjects, setAnalyzingProjects] = useState({});
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await getProjects();
      
      // Ensure data is an array and has valid projects
      if (!Array.isArray(data) || data.length === 0) {
        setProjects([]);
        setError(null);
        setLoading(false);
        return;
      }
      
      setProjects(data);
      
      // Check analysis status for all projects
      const statusPromises = data.map(project => {
        if (!project.id) {
          console.warn('Project missing id:', project);
          return Promise.resolve({ status: 'not_started' });
        }
        return getAnalysisStatus(project.id).catch((err) => {
          console.warn(`Failed to get status for project ${project.id}:`, err);
          return { status: 'not_started' };
        });
      });
      const statuses = await Promise.all(statusPromises);
      
      const statusMap = {};
      data.forEach((project, index) => {
        if (project.id) {
          statusMap[project.id] = statuses[index];
        }
      });
      setAnalyzingProjects(statusMap);
      
      setError(null);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load projects';
      setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
      console.error('Error fetching projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async (projectId) => {
    if (!projectId) {
      console.error('Invalid project ID:', projectId);
      alert('Invalid project. Please refresh the page.');
      return;
    }
    
    try {
      setAnalyzingProjects(prev => ({
        ...prev,
        [projectId]: { status: 'processing' }
      }));
      
      await triggerAnalysis(projectId);
      
      // Poll for status updates
      const pollInterval = setInterval(async () => {
        const status = await getAnalysisStatus(projectId);
        setAnalyzingProjects(prev => ({
          ...prev,
          [projectId]: status
        }));
        
        if (status.status === 'completed') {
          clearInterval(pollInterval);
        } else if (status.status === 'failed') {
          clearInterval(pollInterval);
          alert(`Analysis failed: ${status.error_message || 'Unknown error'}`);
        }
      }, 2000);
      
      // Stop polling after 60 minutes (for large files)
      setTimeout(() => clearInterval(pollInterval), 3600000);
      
    } catch (err) {
      console.error('Failed to trigger analysis:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to start analysis';
      const displayMessage = typeof errorMessage === 'string' 
        ? errorMessage 
        : (Array.isArray(errorMessage) 
          ? errorMessage.map(e => e.msg || JSON.stringify(e)).join(', ')
          : JSON.stringify(errorMessage));
      alert(`Failed to start analysis: ${displayMessage}`);
      setAnalyzingProjects(prev => ({
        ...prev,
        [projectId]: { status: 'failed' }
      }));
    }
  };

  const handleViewAnalysis = (projectId) => {
    if (!projectId) {
      console.error('Invalid project ID:', projectId);
      alert('Invalid project. Please refresh the page.');
      return;
    }
    navigate(`/analysis/${projectId}`);
  };

  const handleNewAssessment = () => {
    navigate('/');
  };

  const getAnalysisButtonText = (projectId) => {
    const status = analyzingProjects[projectId];
    if (!status || status.status === 'not_started') {
      return 'Analyze';
    } else if (status.status === 'processing') {
      return 'Analyzing...';
    } else if (status.status === 'completed') {
      return 'Re-analyze';
    } else if (status.status === 'failed') {
      return 'Retry Analysis';
    }
    return 'Analyze';
  };

  const isAnalysisAvailable = (projectId) => {
    const status = analyzingProjects[projectId];
    return status && status.status === 'completed';
  };

  const isAnalyzing = (projectId) => {
    const status = analyzingProjects[projectId];
    return status && status.status === 'processing';
  };

  if (loading) {
    return <div className="projects-loading">Loading projects...</div>;
  }

  if (error) {
    return <div className="projects-error">{error}</div>;
  }

  return (
    <div className="projects-container">
      <div className="projects-header">
        <h2>Your Assessments</h2>
        <button className="btn-new-assessment" onClick={handleNewAssessment}>
          + New Assessment
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="no-projects">
          <p>No assessments found. Create your first assessment to get started!</p>
          <button className="btn-primary" onClick={handleNewAssessment}>
            Create Assessment
          </button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.filter(p => p && p.id).map(project => (
            <div key={project.id} className="project-card">
              <div className="project-info">
                <h3>{project.project_name || 'Untitled Project'}</h3>
                <p className="project-meta">
                  <strong>Business Unit:</strong> {project.business_unit || 'N/A'}
                </p>
                <p className="project-meta">
                  <strong>Environment:</strong> {project.environment || 'N/A'}
                </p>
                <p className="project-meta">
                  <strong>Created:</strong> {project.created_at ? new Date(project.created_at).toLocaleDateString() : 'N/A'}
                </p>
                
                {analyzingProjects[project.id] && analyzingProjects[project.id].total_files > 0 && (
                  <div className="analysis-summary">
                    <p className="summary-item">
                      📁 {analyzingProjects[project.id].total_files.toLocaleString()} files
                    </p>
                    <p className="summary-item">
                      💾 {analyzingProjects[project.id].total_size_gb?.toFixed(2)} GB
                    </p>
                  </div>
                )}
              </div>
              
              <div className="project-actions">
                <button
                  className="btn-analyze"
                  onClick={() => handleAnalyze(project.id)}
                  disabled={isAnalyzing(project.id)}
                >
                  {isAnalyzing(project.id) && <span className="spinner"></span>}
                  {getAnalysisButtonText(project.id)}
                </button>
                
                {isAnalysisAvailable(project.id) && (
                  <button
                    className="btn-view-analysis"
                    onClick={() => handleViewAnalysis(project.id)}
                  >
                    View Analysis →
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ProjectsList;
