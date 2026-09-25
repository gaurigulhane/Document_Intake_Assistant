import React, { useState } from 'react';
import { AlertOctagon, Check, RefreshCw } from 'lucide-react';

export default function ConflictModal({ conflict, onResolve, onClose }) {
  const [loading, setLoading] = useState(false);

  if (!conflict) return null;

  const handleChoice = async (choice) => {
    setLoading(true);
    try {
      await onResolve(conflict.id, choice);
    } catch (err) {
      alert(err.message || 'Failed to resolve conflict');
    } finally {
      setLoading(false);
    }
  };

  const fieldDisplay = conflict.field.replace(/_/g, ' ').toUpperCase();

  return (
    <div className="modal-backdrop">
      <div className="modal-card conflict-card">
        <div className="modal-header text-amber-500">
          <AlertOctagon size={24} />
          <h3>Information Conflict Detected</h3>
        </div>

        <div className="modal-body">
          <p className="conflict-desc">
            The user response conflicts with previously confirmed information for <strong>{fieldDisplay}</strong>. Please select which value to record:
          </p>

          <div className="conflict-options">
            <div className="option-box old-option">
              <span className="option-label">Previous Confirmed Value</span>
              <div className="option-value">{conflict.old_value || 'None'}</div>
              <button 
                disabled={loading} 
                onClick={() => handleChoice('keep_old')}
                className="btn btn-secondary btn-full"
              >
                {loading ? <RefreshCw size={14} className="spin" /> : <Check size={14} />} Keep Previous
              </button>
            </div>

            <div className="option-box new-option">
              <span className="option-label">New Provided Value</span>
              <div className="option-value">{conflict.new_value || 'None'}</div>
              <button 
                disabled={loading} 
                onClick={() => handleChoice('use_new')}
                className="btn btn-primary btn-full"
              >
                {loading ? <RefreshCw size={14} className="spin" /> : <Check size={14} />} Use New Value
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
