export default function StatusBadge({ status }) {
  const styles = {
    PENDING: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    CLEARED: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    CONFIRMED_FRAUD: "bg-red-500/10 text-red-400 border-red-500/20",
    REVIEWED: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  };
  const style = styles[status] || "bg-neutral-500/10 text-neutral-400 border-neutral-500/20";
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${style}`}>
      {status}
    </span>
  );
}
