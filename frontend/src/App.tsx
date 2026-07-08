import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Settings as SettingsIcon, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle, 
  Terminal, 
  FolderCheck,
  ExternalLink,
  Layers,
  Database,
  UserCheck,
  Clock
} from 'lucide-react';

const API_BASE = "http://localhost:8000";

interface Submission {
  id: number;
  leetcode_submission_id: string;
  problem_id: string;
  problem_title: string;
  difficulty: string;
  language: string;
  topic_tags: string;
  solved_at: string;
  github_commit_sha: string;
  github_file_path: string;
}

interface LogEntry {
  id: number;
  timestamp: string;
  level: string;
  message: string;
  error_code?: string;
  recovery_suggestion?: string;
}

interface SystemStatus {
  github_connected: boolean;
  leetcode_connected: boolean;
  github_repo: string;
  scheduler: {
    status: string;
    sync_interval_minutes: number;
    active_jobs: Array<{ id: string; next_run_time: string }>;
  };
  last_sync_job?: {
    id: number;
    start_time: string;
    end_time?: string;
    status: string;
    error_message?: string;
  };
}

interface StatsData {
  total_solved: number;
  difficulty_breakdown: {
    Easy: number;
    Medium: number;
    Hard: number;
  };
  topic_distribution: Record<string, number>;
}

export default function App() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [stats, setStats] = useState<StatsData | null>(null);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'submissions' | 'logs' | 'settings'>('overview');
  const [syncing, setSyncing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  
  // Settings Form State
  const [githubRepo, setGithubRepo] = useState('');
  const [syncInterval, setSyncInterval] = useState(5);
  const [savingSettings, setSavingSettings] = useState(false);

  const fetchData = async () => {
    try {
      const [statusRes, statsRes, subsRes, logsRes, settingsRes] = await Promise.all([
        fetch(`${API_BASE}/api/status`),
        fetch(`${API_BASE}/api/statistics`),
        fetch(`${API_BASE}/api/submissions?limit=20`),
        fetch(`${API_BASE}/api/logs?limit=25`),
        fetch(`${API_BASE}/api/settings`)
      ]);

      if (statusRes.ok) setStatus(await statusRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
      if (subsRes.ok) setSubmissions(await subsRes.json());
      if (logsRes.ok) setLogs(await logsRes.json());
      
      if (settingsRes.ok) {
        const config = await settingsRes.json();
        setGithubRepo(config.github_repo || '');
        setSyncInterval(config.sync_interval_minutes || 5);
      }
    } catch (err) {
      console.error("Failed to retrieve dashboard APIs: ", err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Poll status every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const triggerSync = async () => {
    setSyncing(true);
    setMessage(null);
    try {
      const res = await fetch(`${API_BASE}/api/sync/trigger`, { method: 'POST' });
      if (res.ok) {
        setMessage("Sync job triggered! Wait a moment for code processing.");
        setTimeout(fetchData, 3000);
      } else {
        setMessage("Failed to start synchronization job.");
      }
    } catch (err) {
      setMessage("Failed to reach backend synchronization server.");
    } finally {
      setSyncing(false);
    }
  };

  const saveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingSettings(true);
    setMessage(null);
    try {
      const res = await fetch(`${API_BASE}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          github_repo: githubRepo,
          sync_interval_minutes: syncInterval
        })
      });
      if (res.ok) {
        setMessage("Configuration updated successfully!");
        fetchData();
      } else {
        setMessage("Failed to save configuration settings.");
      }
    } catch (err) {
      setMessage("Error communicating with settings server.");
    } finally {
      setSavingSettings(false);
    }
  };

  const getDifficultyColor = (diff: string) => {
    const d = diff.toLowerCase();
    if (d === 'easy') return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30 shadow-sm shadow-emerald-500/5';
    if (d === 'medium') return 'text-amber-400 bg-amber-500/10 border-amber-500/30 shadow-sm shadow-amber-500/5';
    return 'text-rose-400 bg-rose-500/10 border-rose-500/30 shadow-sm shadow-rose-500/5';
  };

  return (
    <div className="min-h-screen bg-[#060608] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-950/20 via-black to-[#060608] text-[#F5F5F7] flex flex-col font-sans antialiased">
      {/* Premium Glass Header */}
      <header className="border-b border-white/[0.06] bg-[#060608]/65 backdrop-blur-xl sticky top-0 z-50 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#0071E3] to-[#862bfd] flex items-center justify-center shadow-lg shadow-blue-500/25">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-[#F5F5F7] to-gray-400 bg-clip-text text-transparent">LeetSync Pro</h1>
              <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wider">Accepted submission automation engine</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={triggerSync}
              disabled={syncing}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#0071E3] to-[#0077ED] text-white rounded-xl text-sm font-semibold hover:brightness-110 active:scale-95 transition-all disabled:opacity-50 shadow-md shadow-blue-500/20"
            >
              <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
              Sync Now
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 flex flex-col md:flex-row gap-8">
        
        {/* Navigation Sidebar */}
        <aside className="w-full md:w-64 flex flex-col gap-1.5 shrink-0">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200 border ${activeTab === 'overview' ? 'bg-white/[0.04] text-white border-white/[0.08] shadow-inner shadow-white/5' : 'text-gray-400 border-transparent hover:text-white hover:bg-white/[0.02]'}`}
          >
            <Activity className={`w-4 h-4 ${activeTab === 'overview' ? 'text-[#0071E3]' : ''}`} />
            Overview
          </button>
          <button
            onClick={() => setActiveTab('submissions')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200 border ${activeTab === 'submissions' ? 'bg-white/[0.04] text-white border-white/[0.08] shadow-inner shadow-white/5' : 'text-gray-400 border-transparent hover:text-white hover:bg-white/[0.02]'}`}
          >
            <FolderCheck className={`w-4 h-4 ${activeTab === 'submissions' ? 'text-purple-400' : ''}`} />
            Synced Solutions
          </button>
          <button
            onClick={() => setActiveTab('logs')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200 border ${activeTab === 'logs' ? 'bg-white/[0.04] text-white border-white/[0.08] shadow-inner shadow-white/5' : 'text-gray-400 border-transparent hover:text-white hover:bg-white/[0.02]'}`}
          >
            <Terminal className={`w-4 h-4 ${activeTab === 'logs' ? 'text-amber-400' : ''}`} />
            Sync Logs
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200 border ${activeTab === 'settings' ? 'bg-white/[0.04] text-white border-white/[0.08] shadow-inner shadow-white/5' : 'text-gray-400 border-transparent hover:text-white hover:bg-white/[0.02]'}`}
          >
            <SettingsIcon className={`w-4 h-4 ${activeTab === 'settings' ? 'text-sky-400' : ''}`} />
            Settings
          </button>

          {/* Quick Connection Status Info */}
          <div className="mt-8 p-5 bg-white/[0.02] rounded-2xl border border-white/[0.06] flex flex-col gap-4">
            <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest flex items-center gap-1.5"><UserCheck className="w-3.5 h-3.5" /> Connections</h3>
            <div className="flex items-center justify-between text-xs border-b border-white/[0.04] pb-2.5">
              <span className="flex items-center gap-2 text-gray-400">
                <svg className="w-4 h-4 text-white/80" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg> GitHub
              </span>
              {status?.github_connected ? (
                <span className="flex items-center gap-1 text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded-full text-[10px]">Active</span>
              ) : (
                <span className="flex items-center gap-1 text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded-full text-[10px]">Offline</span>
              )}
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-2 text-gray-400">
                💡 LeetCode
              </span>
              {status?.leetcode_connected ? (
                <span className="flex items-center gap-1 text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded-full text-[10px]">Active</span>
              ) : (
                <span className="flex items-center gap-1 text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded-full text-[10px]">Expired</span>
              )}
            </div>
          </div>
        </aside>

        {/* Dynamic Panel Pane */}
        <section className="flex-1 min-w-0">
          
          {message && (
            <div className="mb-6 p-4 bg-gradient-to-r from-blue-950/30 to-indigo-950/30 border border-blue-500/20 rounded-2xl flex items-center justify-between text-sm text-blue-300">
              <span className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-blue-400" /> {message}</span>
              <button onClick={() => setMessage(null)} className="hover:text-white text-xs">✕</button>
            </div>
          )}

          {activeTab === 'overview' && (
            <div className="flex flex-col gap-8">
              
              {/* Metrics Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                <div className="bg-white/[0.02] border border-white/[0.06] p-6 rounded-3xl flex flex-col gap-2 shadow-lg shadow-black/20 relative overflow-hidden group hover:border-white/10 transition-all duration-300">
                  <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-blue-500 to-indigo-600"></div>
                  <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Total Synced</span>
                  <div className="flex items-baseline justify-between mt-1">
                    <span className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">{stats?.total_solved || 0}</span>
                    <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">Verified</span>
                  </div>
                </div>

                <div className="bg-white/[0.02] border border-white/[0.06] p-6 rounded-3xl flex flex-col gap-2 shadow-lg shadow-black/20 relative overflow-hidden hover:border-emerald-500/20 transition-all duration-300">
                  <div className="absolute top-0 left-0 right-0 h-[2px] bg-emerald-500"></div>
                  <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Easy Solved</span>
                  <div className="flex items-baseline justify-between mt-1">
                    <span className="text-3xl font-extrabold tracking-tight text-emerald-400">{stats?.difficulty_breakdown.Easy || 0}</span>
                  </div>
                </div>

                <div className="bg-white/[0.02] border border-white/[0.06] p-6 rounded-3xl flex flex-col gap-2 shadow-lg shadow-black/20 relative overflow-hidden hover:border-amber-500/20 transition-all duration-300">
                  <div className="absolute top-0 left-0 right-0 h-[2px] bg-amber-500"></div>
                  <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Medium Solved</span>
                  <div className="flex items-baseline justify-between mt-1">
                    <span className="text-3xl font-extrabold tracking-tight text-amber-400">{stats?.difficulty_breakdown.Medium || 0}</span>
                  </div>
                </div>

                <div className="bg-white/[0.02] border border-white/[0.06] p-6 rounded-3xl flex flex-col gap-2 shadow-lg shadow-black/20 relative overflow-hidden hover:border-rose-500/20 transition-all duration-300">
                  <div className="absolute top-0 left-0 right-0 h-[2px] bg-rose-500"></div>
                  <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Hard Solved</span>
                  <div className="flex items-baseline justify-between mt-1">
                    <span className="text-3xl font-extrabold tracking-tight text-rose-400">{stats?.difficulty_breakdown.Hard || 0}</span>
                  </div>
                </div>
              </div>

              {/* Status and Active Scheduler Cards */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Scheduler Status */}
                <div className="bg-white/[0.02] border border-white/[0.06] p-6 rounded-3xl flex flex-col gap-4 shadow-lg shadow-black/15">
                  <div className="flex items-center justify-between border-b border-white/[0.04] pb-4">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-blue-400" />
                      <h3 className="font-bold text-sm">Scheduler Automation</h3>
                    </div>
                    <span className={`text-[10px] px-2.5 py-1 rounded-full font-extrabold ${status?.scheduler.status === 'RUNNING' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                      {status?.scheduler.status}
                    </span>
                  </div>

                  <div className="flex flex-col gap-3 text-sm text-gray-400">
                    <div className="flex justify-between border-b border-white/[0.02] pb-2">
                      <span>Sync Interval</span>
                      <span className="text-white font-semibold">{status?.scheduler.sync_interval_minutes} mins</span>
                    </div>
                    <div className="flex justify-between border-b border-white/[0.02] pb-2">
                      <span>Target Repository</span>
                      <span className="text-blue-400 hover:underline font-semibold font-mono text-xs max-w-[200px] truncate">
                        <a href={`https://github.com/${status?.github_repo}`} target="_blank" rel="noreferrer">
                          {status?.github_repo || 'Not Configured'}
                        </a>
                      </span>
                    </div>
                    <div className="flex justify-between pb-1">
                      <span>Next Sync Runtime</span>
                      <span className="text-white font-mono text-xs">{status?.scheduler.active_jobs[0]?.next_run_time || 'N/A'}</span>
                    </div>
                  </div>
                </div>

                {/* Latest Execution Details */}
                <div className="bg-white/[0.02] border border-white/[0.06] p-6 rounded-3xl flex flex-col gap-4 shadow-lg shadow-black/15">
                  <div className="flex items-center justify-between border-b border-white/[0.04] pb-4">
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4 text-purple-400" />
                      <h3 className="font-bold text-sm">Latest Sync Action</h3>
                    </div>
                    {status?.last_sync_job ? (
                      <span className={`text-[10px] px-2.5 py-1 rounded-full font-extrabold ${status.last_sync_job.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                        {status.last_sync_job.status}
                      </span>
                    ) : (
                      <span className="text-[10px] text-gray-400 font-bold bg-white/5 px-2.5 py-1 rounded-full">No Jobs run</span>
                    )}
                  </div>

                  {status?.last_sync_job ? (
                    <div className="flex flex-col gap-3 text-sm text-gray-400">
                      <div className="flex justify-between border-b border-white/[0.02] pb-2">
                        <span>Job Reference</span>
                        <span className="text-white font-mono text-xs">#{status.last_sync_job.id}</span>
                      </div>
                      <div className="flex justify-between border-b border-white/[0.02] pb-2">
                        <span>Start Time</span>
                        <span className="text-white font-mono text-xs">{new Date(status.last_sync_job.start_time).toLocaleString()}</span>
                      </div>
                      {status.last_sync_job.error_message && (
                        <div className="flex flex-col gap-1 py-1">
                          <span className="text-rose-400 font-bold text-xs uppercase tracking-wide">Error Log:</span>
                          <p className="text-xs text-rose-300 font-mono bg-rose-950/20 p-3 rounded-xl border border-rose-500/15 max-h-24 overflow-y-auto">
                            {status.last_sync_job.error_message}
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="flex-1 flex items-center justify-center text-gray-500 text-xs">
                      Waiting for first scheduled execution.
                    </div>
                  )}
                </div>
              </div>

              {/* Solved List Preview */}
              <div className="bg-white/[0.02] border border-white/[0.06] p-6 rounded-3xl flex flex-col gap-5 shadow-lg shadow-black/15">
                <div className="flex items-center justify-between border-b border-white/[0.04] pb-2">
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-blue-400" />
                    <h3 className="font-bold text-sm">Recent Solved Submissions</h3>
                  </div>
                  <button onClick={() => setActiveTab('submissions')} className="text-xs text-[#0071E3] hover:underline font-semibold">View All</button>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="w-full text-sm border-collapse text-left">
                    <thead>
                      <tr className="border-b border-white/[0.06] text-gray-500 text-[10px] uppercase font-bold tracking-wider">
                        <th className="pb-3 pr-4">ID</th>
                        <th className="pb-3 pr-4">Title</th>
                        <th className="pb-3 pr-4">Difficulty</th>
                        <th className="pb-3 pr-4">Language</th>
                        <th className="pb-3 pr-4">Solved Date</th>
                        <th className="pb-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/[0.04]">
                      {submissions.slice(0, 5).map((sub) => (
                        <tr key={sub.id} className="hover:bg-white/[0.01] transition-all">
                          <td className="py-4 pr-4 font-mono text-xs text-gray-500">{sub.problem_id}</td>
                          <td className="py-4 pr-4 font-bold text-[#F5F5F7]">{sub.problem_title}</td>
                          <td className="py-4 pr-4">
                            <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${getDifficultyColor(sub.difficulty)}`}>
                              {sub.difficulty}
                            </span>
                          </td>
                          <td className="py-4 pr-4 font-mono text-xs text-gray-400">{sub.language}</td>
                          <td className="py-4 pr-4 text-xs text-gray-400">{new Date(sub.solved_at).toLocaleDateString()}</td>
                          <td className="py-4 text-right">
                            <a 
                              href={`https://github.com/${status?.github_repo}/blob/main/${sub.github_file_path}`} 
                              target="_blank" 
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 text-[#0071E3] hover:underline text-xs font-bold"
                            >
                              Code <ExternalLink className="w-3 h-3" />
                            </a>
                          </td>
                        </tr>
                      ))}
                      {submissions.length === 0 && (
                        <tr>
                          <td colSpan={6} className="py-8 text-center text-gray-500 text-sm">
                            No synced submissions found.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'submissions' && (
            <div className="bg-white/[0.02] border border-white/[0.06] p-6 rounded-3xl flex flex-col gap-4 shadow-lg shadow-black/15">
              <div className="border-b border-white/[0.04] pb-4">
                <h2 className="text-lg font-bold">Synchronized Solutions</h2>
                <p className="text-xs text-gray-400">All problems successfully committed to your GitHub landing repository.</p>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse text-left">
                  <thead>
                    <tr className="border-b border-white/[0.06] text-gray-500 text-[10px] uppercase font-bold tracking-wider">
                      <th className="pb-3 pr-4">ID</th>
                      <th className="pb-3 pr-4">Title</th>
                      <th className="pb-3 pr-4">Difficulty</th>
                      <th className="pb-3 pr-4">Language</th>
                      <th className="pb-3 pr-4">Topics</th>
                      <th className="pb-3 pr-4">Commit SHA</th>
                      <th className="pb-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/[0.04]">
                    {submissions.map((sub) => (
                      <tr key={sub.id} className="hover:bg-white/[0.01] transition-all">
                        <td className="py-4 pr-4 font-mono text-xs text-gray-500">{sub.problem_id}</td>
                        <td className="py-4 pr-4 font-bold text-[#F5F5F7]">{sub.problem_title}</td>
                        <td className="py-4 pr-4">
                          <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${getDifficultyColor(sub.difficulty)}`}>
                            {sub.difficulty}
                          </span>
                        </td>
                        <td className="py-4 pr-4 font-mono text-xs text-gray-400">{sub.language}</td>
                        <td className="py-4 pr-4 text-xs text-gray-400 max-w-xs truncate">{sub.topic_tags}</td>
                        <td className="py-4 pr-4 font-mono text-xs text-gray-400">
                          {sub.github_commit_sha ? sub.github_commit_sha.substring(0, 7) : 'N/A'}
                        </td>
                        <td className="py-4 text-right">
                          <a 
                            href={`https://github.com/${status?.github_repo}/blob/main/${sub.github_file_path}`} 
                            target="_blank" 
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 text-[#0071E3] hover:underline text-xs font-bold"
                          >
                            Source <ExternalLink className="w-3 h-3" />
                          </a>
                        </td>
                      </tr>
                    ))}
                    {submissions.length === 0 && (
                      <tr>
                        <td colSpan={7} className="py-8 text-center text-gray-500 text-sm">
                          No synced submissions found.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="bg-white/[0.02] border border-white/[0.06] p-6 rounded-3xl flex flex-col gap-4 shadow-lg shadow-black/15">
              <div className="border-b border-white/[0.04] pb-4">
                <h2 className="text-lg font-bold">System Sync Logs</h2>
                <p className="text-xs text-gray-400">Audit logs tracking automation executions and credentials verification history.</p>
              </div>
              
              <div className="flex flex-col gap-3.5 mt-4">
                {logs.map((log) => (
                  <div key={log.id} className={`p-4 rounded-2xl border transition-all ${log.level === 'ERROR' ? 'bg-rose-500/5 border-rose-500/20 text-rose-200' : 'bg-white/[0.01] border-white/[0.04] text-[#F5F5F7]'}`}>
                    <div className="flex items-start gap-3">
                      {log.level === 'ERROR' ? (
                        <AlertCircle className="w-4.5 h-4.5 text-rose-400 shrink-0 mt-0.5" />
                      ) : (
                        <CheckCircle className="w-4.5 h-4.5 text-emerald-400 shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between text-[10px] text-gray-400 font-mono">
                          <span>{new Date(log.timestamp).toLocaleString()}</span>
                          <span className={`px-1.5 py-0.5 rounded font-bold ${log.level === 'ERROR' ? 'bg-rose-500/10 text-rose-400' : 'bg-emerald-500/10 text-emerald-400'}`}>{log.level}</span>
                        </div>
                        <p className="text-sm font-semibold mt-2 font-mono break-all">{log.message}</p>
                        
                        {log.recovery_suggestion && (
                          <div className="mt-3.5 p-3.5 bg-rose-500/10 rounded-xl text-xs border border-rose-500/15">
                            <span className="font-bold text-rose-400 block mb-1">Recovery Recommendation:</span>
                            {log.recovery_suggestion}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {logs.length === 0 && (
                  <div className="py-8 text-center text-gray-500 text-sm">
                    No logs found.
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="bg-white/[0.02] border border-white/[0.06] p-6 rounded-3xl flex flex-col gap-4 shadow-lg shadow-black/15">
              <div className="border-b border-white/[0.04] pb-4">
                <h2 className="text-lg font-bold">Engine Configuration Settings</h2>
                <p className="text-xs text-gray-400">Configure LeetSync Pro scheduler intervals and target folders.</p>
              </div>
              
              <form onSubmit={saveSettings} className="flex flex-col gap-6 mt-6 max-w-xl">
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-white">GitHub Target Repository</label>
                  <input
                    type="text"
                    value={githubRepo}
                    onChange={(e) => setGithubRepo(e.target.value)}
                    placeholder="e.g. owner/repo"
                    required
                    className="px-4 py-3 bg-[#060608]/40 border border-white/[0.08] rounded-xl text-sm font-mono focus:border-[#0071E3] focus:outline-none text-white focus:ring-1 focus:ring-[#0071E3]/20"
                  />
                  <span className="text-[10px] text-gray-400">Format: owner/repository without spaces.</span>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-white">Sync Interval (Minutes)</label>
                  <input
                    type="number"
                    value={syncInterval}
                    onChange={(e) => setSyncInterval(Number(e.target.value))}
                    min={1}
                    required
                    className="px-4 py-3 bg-[#060608]/40 border border-white/[0.08] rounded-xl text-sm focus:border-[#0071E3] focus:outline-none text-white focus:ring-1 focus:ring-[#0071E3]/20"
                  />
                  <span className="text-[10px] text-gray-400">Minutes to wait between recurring background sync task calls.</span>
                </div>

                <button
                  type="submit"
                  disabled={savingSettings}
                  className="w-fit px-6 py-3 bg-gradient-to-r from-[#0071E3] to-[#0077ED] text-white font-semibold text-sm rounded-xl hover:brightness-110 active:scale-95 transition-all disabled:opacity-50"
                >
                  {savingSettings ? 'Saving...' : 'Save Settings'}
                </button>
              </form>
            </div>
          )}

        </section>
      </main>

      {/* Premium Footer */}
      <footer className="mt-auto border-t border-white/[0.04] py-6 bg-[#060608]/40 text-center">
        <p className="text-xs text-gray-500 font-medium">
          &copy; 2026 LeetSync Pro. Engineered with premium clean architecture.
        </p>
      </footer>
    </div>
  );
}
