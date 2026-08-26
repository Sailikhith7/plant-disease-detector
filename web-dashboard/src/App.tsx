import { useMemo, useState } from "react";

import ResolvedCasesPage from "./pages/ResolvedCasesPage";

import ExpertTriagePage, {
  type Case,
} from "./pages/ExpertTriagePage";

import CaseDetailPage from "./pages/CaseDetailPage";
import StateHotspotMap from "./pages/StateHotspotMap";
import TrendMetrics from "./components/TrendMetrics";

import {
  mockCases,
  type MockCase,
} from "./data/mockCases";

type Page = "triage" | "map" | "analytics";

function App() {
  const [activePage, setActivePage] =
    useState<Page>("triage");

  const [selectedCase, setSelectedCase] =
    useState<Case | null>(null);

  const [resolvedCaseIds, setResolvedCaseIds] =
    useState<number[]>([]);

  const [resolvedDetails, setResolvedDetails] =
    useState<
      Record<
        number,
        {
          resolution_date: string;
          expert_diagnosis: string;
          prescription: string;
        }
      >
    >({});

  const [showResolvedCases, setShowResolvedCases] =
    useState(false);

  // =========================================
  // PENDING EXPERT CASES
  // =========================================

  const pendingCases = useMemo(() => {
    return mockCases.filter(
      (item) =>
        item.status === "Pending Expert" &&
        !resolvedCaseIds.includes(item.case_id)
    );
  }, [resolvedCaseIds]);

  // =========================================
  // CURRENT LIVE DATASET
  // =========================================

  const currentCases = useMemo<MockCase[]>(() => {
    return mockCases.map((item) => {
      if (!resolvedCaseIds.includes(item.case_id)) {
        return item;
      }

      const savedDetails =
        resolvedDetails[item.case_id];

      return {
        ...item,
        status: "Resolved",

        resolution_date:
          savedDetails?.resolution_date ??
          item.resolution_date ??
          new Date().toISOString().split("T")[0],

        expert_diagnosis:
          savedDetails?.expert_diagnosis ??
          item.expert_diagnosis ??
          "No diagnosis recorded.",

        prescription:
          savedDetails?.prescription ??
          item.prescription ??
          "No prescription recorded.",
      };
    });
  }, [
    resolvedCaseIds,
    resolvedDetails,
  ]);

  // =========================================
  // RESOLVE CASE
  // =========================================

  const handleResolveCase = (
    caseId: number,
    expertDiagnosis: string,
    prescription: string
  ) => {
    const today =
      new Date().toISOString().split("T")[0];

    setResolvedDetails((previous) => ({
      ...previous,

      [caseId]: {
        resolution_date: today,
        expert_diagnosis: expertDiagnosis,
        prescription,
      },
    }));

    setResolvedCaseIds((previous) => {
      if (previous.includes(caseId)) {
        return previous;
      }

      return [...previous, caseId];
    });

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

      {/* HEADER */}

      <header className="topbar">

        <div className="brand-section">

          <div className="brand-mark">
            PR
          </div>

          <div>
            <h1>PikRakshak</h1>

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

      {/* CONTENT */}

      <main>

        {/* EXPERT TRIAGE */}

        {activePage === "triage" && (
          <ExpertTriagePage
            cases={pendingCases}
            onSelectCase={(caseData) =>
              setSelectedCase(caseData)
            }
          />
        )}

        {/* MAP */}

        {activePage === "map" && (
          <StateHotspotMap
            cases={currentCases}
          />
        )}

        {/* ANALYTICS */}

        {activePage === "analytics" && (
          <TrendMetrics
            cases={currentCases}
            onResolvedClick={() =>
              setShowResolvedCases(true)
            }
          />
        )}

      </main>

    </div>
  );
}

export default App;