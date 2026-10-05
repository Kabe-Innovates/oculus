import { useEffect, useState } from 'react';
import { Shield } from 'lucide-react';
import { getTransactions, getStats } from '../api/client';
import { useTransactionStream } from '../hooks/useTransactionStream';
import LiveIndicator from '../components/LiveIndicator';
import StatsCards from '../components/StatsCards';
import FilterBar from '../components/FilterBar';
import TransactionTable from '../components/TransactionTable';

export default function Dashboard() {
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState({ verdict: 'ALL', status: 'ALL' });
  const { latestTransaction, isConnected } = useTransactionStream();

  const loadData = async () => {
    try {
      const [txs, s] = await Promise.all([
        getTransactions(),
        getStats()
      ]);
      setTransactions(txs);
      setStats(s);
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
