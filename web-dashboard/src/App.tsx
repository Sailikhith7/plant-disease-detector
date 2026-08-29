
import { useCallback, useEffect, useMemo, useState } from "react";

import ResolvedCasesPage from "./pages/ResolvedCasesPage";
import ExpertTriagePage, { type Case } from "./pages/ExpertTriagePage";
import CaseDetailPage from "./pages/CaseDetailPage";
import StateHotspotMap from "./pages/StateHotspotMap";
import TrendMetrics from "./components/TrendMetrics";
import { type MockCase } from "./data/mockCases";

type Page =
  | "triage"
  | "map"
  | "analytics";

const API_BASE_URL = "http://localhost:8000/api";

function App() {
  const [activePage, setActivePage] = useState<Page>("triage");

  const [selectedCase, setSelectedCase] =
    useState<Case | null>(null);

  const [showResolvedCases, setShowResolvedCases] =
    useState(false);

  // =========================================
  // LIVE BACKEND CASES
  // =========================================

  const [liveCases, setLiveCases] =
    useState<MockCase[]>([]);

  const [isLoading, setIsLoading] =
    useState(true);

  // =========================================
  // FETCH CASES FROM BACKEND
  // =========================================

  const fetchCases = useCallback(async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/cases`
      );

      if (!response.ok) {
        throw new Error(
          `HTTP error! status: ${response.status}`
        );
      }

      const data = await response.json();

      console.log(
        "[PikRakshak] Backend response:",
        data
      );

      // =========================================
      // IMPORTANT:
      //
      // Backend returns:
      //
      // {
      //   status: "success",
      //   cases: [...]
      // }
      //
      // Therefore we must extract data.cases.
      // =========================================

      const backendCases = Array.isArray(data)
        ? data
        : Array.isArray(data?.cases)
          ? data.cases
          : [];

      console.log(
        "[PikRakshak] Cases received:",
        backendCases.length
      );

      // =========================================
      // NORMALIZE BACKEND DATA
      // TO FRONTEND MockCase FORMAT
      // =========================================

      const formattedCases: MockCase[] =
        backendCases.map((item: any) => {
          // Handle confidence values such as:
          // 0.85  -> 85
          // 85    -> 85

          let confidence = 0;

          if (
            typeof item.confidence === "number"
          ) {
            confidence =
              item.confidence <= 1
                ? Math.round(
                    item.confidence * 100
                  )
                : Math.round(
                    item.confidence
                  );
          }

          return {
            ...item,

            // Case ID
            case_id:
              item.id ??
              item.case_id,

            id:
              item.id ??
              item.case_id,

            // Farmer
            farmer_name:
              item.farmer_name ||
              "Unknown Farmer",

            // Crop
            crop:
              item.crop ||
              "Unknown Crop",

            // Disease
            disease:
              (
                item.disease ||
                "Unknown"
              ).replace(/_/g, " "),

            // AI confidence
            confidence,

            // District
            district:
              item.district ||
              "Maharashtra",

            // Severity
            severity:
              item.severity ||
              "Medium",

            // Status
            status:
              item.status ||
              "Pending Expert",

            // GPS coordinates
            gps_lat:
              item.gps_lat ??
              item.lat ??
              item.latitude ??
              20.3888,

            gps_long:
              item.gps_long ??
              item.lng ??
              item.longitude ??
              78.1204,

            // Image
            image_url:
              item.image_url ||
              "/uploads/sample_leaf.jpg",

            // Created date
            date: item.created_at
              ? new Date(
                  item.created_at
                )
                  .toISOString()
                  .split("T")[0]
              : new Date()
                  .toISOString()
                  .split("T")[0],

            // Resolution date
            resolution_date:
              item.resolved_at
                ? new Date(
                    item.resolved_at
                  )
                    .toISOString()
                    .split("T")[0]
                : undefined,

            // Expert diagnosis
            expert_diagnosis:
              item.expert_diagnosis ||
              undefined,

            // Prescription
            prescription:
              item.prescription ||
              undefined,
          };
        });

      console.log(
        "[PikRakshak] Formatted cases:",
        formattedCases
      );

      setLiveCases(formattedCases);
    } catch (err) {
      console.error(
        "[PikRakshak] Failed to fetch live cases from backend:",
        err
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  // =========================================
  // FETCH ON STARTUP
  // AND EVERY 4 SECONDS
  // =========================================

  useEffect(() => {
    fetchCases();

    const interval =
      setInterval(fetchCases, 4000);

    return () =>
      clearInterval(interval);
  }, [fetchCases]);

  // =========================================
  // PENDING CASES
  // =========================================

  const pendingCases = useMemo(() => {
    return liveCases.filter(
      (item) =>
        item.status === "Pending Expert"
    );
  }, [liveCases]);

  // =========================================
  // ALL CURRENT CASES
  // =========================================

  const currentCases =
    useMemo<MockCase[]>(() => {
      return liveCases;
    }, [liveCases]);

  // =========================================
  // RESOLVE CASE
  // =========================================

  const handleResolveCase = async (
    caseId: number,
    expertDiagnosis: string,
    prescription: string
  ) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/cases/${caseId}/resolve`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            expert_diagnosis:
              expertDiagnosis,

            prescription:
              prescription,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Failed to resolve case ID: ${caseId}`
        );
      }

      // Refresh cases immediately
      await fetchCases();
    } catch (error) {
      console.error(
        "[PikRakshak] Resolve error:",
        error
      );
    }

    setSelectedCase(null);
  };

  // =========================================
  // RESOLVED CASES PAGE
  // =========================================

  if (showResolvedCases) {
    return (
      <ResolvedCasesPage
        cases={currentCases}
        onBack={() =>
          setShowResolvedCases(false)
        }
      />
    );
  }

  // =========================================
  // CASE DETAIL PAGE
  // =========================================

  if (selectedCase) {
    return (
      <CaseDetailPage
        caseData={selectedCase}
        onBack={() =>
          setSelectedCase(null)
        }
        onResolve={handleResolveCase}
      />
    );
  }

  // =========================================
  // MAIN DASHBOARD
  // =========================================

  return (
    <div className="app">

      {/* =====================================
          HEADER
      ====================================== */}

      <header className="topbar">

        <div className="brand-section">

          <div className="brand-mark">
            PR
          </div>

          <div>
            <h1>
              PikRakshak
            </h1>

            <p>
              Government Crop Health Monitoring Portal
            </p>
          </div>

        </div>

        {/* PORTAL LABEL */}

        <div className="portal-label">

          <span className="portal-badge">
            GOVERNMENT PORTAL
          </span>

          <span className="portal-subtitle">
            KVK / Agriculture Department
          </span>

        </div>

        {/* NAVIGATION */}

        <nav className="navigation">

          <button
            className={
              activePage === "triage"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              setActivePage("triage")
            }
          >
            Expert Triage
          </button>

          <button
            className={
              activePage === "map"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              setActivePage("map")
            }
          >
            State Outbreak Map
          </button>

          <button
            className={
              activePage === "analytics"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              setActivePage("analytics")
            }
          >
            Analytics
          </button>

        </nav>

      </header>

      {/* =====================================
          CONTENT
      ====================================== */}

      <main>

        {/* LOADING */}

        {isLoading &&
        liveCases.length === 0 ? (

          <div
            style={{
              padding: "2rem",
              textAlign: "center",
              color: "#666",
            }}
          >
            Loading live case records
            from PikRakshak backend...
          </div>

        ) : (

          <>

            {/* =================================
                EXPERT TRIAGE
            ================================= */}

            {activePage === "triage" && (

              <ExpertTriagePage
                cases={pendingCases}
                onSelectCase={(caseData) =>
                  setSelectedCase(
                    caseData
                  )
                }
              />

            )}

            {/* =================================
                STATE OUTBREAK MAP
            ================================= */}

            {activePage === "map" && (

              <StateHotspotMap
                cases={currentCases}
              />

            )}

            {/* =================================
                ANALYTICS
            ================================= */}

            {activePage === "analytics" && (

              <TrendMetrics
                cases={currentCases}
                onResolvedClick={() =>
                  setShowResolvedCases(
                    true
                  )
                }
              />

            )}

          </>

        )}

      </main>

    </div>
  );
}

export default App;

