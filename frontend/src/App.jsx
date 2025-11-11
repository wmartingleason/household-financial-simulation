import { useState } from 'react';
import LandingPage from './components/LandingPage';
import InputForm from './components/InputForm';
import LoadingSpinner from './components/LoadingSpinner';
import ResultsDisplay from './components/ResultsDisplay';
import { calculateRisk } from './services/api';

function App() {
  const [view, setView] = useState('landing');
  const [results, setResults] = useState(null);

  const handleStartSimulation = () => {
    setView('form');
  };

  const handleTrySample = async () => {
    // Sample data based on README example
    const sampleData = {
      monthlyIncome: 5000,
      monthlyExpenses: 3500,
      currentSavings: 10000,
      availableCredit: 30000,
      interestRate: 25,
      timeHorizon: 24
    };

    setView('loading');

    try {
      const data = await calculateRisk(sampleData);
      setResults(data);
      setView('results');
    } catch (error) {
      console.error('Error:', error);
      alert(`Calculation failed.`);
      setView('landing');
    }
  };

  const handleCalculate = async (formData) => {
    setView('loading');

    try {
      const data = await calculateRisk(formData);
      setResults(data);
      setView('results');
    } catch (error) {
      console.error('Error:', error);
      alert(`Calculation failed.`);
      setView('form');
    }
  };

  const handleReset = () => {
    setView('landing');
    setResults(null);
  };

  return (
    <>
      {view === 'landing' && (
        <LandingPage
          onStartSimulation={handleStartSimulation}
          onTrySample={handleTrySample}
        />
      )}
      {view === 'form' && <InputForm onSubmit={handleCalculate} />}
      {view === 'loading' && <LoadingSpinner />}
      {view === 'results' && <ResultsDisplay data={results} onReset={handleReset} />}
    </>
  );
}

export default App;