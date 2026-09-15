import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, RefreshCw, AlertTriangle } from 'lucide-react';
import { endpoints, fetchApi } from '../api';
import './Chatbot.css';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "👋 Hello! I'm your AI Electrical Diagnostic Assistant. I can help you troubleshoot electrical issues, analyze sensor data, or provide safety guidance. How can I help you today?",
      timestamp: new Date().toISOString(),
      metadata: { source: 'system' }
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadHistory = async () => {
    try {
      const history = await fetchApi(endpoints.chatbot + '/history');
      if (history && history.length > 0) {
        setMessages(history);
      }
    } catch (err) {
      console.error('Failed to load history', err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleClear = async () => {
    try {
      await fetchApi(endpoints.chatbot + '/clear', { method: 'POST' });
      setMessages([{
        role: 'assistant',
        content: "Conversation history cleared. How can I help you today?",
        timestamp: new Date().toISOString(),
        metadata: { source: 'system' }
      }]);
    } catch (err) {
      console.error('Failed to clear history', err);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input.trim();
    setInput('');
    
    // Add user message to UI immediately
    const newMsg = {
      role: 'user',
      content: userMsg,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, newMsg]);
    setLoading(true);

    try {
      const response = await fetchApi(endpoints.chatbot, {
        method: 'POST',
        body: JSON.stringify({ message: userMsg })
      });
      
      setMessages(prev => [...prev, response]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I'm sorry, I'm having trouble connecting to the diagnostic engine right now.",
        timestamp: new Date().toISOString(),
        metadata: { source: 'error' }
      }]);
    } finally {
      setLoading(false);
    }
  };

  const formatMessageContent = (content) => {
    // Simple markdown-like formatting for bold and lists
    const formatted = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/_(.*?)_/g, '<em>$1</em>')
      .replace(/\n\n/g, '<br/><br/>')
      .replace(/\n  •/g, '<br/>•')
      .replace(/\n  1./g, '<br/>1.')
      .replace(/\n- /g, '<br/>- ');
    
    return <div dangerouslySetInnerHTML={{ __html: formatted }} />;
  };

  return (
    <div className="chatbot-container h-full flex flex-col animate-fade-in">
      <header className="page-header mb-4 flex justify-between items-center">
        <div>
          <h1 className="text-gradient">AI Diagnostic Assistant</h1>
          <p className="text-muted">Expert electrical troubleshooting guidance</p>
        </div>
        <button onClick={handleClear} className="btn btn-outline text-sm" title="Clear conversation">
          <RefreshCw size={16} /> Clear Chat
        </button>
      </header>

      <div className="chat-interface glass-panel flex flex-col flex-1 overflow-hidden">
        <div className="chat-messages flex-1 overflow-y-auto p-6 flex flex-col gap-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-bubble ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'assistant' ? <Bot size={20} /> : <User size={20} />}
              </div>
              <div className="message-content">
                {formatMessageContent(msg.content)}
                <div className="message-meta mt-2 text-xs opacity-50 flex justify-between">
                  <span>{new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                  {msg.metadata?.source === 'knowledge_base' && <span>(Deterministic)</span>}
                  {msg.metadata?.source === 'llm' && <span>(LLM)</span>}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="message-bubble assistant loading">
              <div className="message-avatar"><Bot size={20} /></div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-area p-4 border-t border-[rgba(255,255,255,0.1)] bg-[rgba(0,0,0,0.2)]">
          <form onSubmit={sendMessage} className="flex gap-2">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe your issue (e.g., 'What causes a short circuit?' or 'My motor is hot')"
              className="input-field flex-1"
              disabled={loading}
            />
            <button type="submit" className="btn btn-primary" disabled={loading || !input.trim()}>
              <Send size={18} />
            </button>
          </form>
          <div className="mt-2 text-center flex items-center justify-center gap-1 text-xs text-muted">
            <AlertTriangle size={12} color="var(--status-warning)" />
            AI Assistant is for guidance only. Always follow standard safety procedures.
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
