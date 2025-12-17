export default function Header() {
  return (
    <div className="h-16 flex items-center justify-between px-6 bg-linear-to-b from-[#0a1226] to-[#050b18] border-b border-white/10">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded bg-teal-500 flex items-center justify-center font-bold">
          R
        </div>
        <div>
          <div className="font-semibold">RadiSense</div>
          <div className="text-xs text-gray-400">
            Satellite-based Radiation Signal Detection
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-sm text-gray-400">
          Sentinel-2 + Landsat-9
        </div>
        <div className="px-3 py-1 rounded-full bg-teal-500/10 text-teal-400 text-sm">
          ● Online
        </div>
      </div>
    </div>
  );
}
