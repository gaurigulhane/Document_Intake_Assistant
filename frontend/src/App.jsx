import React, { useState, useEffect } from 'react';
import { 
  createSession, getSession, sendMessage, updateStateDirectly, 
  getConflicts, resolveConflict, generateDocument 
} from './api/client';
import ChatInterface from './components/ChatInterface';
import LiveStatePreview from './components/LiveStatePreview';
import ConflictModal from './components/ConflictModal';
import DirectEditModal from './components/DirectEditModal';
import DocumentPreviewModal from './components/DocumentPreviewModal';
import EmailModal from './components/EmailModal';
import { FileText, Shield, RefreshCw } from 'lucide-react';
import './App.css';

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [structuredState, setStructuredState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [conflicts, setConflicts] = useState([]);

  // Modals
  const [activeConflict, setActiveConflict] = useState(null);
  const [editField, setEditField] = useState(null);
  const [documentData, setDocumentData] = useState(null);
  const [showEmailModal, setShowEmailModal] = useState(false);

  // Initialize Session
  const initApp = async () => {
    setLoading(true);
    try {
      const data = await createSession();
      setSessionId(data.id);
      setMessages(data.messages || []);
      setStructuredState(data.structured_state);
    } catch (err) {
      console.error("Error initializing session:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    initApp();
  }, []);

  // Poll/Check Conflicts
  const checkConflicts = async (sid) => {
    if (!sid) return;
    try {
      const list = await getConflicts(sid);
      const unresolved = list.filter(c => c.status === 'unresolved');
      setConflicts(unresolved);
      if (unresolved.length > 0) {
        setActiveConflict(unresolved[0]);
      } else {
        setActiveConflict(null);
      }
    } catch (err) {
      console.error("Error fetching conflicts:", err);
    }
  };

  // Handle Send Message
  const handleSendMessage = async (text) => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const updated = await sendMessage(sessionId, text);
      setMessages(updated.messages);
      setStructuredState(updated.structured_state);
      await checkConflicts(sessionId);
    } catch (err) {
      alert("Failed to send message: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle Direct Edit
  const handleDirectEditSave = async (field, value) => {
    if (!sessionId) return;
    const updatedState = await updateStateDirectly(sessionId, field, value);
    setStructuredState(updatedState);
  };

  // Handle Conflict Resolution
  const handleConflictResolve = async (conflictId, choice) => {
    if (!sessionId) return;
    const updatedState = await resolveConflict(sessionId, conflictId, choice);
    setStructuredState(updatedState);
    await checkConflicts(sessionId);
  };

  // Handle Generate Document
  const handleGenerateDocument = async () => {
    if (!sessionId) return;
    try {
      const doc = await generateDocument(sessionId);
      setDocumentData(doc);
    } catch (err) {
      alert("Failed to generate document: " + err.message);
    }
  };

  return (
    <div className="app-wrapper">
      {/* Top Navbar */}
      <header className="navbar">
        <div className="nav-brand">
          <div className="brand-logo">
            <FileText size={22} />
          </div>
          <div>
            <h1>Document Intake Assistant</h1>
            <p className="brand-subtitle">Conversational Interview & Personal Wishes Document Generator</p>
          </div>
        </div>

        <div className="nav-right">
          <div className="badge-legal-notice">
            <Shield size={14} />
            <span>Fictional Demonstration</span>
          </div>
          <button onClick={initApp} className="btn btn-secondary btn-sm" title="Restart Conversation">
            <RefreshCw size={14} /> New Session
          </button>
        </div>
      </header>

      {/* Main Content Split View */}
      <main className="main-content">
        <div className="chat-panel">
          <ChatInterface 
            messages={messages} 
            onSendMessage={handleSendMessage} 
            loading={loading} 
          />
        </div>

        <div className="state-panel">
          <LiveStatePreview 
            structuredState={structuredState} 
            onDirectEdit={(field, val) => setEditField({ field, val })} 
            onGenerateDocument={handleGenerateDocument} 
          />
        </div>
      </main>

      {/* Conflict Modal */}
      {activeConflict && (
        <ConflictModal 
          conflict={activeConflict} 
          onResolve={handleConflictResolve} 
          onClose={() => setActiveConflict(null)} 
        />
      )}

      {/* Direct Edit Modal */}
      {editField && (
        <DirectEditModal 
          field={editField.field} 
          currentValue={editField.val} 
          onSave={handleDirectEditSave} 
          onClose={() => setEditField(null)} 
        />
      )}

      {/* Document Preview Modal */}
      {documentData && (
        <DocumentPreviewModal 
          sessionId={sessionId} 
          documentData={documentData} 
          onOpenEmail={() => setShowEmailModal(true)} 
          onClose={() => setDocumentData(null)} 
        />
      )}

      {/* Email Modal */}
      {showEmailModal && (
        <EmailModal 
          sessionId={sessionId} 
          onClose={() => setShowEmailModal(false)} 
        />
      )}
    </div>
  );
}
