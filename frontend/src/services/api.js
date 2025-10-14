/**
 * API service for communicating with the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Calculate bankruptcy risk by calling the backend API
 * 
 * @param {Object} formData - Form data from the input component
 * @param {number} formData.monthlyIncome - Current monthly income
 * @param {number} formData.monthlyExpenses - Monthly expenses
 * @param {number} formData.currentSavings - Current savings
 * @param {number} formData.availableCredit - Available credit
 * @param {number} formData.interestRate - Interest rate
 * @param {number} formData.timeHorizon - Time horizon in months
 * @returns {Promise<Object>} Risk calculation results
 */
export async function calculateRisk(formData) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/calculate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)
    });

    if (!response.ok) {
      // Try to extract error message from response
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `API request failed with status ${response.status}`
      );
    }

    const data = await response.json();
    return data;

  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

/**
 * Check if the API is running
 * @returns {Promise<boolean>} True if API is healthy
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    return false;
  }
}