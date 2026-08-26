import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  GeoJSON,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";

type Hotspot = {
  id: number;
  district: string;
  disease: string;
  latitude: number;
  longitude: number;
  cases: number;
  risk: "High" | "Medium" | "Low";
};

const mockHotspots: Hotspot[] = [
  {
    id: 1,
    district: "Yavatmal",
    disease: "Pink Bollworm",
    latitude: 20.389,
    longitude: 78.13,
    cases: 12,
    risk: "High",
  },
  {
    id: 2,
    district: "Nanded",
    disease: "Soybean Rust",
    latitude: 19.15,
    longitude: 77.32,
    cases: 8,
    risk: "Medium",
  },
  {
    id: 3,
    district: "Nashik",
    disease: "Purple Blotch",
    latitude: 20.005,
    longitude: 73.78,
    cases: 10,
    risk: "High",
  },
  {
    id: 4,
    district: "Pune",
    disease: "Leaf Curl",
    latitude: 18.52,
    longitude: 73.86,
    cases: 4,
    risk: "Low",
  },
  {
    id: 5,
    district: "Kolhapur",
    disease: "Leaf Spot",
    latitude: 16.705,
    longitude: 74.24,
    cases: 6,
    risk: "Medium",
  },
];

function getRiskColor(risk: Hotspot["risk"]) {
  if (risk === "High") return "#dc2626";
  if (risk === "Medium") return "#f59e0b";
  return "#16a34a";
}

function getDistrictRisk(district: string) {
  const hotspot = mockHotspots.find(
    (item) => item.district.toLowerCase() === district.toLowerCase()
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
  } else if (risk === "Low") {
    fillColor = "#22c55e";
  }

  return {
    color: "#475569",
    weight: 2,
    opacity: 1,
    fillColor,
    fillOpacity: 0.5,
  };
}

function StateHotspotMap() {
  const [districtData, setDistrictData] = useState<any>(null);

  useEffect(() => {
    fetch("/maharashtra_districts.geojson")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load Maharashtra district data.");
        }

        return response.json();
      })
      .then((data) => {
        setDistrictData(data);
      })
      .catch((error) => {
        console.error("GeoJSON loading error:", error);
      });
  }, []);

  const totalCases = mockHotspots.reduce(
    (total, item) => total + item.cases,
    0
  );

  const highRiskCount = mockHotspots.filter(
    (item) => item.risk === "High"
  ).length;

  const mediumRiskCount = mockHotspots.filter(
    (item) => item.risk === "Medium"
  ).length;

  const lowRiskCount = mockHotspots.filter(
    (item) => item.risk === "Low"
  ).length;

  return (
    <div className="map-page">
      <div className="map-header">
        <div>
          <h2>State Outbreak Intelligence</h2>

          <p>
            Monitor district-level crop disease hotspots across Maharashtra.
          </p>
        </div>

        <div className="map-summary">
          <div>
            <span>Total Hotspots</span>
            <strong>{mockHotspots.length}</strong>
          </div>

          <div>
            <span>Total Cases</span>
            <strong>{totalCases}</strong>
          </div>
        </div>
      </div>

      <div className="map-card">
        <MapContainer
          center={[19.7515, 75.7139]}
          zoom={6}
          scrollWheelZoom={true}
          className="maharashtra-map"
        >
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {districtData && (
            <GeoJSON
              data={districtData}
              style={getDistrictStyle}
              onEachFeature={(feature, layer) => {
                const districtName =
                  feature?.properties?.district ?? "Unknown District";

                const risk = getDistrictRisk(districtName);

                const hotspot = mockHotspots.find(
                  (item) =>
                    item.district.toLowerCase() ===
                    districtName.toLowerCase()
                );

                const cases = hotspot?.cases ?? 0;

                layer.bindPopup(`
                  <strong>${districtName}</strong>
                  <br />
                  Risk: ${risk}
                  <br />
                  Reported Cases: ${cases}
                `);
              }}
            />
          )}

          {mockHotspots.map((hotspot) => (
            <CircleMarker
              key={hotspot.id}
              center={[hotspot.latitude, hotspot.longitude]}
              radius={10}
              pathOptions={{
                color: getRiskColor(hotspot.risk),
                fillColor: getRiskColor(hotspot.risk),
                fillOpacity: 0.8,
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
          High Risk ({highRiskCount})
        </div>

        <div>
          <span className="legend-dot medium-dot"></span>
          Medium Risk ({mediumRiskCount})
        </div>

        <div>
          <span className="legend-dot low-dot"></span>
          Low Risk ({lowRiskCount})
        </div>
      </div>
    </div>
  );
}

export default StateHotspotMap;