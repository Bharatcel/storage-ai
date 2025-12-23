import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import AssessmentForm from './components/AssessmentForm';
import ProjectsList from './components/ProjectsList';
import AnalysisDashboard from './components/AnalysisDashboard';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Storage Assessment Application</h1>
          <nav className="header-nav">
            <Link to="/">New Assessment</Link>
            <Link to="/projects">My Projects</Link>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<AssessmentForm />} />
            <Route path="/projects" element={<ProjectsList />} />
            <Route path="/analysis/:projectId" element={<AnalysisDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
