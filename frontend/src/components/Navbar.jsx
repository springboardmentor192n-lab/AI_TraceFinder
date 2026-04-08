import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Fingerprint, History, Info, Home } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  const linkClass = (path) =>
    `flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
      location.pathname === path
      ? 'bg-indigo-600 text-white'
      : 'text-gray-400 hover:bg-slate-800 hover:text-white'
    }`;

  return (
    <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="bg-red-600/10 border border-red-500/20 p-2 rounded-lg">
            <Fingerprint className="w-6 h-6 text-red-500" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">TraceFinder</h1>
            <p className="text-xs text-gray-500">Forensic Scanner ID</p>
          </div>
        </Link>

        <nav className="flex items-center gap-2 bg-slate-800 p-1 rounded-xl border border-slate-700">
          <Link to="/" className={linkClass('/')}><Home className="w-4 h-4"/> Dashboard</Link>
          <Link to="/history" className={linkClass('/history')}><History className="w-4 h-4"/> History</Link>
          <Link to="/about" className={linkClass('/about')}><Info className="w-4 h-4"/> About</Link>
        </nav>
      </div>
    </header>
  );
};

export default Navbar;