import { useState } from 'react';
import { LineChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, BarChart, Bar, Cell } from 'recharts';

// Monte Carlo Trajectory Chart Component
function MonteCarloChart({ samplePaths, aggregateStats, availableCredit }) {
  // Select subset of sample paths to display (30 paths for good visual density)
  const numPathsToShow = Math.min(30, samplePaths.length);
  const selectedPaths = samplePaths.slice(0, numPathsToShow);

  // Transform data for Recharts - include sample paths in the data
  const chartData = aggregateStats.months.map((month, idx) => {
    const dataPoint = {
      month: month,
      median: aggregateStats.p50[idx],
      p75: aggregateStats.p75[idx],
      p25: aggregateStats.p25[idx],
      p90: aggregateStats.p90[idx],
      p10: aggregateStats.p10[idx]
    };

    // Add each sample path as a separate key
    selectedPaths.forEach((path, pathIdx) => {
      dataPoint[`path${pathIdx}`] = path[idx];
    });

    return dataPoint;
  });

  // Format currency for axis
  const formatCurrency = (value) => {
    if (Math.abs(value) >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    }
    if (Math.abs(value) >= 1000) {
      return `${(value / 1000).toFixed(0)}K`;
    }
    return `${value.toFixed(0)}`;
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <p style={{ margin: '0 0 8px 0', fontWeight: '600', color: '#111827' }}>
            Month {data.month}
          </p>
          <p style={{ margin: '4px 0', fontSize: '14px', color: '#3b82f6' }}>
            <strong>Median:</strong> {formatCurrency(data.median)}
          </p>
          <p style={{ margin: '4px 0', fontSize: '14px', color: '#6b7280' }}>
            <strong>75th:</strong> {formatCurrency(data.p75)}
          </p>
          <p style={{ margin: '4px 0', fontSize: '14px', color: '#6b7280' }}>
            <strong>25th:</strong> {formatCurrency(data.p25)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={chartData} margin={{ top: 20, right: 80, left: 70, bottom: 50 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="month"
          label={{ value: 'Months', position: 'insideBottom', offset: -10 }}
          stroke="#6b7280"
        />
        <YAxis
          label={{ value: 'Net Worth ($)', angle: -90, position: 'insideLeft' }}
          tickFormatter={formatCurrency}
          stroke="#6b7280"
        />
        <Tooltip content={<CustomTooltip />} />

        {/* Sample paths - render first so they're in background */}
        {selectedPaths.map((path, idx) => (
          <Line
            key={`path-${idx}`}
            type="monotone"
            dataKey={`path${idx}`}
            stroke="#94a3b8"
            strokeWidth={1}
            strokeOpacity={0.2}
            dot={false}
            isAnimationActive={false}
            legendType="none"
          />
        ))}

        {/* 90th-10th percentile band (lightest) */}
        <Area
          type="monotone"
          dataKey="p90"
          stroke="none"
          fill="#dbeafe"
          fillOpacity={0.4}
        />
        <Area
          type="monotone"
          dataKey="p10"
          stroke="none"
          fill="#ffffff"
          fillOpacity={1}
        />

        {/* 75th-25th percentile band (darker) */}
        <Area
          type="monotone"
          dataKey="p75"
          stroke="none"
          fill="#93c5fd"
          fillOpacity={0.5}
        />
        <Area
          type="monotone"
          dataKey="p25"
          stroke="none"
          fill="#ffffff"
          fillOpacity={1}
        />

        {/* Median line - bold and prominent */}
        <Line
          type="monotone"
          dataKey="median"
          stroke="#3b82f6"
          strokeWidth={3}
          dot={false}
        />

        {/* Threshold lines */}
        <ReferenceLine
          y={0}
          stroke="#6b7280"
          strokeWidth={2}
          label={{ value: 'Break Even', position: 'insideTopRight', offset: 10, fill: '#6b7280', fontSize: 12 }}
        />
        <ReferenceLine
          y={-availableCredit}
          stroke="#ef4444"
          strokeWidth={2}
          strokeDasharray="5 5"
          label={{ value: 'Credit Limit', position: 'insideTopRight', offset: 10, fill: '#ef4444', fontSize: 12 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

// Outcome Distribution Histogram Component
function OutcomeDistribution({ terminalValues, statistics, availableCredit }) {
  // Create histogram bins
  const createHistogram = (values, numBins = 30) => {
    const min = Math.min(...values);
    const max = Math.max(...values);
    const binWidth = (max - min) / numBins;

    const bins = Array(numBins).fill(0).map((_, i) => ({
      binStart: min + i * binWidth,
      binEnd: min + (i + 1) * binWidth,
      count: 0,
      midpoint: min + (i + 0.5) * binWidth
    }));

    // Count values in each bin
    values.forEach(value => {
      const binIndex = Math.min(
        Math.floor((value - min) / binWidth),
        numBins - 1
      );
      if (binIndex >= 0) {
        bins[binIndex].count++;
      }
    });

    return bins;
  };

  // Determine bar color based on bin position
  const getBarColor = (binMidpoint) => {
    return '#10b981';
  };

  const histogramData = createHistogram(terminalValues, 30);

  // Add color to each bin
  const chartData = histogramData.map(bin => ({
    ...bin,
    fill: getBarColor(bin.midpoint)
  }));

  // Format currency
  const formatCurrency = (value) => {
    if (Math.abs(value) >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    }
    if (Math.abs(value) >= 1000) {
      return `${(value / 1000).toFixed(0)}K`;
    }
    return `${value.toFixed(0)}`;
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const percentage = ((data.count / terminalValues.length) * 100).toFixed(1);

      return (
        <div style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <p style={{ margin: '0 0 8px 0', fontWeight: '600', color: '#111827' }}>
            {formatCurrency(data.binStart)} to {formatCurrency(data.binEnd)}
          </p>
          <p style={{ margin: '4px 0', fontSize: '14px', color: '#374151' }}>
            <strong>{data.count.toLocaleString()}</strong> simulations ({percentage}%)
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={chartData} margin={{ top: 40, right: 40, left: 70, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="midpoint"
          label={{ value: 'Final Net Worth ($)', position: 'insideBottom', offset: -10 }}
          tickFormatter={formatCurrency}
          stroke="#6b7280"
        />
        <YAxis
          label={{ value: 'Number of Simulations', angle: -90, position: 'insideLeft' }}
          stroke="#6b7280"
        />
        <Tooltip content={<CustomTooltip />} />

        {/* Bars with dynamic coloring */}
        <Bar
          dataKey="count"
          stroke="#d1d5db"
          strokeWidth={1}
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.fill} />
          ))}
        </Bar>

        {/* Reference lines for key statistics */}
        <ReferenceLine
          x={statistics.terminalStats.median}
          stroke="#3b82f6"
          strokeWidth={3}
          label={{
            value: `Median: ${formatCurrency(statistics.terminalStats.median)}`,
            position: 'top',
            fill: '#3b82f6',
            fontWeight: '600',
            fontSize: 12
          }}
        />
        <ReferenceLine
          x={statistics.terminalStats.mean}
          stroke="#3b82f6"
          strokeWidth={2}
          strokeDasharray="5 5"
          label={{
            value: `Mean: ${formatCurrency(statistics.terminalStats.mean)}`,
            position: 'top',
            fill: '#3b82f6',
            fontSize: 11
          }}
        />

        {/* Zone boundary lines */}
        <ReferenceLine
          x={0}
          stroke="#6b7280"
          strokeWidth={2}
          label={{ value: 'Break Even', position: 'top', fill: '#6b7280', fontSize: 11 }}
        />
        <ReferenceLine
          x={-availableCredit}
          stroke="#ef4444"
          strokeWidth={2}
          strokeDasharray="5 5"
          label={{ value: 'Credit Limit', position: 'top', fill: '#ef4444', fontSize: 11 }}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}

// Survival Curve Chart Component
function SurvivalCurve({ riskMetrics, aggregateStats, availableCredit, metadata }) {
  const survivalData = aggregateStats.months.map((month, idx) => ({
    month: month,
    stayingPositive: riskMetrics.probabilityPositiveByMonth[idx],
    aboveCredit: riskMetrics.probabilityAboveCreditByMonth[idx]
  }));

  // Get color based on probability
  const getColorForProbability = (prob) => {
    if (prob >= 70) return '#10b981';
    if (prob >= 40) return '#f59e0b';
    return '#ef4444';
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const prob = data.stayingPositive;
      const riskLevel = prob >= 70 ? 'Low Risk' : prob >= 40 ? 'Moderate Risk' : 'High Risk';

      return (
        <div style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <p style={{ margin: '0 0 8px 0', fontWeight: '600', color: '#111827' }}>
            Month {data.month}
          </p>
          <p style={{ margin: '4px 0', fontSize: '14px', color: '#10b981' }}>
            <strong>Staying Positive:</strong> {data.stayingPositive.toFixed(1)}%
          </p>
          <p style={{ margin: '4px 0', fontSize: '14px', color: '#ef4444' }}>
            <strong>Above Credit Limit:</strong> {data.aboveCredit.toFixed(1)}%
          </p>
          <p style={{ margin: '6px 0 0 0', fontSize: '13px', color: '#6b7280', fontStyle: 'italic' }}>
            {riskLevel}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={survivalData} margin={{ top: 20, right: 30, left: 60, bottom: 50 }}>
        <defs>
          <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
            <stop offset="50%" stopColor="#f59e0b" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#ef4444" stopOpacity={0.3} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="month"
          label={{ value: 'Months', position: 'insideBottom', offset: -10 }}
          stroke="#6b7280"
        />
        <YAxis
          label={{ value: 'Probability (%)', angle: -90, position: 'insideLeft' }}
          domain={[0, 100]}
          ticks={[0, 20, 40, 60, 80, 100]}
          stroke="#6b7280"
        />
        <Tooltip content={<CustomTooltip />} />

        {/* Reference lines for key probabilities */}
        <ReferenceLine
          y={90}
          stroke="#9ca3af"
          strokeWidth={1}
          strokeDasharray="3 3"
          label={{ value: '90%', position: 'right', fill: '#9ca3af', fontSize: 11 }}
        />
        <ReferenceLine
          y={50}
          stroke="#9ca3af"
          strokeWidth={1}
          strokeDasharray="3 3"
          label={{ value: '50%', position: 'right', fill: '#9ca3af', fontSize: 11 }}
        />

        {/* Area fill for staying positive */}
        <Area
          type="monotone"
          dataKey="stayingPositive"
          stroke="none"
          fill="url(#colorGradient)"
        />

        {/* Line for staying positive - with dynamic color */}
        <Line
          type="monotone"
          dataKey="stayingPositive"
          stroke="#10b981"
          strokeWidth={3}
          dot={false}
          name="Staying Positive"
        />

        {/* Line for staying above credit limit */}
        <Line
          type="monotone"
          dataKey="aboveCredit"
          stroke="#ef4444"
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={false}
          name="Above Credit Limit"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}


export default function ResultsDisplay({ data, onReset }) {
  const [activeVisualizationTab, setActiveVisualizationTab] = useState('trajectories');
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
                <span style={styles.microLabel}>Mean Final Balance</span>
                <span style={styles.microValue}>{formatCurrency(statistics.terminalStats.mean)}</span>
              </div>
              <div style={styles.microStat}>
                <span style={styles.microLabel}>End in Debt</span>
                <span style={styles.microValue}>{statistics.negativeTerminalPct.toFixed(1)}%</span>
              </div>
              <div style={styles.microStat}>
                <span style={styles.microLabel}>Exhaust Credit</span>
                <span style={styles.microValue}>{statistics.creditExhaustionPct.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Primary Visualizations - Tabbed Interface */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Financial Projections</h2>

          {/* Visualization Tab Navigation */}
          <div style={styles.tabContainer}>
            <button
              onClick={() => setActiveVisualizationTab('trajectories')}
              style={{
                ...styles.tab,
                ...(activeVisualizationTab === 'trajectories' ? styles.tabActive : {})
              }}
            >
              Trajectory Paths
            </button>
            <button
              onClick={() => setActiveVisualizationTab('survival')}
              style={{
                ...styles.tab,
                ...(activeVisualizationTab === 'survival' ? styles.tabActive : {})
              }}
            >
              Survival Curve
            </button>
            <button
              onClick={() => setActiveVisualizationTab('distribution')}
              style={{
                ...styles.tab,
                ...(activeVisualizationTab === 'distribution' ? styles.tabActive : {})
              }}
            >
              Outcome Distribution
            </button>
          </div>

          {/* Visualization Content */}
          <div style={{ height: '400px', width: '100%', marginTop: '24px' }}>
            {activeVisualizationTab === 'trajectories' && (
              <MonteCarloChart
                samplePaths={samplePaths}
                aggregateStats={aggregateStats}
                availableCredit={metadata.availableCredit}
              />
            )}

            {activeVisualizationTab === 'survival' && (
              <SurvivalCurve
                riskMetrics={riskMetrics}
                aggregateStats={aggregateStats}
                availableCredit={metadata.availableCredit}
                metadata={metadata}
              />
            )}

            {activeVisualizationTab === 'distribution' && (
              <OutcomeDistribution
                terminalValues={terminalValues}
                statistics={statistics}
                availableCredit={metadata.availableCredit}
              />
            )}
          </div>
        </div>

        {/* Key Statistics Grid */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Key Outcomes</h2>
          <div style={styles.statsGrid}>
            <div style={styles.statCard}>
              <div style={styles.statIcon}>💳</div>
              <div style={styles.statNumber}>{formatCurrency(statistics.medianInterestPaid)}</div>
              <div style={styles.statLabel}>Median Total Interest Paid</div>
            </div>

            <div style={styles.statCard}>
              <div style={styles.statIcon}>💸</div>
              <div style={styles.statNumber}>{formatCurrency(statistics.meanInterestPaid)}</div>
              <div style={styles.statLabel}>Mean Total Interest Paid</div>
            </div>
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
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '20px',
    maxWidth: '600px',
    margin: '0 auto'
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