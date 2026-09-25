import React from 'react';
import { Award, CheckCircle } from 'lucide-react';

export default function CompletionProgressBar({ percentage = 0, confirmedCount = 0, totalCount = 7 }) {
  const isComplete = percentage >= 100;

  return (
    <div className="progress-container">
      <div className="progress-header">
        <div className="progress-title">
          {isComplete ? <CheckCircle size={16} className="text-emerald-400" /> : <Award size={16} className="text-blue-400" />}
          <span>Document Completion</span>
        </div>
        <span className={`progress-percentage ${isComplete ? 'complete' : ''}`}>
          {percentage}%
        </span>
      </div>

      <div className="progress-track">
        <div 
          className={`progress-fill ${isComplete ? 'fill-complete' : ''}`} 
          style={{ width: `${Math.min(percentage, 100)}%` }} 
        />
      </div>

      <div className="progress-footer">
        <span>{confirmedCount} of {totalCount} items confirmed</span>
        {isComplete && <span className="ready-tag">Ready to Export</span>}
      </div>
    </div>
  );
}
