import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AssessmentForm from './components/AssessmentForm';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Storage Assessment Application</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<AssessmentForm />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
