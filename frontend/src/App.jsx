import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Shield, AlertTriangle, Paperclip, Mic, Square, FileText, LogOut, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { supabase } from './supabaseClient';
import Auth from './components/Auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Voice states
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const audioChunks = useRef([]);

  // File states
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) fetchMessages();
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session) fetchMessages();
      else setMessages([]);
    });

    return () => subscription.unsubscribe();
  }, []);

  const fetchMessages = async () => {
    const { data, error } = await supabase
      .from('messages')
      .select('*')
      .order('created_at', { ascending: true });
    
    if (error) console.error('Error fetching history:', error);
    else if (data) {
      setMessages(data.map(m => ({
        role: m.role,
        content: m.content,
        masked: m.masked_content
      })));
    }
  };

  const saveMessage = async (role, content, masked = null) => {
    if (!session) return;
    const { error } = await supabase
      .from('messages')
      .insert([
        { 
          user_id: session.user.id,
          role: role,
          content: content,
          masked_content: masked
        }
      ]);
    if (error) console.error('Error saving message:', error);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  // 1. Text Chat Handler
  const handleSend = async () => {
    if (!inputValue.trim() && !selectedFile) return;

    if (selectedFile) {
        return handleFileUpload();
    }

    const userText = inputValue.trim();
    setInputValue('');
    setError(null);
    
    setMessages((prev) => [...prev, { role: 'user', content: userText }]);
    saveMessage('user', userText); // Persistence
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        user_input: userText
      });

      const { response: aiResponse, masked } = response.data;
      
      const newAiMsg = {
        role: 'ai',
        content: aiResponse,
        masked: masked !== userText ? masked : null
      };

      setMessages((prev) => [...prev, newAiMsg]);
      saveMessage('ai', aiResponse, newAiMsg.masked); // Persistence
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to connect to the server. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // 2. File Upload Handler
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    const prompt = inputValue.trim() || "Analyze this document.";
    const fileName = selectedFile.name;
    const userDisplayMsg = `[File: ${fileName}] ${prompt}`;
    
    setMessages((prev) => [...prev, { role: 'user', content: userDisplayMsg }]);
    saveMessage('user', userDisplayMsg); // Persistence
    
    setSelectedFile(null);
    setInputValue('');
    setIsLoading(true);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('prompt', prompt);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const { response: aiResponse, masked } = response.data;
      
      const newAiMsg = {
        role: 'ai',
        content: aiResponse,
        masked: masked
      };

      setMessages((prev) => [...prev, newAiMsg]);
      saveMessage('ai', aiResponse, masked); // Persistence
    } catch (err) {
      setError('File upload failed. Internal Server Error.');
    } finally {
      setIsLoading(false);
    }
  };

  // 3. Voice Logic
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.current.push(e.data);
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        sendVoice(audioBlob);
        audioChunks.current = [];
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
      setError(null);
    } catch (err) {
      setError("Microphone access denied or not found.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const sendVoice = async (blob) => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', blob, 'voice_input.wav');

    try {
      const response = await axios.post(`${API_BASE_URL}/voice`, formData);
      const { response: aiResponse, original, masked } = response.data;
      const userOriginal = `🎙️ ${original}`;

      setMessages((prev) => [
        ...prev, 
        { role: 'user', content: userOriginal },
        { role: 'ai', content: aiResponse, masked: masked }
      ]);
      
      saveMessage('user', userOriginal);
      saveMessage('ai', aiResponse, masked);
    } catch (err) {
      setError("Voice transcription failed.");
    } finally {
      setIsLoading(false);
    }
  };

  if (!session) {
    return <Auth />;
  }

  return (
    <div className="app-container">
      <header className="header">
        <div className="logo-group">
          <Shield size={36} className="shield-icon" />
          <h1>DataShield AI</h1>
        </div>
        <div className="header-actions">
           <div className="user-profile">
             <User size={18} />
             <span>{session.user.user_metadata?.full_name || session.user.email}</span>
           </div>
           <div className="live-badge">
             <div className="pulse-dot"></div>
             SECURE LIVE
           </div>
           <button onClick={handleLogout} className="logout-btn" title="Sign Out">
             <LogOut size={18} />
             <span>Log Out</span>
           </button>
        </div>
      </header>

      <div className="chat-area">
        {messages.length === 0 && (
          <div className="welcome-widget">
            <div className="robot-container">
              <Shield size={60} color="white" />
            </div>
            <h2>Meet the Shield!</h2>
            <p>Your futuristic AI companion with built-in PII protection. Speak or type freely—I've got your back.</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message-wrapper ${msg.role}`}>
            <div className="message-bubble">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
            
            {msg.role === 'ai' && msg.masked && (
              <div className="masked-notification">
                <span className="masked-tag">🛡️ AI SHIELDED INPUT</span>
                <div className="masked-content">{msg.masked}</div>
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className="message-wrapper ai">
            <div className="typing">
               <span></span><span></span><span></span>
            </div>
          </div>
        )}

        {error && <div className="error-box">{error}</div>}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-section">
        {selectedFile && (
          <div className="file-pill" style={{ marginBottom: '1rem' }}>
            <FileText size={16} /> {selectedFile.name}
            <button 
              onClick={() => setSelectedFile(null)}
              style={{ background: 'transparent', border: 'none', color: 'white', cursor: 'pointer', marginLeft: '0.5rem' }}
            >
              ×
            </button>
          </div>
        )}
        
        <div className="dock">
          <button 
             className="action-btn" 
             onClick={() => fileInputRef.current.click()}
             title="Add File"
          >
            <Paperclip size={24} />
          </button>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileSelect} 
            style={{ display: 'none' }} 
            accept=".pdf,.xlsx,.xls,.csv,.png,.jpg,.jpeg"
          />

          <textarea
            className="input-field"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={selectedFile ? "Tell me about this..." : "Speak your mind..."}
            rows={1}
          />

          {isRecording ? (
            <button className="action-btn recording-state" onClick={stopRecording}>
              <Square size={22} fill="currentColor" />
            </button>
          ) : (
            <button className="action-btn" onClick={startRecording} title="Voice">
              <Mic size={24} />
            </button>
          )}

          <button 
            className="go-button"
            onClick={handleSend}
            disabled={(!inputValue.trim() && !selectedFile) || isLoading}
          >
            <Send size={24} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
