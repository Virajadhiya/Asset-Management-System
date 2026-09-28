import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const DEMO_USERS = [
  { role: 'Executive Engineer', username: 'engineer', password: 'eng123', desc: 'Approvals & lifecycle actions' },
  { role: 'Inspector', username: 'inspector', password: 'insp123', desc: 'Conducts surveys & logs defects' },
  { role: 'Maintenance Officer', username: 'maint_off', password: 'maint123', desc: 'Work execution & repairs' },
  { role: 'Admin', username: 'admin', password: 'admin123', desc: 'Full system control & audit logs' },
  { role: 'Department Head', username: 'dept_head', password: 'dept123', desc: 'Oversight & executive reviews' },
  { role: 'Viewer', username: 'viewer', password: 'view123', desc: 'Read-only inventory access' },
];

export const Login = () => {
  const [username, setUsername] = useState('engineer');
  const [password, setPassword] = useState('eng123');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await login({ username, password });
      navigate('/');
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Login failed. Please check your credentials.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h1 className="text-center text-3xl font-black text-slate-900 tracking-tight">PRAVI</h1>
        <p className="mt-1 text-center text-sm font-semibold text-slate-700">
          Bridge Lifecycle & Management Platform
        </p>
        <p className="text-center text-xs text-slate-500 italic mt-0.5">
          Inspired by MoRTH Indian Bridge Management System (IBMS)
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-md sm:rounded-xl border border-slate-200">
          <form className="space-y-4" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 p-3 rounded text-xs text-red-700">
                {error}
              </div>
            )}
            
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Username
              </label>
              <input
                type="text"
                required
                className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-600 focus:border-blue-600"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                Password
              </label>
              <input
                type="password"
                required
                className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-600 focus:border-blue-600"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
              >
                {isLoading ? 'Authenticating...' : 'Sign in'}
              </button>
            </div>
          </form>

          {/* Quick Demo Credentials Bar */}
          <div className="mt-6 pt-5 border-t border-slate-200">
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
              Quick 1-Click Demo Profiles:
            </div>
            <div className="grid grid-cols-2 gap-2">
              {DEMO_USERS.map((u) => (
                <button
                  key={u.username}
                  type="button"
                  onClick={() => handleQuickLogin(u.username, u.password)}
                  className={`p-2 rounded text-left text-xs border transition-all ${
                    username === u.username
                      ? 'border-blue-500 bg-blue-50 text-blue-900 font-semibold'
                      : 'border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700'
                  }`}
                >
                  <div className="font-bold truncate">{u.role}</div>
                  <div className="text-[10px] text-slate-400 truncate">{u.username} / {u.password}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};