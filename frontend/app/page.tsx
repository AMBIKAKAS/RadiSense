"use client";

import { useState } from "react";
import Header from "@/components/Header";
import MapPanel from "@/components/MapPanel";
import ControlPanel from "@/components/ControlPanel";
// app/layout.tsx OR app/globals.css import



export type AOI = {
  type: "Polygon";
  coordinates: number[][][];
};

export type AnalysisResult = {
  risk_score: number;
  risk_level: string;
};

export default function Home() {
  const [aoi, setAoi] = useState<AOI | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  return (
    <div className="h-screen w-screen overflow-hidden">
      <Header />
      <div className="flex h-[calc(100%-64px)]">
        <MapPanel aoi={aoi} result={result} />
        <ControlPanel setAoi={setAoi} setResult={setResult} />
      </div>
    </div>
  );
}
