import { useNavigate } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import VerdictBadge from './VerdictBadge';
import StatusBadge from './StatusBadge';

export default function TransactionTable({ transactions }) {
  const navigate = useNavigate();

  return (
    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden mt-4">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/5 text-xs font-medium text-neutral-400 uppercase tracking-wider">
              <th className="px-6 py-4 border-b border-white/5">ID</th>
              <th className="px-6 py-4 border-b border-white/5">Amount</th>
              <th className="px-6 py-4 border-b border-white/5">Sender</th>
              <th className="px-6 py-4 border-b border-white/5">Risk Score</th>
              <th className="px-6 py-4 border-b border-white/5">Verdict</th>
              <th className="px-6 py-4 border-b border-white/5">Status</th>
              <th className="px-6 py-4 border-b border-white/5">Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 max-h-[600px] overflow-y-auto">
            {transactions.map((tx) => (
              <tr 
                key={tx.id} 
                onClick={() => navigate(`/transaction/${tx.id}`)}
                className="hover:bg-white/5 transition-colors cursor-pointer group"
              >
                <td className="px-6 py-4 font-mono text-sm text-neutral-300">
                  {tx.id.split('-')[0]}...
                </td>
                <td className="px-6 py-4 text-sm font-medium">
                  ${tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </td>
                <td className="px-6 py-4 text-sm text-neutral-400">
                  {tx.sender_id}
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-col gap-1 w-24">
                    <span className="text-xs font-medium text-neutral-300">{tx.risk_score}</span>
                    <div className="w-full h-0.5 bg-white/10 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${tx.risk_score >= 75 ? "bg-red-400" : tx.risk_score >= 40 ? "bg-amber-400" : "bg-emerald-400"}`}
                        style={{ width: `${Math.min(tx.risk_score, 100)}%` }}
                      />
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <VerdictBadge verdict={tx.verdict} />
                </td>
                <td className="px-6 py-4">
                  <StatusBadge status={tx.status} />
                </td>
                <td className="px-6 py-4 text-sm text-neutral-500 whitespace-nowrap">
                  {formatDistanceToNow(new Date(tx.timestamp), { addSuffix: true })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
