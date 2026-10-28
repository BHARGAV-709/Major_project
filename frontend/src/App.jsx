import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

import Dashboard from './pages/Dashboard';
import Dataset from './pages/Dataset';
import Preprocessing from './pages/Preprocessing';
import WorkloadGenerator from './pages/WorkloadGenerator';
import Resources from './pages/Resources';
import Simulation from './pages/Simulation';
import Algorithms from './pages/Algorithms';
import Experiments from './pages/Experiments';
import Results from './pages/Results';
import GanttView from './pages/GanttView';
import Documentation from './pages/Documentation';

export default function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-slate-50 text-slate-900 font-['Inter',sans-serif]">
        {/* Left Sidebar */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Top Header */}
          <Header />

          {/* Dynamic Page View Body */}
          <main className="flex-1 overflow-y-auto p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dataset" element={<Dataset />} />
              <Route path="/preprocessing" element={<Preprocessing />} />
              <Route path="/workload" element={<WorkloadGenerator />} />
              <Route path="/resources" element={<Resources />} />
              <Route path="/simulation" element={<Simulation />} />
              <Route path="/algorithms" element={<Algorithms />} />
              <Route path="/experiments" element={<Experiments />} />
              <Route path="/results" element={<Results />} />
              <Route path="/gantt" element={<GanttView />} />
              <Route path="/documentation" element={<Documentation />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}
