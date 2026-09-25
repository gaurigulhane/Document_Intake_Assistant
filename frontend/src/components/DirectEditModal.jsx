import React, { useState } from 'react';
import { Edit3, X, Save, RefreshCw } from 'lucide-react';

export default function DirectEditModal({ field, currentValue, onSave, onClose }) {
  const [val, setVal] = useState(currentValue ?? '');
  const [loading, setLoading] = useState(false);

  if (!field) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSave(field, val);
      onClose();
    } catch (err) {
      alert(err.message || 'Failed to update field');
    } finally {
      setLoading(false);
    }
  };

  const fieldLabels = {
    full_name: 'Full Name',
    home_address: 'Home Address',
    covers_worldwide_assets: 'Covers Worldwide Assets',
    has_children: 'Has Children',
    executor_name: 'Executor Name',
    executor_relationship: 'Executor Relationship',
    specific_gifts: 'Specific Gifts',
    additional_wishes: 'Additional Wishes'
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-header">
          <div className="flex items-center gap-2">
            <Edit3 size={18} className="text-blue-400" />
            <h3>Direct Edit: {fieldLabels[field] || field}</h3>
          </div>
          <button onClick={onClose} className="btn-icon"><X size={16} /></button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          {field === 'covers_worldwide_assets' || field === 'has_children' ? (
            <div className="form-group flex-row">
              <label>
                <input 
                  type="radio" 
                  name="boolVal" 
                  checked={val === true || val === 'true'} 
                  onChange={() => setVal(true)} 
                /> Yes
              </label>
              <label>
                <input 
                  type="radio" 
                  name="boolVal" 
                  checked={val === false || val === 'false'} 
                  onChange={() => setVal(false)} 
                /> No
              </label>
            </div>
          ) : field === 'home_address' || field === 'additional_wishes' ? (
            <div className="form-group">
              <textarea 
                rows={4}
                value={val}
                onChange={(e) => setVal(e.target.value)}
                className="form-input"
                placeholder="Enter value..."
              />
            </div>
          ) : (
            <div className="form-group">
              <input 
                type="text"
                value={val}
                onChange={(e) => setVal(e.target.value)}
                className="form-input"
                placeholder="Enter value..."
              />
            </div>
          )}

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn btn-secondary">Cancel</button>
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? <RefreshCw size={14} className="spin" /> : <Save size={14} />} Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
