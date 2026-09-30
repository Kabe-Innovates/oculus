import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, MapPin, Fingerprint, Monitor } from 'lucide-react';
import { getTransaction } from '../api/client';
import RiskGauge from '../components/RiskGauge';
import RuleBreakdown from '../components/RuleBreakdown';
import ReviewActions from '../components/ReviewActions';
import VerdictBadge from '../components/VerdictBadge';
import StatusBadge from '../components/StatusBadge';

export default function TransactionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [transaction, setTransaction] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const tx = await getTransaction(id);
      setTransaction(tx);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  if (loading) return <div className="p-8 text-neutral-400">Loading...</div>;
  if (!transaction) return <div className="p-8 text-red-400">Transaction not found</div>;

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 bg-[#0a0a0a]/80 backdrop-blur-md border-b border-white/10 px-6 py-4 flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="text-neutral-400 hover:text-white transition-colors">
          <ArrowLeft size={20} />
        </button>
        <h1 className="text-lg font-medium text-white flex items-center gap-2">
          Transaction <span className="font-mono text-neutral-400">{id}</span>
        </h1>
        <div className="ml-auto flex items-center gap-3">
          <VerdictBadge verdict={transaction.verdict} />
          <StatusBadge status={transaction.status} />
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-sm font-medium text-white mb-6 uppercase tracking-wider">Transaction Details</h3>
            <div className="grid grid-cols-2 gap-y-6 gap-x-8">
              <DetailItem label="Amount" value={`$${transaction.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} className="text-xl text-white" />
              <DetailItem label="Currency" value={transaction.currency} />
              <DetailItem label="Sender ID" value={transaction.sender_id} />
              <DetailItem label="Receiver ID" value={transaction.receiver_id} />
              <DetailItem icon={<MapPin size={14} />} label="Location" value={transaction.sender_location} />
              <DetailItem icon={<Monitor size={14} />} label="IP Address" value={transaction.ip_address} />
              <DetailItem icon={<Fingerprint size={14} />} label="Device" value={transaction.device_fingerprint} />
              <DetailItem icon={<Clock size={14} />} label="Timestamp" value={new Date(transaction.timestamp).toLocaleString()} />
            </div>
          </div>
          <RuleBreakdown rules={transaction.rule_results} />
        </div>
        <div className="col-span-1 flex flex-col h-full">
          <div className="flex-1">
            <RiskGauge score={transaction.risk_score} verdict={transaction.verdict} />
          </div>
          <ReviewActions transaction={transaction} onReviewed={loadData} />
        </div>
      </main>
    </div>
  );
}

function DetailItem({ icon, label, value, className = "text-sm text-neutral-300" }) {
  return (
    <div>
      <div className="flex items-center gap-1.5 text-xs text-neutral-500 uppercase tracking-wider mb-1">
        {icon}
        {label}
      </div>
      <div className={`font-mono ${className}`}>{value}</div>
    </div>
  );
}
