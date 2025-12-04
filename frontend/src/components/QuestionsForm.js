import React, { useState } from 'react';
import './QuestionsForm.css';

const QuestionsForm = ({
  generalQuestions,
  technicalQuestions,
  responses,
  onResponseChange,
  onSubmit,
  onBack,
  loading
}) => {
  const [activeTab, setActiveTab] = useState('general');

  const renderQuestion = (question) => {
    const currentResponse = responses[question.id] || { value: '', comments: '' };

    return (
      <div key={question.id} className="question-item">
        <div className="question-text">
          {question.text}
        </div>

        {question.type === 'single_choice' ? (
          <div className="question-options">
            {question.options.map((option, idx) => (
              <label key={idx} className="radio-option">
                <input
                  type="radio"
                  name={`question_${question.id}`}
                  value={option}
                  checked={currentResponse.value === option}
                  onChange={(e) => onResponseChange(question.id, e.target.value, currentResponse.comments)}
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
        ) : (
          <div className="question-input">
            <textarea
              value={currentResponse.value}
              onChange={(e) => onResponseChange(question.id, e.target.value, currentResponse.comments)}
              placeholder="Enter your response..."
              rows="3"
            />
          </div>
        )}

        <div className="question-comments">
          <label>Additional Comments (Optional)</label>
          <textarea
            value={currentResponse.comments}
            onChange={(e) => onResponseChange(question.id, currentResponse.value, e.target.value)}
            placeholder="Add any additional comments or clarifications..."
            rows="2"
          />
        </div>
      </div>
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <div className="questions-container">
      <h2>Assessment Questions</h2>
      
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'general' ? 'active' : ''}`}
          onClick={() => setActiveTab('general')}
        >
          General Information ({generalQuestions.length})
        </button>
        <button
          className={`tab ${activeTab === 'technical' ? 'active' : ''}`}
          onClick={() => setActiveTab('technical')}
        >
          Technical Information ({technicalQuestions.length})
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="questions-list">
          {activeTab === 'general' && generalQuestions.map(renderQuestion)}
          {activeTab === 'technical' && technicalQuestions.map(renderQuestion)}
        </div>

        <div className="form-actions">
          <button type="button" onClick={onBack} className="btn btn-secondary">
            Back
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Submitting...' : 'Submit Assessment'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default QuestionsForm;
