export default function LoadingSpinner() {
  return (
    <div style={styles.container}>
      <div style={styles.spinnerWrapper}>
        <div style={styles.spinner}></div>
        <h2 style={styles.title}>Running Monte Carlo Simulation...</h2>
        <p style={styles.subtitle}>Simulating 10,000 scenarios</p>
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
    backgroundColor: '#f3f4f6',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
  },
  spinnerWrapper: {
    textAlign: 'center'
  },
  spinner: {
    width: '60px',
    height: '60px',
    border: '4px solid #e5e7eb',
    borderTop: '4px solid #3b82f6',
    borderRadius: '50%',
    margin: '0 auto 24px',
    animation: 'spin 1s linear infinite'
  },
  title: {
    margin: '0 0 8px 0',
    fontSize: '24px',
    fontWeight: '600',
    color: '#1a1a1a'
  },
  subtitle: {
    margin: '0',
    fontSize: '16px',
    color: '#6b7280'
  }
};

// Add spinner animation
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
document.head.appendChild(styleSheet);