import { useCallback, useEffect, useMemo, useState } from "react";

import ResolvedCasesPage from "./pages/ResolvedCasesPage";
import ExpertTriagePage, { type Case } from "./pages/ExpertTriagePage";
import CaseDetailPage from "./pages/CaseDetailPage";
import StateHotspotMap from "./pages/StateHotspotMap";
import TrendMetrics from "./components/TrendMetrics";
import { type MockCase } from "./data/mockCases";

import { getCases } from "./api/caseApi";

type Page =
  | "triage"
  | "map"
  | "analytics";

const API_BASE_URL = "http://localhost:8000/api";

function App() {
  const [activePage, setActivePage] = useState<Page>("triage");
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [showResolvedCases, setShowResolvedCases] = useState(false);
  
  // Live backend cases state
  const [liveCases, setLiveCases] = useState<MockCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // =========================================
  // FETCH CASES FROM BACKEND
  // =========================================
  const fetchCases = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/cases`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();

      // Normalize backend schema to match frontend MockCase / Case interface
      const formattedCases: MockCase[] = data.map((item: any) => ({
        ...item,
        case_id: item.id ?? item.case_id,
        id: item.id ?? item.case_id,
        farmer_name: item.farmer_name || "Unknown Farmer",
        crop: item.crop || "Unknown Crop",
        disease: (item.disease || "Unknown").replace(/_/g, " "),
        confidence: item.confidence ? Math.round(item.confidence * 100) : 0,
        district: item.district || "Maharashtra",
        severity: item.severity || "Medium",
        status: item.status || "Pending Expert",
        gps_lat: item.gps_lat ?? 20.3888,
        gps_long: item.gps_long ?? 78.1204,
        image_url: item.image_url || "/uploads/sample_leaf.jpg",
        date: item.created_at ? new Date(item.created_at).toISOString().split("T")[0] : new Date().toISOString().split("T")[0],
        resolution_date: item.resolved_at ? new Date(item.resolved_at).toISOString().split("T")[0] : undefined,
        expert_diagnosis: item.expert_diagnosis || undefined,
        prescription: item.prescription || undefined,
      }));

      setLiveCases(formattedCases);
    } catch (err) {
      console.error("[PikRakshak] Failed to fetch live cases from backend:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Poll backend on mount & every 4 seconds for real-time mobile scan updates
  useEffect(() => {
    fetchCases();
    const interval = setInterval(fetchCases, 4000);
    return () => clearInterval(interval);
  }, [fetchCases]);

  // =========================================
  // DERIVED LISTS
  // =========================================
  const pendingCases = useMemo(() => {
    return (liveCases as unknown as Case[]).filter(
      (item: any) => item.status === "Pending Expert"
    );
  }, [liveCases]);

  const currentCases = useMemo<MockCase[]>(() => {
    return liveCases;
  }, [liveCases]);

  // =========================================
  // RESOLVE CASE (PERSIST TO SQLITE BACKEND)
  // =========================================
  const handleResolveCase = async (
    caseId: number,
    expertDiagnosis: string,
    prescription: string
  ) => {
    try {
      const response = await fetch(`${API_BASE_URL}/cases/${caseId}/resolve`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          expert_diagnosis: expertDiagnosis,
          prescription: prescription,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to resolve case ID: ${caseId}`);
      }

      // Refresh case list immediately
      await fetchCases();
    } catch (error) {
      console.error("[PikRakshak] Resolve error:", error);
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
        onBack={() => setShowResolvedCases(false)}
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
        onBack={() => setSelectedCase(null)}
        onResolve={handleResolveCase}
      />
    );
  }

  // =====================================================
  // MAIN DASHBOARD
  // =========================================
  return (
    <div className="app">
      {/* HEADER */}
      <header className="topbar">
        <div className="brand-section">
          <div className="brand-mark">PR</div>
          <div>
            <h1>PikRakshak</h1>
            <p>Government Crop Health Monitoring Portal</p>
          </div>
        </div>

        <div className="portal-label">
          <span className="portal-badge">GOVERNMENT PORTAL</span>
          <span className="portal-subtitle">KVK / Agriculture Department</span>
        </div>

        <nav className="navigation">
          <button
            className={activePage === "triage" ? "nav-button active" : "nav-button"}
            onClick={() => setActivePage("triage")}
          >
            Expert Triage
          </button>

          <button
            className={activePage === "map" ? "nav-button active" : "nav-button"}
            onClick={() => setActivePage("map")}
          >
            State Outbreak Map
          </button>

          <button
            className={activePage === "analytics" ? "nav-button active" : "nav-button"}
            onClick={() => setActivePage("analytics")}
          >
            Analytics
          </button>
        </nav>
      </header>

      {/* CONTENT */}
      <main>
        {isLoading && liveCases.length === 0 ? (
          <div style={{ padding: "2rem", textAlign: "center", color: "#666" }}>
            Loading live case records from PikRakshak backend...
          </div>
        ) : (
          <>
            {/* EXPERT TRIAGE */}
            {activePage === "triage" && (
              <ExpertTriagePage
                cases={pendingCases}
                onSelectCase={(caseData) => setSelectedCase(caseData)}
              />
            )}

            {/* MAP */}
            {activePage === "map" && <StateHotspotMap cases={currentCases} />}

            {/* ANALYTICS */}
            {activePage === "analytics" && (
              <TrendMetrics
                cases={currentCases}
                onResolvedClick={() => setShowResolvedCases(true)}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;