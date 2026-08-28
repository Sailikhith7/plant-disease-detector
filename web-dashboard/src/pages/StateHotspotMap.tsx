import { useEffect, useMemo, useState } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  GeoJSON,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";

import type { MockCase } from "../data/mockCases";

type StateHotspotMapProps = {
  cases: MockCase[];
};

type Hotspot = {
  district: string;
  disease: string;
  latitude: number;
  longitude: number;
  cases: number;
  risk: "High" | "Medium" | "Low";
};

// District coordinate fallbacks across Maharashtra
const DISTRICT_COORDINATES: Record<string, [number, number]> = {
  yavatmal: [20.3888, 78.1204],
  nagpur: [21.1458, 79.0882],
  amravati: [20.9374, 77.7796],
  akola: [20.7002, 77.0082],
  aurangabad: [19.8762, 75.3433],
  chhatrapati_sambhajinagar: [19.8762, 75.3433],
  nashik: [19.9975, 73.7898],
  pune: [18.5204, 73.8567],
  solapur: [17.6599, 75.9064],
  kolhapur: [16.7050, 74.2433],
  satara: [17.6805, 74.0183],
  sangli: [16.8524, 74.5815],
  nanded: [19.1383, 77.3210],
  jalna: [19.8410, 75.8864],
  beed: [18.9891, 75.7601],
  latur: [18.4088, 76.5604],
  osmanabad: [18.1853, 76.0419],
  dharashiv: [18.1853, 76.0419],
  buldhana: [20.5292, 76.1843],
  wardha: [20.7453, 78.6022],
  chandrapur: [19.9615, 79.2961],
  gadchiroli: [20.1849, 79.9948],
  bhandara: [21.1667, 79.6500],
  gondia: [21.4600, 80.2000],
  dhule: [20.9042, 74.7749],
  jalgaon: [21.0077, 75.5626],
  nandurbar: [21.3700, 74.2400],
  ahmednagar: [19.0948, 74.7480],
  ahilyanagar: [19.0948, 74.7480],
  raigad: [18.5158, 73.1812],
  ratnagiri: [16.9902, 73.3120],
  sindhudurg: [16.1180, 73.6980],
  thane: [19.2183, 72.9781],
  palghar: [19.6967, 72.7653],
  mumbai: [19.0760, 72.8777],
};

function getRiskRank(risk?: string) {
  if (risk === "High") return 3;
  if (risk === "Medium") return 2;
  return 1;
}

function getRiskColor(risk?: string) {
  if (risk === "High") return "#dc2626";
  if (risk === "Medium") return "#f59e0b";
  return "#16a34a";
}

function StateHotspotMap({ cases }: StateHotspotMapProps) {
  const [districtData, setDistrictData] = useState<any>(null);

  useEffect(() => {
    fetch("/maharashtra_districts.geojson")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load district GeoJSON");
        }
        return response.json();
      })
      .then((data) => setDistrictData(data))
      .catch((error) => console.error("GeoJSON error:", error));
  }, []);

  const hotspots = useMemo<Hotspot[]>(() => {
    const grouped: Record<string, MockCase[]> = {};

    cases.forEach((item) => {
      const districtKey = (item.district || "Yavatmal").trim();
      if (!grouped[districtKey]) {
        grouped[districtKey] = [];
      }
      grouped[districtKey].push(item);
    });

    return Object.entries(grouped)
      .map(([districtName, districtCases]) => {
        const firstCase: any = districtCases[0];

        const highestRisk = districtCases.reduce((highest, current) => {
          return getRiskRank(current.severity) > getRiskRank(highest.severity)
            ? current
            : highest;
        }, firstCase);

        const diseases = [
          ...new Set(districtCases.map((item) => item.disease || "Unknown Disease")),
        ];

        // Safely extract coordinates with district lookup fallback
        const normalizedDistrict = districtName.toLowerCase().replace(/[\s_-]+/g, "");
        const fallbackCoords =
          DISTRICT_COORDINATES[normalizedDistrict] || [20.3888, 78.1204];

        const lat = Number(
          firstCase.gps_lat ??
          firstCase.lat ??
          firstCase.latitude ??
          fallbackCoords[0]
        );

        const lng = Number(
          firstCase.gps_long ??
          firstCase.lng ??
          firstCase.longitude ??
          fallbackCoords[1]
        );

        return {
          district: districtName,
          disease: diseases.join(", "),
          latitude: isNaN(lat) ? fallbackCoords[0] : lat,
          longitude: isNaN(lng) ? fallbackCoords[1] : lng,
          cases: districtCases.length,
          risk: (highestRisk?.severity as "High" | "Medium" | "Low") || "Medium",
        };
      })
      .filter((h) => !isNaN(h.latitude) && !isNaN(h.longitude));
  }, [cases]);

  function getDistrictRisk(districtName: string) {
    const hotspot = hotspots.find(
      (item) => item.district.toLowerCase() === districtName.toLowerCase()
    );
    return hotspot?.risk ?? "Low";
  }

  function getDistrictStyle(feature?: any) {
    const districtName = feature?.properties?.district ?? "";
    const risk = getDistrictRisk(districtName);

    let fillColor = "#e2e8f0";
    if (risk === "High") {
      fillColor = "#ef4444";
    } else if (risk === "Medium") {
      fillColor = "#f59e0b";
    } else {
      fillColor = "#22c55e";
    }

    return {
      color: "#475569",
      weight: 2,
      opacity: 1,
      fillColor,
      fillOpacity: 0.35,
    };
  }

  const pendingCases = cases.filter(
    (item) => item.status === "Pending Expert"
  ).length;

  const highRiskCases = cases.filter((item) => item.severity === "High").length;
  const mediumRiskCases = cases.filter((item) => item.severity === "Medium").length;
  const lowRiskCases = cases.filter((item) => item.severity === "Low").length;

  return (
    <div className="map-page">
      <div className="map-header">
        <div>
          <h2>State Outbreak Intelligence</h2>
          <p>Monitor district-level crop disease hotspots across Maharashtra.</p>
        </div>

        <div className="map-summary">
          <div>
            <span>Total Cases</span>
            <strong>{cases.length}</strong>
          </div>
          <div>
            <span>Pending Cases</span>
            <strong>{pendingCases}</strong>
          </div>
          <div>
            <span>District Hotspots</span>
            <strong>{hotspots.length}</strong>
          </div>
        </div>
      </div>

      <div className="map-card">
        <MapContainer
          center={[19.7515, 75.7139]}
          zoom={7}
          scrollWheelZoom={true}
          className="maharashtra-map"
          style={{ height: "550px", width: "100%", borderRadius: "8px" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {districtData && (
            <GeoJSON
              data={districtData}
              style={getDistrictStyle}
              onEachFeature={(feature, layer) => {
                const districtName =
                  feature?.properties?.district ?? "Unknown District";
                const hotspot = hotspots.find(
                  (item) =>
                    item.district.toLowerCase() === districtName.toLowerCase()
                );

                layer.bindPopup(`
                  <strong>${districtName}</strong><br />
                  Risk: ${hotspot?.risk ?? "Low"}<br />
                  Reported Cases: ${hotspot?.cases ?? 0}
                `);

                layer.bindTooltip(districtName, { sticky: true });
              }}
            />
          )}

          {hotspots.map((hotspot) => (
            <CircleMarker
              key={hotspot.district}
              center={[hotspot.latitude, hotspot.longitude]}
              radius={12}
              pathOptions={{
                color: getRiskColor(hotspot.risk),
                fillColor: getRiskColor(hotspot.risk),
                fillOpacity: 0.9,
              }}
            >
              <Popup>
                <strong>{hotspot.district}</strong>
                <br />
                Disease: {hotspot.disease}
                <br />
                Cases: {hotspot.cases}
                <br />
                Risk: {hotspot.risk}
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <div className="risk-legend">
        <div>
          <span className="legend-dot high-dot"></span>
          High Risk ({highRiskCases})
        </div>
        <div>
          <span className="legend-dot medium-dot"></span>
          Medium Risk ({mediumRiskCases})
        </div>
        <div>
          <span className="legend-dot low-dot"></span>
          Low Risk ({lowRiskCases})
        </div>
      </div>
    </div>
  );
}

export default StateHotspotMap;