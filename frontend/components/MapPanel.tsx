"use client";

import { useEffect, useRef } from "react";
import Map from "ol/Map";
import View from "ol/View";
import TileLayer from "ol/layer/Tile";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import XYZ from "ol/source/XYZ";
import Feature from "ol/Feature";
import Polygon from "ol/geom/Polygon";
import Circle from "ol/geom/Circle";
import Overlay from "ol/Overlay";
import { fromLonLat } from "ol/proj";
import { Style, Stroke, Fill } from "ol/style";
import { AOI, AnalysisResult } from "@/app/page";

export default function MapPanel({
  aoi,
  result,
}: {
  aoi: AOI | null;
  result: AnalysisResult | null;
}) {
  const mapRef = useRef<Map | null>(null);
  const vectorSource = useRef(new VectorSource());
  const popupRef = useRef<HTMLDivElement>(null);

  // 🔥 INIT MAP (DARK THEME)
  useEffect(() => {
    mapRef.current = new Map({
      target: "map",
      layers: [
        new TileLayer({
          source: new XYZ({
            url: "https://{a-c}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
          }),
        }),
        new VectorLayer({
          source: vectorSource.current,
        }),
      ],
      view: new View({
        center: fromLonLat([78.9, 22.5]),
        zoom: 5,
      }),
    });

    if (popupRef.current) {
      mapRef.current.addOverlay(
        new Overlay({
          element: popupRef.current,
          positioning: "bottom-center",
          offset: [0, -15],
        })
      );
    }
  }, []);

  // 🔥 DRAW AOI + RISK CIRCLE (AFTER RESULT)
  useEffect(() => {
    if (!aoi || !result || !mapRef.current) return;

    vectorSource.current.clear();

    const coords = aoi.coordinates[0];
    const transformed = coords.map(([lon, lat]) =>
      fromLonLat([lon, lat])
    );

    const center = transformed[0];
    const polygon = new Polygon([transformed]);

    let strokeColor = "#22c55e"; // green
    let fillColor = "rgba(34,197,94,0.25)";
    let radius = 3000;

    if (result.risk_level === "MODERATE") {
      strokeColor = "#facc15"; // yellow
      fillColor = "rgba(250,204,21,0.25)";
      radius = 6000;
    }

    if (result.risk_level === "HIGH") {
      strokeColor = "#ef4444"; // red
      fillColor = "rgba(239,68,68,0.25)";
      radius = 10000;
    }

    // AOI POLYGON
    vectorSource.current.addFeature(
      new Feature({
        geometry: polygon,
        style: new Style({
          stroke: new Stroke({
            color: strokeColor,
            width: 2.5,
          }),
          fill: new Fill({
            color: fillColor,
          }),
        }),
      })
    );

    // RISK BUFFER
    vectorSource.current.addFeature(
      new Feature({
        geometry: new Circle(center, radius),
        style: new Style({
          stroke: new Stroke({
            color: strokeColor,
            width: 2,
          }),
          fill: new Fill({
            color: fillColor,
          }),
        }),
      })
    );

    mapRef.current.getView().fit(polygon, {
      padding: [80, 80, 80, 80],
      duration: 600,
    });
  }, [aoi, result]);

  return (
    <>
      <div id="map" className="h-full w-full bg-black" />

      {/* DARK POPUP */}
      {result && (
        <div
          ref={popupRef}
          className="absolute bg-[#0b1220] text-white p-3 rounded-lg shadow-xl border border-white/10"
        >
          <div className="text-xs text-gray-400 mb-1">RADIATION RISK</div>
          <div
            className={`font-semibold ${
              result.risk_level === "HIGH"
                ? "text-red-400"
                : result.risk_level === "MODERATE"
                ? "text-yellow-400"
                : "text-green-400"
            }`}
          >
            {result.risk_level}
          </div>
          <div className="text-sm text-gray-300 mt-1">
            Score: {result.risk_score}
          </div>
        </div>
      )}
    </>
  );
}
