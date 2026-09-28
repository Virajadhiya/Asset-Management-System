import React, { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useAsset } from '../../context/AssetContext';
import { AssetSwitcher } from './AssetSwitcher';

export const AppLayout = () => {
  const { user, logout, hasPermission } = useAuth();
  const { activeMeta, activeAssetType } = useAsset();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const registryLabel = activeAssetType === 'ALL' ? 'Asset Registry' : activeMeta.plural;

  const navItems = [
    { name: 'Dashboard', path: '/', icon: '📊', show: true },
    { name: registryLabel, path: '/bridges', icon: activeMeta.icon, show: true },
    { name: 'Distress Issues', path: '/issues', icon: '🚨', show: true },
    { name: 'GIS Spatial Map', path: '/map', icon: '🗺️', show: true },
    { name: 'Audit Trail', path: '/audit', icon: '📜', show: hasPermission('audit:read') },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row">
      {/* Mobile Header */}
      <div className="md:hidden bg-slate-900 text-white p-4 flex justify-between items-center">
        <div className="font-bold text-xl flex items-center gap-2">
          <span>PRAVI</span>
          <span className="text-xs px-2 py-0.5 rounded bg-blue-600 font-normal">Multi-Asset</span>
        </div>
        <div className="flex items-center gap-2">
          <AssetSwitcher />
          <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
        </div>
      </div>

      {/* Sidebar */}
      <div className={`${isMobileMenuOpen ? 'block' : 'hidden'} md:block w-full md:w-64 bg-slate-900 text-slate-300 flex flex-col flex-shrink-0 transition-all`}>
        <div className="p-6 hidden md:block border-b border-slate-800">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white tracking-tight">PRAVI</h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 bg-blue-600 text-white rounded">
              v2.0
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">National Infrastructure AMS</p>
          <div className="mt-3 p-2 bg-slate-800/80 rounded-lg flex items-center gap-2 text-xs border border-slate-700/50">
            <span className="text-base">{activeMeta.icon}</span>
            <div className="line-clamp-1">
              <div className="text-[10px] text-slate-400 uppercase font-semibold leading-none">Active Scope</div>
              <div className="font-bold text-slate-200 mt-0.5">{activeMeta.label}</div>
            </div>
          </div>
        </div>
        
        <nav className="flex-1 px-4 py-4 space-y-1.5">
          {navItems.filter(item => item.show).map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-2.5 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path))
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'hover:bg-slate-800 hover:text-white text-slate-300'
              }`}
            >
              <span className="text-base">{item.icon}</span>
              <span>{item.name}</span>
            </Link>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header className="bg-white border-b border-slate-200 shadow-sm z-10">
          <div className="px-4 sm:px-6 lg:px-8 py-3.5 flex justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold text-slate-800 hidden md:block">
                {navItems.find(i => location.pathname === i.path || (i.path !== '/' && location.pathname.startsWith(i.path)))?.name || 'Infrastructure Platform'}
              </h2>
            </div>

            <div className="flex items-center gap-4 ml-auto">
              {/* Quick Link to Distress Incidents */}
              <Link
                to="/issues"
                className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 bg-red-50 hover:bg-red-100 border border-red-200 text-red-700 rounded-lg text-xs font-semibold transition-colors"
              >
                <span>🚨</span>
                <span>Report Distress</span>
              </Link>

              {/* Global Asset Switcher in Top Bar */}
              <div className="hidden sm:block">
                <AssetSwitcher />
              </div>

              <div className="h-6 w-px bg-slate-200 hidden sm:block"></div>

              <div className="flex flex-col items-end">
                <span className="text-sm font-bold text-slate-900 leading-none">{user?.full_name}</span>
                <span className="text-[11px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full mt-0.5 font-medium border border-slate-200">{user?.role}</span>
              </div>
              <button
                onClick={logout}
                className="text-xs text-red-600 hover:text-red-800 font-bold px-3 py-1.5 border border-red-200 rounded-lg hover:bg-red-50 transition-colors shadow-xs"
              >
                Logout
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};