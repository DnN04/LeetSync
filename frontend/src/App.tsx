import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Settings as SettingsIcon, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle, 
  Terminal, 
  FolderCheck,
  Check,
  ExternalLink
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
    if (d === 'easy') return 'text-green-400 bg-green-500/10 border-green-500/20';
    if (d === 'medium') return 'text-orange-400 bg-orange-500/10 border-orange-500/20';
    return 'text-red-400 bg-red-500/10 border-red-500/20';
  };

  return (
    <div className="min-h-screen bg-darkBg text-textWhite flex flex-col font-sans antialiased">
      {/* Premium Header */}
      <header className="border-b border-borderDark/60 bg-darkBg/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-accentBlue to-indigo-600 flex items-center justify-center shadow-lg shadow-accentBlue/20">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">LeetSync Pro</h1>
              <p className="text-xs text-textGray">Accepted submissions automation engine</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={triggerSync}
              disabled={syncing}
              className="flex items-center gap-2 px-4 py-2 bg-accentBlue text-white rounded-xl text-sm font-medium hover:bg-opacity-90 active:scale-95 transition-all disabled:opacity-50 shadow-md shadow-accentBlue/10"
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
        <aside className="w-full md:w-64 flex flex-col gap-2 shrink-0">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === 'overview' ? 'bg-cardBg text-textWhite border border-borderDark/40' : 'text-textGray hover:text-textWhite'}`}
          >
            <Activity className="w-4 h-4" />
            Overview
          </button>
          <button
            onClick={() => setActiveTab('submissions')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === 'submissions' ? 'bg-cardBg text-textWhite border border-borderDark/40' : 'text-textGray hover:text-textWhite'}`}
          >
            <FolderCheck className="w-4 h-4" />
            Synced Solutions
          </button>
          <button
            onClick={() => setActiveTab('logs')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === 'logs' ? 'bg-cardBg text-textWhite border border-borderDark/40' : 'text-textGray hover:text-textWhite'}`}
          >
            <Terminal className="w-4 h-4" />
            Sync Logs
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === 'settings' ? 'bg-cardBg text-textWhite border border-borderDark/40' : 'text-textGray hover:text-textWhite'}`}
          >
            <SettingsIcon className="w-4 h-4" />
            Settings
          </button>

          {/* Quick Connection Status Info */}
          <div className="mt-8 p-4 bg-cardBg/30 rounded-2xl border border-borderDark/30 flex flex-col gap-3">
            <h3 className="text-xs font-semibold text-textGray uppercase tracking-wider">Connected Accounts</h3>
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-1.5 text-textGray">
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg> GitHub
              </span>
              {status?.github_connected ? (
                <span className="flex items-center gap-1 text-green-400 font-medium"><Check className="w-3 h-3"/> Active</span>
              ) : (
                <span className="flex items-center gap-1 text-red-400 font-medium"><AlertCircle className="w-3 h-3"/> Disconnected</span>
              )}
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-1.5 text-textGray">
                💡 LeetCode
              </span>
              {status?.leetcode_connected ? (
                <span className="flex items-center gap-1 text-green-400 font-medium"><Check className="w-3 h-3"/> Active</span>
              ) : (
                <span className="flex items-center gap-1 text-red-400 font-medium"><AlertCircle className="w-3 h-3"/> Expired</span>
              )}
            </div>
          </div>
        </aside>

        {/* Dynamic Panel Pane */}
        <section className="flex-1 min-w-0">
          
          {message && (
            <div className="mb-6 p-4 bg-accentBlue/10 border border-accentBlue/20 rounded-2xl flex items-center justify-between text-sm text-blue-300">
              <span>{message}</span>
              <button onClick={() => setMessage(null)} className="hover:text-white">✕</button>
            </div>
          )}

          {activeTab === 'overview' && (
            <div className="flex flex-col gap-8">
              
              {/* Metrics Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-cardBg border border-borderDark/40 p-6 rounded-3xl flex flex-col gap-2">
                  <span className="text-textGray text-xs font-medium">Total Synchronized</span>
                  <div className="flex items-baseline justify-between mt-1">
                    <span className="text-3xl font-bold tracking-tight">{stats?.total_solved || 0}</span>
                    <span className="text-xs text-green-400 font-semibold bg-green-500/10 px-2 py-0.5 rounded-full">100% Accurate</span>
                  </div>
                </div>

                <div className="bg-cardBg border border-borderDark/40 p-6 rounded-3xl flex flex-col gap-2">
                  <span className="text-textGray text-xs font-medium">Easy Solved</span>
                  <div className="flex items-baseline justify-between mt-1">
                    <span className="text-3xl font-bold tracking-tight text-green-400">{stats?.difficulty_breakdown.Easy || 0}</span>
                  </div>
                </div>

                <div className="bg-cardBg border border-borderDark/40 p-6 rounded-3xl flex flex-col gap-2">
                  <span className="text-textGray text-xs font-medium">Medium Solved</span>
                  <div className="flex items-baseline justify-between mt-1">
                    <span className="text-3xl font-bold tracking-tight text-orange-400">{stats?.difficulty_breakdown.Medium || 0}</span>
                  </div>
                </div>

                <div className="bg-cardBg border border-borderDark/40 p-6 rounded-3xl flex flex-col gap-2">
                  <span className="text-textGray text-xs font-medium">Hard Solved</span>
                  <div className="flex items-baseline justify-between mt-1">
                    <span className="text-3xl font-bold tracking-tight text-red-400">{stats?.difficulty_breakdown.Hard || 0}</span>
                  </div>
                </div>
              </div>

              {/* Status and Active Scheduler Cards */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Synchronization Job details */}
                <div className="bg-cardBg border border-borderDark/40 p-6 rounded-3xl flex flex-col gap-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-sm">Scheduler Automation</h3>
                    <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${status?.scheduler.status === 'RUNNING' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                      {status?.scheduler.status}
                    </span>
                  </div>

                  <div className="flex flex-col gap-2 text-sm text-textGray">
                    <div className="flex justify-between border-b border-borderDark/40 py-2">
                      <span>Sync Interval</span>
                      <span className="text-textWhite font-medium">{status?.scheduler.sync_interval_minutes} minutes</span>
                    </div>
                    <div className="flex justify-between border-b border-borderDark/40 py-2">
                      <span>Target Repository</span>
                      <span className="text-textWhite font-mono">{status?.github_repo || 'Not Configured'}</span>
                    </div>
                    <div className="flex justify-between py-2">
                      <span>Next Run Time</span>
                      <span className="text-textWhite font-mono">{status?.scheduler.active_jobs[0]?.next_run_time || 'N/A'}</span>
                    </div>
                  </div>
                </div>

                {/* Latest Execution Details */}
                <div className="bg-cardBg border border-borderDark/40 p-6 rounded-3xl flex flex-col gap-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-sm">Latest Sync Action</h3>
                    {status?.last_sync_job ? (
                      <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${status.last_sync_job.status === 'COMPLETED' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                        {status.last_sync_job.status}
                      </span>
                    ) : (
                      <span className="text-xs text-textGray font-medium bg-borderDark/40 px-2 py-0.5 rounded-full">No Jobs run</span>
                    )}
                  </div>

                  {status?.last_sync_job ? (
                    <div className="flex flex-col gap-2 text-sm text-textGray">
                      <div className="flex justify-between border-b border-borderDark/40 py-2">
                        <span>Job ID</span>
                        <span className="text-textWhite font-mono">#{status.last_sync_job.id}</span>
                      </div>
                      <div className="flex justify-between border-b border-borderDark/40 py-2">
                        <span>Start Time</span>
                        <span className="text-textWhite font-mono">{new Date(status.last_sync_job.start_time).toLocaleString()}</span>
                      </div>
                      {status.last_sync_job.error_message && (
                        <div className="flex flex-col gap-1 py-1">
                          <span className="text-red-400 font-medium">Error Details:</span>
                          <p className="text-xs text-red-300 font-mono bg-red-500/5 p-2 rounded-xl border border-red-500/10 max-h-24 overflow-y-auto">
                            {status.last_sync_job.error_message}
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="flex-1 flex items-center justify-center text-textGray text-sm">
                      Waiting for first scheduled execution.
                    </div>
                  )}
                </div>
              </div>

              {/* Solved List Preview */}
              <div className="bg-cardBg border border-borderDark/40 p-6 rounded-3xl flex flex-col gap-4">
                <h3 className="font-semibold text-sm">Recent Solved Submissions</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm border-collapse text-left">
                    <thead>
                      <tr className="border-b border-borderDark text-textGray text-xs uppercase font-semibold">
                        <th className="pb-3 pr-4">ID</th>
                        <th className="pb-3 pr-4">Title</th>
                        <th className="pb-3 pr-4">Difficulty</th>
                        <th className="pb-3 pr-4">Language</th>
                        <th className="pb-3 pr-4">Solved Date</th>
                        <th className="pb-3">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-borderDark/40">
                      {submissions.slice(0, 5).map((sub) => (
                        <tr key={sub.id} className="hover:bg-borderDark/10">
                          <td className="py-4 pr-4 font-mono text-xs">{sub.problem_id}</td>
                          <td className="py-4 pr-4 font-medium text-textWhite">{sub.problem_title}</td>
                          <td className="py-4 pr-4">
                            <span className={`text-xs px-2 py-0.5 rounded-full border ${getDifficultyColor(sub.difficulty)}`}>
                              {sub.difficulty}
                            </span>
                          </td>
                          <td className="py-4 pr-4 font-mono text-xs text-textGray">{sub.language}</td>
                          <td className="py-4 pr-4 text-xs text-textGray">{new Date(sub.solved_at).toLocaleDateString()}</td>
                          <td className="py-4 text-accentBlue hover:underline text-xs font-semibold">
                            <a 
                              href={`https://github.com/${status?.github_repo}/blob/main/${sub.github_file_path}`} 
                              target="_blank" 
                              rel="noreferrer"
                              className="flex items-center gap-1"
                            >
                              View Code <ExternalLink className="w-3 h-3" />
                            </a>
                          </td>
                        </tr>
                      ))}
                      {submissions.length === 0 && (
                        <tr>
                          <td colSpan={6} className="py-8 text-center text-textGray text-sm">
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
            <div className="bg-cardBg border border-borderDark/40 p-6 rounded-3xl flex flex-col gap-4">
              <h2 className="text-lg font-bold">Synchronized Solutions</h2>
              <p className="text-xs text-textGray">All problems pushed successfully into GitHub portfolio repository.</p>
              <div className="overflow-x-auto mt-4">
                <table className="w-full text-sm border-collapse text-left">
                  <thead>
                    <tr className="border-b border-borderDark text-textGray text-xs uppercase font-semibold">
                      <th className="pb-3 pr-4">ID</th>
                      <th className="pb-3 pr-4">Title</th>
                      <th className="pb-3 pr-4">Difficulty</th>
                      <th className="pb-3 pr-4">Language</th>
                      <th className="pb-3 pr-4">Topics</th>
                      <th className="pb-3 pr-4">Commit SHA</th>
                      <th className="pb-3">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-borderDark/40">
                    {submissions.map((sub) => (
                      <tr key={sub.id} className="hover:bg-borderDark/10">
                        <td className="py-4 pr-4 font-mono text-xs">{sub.problem_id}</td>
                        <td className="py-4 pr-4 font-semibold text-textWhite">{sub.problem_title}</td>
                        <td className="py-4 pr-4">
                          <span className={`text-xs px-2 py-0.5 rounded-full border ${getDifficultyColor(sub.difficulty)}`}>
                            {sub.difficulty}
                          </span>
                        </td>
                        <td className="py-4 pr-4 font-mono text-xs text-textGray">{sub.language}</td>
                        <td className="py-4 pr-4 text-xs text-textGray max-w-xs truncate">{sub.topic_tags}</td>
                        <td className="py-4 pr-4 font-mono text-xs text-textGray">
                          {sub.github_commit_sha ? sub.github_commit_sha.substring(0, 7) : 'N/A'}
                        </td>
                        <td className="py-4 text-accentBlue hover:underline text-xs font-semibold">
                          <a 
                            href={`https://github.com/${status?.github_repo}/blob/main/${sub.github_file_path}`} 
                            target="_blank" 
                            rel="noreferrer"
                            className="flex items-center gap-1"
                          >
                            Source <ExternalLink className="w-3 h-3" />
                          </a>
                        </td>
                      </tr>
                    ))}
                    {submissions.length === 0 && (
                      <tr>
                        <td colSpan={7} className="py-8 text-center text-textGray text-sm">
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
            <div className="bg-cardBg border border-borderDark/40 p-6 rounded-3xl flex flex-col gap-4">
              <h2 className="text-lg font-bold">System Sync Logs</h2>
              <p className="text-xs text-textGray">Audit logs representing background runs and error reports.</p>
              
              <div className="flex flex-col gap-3 mt-4">
                {logs.map((log) => (
                  <div key={log.id} className={`p-4 rounded-2xl border ${log.level === 'ERROR' ? 'bg-red-500/5 border-red-500/20 text-red-300' : 'bg-borderDark/10 border-borderDark/40 text-textWhite'}`}>
                    <div className="flex items-center gap-3">
                      {log.level === 'ERROR' ? (
                        <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
                      ) : (
                        <CheckCircle className="w-4 h-4 text-green-400 shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <span className="text-xs font-mono text-textGray block">
                          {new Date(log.timestamp).toLocaleString()} | {log.level}
                        </span>
                        <p className="text-sm font-medium mt-1 font-mono">{log.message}</p>
                        
                        {log.recovery_suggestion && (
                          <div className="mt-3 p-3 bg-red-500/10 rounded-xl text-xs border border-red-500/15">
                            <span className="font-bold text-red-400 block mb-0.5">Recovery Suggestion:</span>
                            {log.recovery_suggestion}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {logs.length === 0 && (
                  <div className="py-8 text-center text-textGray text-sm">
                    No logs found.
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="bg-cardBg border border-borderDark/40 p-6 rounded-3xl flex flex-col gap-4">
              <h2 className="text-lg font-bold">Engine Configuration Settings</h2>
              <p className="text-xs text-textGray">Configure LeetSync Pro scheduling and target repository.</p>
              
              <form onSubmit={saveSettings} className="flex flex-col gap-6 mt-6 max-w-xl">
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-textWhite">GitHub Target Repository</label>
                  <input
                    type="text"
                    value={githubRepo}
                    onChange={(e) => setGithubRepo(e.target.value)}
                    placeholder="e.g. owner/repo"
                    required
                    className="px-4 py-3 bg-darkBg border border-borderDark/60 rounded-xl text-sm font-mono focus:border-accentBlue focus:outline-none text-textWhite"
                  />
                  <span className="text-xs text-textGray">Format must be owner/repo without spaces.</span>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-sm font-medium text-textWhite">Sync Interval (Minutes)</label>
                  <input
                    type="number"
                    value={syncInterval}
                    onChange={(e) => setSyncInterval(Number(e.target.value))}
                    min={1}
                    required
                    className="px-4 py-3 bg-darkBg border border-borderDark/60 rounded-xl text-sm focus:border-accentBlue focus:outline-none text-textWhite"
                  />
                  <span className="text-xs text-textGray">Interval for scheduled background sync runs.</span>
                </div>

                <button
                  type="submit"
                  disabled={savingSettings}
                  className="w-fit px-6 py-3 bg-accentBlue text-white font-medium text-sm rounded-xl hover:bg-opacity-90 active:scale-95 transition-all disabled:opacity-50"
                >
                  {savingSettings ? 'Saving...' : 'Save Settings'}
                </button>
              </form>
            </div>
          )}

        </section>
      </main>

      {/* Dark Premium Footer */}
      <footer className="mt-auto border-t border-borderDark/40 py-6 bg-darkBg/60 text-center">
        <p className="text-xs text-textGray">
          &copy; 2026 LeetSync Pro. Built with premium clean engineering.
        </p>
      </footer>
    </div>
  );
}
