import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { AssetProvider } from './context/AssetContext';
import { AppLayout } from './components/layout/AppLayout';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { Login } from './pages/Login';
import Dashboard from './pages/Dashboard';
import BridgeList from './pages/BridgeList';
import BridgeDetail from './pages/BridgeDetail';
import MapView from './pages/MapView';
import InspectionForm from './pages/InspectionForm';
import IssueRegistry from './pages/IssueRegistry';
import AuditLogs from './pages/AuditLogs';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AssetProvider>
          <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/bridges" element={<BridgeList />} />
                <Route path="/bridges/:id" element={<BridgeDetail />} />
                <Route path="/issues" element={<IssueRegistry />} />
                <Route path="/map" element={<MapView />} />
              </Route>
            </Route>

            {/* Inspection Form (requires inspection:create) */}
            <Route element={<ProtectedRoute permission="inspection:create" />}>
              <Route element={<AppLayout />}>
                 <Route path="/bridges/:id/inspections/new" element={<InspectionForm />} />
              </Route>
            </Route>

            {/* Audit Logs (requires audit:read) */}
            <Route element={<ProtectedRoute permission="audit:read" />}>
              <Route element={<AppLayout />}>
                <Route path="/audit" element={<AuditLogs />} />
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
        </AssetProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;