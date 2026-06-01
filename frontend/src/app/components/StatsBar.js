'use client';

import { useState, useEffect } from 'react';

const statConfig = [
  {
    key: 'total_images',
    label: 'Total Images',
    accentColor: '#818cf8', // indigo
    icon: (color) => (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="3" />
        <circle cx="8.5" cy="8.5" r="1.5" fill={color} stroke="none" />
        <path d="m21 15-5-5L5 21" />
      </svg>
    ),
  },
  {
    key: 'total_faces',
    label: 'Total Faces',
    accentColor: '#a78bfa', // violet
    icon: (color) => (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="9" />
        <circle cx="9" cy="10" r="1" fill={color} stroke="none" />
        <circle cx="15" cy="10" r="1" fill={color} stroke="none" />
        <path d="M9 15c1 1.5 5 1.5 6 0" />
      </svg>
    ),
  },
  {
    key: 'total_persons',
    label: 'Total Persons',
    accentColor: '#34d399', // emerald
    icon: (color) => (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="10" cy="7" r="4" />
        <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
  },
  {
    key: 'processed_images',
    label: 'Processed Images',
    accentColor: '#fbbf24', // amber
    icon: (color) => (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
        <path d="m9 12 2 2 4-4" />
      </svg>
    ),
  },
];

export default function StatsBar() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch('/api/stats');
        if (!res.ok) throw new Error('Failed to fetch stats');
        const data = await res.json();
        setStats(data);
      } catch (err) {
        console.error('Error fetching stats:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, []);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
      {statConfig.map(({ key, label, accentColor, icon }) => (
        <div key={key} className="glass-card stat-glow p-5 rounded-xl flex items-center gap-4">
          {/* Icon */}
          <div
            className="flex items-center justify-center w-11 h-11 rounded-lg shrink-0"
            style={{
              backgroundColor: `${accentColor}15`,
              border: `1px solid ${accentColor}25`,
            }}
          >
            {icon(accentColor)}
          </div>

          {/* Content */}
          <div className="flex flex-col min-w-0">
            {loading ? (
              <div className="h-8 w-16 rounded-md bg-white/5 animate-pulse" />
            ) : (
              <span className="text-2xl font-bold text-white tracking-tight leading-none">
                {stats?.[key] ?? '—'}
              </span>
            )}
            <span
              className="text-xs font-medium mt-1 truncate"
              style={{ color: '#8b8b9e' }}
            >
              {label}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
