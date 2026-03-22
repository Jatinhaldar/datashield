import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Shield, AlertTriangle } from 'lucide-react';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const messagesEndRef = useRef(null);
  const scrollAreaRef = useRef(null);

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

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userText = inputValue.trim();
    setInputValue('');
    setError(null);
    
    // Add user message to history
    const newUserMsg = { role: 'user', content: userText };
    setMessages((prev) => [...prev, newUserMsg]);
    setIsLoading(true);

    try {
      // API call to the backend
      // Using a relative path or full local URL for development
      const response = await axios.post('http://localhost:8000/chat', {
        message: userText
      });

      const { response: aiResponse, masked_query: maskedQuery } = response.data;
      
      // Determine if masking actually happened (e.g. if masked_query != userText)
      const isMasked = maskedQuery && maskedQuery !== userText;

      const newAiMsg = {
        role: 'ai',
        content: aiResponse || 'No response',
        maskedQuery: isMasked ? maskedQuery : null
      };

      setMessages((prev) => [...prev, newAiMsg]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to connect to the server. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>
          <Shield size={24} color="var(--accent-color)" />
          SecureAI Shield
        </h1>
        <p>Chat securely with PII protection enabled.</p>
      </header>

      <div className="chat-area" ref={scrollAreaRef}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '2rem' }}>
            <p>Start a conversation. Sensing any PII (adhar, medical) will be automatically masked.</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message-wrapper ${msg.role}`}>
            <div className="message-bubble">
              {msg.content}
            </div>
            
            {/* Masked Input Display */}
            {msg.role === 'ai' && msg.maskedQuery && (
              <div className="masked-container" title="This is what the AI actually received">
                <div className="masked-label">
                  <AlertTriangle size={14} /> PII Masked Input Sent to AI:
                </div>
                <div className="masked-text">
                  {msg.maskedQuery}
                </div>
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className="message-wrapper ai">
            <div className="message-bubble" style={{ padding: '0.75rem 0.5rem' }}>
              <div className="loading-dots">
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <div className="input-form">
          <textarea
            className="chat-input"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Type your message securely..."
            rows={1}
            disabled={isLoading}
          />
          <button 
            className="send-button"
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            title="Send"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
