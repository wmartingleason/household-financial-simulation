import { useState } from 'react';

export default function ResultsDisplay({ data, onReset }) {
  const [activeTab, setActiveTab] = useState('survival');
  const [detailsExpanded, setDetailsExpanded] = useState(false);

  // Handle case where data is undefined
  if (!data) {
    return <div>No data available</div>;
  }

  const { samplePaths, terminalValues, aggregateStats, statistics, riskMetrics, metadata } = data;
  const { initialIncome: monthlyIncome, monthlyExpenses, initialFund: currentSavings, nMonths: timeHorizon, nSimulations } = metadata;

  // Determine outcome level and color based on median terminal balance
  const getOutcomeLevel = (medianBalance, expenses) => {
    const monthsCovered = medianBalance / expenses;
    if (monthsCovered >= 6) return { level: 'Strong', color: '#10b981', bg: '#d1fae5' };
    if (monthsCovered >= 3) return { level: 'Stable', color: '#3b82f6', bg: '#dbeafe' };
    if (monthsCovered >= 0) return { level: 'At Risk', color: '#f59e0b', bg: '#fef3c7' };
    return { level: 'Distressed', color: '#ef4444', bg: '#fee2e2' };
  };

  const { level, color, bg } = getOutcomeLevel(statistics.terminalStats.median, monthlyExpenses);
  const negativeCount = Math.round((statistics.negativeTerminalPct / 100) * nSimulations);

  // Format currency
  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A';
    const formatted = Math.abs(value).toLocaleString(undefined, { maximumFractionDigits: 0 });
    return value < 0 ? `-$${formatted}` : `$${formatted}`;
  };

  return (
    <div style={styles.container}>
      <div style={styles.mainCard}>
        {/* Hero Section */}
        <div style={styles.hero}>
          <div style={styles.heroContent}>
            <h1 style={{ ...styles.mainNumber, color }}>
              {formatCurrency(statistics.terminalStats.median)}
            </h1>
            <div style={{ ...styles.badge, backgroundColor: color, color: '#ffffff' }}>
              {level} Position
            </div>
            <p style={styles.heroSubtext}>Median Projected Balance at {timeHorizon} Months</p>

            {/* Micro-stats */}
            <div style={styles.microStats}>
              <div style={styles.microStat}>
                <span style={styles.microLabel}>Emergency Fund</span>
                <span style={styles.microValue}>{riskMetrics.emergencyFundMonths.toFixed(1)} months</span>
              </div>
              <div style={styles.microStat}>
                <span style={styles.microLabel}>Best Case (95th)</span>
                <span style={styles.microValue}>{formatCurrency(statistics.terminalStats.p95)}</span>
              </div>
              <div style={styles.microStat}>
                <span style={styles.microLabel}>Worst Case (5th)</span>
                <span style={styles.microValue}>{formatCurrency(statistics.terminalStats.p5)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Primary Visualization - Monte Carlo Trajectories */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Projected Savings Trajectories</h2>
          <div style={{ ...styles.chartPlaceholder, height: '400px' }}>
            <div style={styles.placeholderContent}>
              <div style={styles.placeholderIcon}>📈</div>
              <p style={styles.placeholderText}>Monte Carlo Trajectory Chart</p>
              <p style={styles.placeholderSubtext}>
                Showing {samplePaths.length} simulated paths with percentile bands
              </p>
            </div>
          </div>
        </div>

        {/* Key Statistics Grid */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Key Outcomes</h2>
          <div style={styles.statsGrid}>
            <div style={styles.statCard}>
              <div style={styles.statIcon}>💰</div>
              <div style={styles.statNumber}>{formatCurrency(statistics.terminalStats.mean)}</div>
              <div style={styles.statLabel}>Mean Final Balance</div>
            </div>

            <div style={styles.statCard}>
              <div style={styles.statIcon}>📊</div>
              <div style={styles.statNumber}>{statistics.negativeTerminalPct.toFixed(1)}%</div>
              <div style={styles.statLabel}>End in Debt</div>
            </div>

            <div style={styles.statCard}>
              <div style={styles.statIcon}>⚠️</div>
              <div style={styles.statNumber}>{statistics.everNegativePct.toFixed(1)}%</div>
              <div style={styles.statLabel}>Go Negative at Any Point</div>
            </div>

            <div style={styles.statCard}>
              <div style={styles.statIcon}>📉</div>
              <div style={styles.statNumber}>{formatCurrency(statistics.medianMinBalance)}</div>
              <div style={styles.statLabel}>Median Lowest Point</div>
            </div>

            <div style={styles.statCard}>
              <div style={styles.statIcon}>⏱️</div>
              <div style={styles.statNumber}>
                {statistics.medianMonthsToNegative ? `${statistics.medianMonthsToNegative.toFixed(0)} mo` : 'N/A'}
              </div>
              <div style={styles.statLabel}>Time to First Negative</div>
            </div>

            <div style={styles.statCard}>
              <div style={styles.statIcon}>📈</div>
              <div style={styles.statNumber}>{formatCurrency(statistics.terminalStats.p75)}</div>
              <div style={styles.statLabel}>75th Percentile Outcome</div>
            </div>
          </div>
        </div>

        {/* Secondary Visualizations - Tabs */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Detailed Analysis</h2>

          {/* Tab Navigation */}
          <div style={styles.tabContainer}>
            <button
              onClick={() => setActiveTab('survival')}
              style={{
                ...styles.tab,
                ...(activeTab === 'survival' ? styles.tabActive : {})
              }}
            >
              Survival Curve
            </button>
            <button
              onClick={() => setActiveTab('distribution')}
              style={{
                ...styles.tab,
                ...(activeTab === 'distribution' ? styles.tabActive : {})
              }}
            >
              Outcome Distribution
            </button>
            <button
              onClick={() => setActiveTab('percentiles')}
              style={{
                ...styles.tab,
                ...(activeTab === 'percentiles' ? styles.tabActive : {})
              }}
            >
              Percentile Bands
            </button>
          </div>

          {/* Tab Content */}
          <div style={styles.tabContent}>
            {activeTab === 'survival' && (
              <div style={{ ...styles.chartPlaceholder, height: '300px' }}>
                <div style={styles.placeholderContent}>
                  <div style={styles.placeholderIcon}>📉</div>
                  <p style={styles.placeholderText}>Survival Curve</p>
                  <p style={styles.placeholderSubtext}>
                    Probability of remaining solvent over time
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'distribution' && (
              <div style={{ ...styles.chartPlaceholder, height: '300px' }}>
                <div style={styles.placeholderContent}>
                  <div style={styles.placeholderIcon}>📊</div>
                  <p style={styles.placeholderText}>Terminal Balance Distribution</p>
                  <p style={styles.placeholderSubtext}>
                    Histogram of {terminalValues.length.toLocaleString()} simulation outcomes
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'percentiles' && (
              <div style={{ ...styles.chartPlaceholder, height: '300px' }}>
                <div style={styles.placeholderContent}>
                  <div style={styles.placeholderIcon}>📈</div>
                  <p style={styles.placeholderText}>Percentile Bands Over Time</p>
                  <p style={styles.placeholderSubtext}>
                    10th, 25th, 50th, 75th, 90th percentile trajectories
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Simulation Details - Collapsible */}
        <div style={styles.section}>
          <button
            onClick={() => setDetailsExpanded(!detailsExpanded)}
            style={styles.expandButton}
          >
            <span>Simulation Parameters</span>
            <span style={{ transform: detailsExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}>
              ▼
            </span>
          </button>

          {detailsExpanded && (
            <div style={styles.detailsContent}>
              <div style={styles.detailsGrid}>
                <div style={styles.detailItem}>
                  <span style={styles.detailLabel}>Monthly Income</span>
                  <span style={styles.detailValue}>{formatCurrency(monthlyIncome)}</span>
                </div>
                <div style={styles.detailItem}>
                  <span style={styles.detailLabel}>Monthly Expenses</span>
                  <span style={styles.detailValue}>{formatCurrency(monthlyExpenses)}</span>
                </div>
                <div style={styles.detailItem}>
                  <span style={styles.detailLabel}>Net Monthly</span>
                  <span style={styles.detailValue}>{formatCurrency(riskMetrics.monthlyNetIncome)}</span>
                </div>
                <div style={styles.detailItem}>
                  <span style={styles.detailLabel}>Starting Savings</span>
                  <span style={styles.detailValue}>{formatCurrency(currentSavings)}</span>
                </div>
                <div style={styles.detailItem}>
                  <span style={styles.detailLabel}>Time Horizon</span>
                  <span style={styles.detailValue}>{timeHorizon} months</span>
                </div>
                <div style={styles.detailItem}>
                  <span style={styles.detailLabel}>Simulations Run</span>
                  <span style={styles.detailValue}>{nSimulations.toLocaleString()}</span>
                </div>
              </div>

              <div style={styles.insightBox}>
                <p style={styles.insightText}>
                  In <strong>{negativeCount.toLocaleString()}</strong> out of <strong>{nSimulations.toLocaleString()}</strong> simulations
                  ({statistics.negativeTerminalPct.toFixed(1)}%), the final balance was negative.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div style={styles.actionButtons}>
          <button onClick={onReset} style={styles.primaryButton}>
            Run New Simulation
          </button>
          <button style={styles.secondaryButton}>
            Download Report
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    minHeight: '100vh',
    padding: '40px 20px',
    backgroundColor: '#f9fafb',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
  },
  mainCard: {
    backgroundColor: '#ffffff',
    borderRadius: '16px',
    padding: '48px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    width: '100%',
    maxWidth: '1100px'
  },
  hero: {
    textAlign: 'center',
    padding: '32px 0 48px 0',
    borderBottom: '2px solid #e5e7eb'
  },
  heroContent: {
    maxWidth: '600px',
    margin: '0 auto'
  },
  mainNumber: {
    fontSize: '72px',
    fontWeight: '800',
    margin: '0 0 16px 0',
    lineHeight: '1',
    letterSpacing: '-0.02em'
  },
  badge: {
    display: 'inline-block',
    padding: '8px 20px',
    borderRadius: '24px',
    fontSize: '15px',
    fontWeight: '600',
    marginBottom: '12px',
    textTransform: 'uppercase',
    letterSpacing: '0.05em'
  },
  heroSubtext: {
    fontSize: '18px',
    color: '#6b7280',
    margin: '0 0 32px 0',
    fontWeight: '500'
  },
  microStats: {
    display: 'flex',
    justifyContent: 'center',
    gap: '32px',
    marginTop: '24px',
    flexWrap: 'wrap'
  },
  microStat: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '4px'
  },
  microLabel: {
    fontSize: '13px',
    color: '#9ca3af',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    fontWeight: '600'
  },
  microValue: {
    fontSize: '18px',
    color: '#1f2937',
    fontWeight: '700'
  },
  section: {
    marginTop: '48px'
  },
  sectionTitle: {
    fontSize: '24px',
    fontWeight: '700',
    color: '#111827',
    margin: '0 0 24px 0',
    letterSpacing: '-0.01em'
  },
  chartPlaceholder: {
    backgroundColor: '#f3f4f6',
    borderRadius: '12px',
    border: '2px dashed #d1d5db',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  placeholderContent: {
    textAlign: 'center',
    padding: '40px'
  },
  placeholderIcon: {
    fontSize: '48px',
    marginBottom: '16px'
  },
  placeholderText: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#374151',
    margin: '0 0 8px 0'
  },
  placeholderSubtext: {
    fontSize: '14px',
    color: '#6b7280',
    margin: '0'
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px'
  },
  statCard: {
    backgroundColor: '#f9fafb',
    padding: '24px',
    borderRadius: '12px',
    border: '1px solid #e5e7eb',
    textAlign: 'center',
    transition: 'transform 0.2s, box-shadow 0.2s',
    cursor: 'default'
  },
  statIcon: {
    fontSize: '32px',
    marginBottom: '12px'
  },
  statNumber: {
    fontSize: '28px',
    fontWeight: '700',
    color: '#111827',
    marginBottom: '8px'
  },
  statLabel: {
    fontSize: '14px',
    color: '#6b7280',
    fontWeight: '500'
  },
  tabContainer: {
    display: 'flex',
    gap: '8px',
    borderBottom: '2px solid #e5e7eb',
    marginBottom: '24px'
  },
  tab: {
    padding: '12px 24px',
    fontSize: '15px',
    fontWeight: '600',
    color: '#6b7280',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: '3px solid transparent',
    cursor: 'pointer',
    transition: 'all 0.2s',
    marginBottom: '-2px'
  },
  tabActive: {
    color: '#3b82f6',
    borderBottomColor: '#3b82f6'
  },
  tabContent: {
    marginTop: '0'
  },
  expandButton: {
    width: '100%',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 20px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#374151',
    backgroundColor: '#f9fafb',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  },
  detailsContent: {
    marginTop: '20px',
    padding: '24px',
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
    border: '1px solid #e5e7eb'
  },
  detailsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
    marginBottom: '20px'
  },
  detailItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px'
  },
  detailLabel: {
    fontSize: '13px',
    color: '#6b7280',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.05em'
  },
  detailValue: {
    fontSize: '18px',
    color: '#111827',
    fontWeight: '700'
  },
  insightBox: {
    padding: '16px',
    backgroundColor: '#ffffff',
    borderRadius: '8px',
    border: '1px solid #e5e7eb'
  },
  insightText: {
    fontSize: '15px',
    color: '#374151',
    lineHeight: '1.6',
    margin: '0'
  },
  actionButtons: {
    display: 'flex',
    gap: '16px',
    marginTop: '48px'
  },
  primaryButton: {
    flex: 1,
    padding: '16px 32px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#ffffff',
    backgroundColor: '#3b82f6',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  },
  secondaryButton: {
    flex: 1,
    padding: '16px 32px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#374151',
    backgroundColor: '#ffffff',
    border: '2px solid #e5e7eb',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s'
  }
};