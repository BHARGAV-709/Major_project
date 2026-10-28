import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Database, 
  SlidersHorizontal, 
  Layers, 
  Cpu, 
  PlayCircle, 
  BrainCircuit, 
  FlaskConical, 
  BarChart3, 
  GanttChartSquare, 
  BookOpenCheck 
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Dataset', path: '/dataset', icon: Database },
  { name: 'Preprocessing', path: '/preprocessing', icon: SlidersHorizontal },
  { name: 'Workload Generator', path: '/workload', icon: Layers },
  { name: 'Resource Manager', path: '/resources', icon: Cpu },
  { name: 'Simulation Engine', path: '/simulation', icon: PlayCircle },
  { name: 'Algorithms Suite', path: '/algorithms', icon: BrainCircuit },
  { name: 'Benchmark Suite', path: '/experiments', icon: FlaskConical },
  { name: 'Results & Analytics', path: '/results', icon: BarChart3 },
  { name: 'Gantt View', path: '/gantt', icon: GanttChartSquare },
  { name: 'Documentation', path: '/documentation', icon: BookOpenCheck },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen sticky top-0 shadow-sm z-30">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-100 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-brand-600 flex items-center justify-center text-white shadow-md shadow-brand-500/20 font-bold text-lg">
          E
        </div>
        <div>
          <h1 className="font-bold text-slate-900 text-sm tracking-tight">Enterprise Analytics</h1>
          <p className="text-xs text-brand-600 font-medium">Resource Scheduler</p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-brand-50 text-brand-700 font-semibold shadow-xs border border-brand-100'
                    : 'text-slate-600 hover:bg-slate-100/70 hover:text-slate-900'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/50">
        <div className="text-[11px] text-slate-500 font-medium">Academic Final-Year Project</div>
        <div className="text-[10px] text-slate-400 mt-0.5">Heuristics • Metaheuristics • RL</div>
      </div>
    </aside>
  );
}
