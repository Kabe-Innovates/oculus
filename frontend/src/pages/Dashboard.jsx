import { useEffect, useState } from 'react';
import { Shield, Play, Square } from 'lucide-react';
import { getTransactions, getStats, getSimulatorStatus, startSimulator, stopSimulator } from '../api/client';
import { useTransactionStream } from '../hooks/useTransactionStream';
import LiveIndicator from '../components/LiveIndicator';
import StatsCards from '../components/StatsCards';
import FilterBar from '../components/FilterBar';
import TransactionTable from '../components/TransactionTable';

export default function Dashboard() {
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState({ verdict: 'ALL', status: 'ALL' });
  const [simRunning, setSimRunning] = useState(false);
  const { latestTransaction, isConnected } = useTransactionStream();

  const loadData = async () => {
    try {
      const [txs, s, sim] = await Promise.all([
        getTransactions(),
        getStats(),
        getSimulatorStatus()
      ]);
      setTransactions(txs);
      setStats(s);
      setSimRunning(sim.running);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (latestTransaction) {
      setTransactions((prev) => {
        if (prev.find((tx) => tx.id === latestTransaction.id)) return prev;
        return [latestTransaction, ...prev].slice(0, 100);
      });
    }
  }, [latestTransaction]);

  const toggleSimulator = async () => {
    try {
      if (simRunning) await stopSimulator();
      else await startSimulator();
      setSimRunning(!simRunning);
    } catch (e) {
      console.error(e);
    }
  };

  const filteredTransactions = transactions.filter((tx) => {
    if (filter.verdict !== 'ALL' && tx.verdict !== filter.verdict) return false;
    if (filter.status !== 'ALL' && tx.status !== filter.status) return false;
    return true;
  });

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 bg-[#0a0a0a]/80 backdrop-blur-md border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="text-white" size={24} />
          <h1 className="text-xl font-semibold tracking-tight text-white">SentinelPay</h1>
          <span className="text-neutral-500">Fraud Detection</span>
        </div>
        <div className="flex items-center gap-6">
          <LiveIndicator isConnected={isConnected} />
          <button
            onClick={toggleSimulator}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              simRunning
                ? 'bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20'
                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20'
            }`}
          >
            {simRunning ? <Square size={16} /> : <Play size={16} />}
            {simRunning ? 'Stop Simulator' : 'Start Simulator'}
          </button>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-6 py-8">
        <StatsCards stats={stats} />
        <div className="mt-8">
          <FilterBar filter={filter} setFilter={setFilter} />
        </div>
        <TransactionTable transactions={filteredTransactions} />
      </main>
    </div>
  );
}
