export default function LiveIndicator({ isConnected }) {
  return (
    <div className="flex items-center gap-2 text-sm font-medium">
      <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500 animate-pulse" : "bg-red-500"}`} />
      <span className={isConnected ? "text-green-400" : "text-red-400"}>
        {isConnected ? "Live" : "Disconnected"}
      </span>
    </div>
  );
}
