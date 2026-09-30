export default function RuleBreakdown({ rules }) {
  if (!rules || rules.length === 0) return null;
  
  const formatName = (name) => name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-6 mt-6">
      <h3 className="text-sm font-medium text-white mb-6 uppercase tracking-wider">Rule Breakdown</h3>
      <div className="space-y-6">
        {rules.map((rule, idx) => (
          <div key={idx} className="space-y-2">
            <div className="flex justify-between items-center text-sm">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${rule.triggered ? "bg-red-500" : "bg-emerald-500"}`} />
                <span className="font-medium text-neutral-200">{formatName(rule.rule_name)}</span>
              </div>
              <span className="text-neutral-400">{rule.score} / 100</span>
            </div>
            <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${rule.score >= 75 ? "bg-red-400" : rule.score >= 40 ? "bg-amber-400" : "bg-emerald-400"}`}
                style={{ width: `${rule.score}%` }}
              />
            </div>
            <p className="text-xs text-neutral-500">{rule.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
