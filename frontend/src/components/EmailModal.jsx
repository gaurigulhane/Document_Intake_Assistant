import React, { useState } from 'react';
import { Mail, Send, X, RefreshCw } from 'lucide-react';
import { sendEmail } from '../api/client';

export default function EmailModal({ sessionId, onClose }) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    setMsg(null);
    try {
      const res = await sendEmail(sessionId, email);
      setMsg({ type: 'success', text: res.message || 'Email sent successfully!' });
    } catch (err) {
      setMsg({ type: 'error', text: err.message || 'Failed to send email.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-header">
          <div className="flex items-center gap-2">
            <Mail size={18} className="text-emerald-400" />
            <h3>Email Generated Document</h3>
          </div>
          <button onClick={onClose} className="btn-icon"><X size={16} /></button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          <p className="text-sm text-slate-300">
            Enter your email address to receive your Personal Wishes Document as a PDF attachment.
          </p>

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input 
              type="email" 
              required
              placeholder="user@example.com" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="form-input"
            />
          </div>

          {msg && (
            <div className={`alert-box ${msg.type === 'success' ? 'alert-success' : 'alert-error'}`}>
              {msg.text}
            </div>
          )}

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn btn-secondary">Close</button>
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? <RefreshCw size={14} className="spin" /> : <Send size={14} />} Send Document
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
