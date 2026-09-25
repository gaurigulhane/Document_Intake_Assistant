import React from 'react';
import { Database, Edit3, User, Home, Globe, Users, ShieldAlert, Gift, HeartHandshake } from 'lucide-react';
import ConfirmationBadge from './ConfirmationBadge';
import CompletionProgressBar from './CompletionProgressBar';

export default function LiveStatePreview({ structuredState, onDirectEdit, onGenerateDocument }) {
  if (!structuredState) return null;

  const { data, statuses, completion_percentage, confirmed_count, total_required_count } = structuredState;

  const renderFieldRow = (key, label, valueDisplay, icon, editKey = key) => {
    const status = statuses?.[key] || 'unknown';
    return (
      <div className="state-field-row" key={key}>
        <div className="field-info">
          <div className="field-label-group">
            {icon}
            <span className="field-title">{label}</span>
          </div>
          <div className="field-value-text">{valueDisplay || <span className="empty-placeholder">Not provided</span>}</div>
        </div>

        <div className="field-actions">
          <ConfirmationBadge status={status} />
          <button 
            onClick={() => onDirectEdit(editKey, data?.[key] ?? '')}
            className="btn-edit" 
            title="Edit value directly"
          >
            <Edit3 size={13} />
          </button>
        </div>
      </div>
    );
  };

  const executor = data?.executor || {};
  const executorDisplay = executor.name ? `${executor.name} (${executor.relationship || 'Relationship unknown'})` : null;

  const gifts = data?.specific_gifts || [];
  const giftsDisplay = gifts.length > 0 ? gifts.join(', ') : null;

  const children = data?.children || [];
  const kidsDisplay = data?.has_children === true 
    ? (children.length > 0 ? `Yes (${children.join(', ')})` : 'Yes') 
    : (data?.has_children === false ? 'No children' : null);

  const worldwideDisplay = data?.covers_worldwide_assets === true 
    ? 'Yes (Worldwide)' 
    : (data?.covers_worldwide_assets === false ? 'No (Local only)' : null);

  return (
    <aside className="sidebar-container">
      <div className="sidebar-header">
        <div className="flex items-center gap-2">
          <Database size={18} className="text-blue-400" />
          <h2>Structured State</h2>
        </div>
        <span className="live-tag">Live Preview</span>
      </div>

      <CompletionProgressBar 
        percentage={completion_percentage} 
        confirmedCount={confirmed_count} 
        totalCount={total_required_count} 
      />

      <div className="state-fields-list">
        {renderFieldRow('full_name', 'Full Name', data?.full_name, <User size={15} />)}
        {renderFieldRow('home_address', 'Home Address', data?.home_address, <Home size={15} />)}
        {renderFieldRow('covers_worldwide_assets', 'Worldwide Assets', worldwideDisplay, <Globe size={15} />)}
        {renderFieldRow('has_children', 'Children Info', kidsDisplay, <Users size={15} />)}
        {renderFieldRow('executor', 'Executor Appointed', executorDisplay, <ShieldAlert size={15} />, 'executor_name')}
        {renderFieldRow('specific_gifts', 'Specific Gifts', giftsDisplay, <Gift size={15} />)}
        {renderFieldRow('additional_wishes', 'Additional Wishes', data?.additional_wishes, <HeartHandshake size={15} />)}
      </div>

      <div className="sidebar-footer">
        <button 
          onClick={onGenerateDocument} 
          className="btn btn-primary btn-full btn-glow"
        >
          Generate Document Draft
        </button>
      </div>
    </aside>
  );
}
