import React from 'react';
import { CheckCircle2, AlertTriangle, AlertOctagon, HelpCircle, Check } from 'lucide-react';

export default function ConfirmationBadge({ status }) {
  switch (status) {
    case 'confirmed':
      return (
        <span className="badge badge-confirmed">
          <CheckCircle2 size={12} /> Confirmed
        </span>
      );
    case 'needs_confirmation':
      return (
        <span className="badge badge-needs-confirmation">
          <AlertTriangle size={12} /> Needs Confirmation
        </span>
      );
    case 'conflicted':
      return (
        <span className="badge badge-conflicted">
          <AlertOctagon size={12} /> Conflict Detected
        </span>
      );
    case 'captured':
      return (
        <span className="badge badge-captured">
          <Check size={12} /> Captured
        </span>
      );
    default:
      return (
        <span className="badge badge-unknown">
          <HelpCircle size={12} /> Unknown
        </span>
      );
  }
}
