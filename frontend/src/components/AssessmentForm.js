import React, { useState, useEffect } from 'react';
import BasicInfoForm from './BasicInfoForm';
import QuestionsForm from './QuestionsForm';
import ResultsUpload from './ResultsUpload';
import { getQuestions, createCompleteAssessment, getScriptList, downloadScript } from '../services/api';
import './AssessmentForm.css';

const AssessmentForm = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [projectData, setProjectData] = useState(null);
  const [questions, setQuestions] = useState({ general: [], technical: [] });
  const [responses, setResponses] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [availableScripts, setAvailableScripts] = useState([]);

  useEffect(() => {
    fetchQuestions();
    fetchScripts();
  }, []);

  const fetchQuestions = async () => {
    try {
      const data = await getQuestions();
      setQuestions(data);
    } catch (err) {
      setError('Failed to load questions. Please try again.');
      console.error(err);
    }
  };

  const fetchScripts = async () => {
    try {
      const data = await getScriptList();
      setAvailableScripts(data.scripts || []);
    } catch (err) {
      console.error('Failed to load scripts:', err);
      // Don't set error state, scripts are optional
    }
  };

  const handleBasicInfoSubmit = (data) => {
    setProjectData(data);
    setCurrentStep(2);
  };

  const handleResponseChange = (questionId, value, comments = '') => {
    setResponses(prev => ({
      ...prev,
      [questionId]: { value, comments }
    }));
  };

  const handleFinalSubmit = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get all questions to include question text
      const allQuestions = [...questions.general, ...questions.technical];
      
      // Format responses for API with question text
      const formattedResponses = Object.entries(responses).map(([questionId, data]) => {
        const question = allQuestions.find(q => q.id === questionId);
        return {
          question_id: questionId,
          question_text: question ? question.text : '',
          response_value: data.value,
          comments: data.comments || null
        };
      });

      const assessmentData = {
        project: projectData,
        responses: formattedResponses
      };

      await createCompleteAssessment(assessmentData);
      setSuccess(true);
      setCurrentStep(3);
    } catch (err) {
      setError('Failed to submit assessment. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setCurrentStep(1);
    setProjectData(null);
    setResponses({});
    setSuccess(false);
    setError(null);
  };

  const handleDownloadScript = async (filename) => {
    try {
      await downloadScript(filename);
    } catch (err) {
      console.error('Failed to download script:', err);
      setError(`Failed to download ${filename}. Please try again or contact support.`);
    }
  };

  const generalQuestions = questions.general;
  const technicalQuestions = questions.technical;

  return (
    <div className="assessment-container">
      <div className="progress-bar">
        <div className={`step ${currentStep >= 1 ? 'active' : ''}`}>
          <div className="step-number">1</div>
          <div className="step-label">Basic Info</div>
        </div>
        <div className={`step ${currentStep >= 2 ? 'active' : ''}`}>
          <div className="step-number">2</div>
          <div className="step-label">Assessment</div>
        </div>
        <div className={`step ${currentStep >= 3 ? 'active' : ''}`}>
          <div className="step-number">3</div>
          <div className="step-label">Complete</div>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {currentStep === 1 && (
        <BasicInfoForm onSubmit={handleBasicInfoSubmit} />
      )}

      {currentStep === 2 && (
        <QuestionsForm
          generalQuestions={generalQuestions}
          technicalQuestions={technicalQuestions}
          responses={responses}
          onResponseChange={handleResponseChange}
          onSubmit={handleFinalSubmit}
          onBack={() => setCurrentStep(1)}
          loading={loading}
        />
      )}

      {currentStep === 3 && success && (
        <div className="success-container">
          <div className="success-icon">✓</div>
          <h2>Assessment Submitted Successfully!</h2>
          <p>Your assessment has been saved to the database.</p>
          
          {availableScripts.length > 0 && (
            <div className="scripts-section">
              <h3>Download Assessment Scripts</h3>
              <p className="scripts-description">Download the required scripts for your storage assessment:</p>
              <div className="scripts-list">
                {availableScripts.map((script) => (
                  <button
                    key={script.filename}
                    onClick={() => handleDownloadScript(script.filename)}
                    className="btn btn-script"
                  >
                    📥 {script.filename}
                    <span className="script-size">
                      ({(script.size / 1024).toFixed(1)} KB)
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {projectData && (
            <ResultsUpload 
              projectId={projectData.id}
              onUploadComplete={(result) => {
                console.log('Upload complete:', result);
              }}
            />
          )}
          
          <button onClick={handleReset} className="btn btn-primary">
            Start New Assessment
          </button>
        </div>
      )}
    </div>
  );
};

export default AssessmentForm;
