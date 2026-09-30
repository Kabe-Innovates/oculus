export default function FilterBar({ filter, setFilter }) {
  const verdicts = ["All", "Allow", "Review", "Block"];
  return (
    <div className="flex justify-between items-center bg-white/5 border border-white/10 rounded-xl p-2">
      <div className="flex gap-2">
        {verdicts.map((v) => (
          <button
            key={v}
            onClick={() => setFilter({ ...filter, verdict: v.toUpperCase() })}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${filter.verdict === v.toUpperCase() ? "bg-white/10 text-white" : "text-neutral-500 hover:text-neutral-300"}`}
          >
            {v}
          </button>
        ))}
      </div>
      <div>
        <select
          value={filter.status}
          onChange={(e) => setFilter({ ...filter, status: e.target.value })}
          className="bg-transparent border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white outline-none focus:border-white/20"
        >
          <option value="ALL" className="bg-neutral-900">All Status</option>
          <option value="PENDING" className="bg-neutral-900">Pending</option>
          <option value="CLEARED" className="bg-neutral-900">Cleared</option>
          <option value="CONFIRMED_FRAUD" className="bg-neutral-900">Confirmed Fraud</option>
        </select>
      </div>
    </div>
  );
}
