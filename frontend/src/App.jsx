import { useState } from 'react';
import InputForm from './components/InputForm';
import LoadingSpinner from './components/LoadingSpinner';
import ResultsDisplay from './components/ResultsDisplay';
import { calculateRisk } from './services/api';

function App() {
  const [view, setView] = useState('form');
  const [results, setResults] = useState(null);

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
    setView('form');
    setResults(null);
  };

  return (
    <>
      {view === 'form' && <InputForm onSubmit={handleCalculate} />}
      {view === 'loading' && <LoadingSpinner />}
      {view === 'results' && <ResultsDisplay data={results} onReset={handleReset} />}
    </>
  );
}

export default App;