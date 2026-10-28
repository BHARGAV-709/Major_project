import React from 'react';
import { motion } from 'framer-motion';

export default function MetricCard({ title, value, unit = '', icon: Icon, description, color = 'brand' }) {
  const colorStyles = {
    brand: 'bg-brand-50 text-brand-600 border-brand-100',
    emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
    rose: 'bg-rose-50 text-rose-600 border-rose-100',
    indigo: 'bg-indigo-50 text-indigo-600 border-indigo-100',
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs hover:shadow-md transition-shadow"
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className={`w-9 h-9 rounded-lg flex items-center justify-center border ${colorStyles[color] || colorStyles.brand}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-1">
        <span className="text-2xl font-bold text-slate-900 tracking-tight">{value}</span>
        {unit && <span className="text-sm font-medium text-slate-500">{unit}</span>}
      </div>

      {description && (
        <p className="mt-2 text-xs text-slate-500 font-normal">{description}</p>
      )}
    </motion.div>
  );
}
