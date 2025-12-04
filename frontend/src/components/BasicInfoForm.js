import React, { useState } from 'react';
import './BasicInfoForm.css';

const BasicInfoForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    project_name: '',
    environment: '',
    business_purpose: '',
    business_criticality: '',
    business_owners: '',
    storage_owners: ''
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validate = () => {
    const newErrors = {};
    
    if (!formData.project_name.trim()) {
      newErrors.project_name = 'Project name is required';
    }
    if (!formData.environment) {
      newErrors.environment = 'Environment is required';
    }
    if (!formData.business_purpose.trim()) {
      newErrors.business_purpose = 'Business purpose is required';
    }
    if (!formData.business_criticality) {
      newErrors.business_criticality = 'Business criticality is required';
    }
    if (!formData.business_owners.trim()) {
      newErrors.business_owners = 'Business owner(s) is required';
    }
    if (!formData.storage_owners.trim()) {
      newErrors.storage_owners = 'Storage owner(s) is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  return (
    <div className="form-container">
      <h2>Basic Project Information</h2>
      <form onSubmit={handleSubmit} className="basic-info-form">
        
        <div className="form-group">
          <label htmlFor="project_name">
            Project Name <span className="required">*</span>
          </label>
          <input
            type="text"
            id="project_name"
            name="project_name"
            value={formData.project_name}
            onChange={handleChange}
            className={errors.project_name ? 'error' : ''}
            placeholder="Enter project name"
          />
          {errors.project_name && <span className="error-message">{errors.project_name}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="environment">
            Environment <span className="required">*</span>
          </label>
          <select
            id="environment"
            name="environment"
            value={formData.environment}
            onChange={handleChange}
            className={errors.environment ? 'error' : ''}
          >
            <option value="">Select environment</option>
            <option value="Development">Development</option>
            <option value="QA">QA</option>
            <option value="Production">Production</option>
          </select>
          {errors.environment && <span className="error-message">{errors.environment}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="business_purpose">
            Business Purpose / Storage Migration Objective <span className="required">*</span>
          </label>
          <textarea
            id="business_purpose"
            name="business_purpose"
            value={formData.business_purpose}
            onChange={handleChange}
            className={errors.business_purpose ? 'error' : ''}
            placeholder="Describe the business purpose or storage migration objective"
            rows="4"
          />
          {errors.business_purpose && <span className="error-message">{errors.business_purpose}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="business_criticality">
            Business Criticality <span className="required">*</span>
          </label>
          <select
            id="business_criticality"
            name="business_criticality"
            value={formData.business_criticality}
            onChange={handleChange}
            className={errors.business_criticality ? 'error' : ''}
          >
            <option value="">Select criticality level</option>
            <option value="1">1 - Lower priority applications</option>
            <option value="2">2 - High Criticality Applications without sustaining serious damage to operations and revenue</option>
            <option value="3">3 - Mission Critical with significant business impact to revenue and reputation</option>
          </select>
          {errors.business_criticality && <span className="error-message">{errors.business_criticality}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="business_owners">
            Business / Project Owner(s) <span className="required">*</span>
          </label>
          <input
            type="text"
            id="business_owners"
            name="business_owners"
            value={formData.business_owners}
            onChange={handleChange}
            className={errors.business_owners ? 'error' : ''}
            placeholder="Enter business/project owner names"
          />
          {errors.business_owners && <span className="error-message">{errors.business_owners}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="storage_owners">
            Storage Owner(s) <span className="required">*</span>
          </label>
          <input
            type="text"
            id="storage_owners"
            name="storage_owners"
            value={formData.storage_owners}
            onChange={handleChange}
            className={errors.storage_owners ? 'error' : ''}
            placeholder="Enter storage owner names"
          />
          {errors.storage_owners && <span className="error-message">{errors.storage_owners}</span>}
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary">
            Next: Assessment Questions
          </button>
        </div>
      </form>
    </div>
  );
};

export default BasicInfoForm;
