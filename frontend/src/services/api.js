import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Project APIs
export const createProject = async (projectData) => {
  const response = await api.post('/projects', projectData);
  return response.data;
};

export const getProjects = async () => {
  const response = await api.get('/projects');
  return response.data;
};

export const getProject = async (projectId) => {
  const response = await api.get(`/projects/${projectId}`);
  return response.data;
};

// Question APIs
export const getQuestions = async (category = null) => {
  const url = category ? `/questions?category=${category}` : '/questions';
  const response = await api.get(url);
  return response.data;
};

// Assessment APIs
export const createCompleteAssessment = async (assessmentData) => {
  const response = await api.post('/assessments/complete', assessmentData);
  return response.data;
};

export const getProjectResponses = async (projectId) => {
  const response = await api.get(`/projects/${projectId}/responses`);
  return response.data;
};

// Script Download APIs
export const getScriptList = async () => {
  const response = await api.get('/script/list');
  return response.data;
};

export const downloadScript = async (filename) => {
  const response = await api.get(`/script/download/${filename}`, {
    responseType: 'blob', // Important for file download
  });
  
  // Create blob link to download
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.parentNode.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// Script Results Upload APIs
export const uploadScriptResults = async (projectId, files) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  const response = await api.post(`/results/upload-results/${projectId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getProjectResults = async (projectId) => {
  const response = await api.get(`/results/results/${projectId}`);
  return response.data;
};

export const deleteScriptResult = async (resultId) => {
  const response = await api.delete(`/results/results/${resultId}`);
  return response.data;
};

export default api;
