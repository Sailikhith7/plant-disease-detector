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

// =====================================================
// DISTRICT COORDINATES
// =====================================================

const DISTRICT_COORDINATES: Record<
  string,
  [number, number]
> = {
  yavatmal: [20.3888, 78.1204],
  nagpur: [21.1458, 79.0882],
  amravati: [20.9374, 77.7796],
  akola: [20.7002, 77.0082],
  aurangabad: [19.8762, 75.3433],
  chhatrapatisambhajinagar: [19.8762, 75.3433],
  nashik: [19.9975, 73.7898],
  pune: [18.5204, 73.8567],
  solapur: [17.6599, 75.9064],
  kolhapur: [16.705, 74.2433],
  satara: [17.6805, 74.0183],
  sangli: [16.8524, 74.5815],
  nanded: [19.1383, 77.321],
  jalna: [19.841, 75.8864],
  beed: [18.9891, 75.7601],
  latur: [18.4088, 76.5604],
  osmanabad: [18.1853, 76.0419],
  dharashiv: [18.1853, 76.0419],
  buldhana: [20.5292, 76.1843],
  wardha: [20.7453, 78.6022],
  chandrapur: [19.9615, 79.2961],
  gadchiroli: [20.1849, 79.9948],
  bhandara: [21.1667, 79.65],
  gondia: [21.46, 80.2],
  dhule: [20.9042, 74.7749],
  jalgaon: [21.0077, 75.5626],
  nandurbar: [21.37, 74.24],
  ahmednagar: [19.0948, 74.748],
  ahilyanagar: [19.0948, 74.748],
  raigad: [18.5158, 73.1812],
  ratnagiri: [16.9902, 73.312],
  sindhudurg: [16.118, 73.698],
  thane: [19.2183, 72.9781],
  palghar: [19.6967, 72.7653],
  mumbai: [19.076, 72.8777],
};

// =====================================================
// MANUAL ADVISORY DISTRICTS
// =====================================================

const MANUAL_DISTRICTS = [
  "Yavatmal",
  "Nagpur",
  "Nashik",
  "Nanded",
  "Amravati",
  "Akola",
  "Pune",
  "Sangli",
  "Kolhapur",
  "Wardha",
  "Latur",
  "Jalgaon",
  "Dhule",
  "Solapur",
  "Satara",
];

// =====================================================
// MODEL CROPS + EXACT 27 MODEL CLASSES
// =====================================================

const MODEL_OPTIONS = {
  Cotton: [
    "cotton_bacterial_blight",
    "cotton_curl_virus",
    "cotton_fussarium_wilt",
    "cotton_healthy",
  ],

  Groundnut: [
    "groundnut_early_leaf_spot",
    "groundnut_early_rust",
    "groundnut_healthy_leaf",
    "groundnut_late_leaf_spot",
    "groundnut_late_rust",
    "groundnut_nutrition_deficiency",
  ],

  Ragi: [
    "ragi_downy",
    "ragi_healthy",
    "ragi_mottle",
    "ragi_seedling",
    "ragi_smut",
    "ragi_wilt",
  ],

  Rice: [
    "rice_bacterial_leaf_blight",
    "rice_brown_spot",
    "rice_healthy",
    "rice_leaf_blast",
    "rice_leaf_scald",
    "rice_sheath_blight",
  ],

  Sugarcane: [
    "sugarcane_healthy",
    "sugarcane_mosaic",
    "sugarcane_redrot",
    "sugarcane_rust",
    "sugarcane_yellow",
  ],
} as const;

type ModelCrop = keyof typeof MODEL_OPTIONS;

const MODEL_CROPS =
  Object.keys(
    MODEL_OPTIONS
  ) as ModelCrop[];

// =====================================================
// DISPLAY MODEL LABEL
// =====================================================

function formatModelLabel(
  label: string
) {
  return label
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() +
        word.slice(1)
    )
    .join(" ");
}

// =====================================================
// RISK COLOR
// =====================================================

function getRiskColor(
  risk?: string
) {
  if (risk === "High") {
    return "#dc2626";
  }

  if (risk === "Medium") {
    return "#f59e0b";
  }

  return "#16a34a";
}

// =====================================================
// COMPONENT
// =====================================================

function StateHotspotMap({
  cases,
}: StateHotspotMapProps) {

  // ===================================================
  // MAP STATE
  // ===================================================

  const [districtData, setDistrictData] =
    useState<any>(null);

  const [apiOutbreaks, setApiOutbreaks] =
    useState<Outbreak[]>([]);

  // ===================================================
  // EXISTING AUTOMATIC BROADCAST STATE
  // ===================================================

  const [
    selectedOutbreak,
    setSelectedOutbreak,
  ] = useState<Outbreak | null>(null);

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

  // ===================================================
  // MANUAL BROADCAST STATE
  // ===================================================

  const [
    manualDistricts,
    setManualDistricts,
  ] = useState<string[]>([]);

  const [manualCrop, setManualCrop] =
    useState<ModelCrop>("Cotton");

  const [manualDisease, setManualDisease] =
    useState(
      MODEL_OPTIONS.Cotton[0]
    );

  const [manualMessage, setManualMessage] =
    useState("");

  const [
    isManualBroadcasting,
    setIsManualBroadcasting,
  ] = useState(false);

  const [
    manualBanner,
    setManualBanner,
  ] = useState<string | null>(null);

  const [
    manualError,
    setManualError,
  ] = useState<string | null>(null);

  // ===================================================
  // CHANGE DISEASE OPTIONS WHEN CROP CHANGES
  // ===================================================

  useEffect(() => {
    setManualDisease(
      MODEL_OPTIONS[manualCrop][0]
    );
  }, [manualCrop]);

  // ===================================================
  // LOAD MAHARASHTRA DISTRICT GEOJSON
  // ===================================================

  useEffect(() => {
    fetch(
      "/maharashtra_districts.geojson"
    )
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
      .catch((err) => {
        console.error(
          "GeoJSON error:",
          err
        );
      });
  }, []);

  // ===================================================
  // LOAD OUTBREAKS FROM API
  // ===================================================

  useEffect(() => {
    async function loadOutbreaks() {
      try {
        setError(null);

        const data =
          await getOutbreaks(
            OUTBREAK_THRESHOLD
          );

        const outbreakList =
          Array.isArray(data)
            ? data
            : data?.outbreaks ?? [];

        setApiOutbreaks(
          outbreakList
        );
      } catch (err) {
        console.error(
          "Outbreak loading error:",
          err
        );
      }
    }

    loadOutbreaks();
  }, [cases]);

  // ===================================================
  // DERIVED OUTBREAKS
  // ===================================================

  const outbreaks =
    useMemo<Outbreak[]>(() => {

      if (
        apiOutbreaks.length > 0
      ) {
        return apiOutbreaks;
      }

      const grouped: Record<
        string,
        {
          district: string;
          crop: string;
          disease: string;
          count: number;
        }
      > = {};

      cases.forEach(
        (c: any) => {

          if (
            c.status &&
            c.status
              .toLowerCase()
              .includes("resolve")
          ) {
            return;
          }

          const district =
            c.district ||
            "Yavatmal";

          const crop =
            c.crop ||
            "Cotton";

          const disease =
            c.disease ||
            "Unknown Disease";

          const key =
            `${district}_${crop}_${disease}`;

          if (!grouped[key]) {
            grouped[key] = {
              district,
              crop,
              disease,
              count: 0,
            };
          }

          grouped[key].count += 1;
        }
      );

      return Object.values(
        grouped
      )
        .filter(
          (item) =>
            item.count >=
            OUTBREAK_THRESHOLD
        )
        .map(
          (item) => ({
            district:
              item.district,
            crop:
              item.crop,
            disease:
              item.disease,
            case_count:
              item.count,
          })
        );
    }, [
      apiOutbreaks,
      cases,
    ]);

  // ===================================================
  // CREATE DISTRICT HOTSPOTS
  // ===================================================

  const hotspots =
    useMemo<Hotspot[]>(() => {

      const grouped: Record<
        string,
        MockCase[]
      > = {};

      cases.forEach(
        (item) => {

          const districtKey =
            (
              item.district ||
              "Yavatmal"
            ).trim();

          if (
            !grouped[districtKey]
          ) {
            grouped[districtKey] =
              [];
          }

          grouped[districtKey].push(
            item
          );
        }
      );

      return Object.entries(
        grouped
      )
        .map(
          ([
            districtName,
            districtCases,
          ]) => {

            const firstCase: any =
              districtCases[0];

            const diseases = [
              ...new Set(
                districtCases.map(
                  (item) =>
                    item.disease ||
                    "Unknown Disease"
                )
              ),
            ];

            const crops = [
              ...new Set(
                districtCases.map(
                  (item) =>
                    item.crop ||
                    "Unknown Crop"
                )
              ),
            ];

            const count =
              districtCases.length;

            const computedRisk:
              | "High"
              | "Medium"
              | "Low" =
              count >=
              OUTBREAK_THRESHOLD
                ? "High"
                : districtCases.some(
                    (c) =>
                      c.severity ===
                      "High"
                  )
                ? "High"
                : districtCases.some(
                    (c) =>
                      c.severity ===
                      "Medium"
                  )
                ? "Medium"
                : "Low";

            const normalizedDistrict =
              districtName
                .toLowerCase()
                .replace(
                  /[\s_-]+/g,
                  ""
                );

            const fallbackCoords =
              DISTRICT_COORDINATES[
                normalizedDistrict
              ] || [
                20.3888,
                78.1204,
              ];

            const lat =
              Number(
                firstCase.gps_lat ??
                  firstCase.lat ??
                  firstCase.latitude ??
                  fallbackCoords[0]
              );

            const lng =
              Number(
                firstCase.gps_long ??
                  firstCase.lng ??
                  firstCase.longitude ??
                  fallbackCoords[1]
              );

            return {
              district:
                districtName,

              disease:
                diseases.join(", "),

              crop:
                crops.join(", "),

              latitude:
                Number.isNaN(lat)
                  ? fallbackCoords[0]
                  : lat,

              longitude:
                Number.isNaN(lng)
                  ? fallbackCoords[1]
                  : lng,

              cases:
                count,

              risk:
                computedRisk,
            };
          }
        )
        .filter(
          (item) =>
            !Number.isNaN(
              item.latitude
            ) &&
            !Number.isNaN(
              item.longitude
            )
        );
    }, [cases]);

  // ===================================================
  // DISTRICT RISK
  // ===================================================

  function getDistrictRisk(
    districtName: string
  ) {

    const hotspot =
      hotspots.find(
        (item) =>
          item.district
            .toLowerCase() ===
          districtName.toLowerCase()
      );

    return (
      hotspot?.risk ??
      "Low"
    );
  }

  // ===================================================
  // GEOJSON STYLE
  // ===================================================

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
      color:
        "#475569",
      weight: 2,
      opacity: 1,
      fillColor:
        getRiskColor(risk),
      fillOpacity: 0.35,
    };
  }

  // ===================================================
  // EXISTING AUTOMATIC BROADCAST
  // ===================================================

  function openBroadcast(
    outbreak: Outbreak
  ) {

    setSelectedOutbreak(
      outbreak
    );

    setOfficerMsg(
      `🚨 कृषी विभाग चेतावणी: ${outbreak.district} जिल्ह्यात ${outbreak.crop} पिकावर ${outbreak.disease} रोगाचा प्रादुर्भाव वाढला आहे. शेतकऱ्यांनी तातडीने प्रतिबंधात्मक उपाययोजना कराव्यात.`
    );

    setBanner(null);
    setError(null);

    setIsModalOpen(
      true
    );
  }

  async function handleBroadcast() {

    if (
      !selectedOutbreak
    ) {
      return;
    }

    if (
      !officerMsg.trim()
    ) {
      setError(
        "Please enter an advisory message."
      );

      return;
    }

    try {

      setIsBroadcasting(
        true
      );

      setError(null);
      setBanner(null);

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

      setBanner(
        `Advisory successfully broadcast to ${selectedOutbreak.district} farmers via Telegram!`
      );

      setIsModalOpen(
        false
      );

      setSelectedOutbreak(
        null
      );

      setOfficerMsg("");

    } catch (err) {

      console.error(
        "Broadcast error:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Failed to broadcast advisory."
      );

    } finally {

      setIsBroadcasting(
        false
      );

    }
  }

  // ===================================================
  // MANUAL DISTRICT TOGGLE
  // ===================================================

  function toggleManualDistrict(
    district: string
  ) {

    setManualDistricts(
      (previous) => {

        if (
          previous.includes(
            district
          )
        ) {

          return previous.filter(
            (item) =>
              item !== district
          );
        }

        return [
          ...previous,
          district,
        ];
      }
    );
  }

  // ===================================================
  // MANUAL BROADCAST
  // ===================================================

  async function handleManualBroadcast() {

    setManualError(null);
    setManualBanner(null);

    if (
      manualDistricts.length ===
      0
    ) {

      setManualError(
        "Please select at least one district."
      );

      return;
    }

    if (
      !manualMessage.trim()
    ) {

      setManualError(
        "Please enter an advisory message."
      );

      return;
    }

    try {

      setIsManualBroadcasting(
        true
      );

      let successfulDistricts =
        0;

      const failedDistricts:
        string[] = [];

      for (
        const district of
        manualDistricts
      ) {

        try {

          await sendBroadcastAdvisory({
            district:
              district,

            crop:
              manualCrop,

            disease:
              manualDisease,

            custom_message:
              manualMessage.trim(),
          });

          successfulDistricts +=
            1;

        } catch (err) {

          console.error(
            `Manual broadcast failed for ${district}:`,
            err
          );

          failedDistricts.push(
            district
          );
        }
      }

      if (
        failedDistricts.length ===
        0
      ) {

        setManualBanner(
          `Advisory successfully dispatched to ${successfulDistricts} selected district${successfulDistricts === 1 ? "" : "s"}.`
        );

      } else {

        setManualBanner(
          `Advisory sent to ${successfulDistricts} district${successfulDistricts === 1 ? "" : "s"}. Failed: ${failedDistricts.join(", ")}.`
        );

      }

      setManualDistricts([]);
      setManualMessage("");

    } catch (err) {

      console.error(
        "Manual broadcast error:",
        err
      );

      setManualError(
        err instanceof Error
          ? err.message
          : "Failed to dispatch manual advisory."
      );

    } finally {

      setIsManualBroadcasting(
        false
      );

    }
  }

  // ===================================================
  // SUMMARY COUNTS
  // ===================================================

  const pendingCases =
    cases.filter(
      (item) =>
        item.status ===
          "Pending Expert" ||
        item.status === "OPEN"
    ).length;

  const highRiskCount =
    hotspots.filter(
      (item) =>
        item.risk === "High"
    ).length;

  const mediumRiskCount =
    hotspots.filter(
      (item) =>
        item.risk === "Medium"
    ).length;

  const lowRiskCount =
    hotspots.filter(
      (item) =>
        item.risk === "Low"
    ).length;

  // ===================================================
  // RENDER
  // ===================================================

  return (
    <div className="map-page">

      {/* =================================================
          HEADER
      ================================================= */}

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
            <span>
              Total Cases
            </span>

            <strong>
              {cases.length}
            </strong>
          </div>

          <div>
            <span>
              Pending Cases
            </span>

            <strong>
              {pendingCases}
            </strong>
          </div>

          <div>
            <span>
              District Hotspots
            </span>

            <strong>
              {hotspots.length}
            </strong>
          </div>

        </div>

      </div>


      {/* =================================================
          AUTOMATIC BANNER
      ================================================= */}

      {banner && (

        <div
          style={{
            background:
              "#dcfce7",
            color:
              "#166534",
            padding:
              "12px 16px",
            borderRadius:
              "10px",
            marginBottom:
              "18px",
            fontWeight:
              600,
          }}
        >
          ✅ {banner}
        </div>

      )}


      {error && (

        <div
          style={{
            background:
              "#fee2e2",
            color:
              "#b91c1c",
            padding:
              "12px 16px",
            borderRadius:
              "10px",
            marginBottom:
              "18px",
            fontWeight:
              600,
          }}
        >
          ❌ {error}
        </div>

      )}


      {/* =================================================
          MAP
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
          style={{
            height:
              "550px",
            width:
              "100%",
            borderRadius:
              "8px",
          }}
        >

          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />


          {districtData && (

            <GeoJSON
              data={
                districtData
              }

              style={
                getDistrictStyle
              }

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
                  <strong>${districtName}</strong><br />
                  Risk: ${hotspot?.risk ?? "Low"}<br />
                  Reported Cases: ${hotspot?.cases ?? 0}
                `);

                layer.bindTooltip(
                  districtName,
                  {
                    sticky:
                      true,
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

                radius={14}

                pathOptions={{
                  color:
                    getRiskColor(
                      hotspot.risk
                    ),

                  fillColor:
                    getRiskColor(
                      hotspot.risk
                    ),

                  fillOpacity:
                    0.9,
                }}
              >

                <Popup>

                  <strong>
                    {
                      hotspot.district
                    }
                  </strong>

                  <br />

                  Crop:{" "}
                  {
                    hotspot.crop
                  }

                  <br />

                  Disease:{" "}
                  {
                    hotspot.disease
                  }

                  <br />

                  Cases:{" "}
                  {
                    hotspot.cases
                  }

                  <br />

                  Risk:{" "}
                  {
                    hotspot.risk
                  }

                </Popup>

              </CircleMarker>

            )
          )}

        </MapContainer>

      </div>


      {/* =================================================
          EXISTING AUTOMATIC OUTBREAK TABLE
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

                  <th>
                    District
                  </th>

                  <th>
                    Target Crop
                  </th>

                  <th>
                    Detected Outbreak
                  </th>

                  <th>
                    Reported Complaints
                  </th>

                  <th>
                    Action
                  </th>

                </tr>

              </thead>


              <tbody>

                {outbreaks.map(
                  (
                    item,
                    index
                  ) => (

                    <tr
                      key={`${item.district}-${item.crop}-${index}`}
                    >

                      <td>
                        <strong>
                          {
                            item.district
                          }
                        </strong>
                      </td>

                      <td>
                        {
                          item.crop
                        }
                      </td>

                      <td>

                        <span className="severity high">
                          {
                            item.disease
                          }
                        </span>

                      </td>

                      <td>

                        <span className="outbreak-count">
                          {
                            item.case_count
                          }{" "}
                          complaints
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
          MANUAL ADVISORY BROADCAST
      ================================================= */}

      <div
        className="outbreak-table-card"
        style={{
          marginTop:
            "24px",
        }}
      >

        <div className="outbreak-table-header">

          <div>

            <h3>
              📢 Manual Advisory Broadcast
            </h3>

            <p>
              Select one or more districts,
              choose a model crop and disease
              class, and send your own advisory.
            </p>

          </div>

        </div>


        {/* MANUAL SUCCESS */}

        {manualBanner && (

          <div
            style={{
              background:
                "#dcfce7",
              color:
                "#166534",
              padding:
                "12px 16px",
              margin:
                "0 24px 18px",
              borderRadius:
                "10px",
              fontWeight:
                600,
            }}
          >
            ✅ {manualBanner}
          </div>

        )}


        {/* MANUAL ERROR */}

        {manualError && (

          <div
            style={{
              background:
                "#fee2e2",
              color:
                "#b91c1c",
              padding:
                "12px 16px",
              margin:
                "0 24px 18px",
              borderRadius:
                "10px",
              fontWeight:
                600,
            }}
          >
            ❌ {manualError}
          </div>

        )}


        {/* =================================================
            DISTRICTS
        ================================================= */}

        <div
          style={{
            padding:
              "0 24px 22px",
          }}
        >

          <label
            style={{
              display:
                "block",
              fontWeight:
                700,
              marginBottom:
                "10px",
            }}
          >
            Select Districts
          </label>


          <div
            style={{
              display:
                "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(150px, 1fr))",
              gap:
                "8px",
              maxWidth:
                "1000px",
            }}
          >

            {MANUAL_DISTRICTS.map(
              (district) => {

                const selected =
                  manualDistricts.includes(
                    district
                  );

                return (

                  <label
                    key={
                      district
                    }

                    style={{
                      display:
                        "flex",
                      alignItems:
                        "center",
                      gap:
                        "8px",
                      padding:
                        "9px 10px",

                      border:
                        selected
                          ? "2px solid #166534"
                          : "1px solid #e2e8f0",

                      borderRadius:
                        "8px",

                      cursor:
                        "pointer",

                      background:
                        selected
                          ? "#f0fdf4"
                          : "#ffffff",
                    }}
                  >

                    <input
                      type="checkbox"
                      checked={
                        selected
                      }
                      onChange={() =>
                        toggleManualDistrict(
                          district
                        )
                      }
                    />

                    <span>
                      {
                        district
                      }
                    </span>

                  </label>

                );
              }
            )}

          </div>

        </div>


        {/* =================================================
            CROP + DISEASE
        ================================================= */}

        <div
          style={{
            display:
              "grid",
            gridTemplateColumns:
              "minmax(250px, 350px) minmax(300px, 420px)",
            gap:
              "16px",
            padding:
              "0 24px 22px",
          }}
        >

          {/* CROP */}

          <div>

            <label
              style={{
                display:
                  "block",
                fontWeight:
                  700,
                marginBottom:
                  "8px",
              }}
            >
              Crop
            </label>


            <select
              value={
                manualCrop
              }

              onChange={(event) =>
                setManualCrop(
                  event.target.value as ModelCrop
                )
              }

              style={{
                width:
                  "100%",
                padding:
                  "11px 12px",
                border:
                  "1px solid #cbd5e1",
                borderRadius:
                  "8px",
                background:
                  "#ffffff",
              }}
            >

              {MODEL_CROPS.map(
                (crop) => (

                  <option
                    key={
                      crop
                    }
                    value={
                      crop
                    }
                  >
                    {
                      crop
                    }
                  </option>

                )
              )}

            </select>

          </div>


          {/* DISEASE */}

          <div>

            <label
              style={{
                display:
                  "block",
                fontWeight:
                  700,
                marginBottom:
                  "8px",
              }}
            >
              Disease / Model Class
            </label>


            <select
              value={
                manualDisease
              }

              onChange={(event) =>
                setManualDisease(
                  event.target.value
                )
              }

              style={{
                width:
                  "100%",
                padding:
                  "11px 12px",
                border:
                  "1px solid #cbd5e1",
                borderRadius:
                  "8px",
                background:
                  "#ffffff",
              }}
            >

              {MODEL_OPTIONS[
                manualCrop
              ].map(
                (disease) => (

                  <option
                    key={
                      disease
                    }

                    value={
                      disease
                    }
                  >
                    {
                      formatModelLabel(
                        disease
                      )
                    }
                  </option>

                )
              )}

            </select>

          </div>

        </div>


        {/* =================================================
            ADVISORY MESSAGE
        ================================================= */}

        <div
          style={{
            padding:
              "0 24px 22px",
          }}
        >

          <label
            style={{
              display:
                "block",
              fontWeight:
                700,
              marginBottom:
                "8px",
            }}
          >
            Advisory Message
          </label>


          <textarea
            rows={5}

            value={
              manualMessage
            }

            onChange={(event) =>
              setManualMessage(
                event.target.value
              )
            }

            placeholder="Enter official advisory message in Marathi or English..."

            disabled={
              isManualBroadcasting
            }

            style={{
              width:
                "100%",
              maxWidth:
                "1000px",
              padding:
                "12px",
              border:
                "1px solid #cbd5e1",
              borderRadius:
                "8px",
              resize:
                "vertical",
              boxSizing:
                "border-box",
              fontFamily:
                "inherit",
            }}
          />

        </div>


        {/* =================================================
            MANUAL DISPATCH
        ================================================= */}

        <div
          style={{
            padding:
              "0 24px 24px",
            display:
              "flex",
            alignItems:
              "center",
            gap:
              "16px",
            flexWrap:
              "wrap",
          }}
        >

          <button
            className="broadcast-button"
            type="button"
            onClick={
              handleManualBroadcast
            }
            disabled={
              isManualBroadcasting
            }
            style={{
              padding:
                "12px 22px",
              opacity:
                isManualBroadcasting
                  ? 0.7
                  : 1,
            }}
          >
            {
              isManualBroadcasting
                ? "Sending..."
                : "📢 Dispatch Advisory"
            }
          </button>


          <span
            style={{
              color:
                "#64748b",
              fontSize:
                "14px",
            }}
          >
            {
              manualDistricts.length
            }{" "}
            district
            {
              manualDistricts.length ===
              1
                ? ""
                : "s"
            }{" "}
            selected
          </span>

        </div>

      </div>


      {/* =================================================
          RISK LEGEND
      ================================================= */}

      <div className="risk-legend">

        <div>

          <span className="legend-dot high-dot">
          </span>

          High Risk (
          {
            highRiskCount
          }
          )

        </div>


        <div>

          <span className="legend-dot medium-dot">
          </span>

          Medium Risk (
          {
            mediumRiskCount
          }
          )

        </div>


        <div>

          <span className="legend-dot low-dot">
          </span>

          Low Risk (
          {
            lowRiskCount
          }
          )

        </div>

      </div>


      {/* =================================================
          EXISTING AUTOMATIC BROADCAST MODAL
      ================================================= */}

      {isModalOpen &&
        selectedOutbreak && (

          <div
            className="modal-overlay"

            onClick={() => {

              if (
                !isBroadcasting
              ) {

                setIsModalOpen(
                  false
                );

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
                    Send official advisory
                    to affected farmers
                    via Telegram & SMS.
                  </p>

                </div>


                <button
                  className="modal-close"

                  onClick={() =>
                    !isBroadcasting &&
                    setIsModalOpen(
                      false
                    )
                  }

                  disabled={
                    isBroadcasting
                  }
                >
                  ×
                </button>

              </div>


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

                value={
                  officerMsg
                }

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
                    setIsModalOpen(
                      false
                    )
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
                  {
                    isBroadcasting
                      ? "Sending..."
                      : "📢 Dispatch Advisory"
                  }
                </button>

              </div>

            </div>

          </div>

        )}

    </div>
  );
}

export default StateHotspotMap;