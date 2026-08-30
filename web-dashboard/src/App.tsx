import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import ResolvedCasesPage from "./pages/ResolvedCasesPage";
import ExpertTriagePage, {
  type Case,
} from "./pages/ExpertTriagePage";
import CaseDetailPage from "./pages/CaseDetailPage";
import StateHotspotMap from "./pages/StateHotspotMap";
import TrendMetrics from "./components/TrendMetrics";
import { type MockCase } from "./data/mockCases";

type Page =
  | "triage"
  | "map"
  | "analytics";

const API_BASE_URL =
  "http://localhost:8000/api";

const CONFIDENCE_THRESHOLD = 75;

const RESOLVED_STORAGE_KEY =
  "pikrashak_resolved_case_ids";

function App() {
  const [activePage, setActivePage] =
    useState<Page>("triage");

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
  // EXPERT-RESOLVED CASES
  //
  // These persist across page refreshes.
  // =========================================

  const [resolvedCaseIds, setResolvedCaseIds] =
    useState<(number | string)[]>(() => {
      try {
        const stored =
          localStorage.getItem(
            RESOLVED_STORAGE_KEY
          );

        if (!stored) {
          return [];
        }

        const parsed =
          JSON.parse(stored);

        return Array.isArray(parsed)
          ? parsed
          : [];
      } catch {
        return [];
      }
    });

  // =========================================
  // APPROVED AI CASES
  //
  // Session-only.
  // Refreshing the website resets these,
  // so the examiner sees the AI Auto-Resolved
  // section again.
  // =========================================

  const [approvedCaseIds, setApprovedCaseIds] =
    useState<(number | string)[]>([]);

  // =========================================
  // SAVE EXPERT-RESOLVED CASES
  // =========================================

  useEffect(() => {
    localStorage.setItem(
      RESOLVED_STORAGE_KEY,
      JSON.stringify(
        resolvedCaseIds
      )
    );
  }, [resolvedCaseIds]);

  // =========================================
  // FETCH CASES FROM BACKEND
  // =========================================

  const fetchCases = useCallback(
    async () => {
      try {
        const response =
          await fetch(
            `${API_BASE_URL}/cases/`
          );

        if (!response.ok) {
          throw new Error(
            `HTTP error! status: ${response.status}`
          );
        }

        const data =
          await response.json();

        const backendCases =
          Array.isArray(data)
            ? data
            : Array.isArray(
                data?.cases
              )
              ? data.cases
              : [];

        const formattedCases:
          MockCase[] =
          backendCases.map(
            (item: any) => {
              let confidence = 0;

              if (
                typeof item.confidence ===
                "number"
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
                  ).replace(
                    /_/g,
                    " "
                  ),

                // Confidence
                confidence,

                // District
                district:
                  item.district ||
                  "Maharashtra",

                // Severity
                severity:
                  item.severity ||
                  "Medium",

                // Original backend status
                status:
                  item.status ||
                  "Pending Expert",

                // GPS
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

                // Date
                date:
                  item.created_at
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
                  item.expert_response ||
                  undefined,

                // Prescription
                prescription:
                  item.prescription ||
                  undefined,
              };
            }
          );

        setLiveCases(
          formattedCases
        );
      } catch (error) {
        console.error(
          "[PikRakshak] Failed to fetch live cases from backend:",
          error
        );
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // =========================================
  // INITIAL FETCH + POLLING
  // =========================================

  useEffect(() => {
    fetchCases();

    const interval =
      setInterval(
        fetchCases,
        4000
      );

    return () =>
      clearInterval(interval);
  }, [fetchCases]);

  // =========================================
  // PENDING EXPERT CASES
  //
  // Confidence < 75
  // Not already resolved.
  // Not already approved.
  // =========================================

  const pendingCases =
    useMemo(() => {
      return liveCases.filter(
        (item) => {
          const isExpertResolved =
            resolvedCaseIds.includes(
              item.case_id
            );

          const isAIApproved =
            approvedCaseIds.includes(
              item.case_id
            );

          return (
            item.confidence <
              CONFIDENCE_THRESHOLD &&
            !isExpertResolved &&
            !isAIApproved
          );
        }
      );
    }, [
      liveCases,
      resolvedCaseIds,
      approvedCaseIds,
    ]);

  // =========================================
  // AI AUTO-RESOLVED CASES
  //
  // Confidence >= 75
  // Not already approved.
  // Not manually resolved.
  // =========================================

  const autoResolvedCases =
    useMemo(() => {
      return liveCases.filter(
        (item) => {
          const isAIApproved =
            approvedCaseIds.includes(
              item.case_id
            );

          const isExpertResolved =
            resolvedCaseIds.includes(
              item.case_id
            );

          return (
            item.confidence >=
              CONFIDENCE_THRESHOLD &&
            !isAIApproved &&
            !isExpertResolved
          );
        }
      );
    }, [
      liveCases,
      approvedCaseIds,
      resolvedCaseIds,
    ]);

  // =========================================
  // ALL CURRENT CASES
  // =========================================

  const currentCases =
    useMemo<MockCase[]>(() => {
      return liveCases.map(
        (item) => {
          const isExpertResolved =
            resolvedCaseIds.includes(
              item.case_id
            );

          const isAIApproved =
            approvedCaseIds.includes(
              item.case_id
            );

          // Expert manually resolved
          if (
            isExpertResolved
          ) {
            return {
              ...item,
              status: "Resolved",
            };
          }

          // High-confidence AI case approved
          if (
            isAIApproved
          ) {
            return {
              ...item,
              status: "Resolved",
            };
          }

          // High confidence, waiting for approval
          if (
            item.confidence >=
            CONFIDENCE_THRESHOLD
          ) {
            return {
              ...item,
              status:
                "AI Auto-Resolved",
            };
          }

          // Low confidence
          return {
            ...item,
            status:
              "Pending Expert",
          };
        }
      );
    }, [
      liveCases,
      resolvedCaseIds,
      approvedCaseIds,
    ]);

  // =========================================
  // ANALYTICS CASES
  //
  // BOTH TYPES ARE INCLUDED:
  //
  // 1. High-confidence + Expert approved
  // 2. Low-confidence + Expert manually resolved
  // =========================================

  const analyticsCases =
    useMemo(() => {
      return currentCases.filter(
        (item) => {
          const isExpertResolved =
            resolvedCaseIds.includes(
              item.case_id
            );

          const isAIApproved =
            approvedCaseIds.includes(
              item.case_id
            );

          return (
            isExpertResolved ||
            isAIApproved
          );
        }
      );
    }, [
      currentCases,
      resolvedCaseIds,
      approvedCaseIds,
    ]);

  // =========================================
  // APPROVE ALL AI CASES
  // =========================================

  const handleApproveAll = (
    caseIds:
      (number | string)[]
  ) => {
    setApprovedCaseIds(
      (previous) => {
        const newIds =
          caseIds.filter(
            (id) =>
              !previous.includes(id)
          );

        return [
          ...previous,
          ...newIds,
        ];
      }
    );
  };

  // =========================================
  // RESOLVE ONE PENDING CASE
  // =========================================

  const handleResolveCase =
    async (
      caseId:
        string | number,

      expertDiagnosis:
        string,

      prescription:
        string
    ) => {
      try {
        const response =
          await fetch(
            `${API_BASE_URL}/cases/${caseId}/resolve`,
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body: JSON.stringify({
                expert_response:
                  `${expertDiagnosis} - Prescription: ${prescription}`,
              }),
            }
          );

        if (!response.ok) {
          throw new Error(
            `Failed to resolve case ID: ${caseId}`
          );
        }

        // Store immediately before polling refresh.
        setResolvedCaseIds(
          (previous) => {
            if (
              previous.includes(
                caseId
              )
            ) {
              return previous;
            }

            return [
              ...previous,
              caseId,
            ];
          }
        );

        await fetchCases();

      } catch (error) {
        console.error(
          "[PikRakshak] Resolve error:",
          error
        );
      }

      setSelectedCase(
        null
      );
    };

  // =========================================
  // RESOLVED CASES PAGE
  // =========================================

  if (
    showResolvedCases
  ) {
    return (
      <ResolvedCasesPage
        cases={
          currentCases
        }
        onBack={() =>
          setShowResolvedCases(
            false
          )
        }
      />
    );
  }

  // =========================================
  // CASE DETAIL PAGE
  // =========================================

  if (
    selectedCase
  ) {
    return (
      <CaseDetailPage
        caseData={
          selectedCase
        }
        onBack={() =>
          setSelectedCase(
            null
          )
        }
        onResolve={
          handleResolveCase
        }
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

        <div className="portal-label">

          <span className="portal-badge">
            GOVERNMENT PORTAL
          </span>

          <span className="portal-subtitle">
            KVK / Agriculture Department
          </span>

        </div>

        <nav className="navigation">

          <button
            className={
              activePage ===
              "triage"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              setActivePage(
                "triage"
              )
            }
          >
            Expert Triage
          </button>

          <button
            className={
              activePage ===
              "map"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              setActivePage(
                "map"
              )
            }
          >
            State Outbreak Map
          </button>

          <button
            className={
              activePage ===
              "analytics"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              setActivePage(
                "analytics"
              )
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

        {isLoading &&
        liveCases.length === 0 ? (

          <div
            style={{
              padding:
                "2rem",
              textAlign:
                "center",
              color:
                "#666",
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

            {activePage ===
              "triage" && (

              <ExpertTriagePage
                cases={
                  currentCases
                }

                onSelectCase={(
                  caseData
                ) =>
                  setSelectedCase(
                    caseData
                  )
                }

                onApproveAll={
                  handleApproveAll
                }

              />

            )}

            {/* =================================
                STATE OUTBREAK MAP
            ================================= */}

            {activePage ===
              "map" && (

              <StateHotspotMap
                cases={
                  currentCases
                }
              />

            )}

            {/* =================================
                ANALYTICS
            ================================= */}

            {activePage ===
              "analytics" && (

              <TrendMetrics
                cases={
                  analyticsCases
                }

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