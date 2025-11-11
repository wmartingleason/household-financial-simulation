export default function LandingPage({ onStartSimulation, onTrySample }) {
  return (
    <div style={styles.container}>
      <div style={styles.contentCard}>
        <h1 style={styles.mainTitle}>Household Financial Risk Simulator</h1>

        <div style={styles.descriptionSection}>
          <p style={styles.subtitle}>
            A Monte Carlo simulation platform for analyzing household financial risk using real-world income volatility patterns
          </p>

          <div style={styles.featureGrid}>
            <div style={styles.featureCard}>
              <h3 style={styles.featureTitle}>Real-World Data</h3>
              <p style={styles.featureText}>
                Powered by SIPP (Survey of Income and Program Participation) data, modeling income volatility through compound Poisson jump processes
              </p>
            </div>

            <div style={styles.featureCard}>
              <h3 style={styles.featureTitle}>Advanced Analytics</h3>
              <p style={styles.featureText}>
                10,000+ Monte Carlo simulations provide comprehensive risk metrics including debt probability and survival curves
              </p>
            </div>

            <div style={styles.featureCard}>
              <h3 style={styles.featureTitle}>Interactive Visualizations</h3>
              <p style={styles.featureText}>
                Explore trajectory plots, outcome distributions, and detailed statistical breakdowns of your financial scenarios
              </p>
            </div>
          </div>

          <div style={styles.modelInfo}>
            <h3 style={styles.modelTitle}>Income Volatility Model</h3>
            <p style={styles.modelText}>
              Our model captures real household income dynamics with:
            </p>
            <ul style={styles.modelList}>
              <li><strong>27.3%</strong> monthly probability of income change</li>
              <li><strong>23.2%</strong> median jump size (lognormal distribution)</li>
              <li><strong>50/50</strong> split between upward and downward changes</li>
            </ul>
          </div>
        </div>

        <div style={styles.buttonContainer}>
          <button
            onClick={onStartSimulation}
            style={styles.primaryButton}
            className="primary-button"
          >
            Start Custom Simulation
          </button>

          <button
            onClick={onTrySample}
            style={styles.secondaryButton}
            className="secondary-button"
          >
            Try Sample Input
          </button>
        </div>

        <p style={styles.footnote}>
          Analyze your financial resilience across various scenarios and time horizons
        </p>
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
  contentCard: {
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    padding: '48px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    width: '100%',
    maxWidth: '900px'
  },
  mainTitle: {
    margin: '0 0 16px 0',
    fontSize: '36px',
    fontWeight: '700',
    color: '#1a1a1a',
    textAlign: 'center',
    lineHeight: '1.2'
  },
  subtitle: {
    fontSize: '18px',
    color: '#4b5563',
    textAlign: 'center',
    marginBottom: '40px',
    lineHeight: '1.6'
  },
  descriptionSection: {
    marginBottom: '40px'
  },
  featureGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '32px'
  },
  featureCard: {
    padding: '24px',
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
    border: '1px solid #e5e7eb'
  },
  featureTitle: {
    margin: '0 0 12px 0',
    fontSize: '18px',
    fontWeight: '600',
    color: '#1f2937'
  },
  featureText: {
    margin: '0',
    fontSize: '14px',
    color: '#6b7280',
    lineHeight: '1.6'
  },
  modelInfo: {
    padding: '24px',
    backgroundColor: '#eff6ff',
    borderRadius: '8px',
    border: '1px solid #bfdbfe'
  },
  modelTitle: {
    margin: '0 0 12px 0',
    fontSize: '18px',
    fontWeight: '600',
    color: '#1e40af'
  },
  modelText: {
    margin: '0 0 12px 0',
    fontSize: '14px',
    color: '#1e40af'
  },
  modelList: {
    margin: '0',
    paddingLeft: '20px',
    fontSize: '14px',
    color: '#1e40af',
    lineHeight: '1.8'
  },
  buttonContainer: {
    display: 'flex',
    gap: '16px',
    justifyContent: 'center',
    marginTop: '32px',
    flexWrap: 'wrap'
  },
  primaryButton: {
    padding: '14px 32px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#ffffff',
    backgroundColor: '#3b82f6',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    minWidth: '200px'
  },
  secondaryButton: {
    padding: '14px 32px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#3b82f6',
    backgroundColor: '#ffffff',
    border: '2px solid #3b82f6',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    minWidth: '200px'
  },
  footnote: {
    marginTop: '24px',
    fontSize: '14px',
    color: '#9ca3af',
    textAlign: 'center'
  }
};

// Add hover effects via CSS
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  .primary-button:hover {
    background-color: #2563eb !important;
  }
  .secondary-button:hover {
    background-color: #eff6ff !important;
  }
`;
document.head.appendChild(styleSheet);
