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

function getRiskRank(
  risk: "High" | "Medium" | "Low"
) {
  if (risk === "High") return 3;
  if (risk === "Medium") return 2;
  return 1;
}

function getRiskColor(
  risk: "High" | "Medium" | "Low"
) {
  if (risk === "High") return "#dc2626";
  if (risk === "Medium") return "#f59e0b";
  return "#16a34a";
}

function StateHotspotMap({
  cases,
}: StateHotspotMapProps) {

  const [districtData, setDistrictData] =
    useState<any>(null);

  useEffect(() => {
    fetch("/maharashtra_districts.geojson")
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            "Failed to load district GeoJSON"
          );
        }

        return response.json();
      })
      .then((data) => {
        setDistrictData(data);
      })
      .catch((error) => {
        console.error(
          "GeoJSON error:",
          error
        );
      });
  }, []);

  const hotspots = useMemo<Hotspot[]>(() => {

    const grouped: Record<
      string,
      MockCase[]
    > = {};

    cases.forEach((item) => {
      if (!grouped[item.district]) {
        grouped[item.district] = [];
      }

      grouped[item.district].push(item);
    });

    return Object.values(grouped).map(
      (districtCases) => {

        const firstCase =
          districtCases[0];

        const highestRisk =
          districtCases.reduce(
            (highest, current) =>
              getRiskRank(
                current.severity
              ) >
              getRiskRank(
                highest.severity
              )
                ? current
                : highest,
            firstCase
          );

        const diseases = [
          ...new Set(
            districtCases.map(
              (item) => item.disease
            )
          ),
        ];

        return {
          district: firstCase.district,

          disease:
            diseases.join(", "),

          latitude:
            firstCase.latitude,

          longitude:
            firstCase.longitude,

          cases:
            districtCases.length,

          risk:
            highestRisk.severity,
        };
      }
    );
  }, [cases]);

  function getDistrictRisk(
    districtName: string
  ) {
    const hotspot =
      hotspots.find(
        (item) =>
          item.district.toLowerCase() ===
          districtName.toLowerCase()
      );

    return hotspot?.risk ?? "Low";
  }

  function getDistrictStyle(
    feature?: any
  ) {

    const districtName =
      feature?.properties?.district ??
      "";

    const risk =
      getDistrictRisk(
        districtName
      );

    let fillColor =
      "#e2e8f0";

    if (risk === "High") {
      fillColor =
        "#ef4444";
    } else if (risk === "Medium") {
      fillColor =
        "#f59e0b";
    } else {
      fillColor =
        "#22c55e";
    }

    return {
      color: "#475569",
      weight: 2,
      opacity: 1,
      fillColor,
      fillOpacity: 0.35,
    };
  }

  const pendingCases =
    cases.filter(
      (item) =>
        item.status ===
        "Pending Expert"
    ).length;

  const highRiskCases =
    cases.filter(
      (item) =>
        item.severity ===
        "High"
    ).length;

  const mediumRiskCases =
    cases.filter(
      (item) =>
        item.severity ===
        "Medium"
    ).length;

  const lowRiskCases =
    cases.filter(
      (item) =>
        item.severity ===
        "Low"
    ).length;

  return (
    <div className="map-page">

      <div className="map-header">

        <div>
          <h2>
            State Outbreak Intelligence
          </h2>

          <p>
            Monitor district-level crop
            disease hotspots across
            Maharashtra.
          </p>
        </div>

        <div className="map-summary">

          <div>
            <span>Total Cases</span>
            <strong>
              {cases.length}
            </strong>
          </div>

          <div>
            <span>Pending Cases</span>
            <strong>
              {pendingCases}
            </strong>
          </div>

          <div>
            <span>District Hotspots</span>
            <strong>
              {hotspots.length}
            </strong>
          </div>

        </div>
      </div>

      <div className="map-card">

        <MapContainer
          center={[
            19.7515,
            75.7139,
          ]}
          zoom={7}
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
              onEachFeature={(
                feature,
                layer
              ) => {

                const districtName =
                  feature?.properties
                    ?.district ??
                  "Unknown District";

                const hotspot =
                  hotspots.find(
                    (item) =>
                      item.district
                        .toLowerCase() ===
                      districtName
                        .toLowerCase()
                  );

                layer.bindPopup(`
                  <strong>
                    ${districtName}
                  </strong>
                  <br />
                  Risk:
                  ${hotspot?.risk ?? "Low"}
                  <br />
                  Reported Cases:
                  ${hotspot?.cases ?? 0}
                `);

                layer.bindTooltip(
                  districtName,
                  {
                    sticky: true,
                  }
                );
              }}
            />
          )}

          {hotspots.map(
            (hotspot) => (
              <CircleMarker
                key={
                  hotspot.district
                }
                center={[
                  hotspot.latitude,
                  hotspot.longitude,
                ]}
                radius={10}
                pathOptions={{
                  color:
                    getRiskColor(
                      hotspot.risk
                    ),

                  fillColor:
                    getRiskColor(
                      hotspot.risk
                    ),

                  fillOpacity: 0.9,
                }}
              >

                <Popup>

                  <strong>
                    {hotspot.district}
                  </strong>

                  <br />

                  Disease:
                  {` ${hotspot.disease}`}

                  <br />

                  Cases:
                  {` ${hotspot.cases}`}

                  <br />

                  Risk:
                  {` ${hotspot.risk}`}

                </Popup>

              </CircleMarker>
            )
          )}

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