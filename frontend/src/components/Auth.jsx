import React, { useState } from 'react';
import { supabase } from '../supabaseClient';
import { Shield, Mail, Lock, UserPlus, LogIn, Loader2, User, Phone, CheckCircle } from 'lucide-react';

export default function Auth() {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [message, setMessage] = useState('');

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    
    if (isSignUp && password !== confirmPassword) {
      setMessage("Passwords do not match");
      setLoading(false);
      return;
    }

    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({ 
          email, 
          password,
          options: {
            data: {
              full_name: name,
              phone_number: phone
            }
          }
        });
        if (error) throw error;
        setMessage('Registration successful! Please sign in.');
        setIsSignUp(false); // Switch to sign in after success
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      }
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <Shield size={48} className="shield-icon" />
          <h2>{isSignUp ? 'Join DataShield' : 'Welcome Back'}</h2>
          <p>{isSignUp ? 'Create your secure account' : 'Access your encrypted workspace'}</p>
        </div>

        <form onSubmit={handleAuth} className="auth-form">
          {isSignUp && (
            <>
              <div className="input-group">
                <User size={18} className="input-icon" />
                <input 
                  type="text" 
                  placeholder="Full Name" 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div className="input-group">
                <Phone size={18} className="input-icon" />
                <input 
                  type="tel" 
                  placeholder="Phone Number" 
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required
                />
              </div>
            </>
          )}

          <div className="input-group">
            <Mail size={18} className="input-icon" />
            <input 
              type="email" 
              placeholder="Email Address" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          
          <div className="input-group">
            <Lock size={18} className="input-icon" />
            <input 
              type="password" 
              placeholder="Password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {isSignUp && (
            <div className="input-group">
              <CheckCircle size={18} className="input-icon" />
              <input 
                type="password" 
                placeholder="Confirm Password" 
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
          )}

          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? <Loader2 className="animate-spin" /> : (isSignUp ? <UserPlus size={18} /> : <LogIn size={18} />)}
            {isSignUp ? 'Create Account' : 'Sign In'}
          </button>
        </form>

        {message && (
          <div className={`auth-msg ${message.includes('successful') || message.includes('Check') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}

        <div className="auth-footer">
          <button onClick={() => {
            setIsSignUp(!isSignUp);
            setMessage('');
          }} className="toggle-btn">
            {isSignUp ? 'Already have an account? Sign In' : "Don't have an account? Sign Up"}
          </button>
        </div>
      </div>
    </div>
  );
}
