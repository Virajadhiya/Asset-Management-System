import React from 'react';

export const ConditionBadge = ({ condition }: { condition: string | null }) => {
  if (!condition) return <span className="text-slate-400 text-xs">N/A</span>;
  const colors: Record<string, string> = {
    EXCELLENT: 'bg-green-100 text-green-800',
    GOOD: 'bg-blue-100 text-blue-800',
    FAIR: 'bg-yellow-100 text-yellow-800',
    POOR: 'bg-orange-100 text-orange-800',
    CRITICAL: 'bg-red-100 text-red-800',
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[condition] || 'bg-gray-100 text-gray-800'}`}>
      {condition}
    </span>
  );
};