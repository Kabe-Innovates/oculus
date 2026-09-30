export default function RiskGauge({ score, verdict }) {
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  
  let colorClass = "stroke-emerald-400";
  if (score >= 40 && score < 75) colorClass = "stroke-amber-400";
  if (score >= 75) colorClass = "stroke-red-400";

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-6 flex flex-col items-center justify-center h-full">
      <div className="relative w-40 h-40 flex items-center justify-center">
        <svg className="transform -rotate-90 w-full h-full" viewBox="0 0 160 160">
          <circle
            className="stroke-white/10"
            strokeWidth="12"
            fill="transparent"
            r={radius}
            cx="80"
            cy="80"
          />
          <circle
            className={`transition-all duration-1000 ease-out ${colorClass}`}
            strokeWidth="12"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            r={radius}
            cx="80"
            cy="80"
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className="text-4xl font-semibold">{Math.round(score)}</span>
          <span className="text-xs text-neutral-400 uppercase tracking-widest mt-1">{verdict}</span>
        </div>
      </div>
    </div>
  );
}
