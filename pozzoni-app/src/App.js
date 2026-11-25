import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [side, setSide] = useState('left');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pdfUrl, setPdfUrl] = useState(null);
  const [progress, setProgress] = useState(0);

  // === SURGICALLY FIXED PLUMBING ===
  const handleAnalyze = async () => {
    if (!file) {
      setError("Please select a video file first!");
      return;
    }

    setError('');
    setLoading(true);
    setProgress(0); 
    setPdfUrl(null); 

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev < 60) return prev + 5;       
        if (prev < 85) return prev + 2;       
        if (prev < 95) return prev + 0.5;     
        return prev;                          
      });
    }, 500);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('target_side', side);

    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error("Analysis failed. Make sure the backend server is running!");
      }

      // Securely handle the PDF Blob
      const blob = await response.blob();
      
      if (blob.type !== "application/pdf") {
          const text = await blob.text();
          throw new Error("Backend Error: " + text);
      }

      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }));

      clearInterval(progressInterval);
      setProgress(100);

      setTimeout(() => {
        setPdfUrl(url);
        setLoading(false);
      }, 600);

    } catch (err) {
      clearInterval(progressInterval);
      setError(err.message);
      setLoading(false);
      setProgress(0);
    }
  };

  // === YOUR BEAUTIFUL UI (UNTOUCHED) ===
  return (
    <div style={styles.container}>
      
      {/* THE 3-LOGO HEADER */}
      <div style={styles.logoHeader}>
        <img src="/rush-logo.png" alt="The Rush Logo" style={styles.logo} />
        <img src="/aou-logo.png" alt="AOU Logo" style={styles.centerLogo} />
        <img src="/monta-logo.png" alt="Monta AI Logo" style={styles.logo} />
      </div>

      {/* MAIN UPLOAD CARD */}
      <div style={styles.glassCard}>
        <h1 style={styles.title}>AI Pozzoni Padel Coach</h1>
        <p style={styles.subtitle}>Upload a court video to generate your structural analysis.</p>

        <div style={styles.uploadSection}>
          <input 
            type="file" 
            accept="video/mp4,video/x-m4v,video/*" 
            onChange={(e) => setFile(e.target.files[0])}
            style={styles.fileInput}
          />
        </div>

        <div style={styles.switchContainer}>
          <label style={styles.radioLabel}>
            <input 
              type="radio" 
              value="left" 
              checked={side === 'left'} 
              onChange={(e) => setSide(e.target.value)} 
              style={{marginRight: '8px'}}
            />
            Track Left Player
          </label>
          <label style={styles.radioLabel}>
            <input 
              type="radio" 
              value="right" 
              checked={side === 'right'} 
              onChange={(e) => setSide(e.target.value)} 
              style={{marginRight: '8px'}}
            />
            Track Right Player
          </label>
        </div>

        {error && <p style={styles.errorText}>⚠️ {error}</p>}

        {/* DYNAMIC PROGRESS BUTTON */}
        <button 
          onClick={handleAnalyze} 
          disabled={loading}
          style={{
            ...styles.button, 
            opacity: loading ? 0.9 : 1,
            position: 'relative', 
            overflow: 'hidden'
          }}
        >
          {/* THE GREEN FILL BAR */}
          {loading && (
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              height: '100%',
              width: `${progress}%`,
              backgroundColor: '#10b981',
              transition: 'width 0.5s ease',
              zIndex: 1
            }} />
          )}

          {/* THE BUTTON TEXT */}
          <span style={{ position: 'relative', zIndex: 2 }}>
            {loading ? `⚙️ Analyzing Video (${Math.floor(progress)}%)...` : "Generate AI Report"}
          </span>
        </button>

      </div>

      {/* PDF VIEWER */}
      {pdfUrl && (
        <div style={styles.reportContainer}>
          <h2 style={styles.reportTitle}>✅ Analysis Complete</h2>
          <iframe 
            src={pdfUrl} 
            title="AI Pozzoni Report" 
            style={styles.pdfViewer}
          ></iframe>
          <a 
            href={pdfUrl} 
            download={`AI_Pozzoni_${side.toUpperCase()}_Report.pdf`} 
            style={styles.downloadButton}
          >
            📥 Download PDF Report
          </a>
        </div>
      )}

      {/* SIGNATURE FOOTER */}
      <div style={styles.footer}>
        <p>Developed by Ali Shawki</p>
      </div>

    </div>
  );
}

// === PREMIUM UI DESIGN STYLES (UNTOUCHED) ===
const styles = {
  container: {
    fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    backgroundImage: 'url("/background.jpg")',
    backgroundSize: '100% auto', 
    backgroundRepeat: 'no-repeat', 
    backgroundColor: '#0f2027', 
    backgroundPosition: 'center', 
    backgroundAttachment: 'fixed', 
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    paddingTop: '30px',
    color: '#ffffff'
  },
  logoHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
    maxWidth: '750px', 
    marginBottom: '20px',
  },
  logo: {
    height: '60px', 
    width: '120px', 
    objectFit: 'contain',
    backgroundColor: 'rgba(255, 255, 255, 0.9)', 
    padding: '10px',
    borderRadius: '12px',
    boxShadow: '0 4px 15px rgba(0,0,0,0.3)',
  },
  centerLogo: {
    height: '75px', 
    width: '150px',
    objectFit: 'contain',
    backgroundColor: 'rgba(255, 255, 255, 0.9)', 
    padding: '12px',
    borderRadius: '12px',
    boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
  },
  glassCard: {
    backgroundColor: 'rgba(0, 0, 0, 0.5)', 
    backdropFilter: 'blur(12px)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    padding: '40px', 
    borderRadius: '20px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.6)', 
    display: 'flex',
    flexDirection: 'column', 
    alignItems: 'center', 
    width: '450px',
    marginBottom: '40px',
    textAlign: 'center'
  },
  title: { 
    margin: '0 0 10px 0',
    fontSize: '28px',
    fontWeight: '700',
    letterSpacing: '1px'
  },
  subtitle: { 
    color: '#d1d5db', 
    marginBottom: '30px',
    fontSize: '15px'
  },
  uploadSection: {
    width: '100%',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    border: '2px dashed rgba(255, 255, 255, 0.3)',
    borderRadius: '10px',
    padding: '20px',
    marginBottom: '25px'
  },
  fileInput: { 
    color: 'white',
    width: '100%',
    cursor: 'pointer'
  },
  switchContainer: { 
    display: 'flex', 
    justifyContent: 'space-between', 
    width: '100%', 
    marginBottom: '30px',
    backgroundColor: 'rgba(0,0,0,0.3)',
    padding: '15px',
    borderRadius: '10px'
  },
  radioLabel: { 
    fontSize: '16px', 
    cursor: 'pointer',
    fontWeight: '500'
  },
  button: {
    backgroundColor: '#0ea5e9', 
    color: 'white', 
    border: 'none', 
    padding: '16px',
    borderRadius: '10px', 
    fontSize: '16px', 
    fontWeight: 'bold', 
    cursor: 'pointer', 
    width: '100%',
    boxShadow: '0 4px 15px rgba(14, 165, 233, 0.4)',
  },
  errorText: { 
    color: '#ef4444', 
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    padding: '10px',
    borderRadius: '5px',
    marginBottom: '20px',
    width: '100%'
  },
  reportContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    padding: '30px',
    borderRadius: '15px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.7)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    width: '850px',
    marginBottom: '40px'
  },
  reportTitle: {
    color: '#059669', 
    marginBottom: '20px',
    marginTop: '0'
  },
  pdfViewer: {
    width: '100%',
    height: '600px',
    border: '1px solid #ccc',
    borderRadius: '10px',
    marginBottom: '25px'
  },
  downloadButton: {
    backgroundColor: '#10b981', 
    color: 'white',
    textDecoration: 'none',
    padding: '14px 28px',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 'bold',
    boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)',
  },
  footer: {
    marginTop: 'auto', 
    padding: '15px',
    color: 'rgba(255, 255, 255, 0.9)', 
    fontSize: '14px',
    letterSpacing: '1px',
    fontWeight: '600',
    backgroundColor: 'rgba(0,0,0,0.6)', 
    width: '100%',
    textAlign: 'center'
  }
};

export default App;