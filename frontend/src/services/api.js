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

export default api;
