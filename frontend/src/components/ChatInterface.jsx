import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, RefreshCw } from 'lucide-react';

export default function ChatInterface({ messages = [], onSendMessage, loading }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleChipClick = (text) => {
    if (loading) return;
    onSendMessage(text);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-header-info">
          <div className="bot-avatar">
            <Bot size={20} />
          </div>
          <div>
            <h3>Intake Assistant</h3>
            <span className="status-online">● Online & Ready</span>
          </div>
        </div>
      </div>

      <div className="chat-messages-area">
        {messages.map((msg) => (
          <div 
            key={msg.id || Math.random()} 
            className={`chat-bubble-container ${msg.role === 'user' ? 'bubble-user' : 'bubble-assistant'}`}
          >
            <div className="avatar-icon">
              {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
            </div>
            <div className="bubble-content">
              <p>{msg.content}</p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-bubble-container bubble-assistant">
            <div className="avatar-icon">
              <Bot size={14} />
            </div>
            <div className="bubble-content typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-suggestions">
        <span className="suggestion-label"><Sparkles size={12} /> Suggestions:</span>
        <button onClick={() => handleChipClick("My name is Jane Smith")} className="chip">
          "My name is Jane Smith"
        </button>
        <button onClick={() => handleChipClick("I don't have children and my brother James is my executor")} className="chip">
          "No children, brother James is executor"
        </button>
        <button onClick={() => handleChipClick("My home address is 10 Downing Street, London")} className="chip">
          "10 Downing St, London"
        </button>
      </div>

      <form onSubmit={handleSubmit} className="chat-input-area">
        <input 
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your response here..."
          className="chat-input"
          disabled={loading}
        />
        <button type="submit" disabled={!input.trim() || loading} className="btn-send">
          {loading ? <RefreshCw size={16} className="spin" /> : <Send size={16} />}
        </button>
      </form>
    </div>
  );
}
