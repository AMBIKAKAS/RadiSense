"use client";

import { useState } from "react";
import { runAnalysis } from "../lib/api";
import { AOI, AnalysisResult } from "@/app/page";

export default function ControlPanel({
  setAoi,
  setResult,
}: {
  setAoi: (aoi: AOI) => void;
  setResult: (r: AnalysisResult) => void;
}) {
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [startDate, setStartDate] = useState("2023-01-01");
  const [endDate, setEndDate] = useState("2024-01-01");
  const [loading, setLoading] = useState(false);
  const [localResult, setLocalResult] = useState<AnalysisResult | null>(null);

  function generateAOI(lat: number, lon: number): AOI {
    const d = 0.03;
    return {
      type: "Polygon",
      coordinates: [[
        [lon - d, lat - d],
        [lon + d, lat - d],
        [lon + d, lat + d],
        [lon - d, lat + d],
        [lon - d, lat - d],
      ]],
    };
  }

  async function handleRun() {
    if (!lat || !lon || loading) return;

    const polygon = generateAOI(+lat, +lon);
    setAoi(polygon);

    setLoading(true);
    setLocalResult(null);

    try {
      const res = await runAnalysis({
        aoi: polygon,
        start_date: startDate,
        end_date: endDate,
      });

      const finalResult = {
        risk_score: res.risk_score,
        risk_level: res.risk_level,
      };

      setResult(finalResult);
      setLocalResult(finalResult);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-96 bg-linear-to-b from-[#0a1226] to-[#050b18] border-l border-white/10 p-6 flex flex-col justify-between">

      <div>
        <h2 className="text-lg font-semibold mb-2">Analysis Controls</h2>
        <p className="text-sm text-gray-400 mb-6">
          Configure radiation signal detection parameters
        </p>

        {/* DATE */}
        <div className="mb-6">
          <label className="text-sm text-gray-400">ANALYSIS PERIOD</label>
          <div className="grid grid-cols-2 gap-2 mt-2">
            <input type="date" value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="bg-white/5 border border-white/10 p-2 rounded text-sm" />
            <input type="date" value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="bg-white/5 border border-white/10 p-2 rounded text-sm" />
          </div>
        </div>

        {/* COORDS */}
        <div className="mb-6">
          <label className="text-sm text-gray-400">COORDINATES</label>
          <div className="space-y-2 mt-2">
            <input placeholder="Latitude"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              className="w-full bg-white/5 border border-white/10 p-2 rounded" />
            <input placeholder="Longitude"
              value={lon}
              onChange={(e) => setLon(e.target.value)}
              className="w-full bg-white/5 border border-white/10 p-2 rounded" />
          </div>
        </div>

        {/* BUTTON */}
        <button
          disabled={loading}
          onClick={handleRun}
          className={`w-full py-3 rounded font-semibold transition ${
            loading
              ? "bg-gray-500 cursor-not-allowed"
              : "bg-teal-600 hover:bg-teal-500 text-black"
          }`}
        >
          {loading ? "Analyzing…" : "▶ Run Analysis"}
        </button>

        {/* RESULT */}
        <div className="mt-8 p-6 rounded bg-white/5 border border-white/10 text-center">
          {loading ? (
            <div className="text-gray-400 animate-pulse">
              Processing satellite signals…
            </div>
          ) : !localResult ? (
            <>
              <div className="text-2xl mb-2">∿</div>
              <div className="text-gray-400 text-sm">
                No analysis yet
              </div>
            </>
          ) : (
            <>
              <div className="text-sm text-gray-400 mb-2">RESULT</div>
              <div
                className={`text-2xl font-bold ${
                  localResult.risk_level === "HIGH"
                    ? "text-red-400"
                    : localResult.risk_level === "MODERATE"
                    ? "text-yellow-400"
                    : "text-green-400"
                }`}
              >
                {localResult.risk_level} RISK
              </div>
              <div className="text-sm text-gray-400 mt-2">
                Score: <span className="text-white">{localResult.risk_score}</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
