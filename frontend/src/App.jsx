
import React, { useState } from 'react';
import { marked } from 'marked';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [page, setPage] = useState('landing');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupOtpSent, setSignupOtpSent] = useState(false);
  const [signupOtp, setSignupOtp] = useState('');
  const [signupMsg, setSignupMsg] = useState('');
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginOtpSent, setLoginOtpSent] = useState(false);
  const [loginOtp, setLoginOtp] = useState('');
  const [loginMsg, setLoginMsg] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState('');

  // --- RAGBot State ---
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadMsg, setUploadMsg] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [context, setContext] = useState([]);
  const [scores, setScores] = useState([]);
  const [chatMsg, setChatMsg] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // --- Signup Flow ---
  const handleSignup = async (e) => {
    e.preventDefault();
    setSignupMsg('');
    const resp = await fetch(`${API_URL}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: signupEmail, password: signupPassword })
    });
    const data = await resp.json();
    setSignupMsg(data.message);
    if (data.success) setSignupOtpSent(true);
  };

  const handleSignupOtp = async (e) => {
    e.preventDefault();
    setSignupMsg('');
    const resp = await fetch(`${API_URL}/verify-2fa`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: signupEmail, otp: signupOtp })
    });
    const data = await resp.json();
    setSignupMsg(data.message);
    if (data.success) {
      setSignupOtpSent(false);
      setSignupEmail('');
      setSignupPassword('');
      setSignupOtp('');
      setPage('landing');
    }
  };

  // --- Login Flow ---
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginMsg('');
    const resp = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: loginEmail, password: loginPassword })
    });
    const data = await resp.json();
    setLoginMsg(data.message);
    if (data.success) setLoginOtpSent(true);
  };

  const handleLoginOtp = async (e) => {
    e.preventDefault();
    setLoginMsg('');
    const resp = await fetch(`${API_URL}/verify-2fa`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: loginEmail, otp: loginOtp })
    });
    const data = await resp.json();
    setLoginMsg(data.message);
    if (data.success) {
      setIsLoggedIn(true);
      setUser(loginEmail);
      setLoginOtpSent(false);
      setLoginOtp('');
      setPage('bot');
    }
  };

  const handleLogout = async () => {
    await fetch(`${API_URL}/logout`, { method: 'POST' });
    setIsLoggedIn(false);
    setUser('');
    setLoginEmail('');
    setLoginPassword('');
    setPage('landing');
  };

  // --- UI Pages ---
  return (
    <div className="container">
      {page === 'landing' && (
        <div className="centered">
          <h1>RAGBot - Your Intelligent Enterprise Assistant</h1>
          <button onClick={() => setPage('login')}>Sign In</button>
          <button onClick={() => setPage('signup')}>Sign Up</button>
        </div>
      )}
      {page === 'signup' && (
        <div className="centered">
          <h2>Sign Up</h2>
          {!signupOtpSent ? (
            <form onSubmit={handleSignup}>
              <input type="email" placeholder="Email" value={signupEmail} onChange={e => setSignupEmail(e.target.value)} required />
              <input type="password" placeholder="Password" value={signupPassword} onChange={e => setSignupPassword(e.target.value)} required />
              <button type="submit">Register</button>
              <button type="button" onClick={() => setPage('landing')}>Back</button>
            </form>
          ) : (
            <form onSubmit={handleSignupOtp}>
              <p>OTP sent to {signupEmail}. Please verify to activate your account.</p>
              <input type="text" placeholder="Enter OTP" value={signupOtp} onChange={e => setSignupOtp(e.target.value)} required />
              <button type="submit">Verify OTP</button>
              <button type="button" onClick={() => { setSignupOtpSent(false); setSignupOtp(''); }}>Back</button>
            </form>
          )}
          {signupMsg && <div className="msg">{signupMsg}</div>}
        </div>
      )}
      {page === 'login' && (
        <div className="centered">
          <h2>Sign In</h2>
          {!loginOtpSent ? (
            <form onSubmit={handleLogin}>
              <input type="email" placeholder="Email" value={loginEmail} onChange={e => setLoginEmail(e.target.value)} required />
              <input type="password" placeholder="Password" value={loginPassword} onChange={e => setLoginPassword(e.target.value)} required />
              <button type="submit">Login</button>
              <button type="button" onClick={() => setPage('landing')}>Back</button>
            </form>
          ) : (
            <form onSubmit={handleLoginOtp}>
              <p>OTP sent to {loginEmail}. Please verify to complete login.</p>
              <input type="text" placeholder="Enter OTP" value={loginOtp} onChange={e => setLoginOtp(e.target.value)} required />
              <button type="submit">Verify & Enter Bot</button>
              <button type="button" onClick={() => { setLoginOtpSent(false); setLoginOtp(''); }}>Back</button>
            </form>
          )}
          {loginMsg && <div className="msg">{loginMsg}</div>}
        </div>
      )}
      {page === 'bot' && isLoggedIn && (
        <div className="centered" style={{width: '100%'}}>
          <h2>Welcome to RAGBot!</h2>
          <div className="msg">Logged in as {user}</div>
          <button onClick={handleLogout}>Logout</button>
          <div style={{marginTop: 30, width: '100%'}}>
            {/* Document Upload */}
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                setUploadMsg('');
                if (!uploadFile) return;
                const formData = new FormData();
                formData.append('file', uploadFile);
                const resp = await fetch(`${API_URL}/upload`, {
                  method: 'POST',
                  body: formData
                });
                const data = await resp.json();
                setUploadMsg(data.message || data.error);
              }}
              style={{marginBottom: 16, width: '100%'}}
            >
              <label style={{marginBottom: 8, fontWeight: 500}}>Upload PDF Document</label>
              <input
                type="file"
                accept="application/pdf"
                onChange={e => setUploadFile(e.target.files[0])}
                style={{marginBottom: 8}}
              />
              <button type="submit">Upload & Index</button>
              {uploadMsg && <div className="msg">{uploadMsg}</div>}
            </form>

            {/* Chat UI */}
            <div style={{width: '100%', marginTop: 24}}>
              <form
                onSubmit={async (e) => {
                  e.preventDefault();
                  setChatMsg('');
                  setAnswer('');
                  setContext([]);
                  setScores([]);
                  if (!question) return;
                  setChatLoading(true);
                  const resp = await fetch(`${API_URL}/ask`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                  });
                  const data = await resp.json();
                  setChatLoading(false);
                  if (data.answer) {
                    setAnswer(data.answer);
                    setContext(data.context || []);
                    setScores(data.scores || []);
                  } else {
                    setChatMsg(data.error || 'No answer.');
                  }
                }}
                style={{display: 'flex', flexDirection: 'column', gap: 8, width: '100%'}}
              >
                <label style={{fontWeight: 500}}>Ask a question about your document</label>
                <input
                  type="text"
                  placeholder="Type your question..."
                  value={question}
                  onChange={e => setQuestion(e.target.value)}
                  style={{marginBottom: 4}}
                />
                <button type="submit" disabled={chatLoading}>{chatLoading ? 'Thinking...' : 'Ask'}</button>
              </form>
              {chatMsg && <div className="msg">{chatMsg}</div>}
              {answer && (
                <div
                  className="msg"
                  style={{background: '#f0fdf4', color: '#166534', marginTop: 16, textAlign: 'left'}}
                >
                  <strong>Answer:</strong>
                  <div
                    style={{marginTop: 8}}
                    dangerouslySetInnerHTML={{ __html: marked.parse(answer) }}
                  />
                </div>
              )}
              {/* Context chunks hidden as requested */}
            </div>
          </div>
        </div>
      )}
  </div>
  );
}

export default App;
