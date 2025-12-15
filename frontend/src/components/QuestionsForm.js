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

  const handleMultiSelectChange = (questionId, optionText, isExclusive, currentValue, currentComments) => {
    let newValues = [];
    
    if (currentValue) {
      newValues = currentValue.split(', ').filter(v => v);
    }

    if (isExclusive) {
      // If clicking an exclusive option, clear all others and select only this
      newValues = [optionText];
    } else {
      // Remove any exclusive options if they exist
      const question = [...generalQuestions, ...technicalQuestions].find(q => q.id === questionId);
      const exclusiveOptions = question.options.filter(opt => opt.is_exclusive).map(opt => opt.text);
      newValues = newValues.filter(v => !exclusiveOptions.includes(v));
      
      // Toggle the current option
      const index = newValues.indexOf(optionText);
      if (index > -1) {
        newValues.splice(index, 1);
      } else {
        newValues.push(optionText);
      }
    }

    const newValue = newValues.join(', ');
    onResponseChange(questionId, newValue, currentComments);
  };

  const renderQuestion = (question) => {
    const currentResponse = responses[question.id] || { value: '', comments: '' };
    const selectedValues = currentResponse.value ? currentResponse.value.split(', ').filter(v => v) : [];
    const hasExclusiveSelection = question.options?.some(opt => 
      opt.is_exclusive && selectedValues.includes(opt.text)
    );

    return (
      <div key={question.id} className="question-item">
        <div className="question-text">
          {question.text}
          {question.description && (
            <div className="question-description">{question.description}</div>
          )}
        </div>

        {/* MCQ - Single Choice Radio Buttons */}
        {(question.type === 'MCQ' || question.type === 'single_choice') && (
          <div className="question-options">
            {question.options && question.options.map((option, idx) => (
              <label key={idx} className="radio-option">
                <input
                  type="radio"
                  name={`question_${question.id}`}
                  value={typeof option === 'string' ? option : option.text}
                  checked={currentResponse.value === (typeof option === 'string' ? option : option.text)}
                  onChange={(e) => onResponseChange(question.id, e.target.value, currentResponse.comments)}
                />
                <span>{typeof option === 'string' ? option : option.text}</span>
              </label>
            ))}
          </div>
        )}

        {/* MULTISELECT - Multiple Choice Checkboxes */}
        {question.type === 'MULTISELECT' && (
          <div className="question-options">
            {question.options && question.options.map((option, idx) => {
              const optionText = typeof option === 'string' ? option : option.text;
              const isExclusive = option.is_exclusive || false;
              const isChecked = selectedValues.includes(optionText);
              const isDisabled = hasExclusiveSelection && !isExclusive && !isChecked;

              return (
                <label key={idx} className={`checkbox-option ${isDisabled ? 'disabled' : ''}`}>
                  <input
                    type="checkbox"
                    value={optionText}
                    checked={isChecked}
                    disabled={isDisabled}
                    onChange={() => handleMultiSelectChange(
                      question.id, 
                      optionText, 
                      isExclusive,
                      currentResponse.value,
                      currentResponse.comments
                    )}
                  />
                  <span>{optionText}</span>
                  {isExclusive && <span className="exclusive-badge">⚠️ Requires explanation</span>}
                </label>
              );
            })}
          </div>
        )}

        {/* TEXT, NUMBER, or other input types */}
        {(question.type === 'TEXT' || question.type === 'NUMBER' || question.type === 'text_input') && (
          <div className="question-input">
            <textarea
              value={currentResponse.value}
              onChange={(e) => onResponseChange(question.id, e.target.value, currentResponse.comments)}
              placeholder="Enter your response..."
              rows="3"
            />
          </div>
        )}

        {/* FILE_UPLOAD */}
        {question.type === 'FILE_UPLOAD' && (
          <div className="question-input">
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.txt"
              onChange={(e) => {
                // TODO: Handle file upload
                const fileName = e.target.files[0]?.name || '';
                onResponseChange(question.id, fileName, currentResponse.comments);
              }}
            />
            <small>Allowed: PDF, PNG, JPG, TXT (Max 10MB)</small>
          </div>
        )}

        {/* Comments Section - Required for exclusive options */}
        <div className="question-comments">
          <label>
            Additional Comments {hasExclusiveSelection && <span className="required">*</span>}
            {hasExclusiveSelection && <span className="hint"> (Required: Please explain your selection)</span>}
          </label>
          <textarea
            value={currentResponse.comments}
            onChange={(e) => onResponseChange(question.id, currentResponse.value, e.target.value)}
            placeholder={hasExclusiveSelection 
              ? "Please provide details about your selection..." 
              : "Add any additional comments or clarifications..."}
            rows="2"
            required={hasExclusiveSelection}
            className={hasExclusiveSelection && !currentResponse.comments ? 'required-field' : ''}
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
