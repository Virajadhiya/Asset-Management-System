import React from 'react';

export const StatusBadge = ({ status }: { status: string }) => {
  const colors: Record<string, string> = {
    OPERATIONAL: 'bg-green-100 text-green-800',
    UNDER_CONSTRUCTION: 'bg-blue-100 text-blue-800',
    UNDER_MAINTENANCE: 'bg-yellow-100 text-yellow-800',
    UNDER_REHABILITATION: 'bg-orange-100 text-orange-800',
    CLOSED: 'bg-red-100 text-red-800',
    PLANNED: 'bg-slate-100 text-slate-800',
    DECOMMISSIONED: 'bg-slate-200 text-slate-800',
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
      {status.replace(/_/g, ' ')}
    </span>
  );
};