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

import {
  getOutbreaks,
  sendBroadcastAdvisory,
} from "../api/caseApi";

type StateHotspotMapProps = {
  cases: MockCase[];
};

type Hotspot = {
  district: string;
  disease: string;
  crop: string;
  latitude: number;
  longitude: number;
  cases: number;
  risk: "High" | "Medium" | "Low";
};

type Outbreak = {
  district: string;
  crop: string;
  disease: string;
  case_count: number;
};

const OUTBREAK_THRESHOLD = 5;

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
  if (risk === "High") {
    return "#dc2626";
  }

  if (risk === "Medium") {
    return "#f59e0b";
  }

  return "#16a34a";
}

function StateHotspotMap({
  cases,
}: StateHotspotMapProps) {
  const [districtData, setDistrictData] =
    useState<any>(null);

  const [outbreaks, setOutbreaks] =
    useState<Outbreak[]>([]);

  const [selectedOutbreak, setSelectedOutbreak] =
    useState<Outbreak | null>(null);

  const [officerMsg, setOfficerMsg] =
    useState("");

  const [isModalOpen, setIsModalOpen] =
    useState(false);

  const [isBroadcasting, setIsBroadcasting] =
    useState(false);

  const [banner, setBanner] =
    useState<string | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  // =====================================================
  // LOAD MAHARASHTRA DISTRICT GEOJSON
  // =====================================================

  useEffect(() => {
    fetch("/maharashtra_districts.geojson")
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            "Failed to load district GeoJSON."
          );
        }

        return response.json();
      })
      .then((data) => {
        setDistrictData(data);
      })
      .catch((err) => {
        console.error(
          "GeoJSON error:",
          err
        );
      });
  }, []);

  // =====================================================
  // LOAD REAL ACTIVE OUTBREAKS FROM BACKEND
  // =====================================================

  useEffect(() => {
    async function loadOutbreaks() {
      try {
        setError(null);

        const data =
          await getOutbreaks(
            OUTBREAK_THRESHOLD
          );

        const normalized =
          Array.isArray(data)
            ? data
            : data?.outbreaks ?? [];

        setOutbreaks(normalized);
      } catch (err) {
        console.error(
          "Failed to load outbreaks:",
          err
        );

        setError(
          "Unable to load outbreak data from backend."
        );
      }
    }

    loadOutbreaks();
  }, [cases]);

  // =====================================================
  // EXISTING MAP HOTSPOTS
  // =====================================================

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

        const crops = [
          ...new Set(
            districtCases.map(
              (item) => item.crop
            )
          ),
        ];

        return {
          district:
            firstCase.district,

          disease:
            diseases.join(", "),

          crop:
            crops.join(", "),

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

  // =====================================================
  // DISTRICT COLORS
  // =====================================================

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

    return {
      color: "#475569",
      weight: 2,
      opacity: 1,
      fillColor:
        getRiskColor(risk),
      fillOpacity: 0.35,
    };
  }

  // =====================================================
  // OPEN BROADCAST MODAL
  // =====================================================

  function openBroadcast(
    outbreak: Outbreak
  ) {
    setSelectedOutbreak(
      outbreak
    );

    setOfficerMsg(
      `तात्काळ सूचना: ${outbreak.district} जिल्ह्यात ${outbreak.crop} पिकामध्ये ${outbreak.disease} संदर्भात प्रादुर्भाव आढळला आहे.`
    );

    setBanner(null);
    setError(null);
    setIsModalOpen(true);
  }

  // =====================================================
  // SEND BROADCAST THROUGH BACKEND
  // =====================================================

  async function handleBroadcast() {
    if (!selectedOutbreak) {
      return;
    }

    if (!officerMsg.trim()) {
      setError(
        "Please enter an advisory message."
      );
      return;
    }

    setIsBroadcasting(true);
    setBanner(null);
    setError(null);

    try {
      const result =
        await sendBroadcastAdvisory({
          district:
            selectedOutbreak.district,

          crop:
            selectedOutbreak.crop,

          disease:
            selectedOutbreak.disease,

          custom_message:
            officerMsg.trim(),
        });

      setIsModalOpen(false);

      setBanner(
        `✅ Advisory successfully broadcasted to ${
          result?.total_farmers_notified ?? 0
        } farmers.`
      );

      setSelectedOutbreak(null);
    } catch (err) {
      console.error(
        "Broadcast failed:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Broadcast delivery failed."
      );
    } finally {
      setIsBroadcasting(false);
    }
  }

  // =====================================================
  // SUMMARY
  // =====================================================

  const totalCases =
    cases.length;

  const pendingCases =
    cases.filter(
      (item) =>
        item.status ===
        "Pending Expert"
    ).length;

  const highRiskCases =
    cases.filter(
      (item) =>
        item.severity === "High"
    ).length;

  const mediumRiskCases =
    cases.filter(
      (item) =>
        item.severity === "Medium"
    ).length;

  const lowRiskCases =
    cases.filter(
      (item) =>
        item.severity === "Low"
    ).length;

  return (
    <div className="map-page">

      {/* HEADER */}

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
              {totalCases}
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

      {/* SUCCESS / ERROR BANNER */}

      {banner && (
        <div
          style={{
            background: "#dcfce7",
            color: "#166534",
            padding: "12px 16px",
            borderRadius: "10px",
            marginBottom: "18px",
            fontWeight: 600,
          }}
        >
          {banner}
        </div>
      )}

      {error && (
        <div
          style={{
            background: "#fee2e2",
            color: "#b91c1c",
            padding: "12px 16px",
            borderRadius: "10px",
            marginBottom: "18px",
            fontWeight: 600,
          }}
        >
          ❌ {error}
        </div>
      )}

      {/* =================================================
          MAP FIRST
      ================================================= */}

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

          {/* DISTRICT BORDERS */}

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

          {/* HOTSPOT MARKERS */}

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

                  Crop:
                  {` ${hotspot.crop}`}

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

      {/* =================================================
          OUTBREAK TABLE BELOW MAP
      ================================================= */}

      <div className="outbreak-table-card">

        <div className="outbreak-table-header">

          <div>
            <h3>
              🚨 Critical Outbreak Zones
              Requiring Advisory Broadcast
            </h3>

            <p>
              Automatically detected when
              complaints reach{" "}
              {OUTBREAK_THRESHOLD}.
            </p>
          </div>

        </div>

        {outbreaks.length > 0 ? (

          <div className="outbreak-table-wrapper">

            <table>

              <thead>
                <tr>
                  <th>District</th>
                  <th>Target Crop</th>
                  <th>Detected Outbreak</th>
                  <th>Reported Complaints</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>

                {outbreaks.map(
                  (item, index) => (

                    <tr
                      key={`${item.district}-${item.crop}-${index}`}
                    >

                      <td>
                        <strong>
                          {item.district}
                        </strong>
                      </td>

                      <td>
                        {item.crop}
                      </td>

                      <td>
                        <span className="severity high">
                          {item.disease}
                        </span>
                      </td>

                      <td>
                        <span className="outbreak-count">
                          {item.case_count}
                          {" complaints"}
                        </span>
                      </td>

                      <td>

                        <button
                          className="broadcast-button"
                          onClick={() =>
                            openBroadcast(
                              item
                            )
                          }
                        >
                          📢 Broadcast Advisory
                        </button>

                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

        ) : (

          <div className="outbreak-empty">
            No critical outbreaks detected.
          </div>

        )}

      </div>

      {/* =================================================
          RISK LEGEND
      ================================================= */}

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

      {/* =================================================
          BROADCAST MODAL
      ================================================= */}

      {isModalOpen &&
        selectedOutbreak && (

          <div
            className="modal-overlay"
            onClick={() => {
              if (!isBroadcasting) {
                setIsModalOpen(false);
              }
            }}
          >

            <div
              className="broadcast-modal"
              onClick={(event) =>
                event.stopPropagation()
              }
            >

              <div className="modal-header">

                <div>
                  <h3>
                    Broadcast Advisory
                  </h3>

                  <p>
                    Send a custom advisory
                    to affected farmers.
                  </p>
                </div>

                <button
                  className="modal-close"
                  onClick={() =>
                    !isBroadcasting &&
                    setIsModalOpen(false)
                  }
                  disabled={
                    isBroadcasting
                  }
                >
                  ×
                </button>

              </div>

              {/* AUTO FILLED */}

              <div className="broadcast-details">

                <div>
                  <span>
                    District
                  </span>

                  <strong>
                    {
                      selectedOutbreak.district
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Crop
                  </span>

                  <strong>
                    {
                      selectedOutbreak.crop
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Disease
                  </span>

                  <strong>
                    {
                      selectedOutbreak.disease
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Complaints
                  </span>

                  <strong>
                    {
                      selectedOutbreak.case_count
                    }
                  </strong>
                </div>

              </div>

              <label className="broadcast-label">
                Custom Advisory Message
              </label>

              <textarea
                className="broadcast-textarea"
                rows={5}
                value={officerMsg}
                onChange={(event) =>
                  setOfficerMsg(
                    event.target.value
                  )
                }
                placeholder="Enter Marathi or English advisory..."
                disabled={
                  isBroadcasting
                }
              />

              <div className="modal-actions">

                <button
                  className="cancel-button"
                  onClick={() =>
                    setIsModalOpen(false)
                  }
                  disabled={
                    isBroadcasting
                  }
                >
                  Cancel
                </button>

                <button
                  className="send-broadcast-button"
                  onClick={
                    handleBroadcast
                  }
                  disabled={
                    isBroadcasting
                  }
                >
                  {isBroadcasting
                    ? "Sending..."
                    : "📢 Dispatch Advisory"}
                </button>

              </div>

            </div>

          </div>

        )}

    </div>
  );
}

export default StateHotspotMap;