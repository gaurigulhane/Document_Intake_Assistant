import React from 'react';
import { FileText, Download, Mail, X, AlertTriangle } from 'lucide-react';
import { getPDFUrl } from '../api/client';

export default function DocumentPreviewModal({ sessionId, documentData, onOpenEmail, onClose }) {
  if (!documentData) return null;

  const pdfUrl = getPDFUrl(sessionId);

  return (
    <div className="modal-backdrop">
      <div className="modal-card doc-modal">
        <div className="modal-header">
          <div className="flex items-center gap-2">
            <FileText size={20} className="text-blue-400" />
            <h3>Personal Wishes Document Preview</h3>
          </div>
          <button onClick={onClose} className="btn-icon"><X size={16} /></button>
        </div>

        <div className="disclaimer-banner">
          <AlertTriangle size={16} />
          <span>FICTIONAL DOCUMENT — NOT LEGAL ADVICE</span>
        </div>

        <div className="modal-body doc-content-box">
          <pre className="doc-text">{documentData.document_text}</pre>
        </div>

        <div className="modal-actions">
          <button onClick={onClose} className="btn btn-secondary">Close</button>
          <button onClick={onOpenEmail} className="btn btn-secondary">
            <Mail size={14} /> Email PDF
          </button>
          <a href={pdfUrl} download target="_blank" rel="noreferrer" className="btn btn-primary">
            <Download size={14} /> Download PDF
          </a>
        </div>
      </div>
    </div>
  );
}
