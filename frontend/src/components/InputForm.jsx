import { useState } from 'react';

export default function InputForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    monthlyIncome: '',
    monthlyExpenses: '',
    currentSavings: '',
    availableCredit: '',
    interestRate: '',
    timeHorizon: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = () => {
    const data = {
      monthlyIncome: parseFloat(formData.monthlyIncome),
      monthlyExpenses: parseFloat(formData.monthlyExpenses),
      currentSavings: parseFloat(formData.currentSavings),
      availableCredit: parseFloat(formData.availableCredit),
      interestRate: parseFloat(formData.interestRate),
      timeHorizon: parseInt(formData.timeHorizon)
    };

    onSubmit(data);
  };

  const isFormValid = () => {
    return Object.values(formData).every(value => value !== '' && parseFloat(value) >= 0);
  };

  return (
    <div style={styles.container}>
      <div style={styles.formCard}>
        <h2 style={styles.title}>Calculate Bankruptcy Risk</h2>

        <div style={styles.inputGroup}>
          <label style={styles.label}>Current Monthly Income ($)</label>
          <input
            type="number"
            name="monthlyIncome"
            value={formData.monthlyIncome}
            onChange={handleChange}
            style={styles.input}
            placeholder="e.g., 5000"
            min="0"
            step="10"
          />
        </div>

        <div style={styles.inputGroup}>
          <label style={styles.label}>Monthly Expenses ($)</label>
          <input
            type="number"
            name="monthlyExpenses"
            value={formData.monthlyExpenses}
            onChange={handleChange}
            style={styles.input}
            placeholder="e.g., 3500"
            min="0"
            step="10"
          />
        </div>

        <div style={styles.inputGroup}>
          <label style={styles.label}>Current Savings ($)</label>
          <input
            type="number"
            name="currentSavings"
            value={formData.currentSavings}
            onChange={handleChange}
            style={styles.input}
            placeholder="e.g., 10000"
            min="0"
            step="10"
          />
        </div>

        <div style={styles.inputGroup}>
          <label style={styles.label}>Available Credit ($)</label>
          <input
            type="number"
            name="availableCredit"
            value={formData.availableCredit}
            onChange={handleChange}
            style={styles.input}
            placeholder="e.g., 30000"
            min="0"
            step="10"
          />
        </div>

        <div style={styles.inputGroup}>
          <label style={styles.label}>Interest Rate (%)</label>
          <input
            type="number"
            name="interestRate"
            value={formData.interestRate}
            onChange={handleChange}
            style={styles.input}
            placeholder="e.g., 25"
            min="0"
            step="1"
          />
        </div>

        <div style={styles.inputGroup}>
          <label style={styles.label}>Time Horizon (months)</label>
          <input
            type="number"
            name="timeHorizon"
            value={formData.timeHorizon}
            onChange={handleChange}
            style={styles.input}
            placeholder="e.g., 12"
            min="1"
            step="1"
          />
        </div>

        <button
          onClick={handleSubmit}
          style={{
            ...styles.button,
            ...(isFormValid() ? {} : styles.buttonDisabled)
          }}
          disabled={!isFormValid()}
        >
          Calculate Risk
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    padding: '20px',
    backgroundColor: '#f3f4f6',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
  },
  formCard: {
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    padding: '32px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    width: '100%',
    maxWidth: '500px'
  },
  title: {
    margin: '0 0 24px 0',
    fontSize: '24px',
    fontWeight: '600',
    color: '#1a1a1a'
  },
  inputGroup: {
    marginBottom: '20px'
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#374151'
  },
  input: {
    width: '100%',
    padding: '12px',
    fontSize: '16px',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    boxSizing: 'border-box',
    transition: 'border-color 0.2s',
    outline: 'none'
  },
  button: {
    width: '100%',
    padding: '14px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#ffffff',
    backgroundColor: '#3b82f6',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    marginTop: '8px',
    transition: 'background-color 0.2s'
  },
  buttonDisabled: {
    backgroundColor: '#9ca3af',
    cursor: 'not-allowed'
  }
};

// Add hover effect via CSS
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  input:focus {
    border-color: #3b82f6 !important;
  }
  button:not(:disabled):hover {
    background-color: #2563eb !important;
  }
`;
document.head.appendChild(styleSheet);