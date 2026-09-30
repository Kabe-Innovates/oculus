export default function VerdictBadge({ verdict }) {
  const styles = {
    ALLOW: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    REVIEW: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    BLOCK: "bg-red-500/10 text-red-400 border-red-500/20",
  };
  const style = styles[verdict] || "bg-neutral-500/10 text-neutral-400 border-neutral-500/20";
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${style}`}>
      {verdict}
    </span>
  );
}
