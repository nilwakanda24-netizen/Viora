import React, { useState } from 'react';
import './App.css';

function App() {
  const [xrayFile, setXrayFile] = useState(null);
  const [bloodData, setBloodData] = useState({
    hemoglobin: '',
    white_blood_cells: '',
    platelets: '',
    crp: '',
    cholesterol: '',
    glucose: ''
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setXrayFile(e.target.files[0]);
  };

  const handleBloodChange = (e) => {
    setBloodData({
      ...bloodData,
      [e.target.name]: parseFloat(e.target.value) || ''
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData();
    formData.append('xray_file', xrayFile);
    formData.append('blood_data', JSON.stringify(bloodData));

    try {
      const response = await fetch('http://localhost:8000/analyze/complete', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      setResult(data.result);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header>
        <h1>🏥 Viora - AI Medical Screening</h1>
        <p className="disclaimer">
          ⚠️ Sistema de suport clínic. NO substitueix el diagnòstic mèdic professional.
        </p>
      </header>

      <main>
        <form onSubmit={handleSubmit}>
          <section className="upload-section">
            <h2>📸 Radiografia de Tòrax</h2>
            <input 
              type="file" 
              accept="image/*" 
              onChange={handleFileChange}
              required
            />
          </section>

          <section className="blood-section">
            <h2>🩸 Analítica de Sang</h2>
            <div className="blood-inputs">
              <input name="hemoglobin" placeholder="Hemoglobina (g/dL)" onChange={handleBloodChange} />
              <input name="white_blood_cells" placeholder="Glòbuls blancs (/μL)" onChange={handleBloodChange} />
              <input name="platelets" placeholder="Plaquetes (/μL)" onChange={handleBloodChange} />
              <input name="crp" placeholder="PCR (mg/L)" onChange={handleBloodChange} />
              <input name="cholesterol" placeholder="Colesterol (mg/dL)" onChange={handleBloodChange} />
              <input name="glucose" placeholder="Glucosa (mg/dL)" onChange={handleBloodChange} />
            </div>
          </section>

          <button type="submit" disabled={loading}>
            {loading ? 'Analitzant...' : '🔬 Analitzar'}
          </button>
        </form>

        {result && (
          <section className="results">
            <h2>📋 Resultats</h2>
            <div className={`risk-level ${result.risk_level.toLowerCase()}`}>
              <strong>Nivell de Risc:</strong> {result.risk_level}
            </div>
            <div className="condition">
              <strong>Possible Condició:</strong> {result.possible_condition}
            </div>
            <div className="evidence">
              <strong>Evidències:</strong>
              <ul>
                {result.evidence.map((ev, i) => <li key={i}>{ev}</li>)}
              </ul>
            </div>
            <div className="recommendations">
              <strong>Recomanacions:</strong>
              <ul>
                {result.recommendations.map((rec, i) => <li key={i}>{rec}</li>)}
              </ul>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
