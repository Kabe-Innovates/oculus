import { Activity, AlertTriangle, ShieldX, Gauge } from 'lucide-react';

export default function StatsCards({ stats }) {
  if (!stats) return null;
  return (
    <div className="grid grid-cols-4 gap-4">
      <Card icon={<Activity className="text-blue-400" size={20} />} label="Total Transactions" value={stats.total_transactions} />
      <Card icon={<AlertTriangle className="text-amber-400" size={20} />} label="Flagged" value={stats.flagged_count} />
      <Card icon={<ShieldX className="text-red-400" size={20} />} label="Blocked" value={stats.blocked_count} />
      <Card icon={<Gauge className="text-emerald-400" size={20} />} label="Avg Risk Score" value={stats.avg_risk_score.toFixed(1)} />
    </div>
  );
}

function Card({ icon, label, value }) {
  return (
    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:bg-white/8 transition-all duration-200">
      <div className="flex items-center gap-3 mb-4">
        {icon}
        <h3 className="text-sm text-neutral-400">{label}</h3>
      </div>
      <p className="text-3xl font-semibold tracking-tight">{value}</p>
    </div>
  );
}
