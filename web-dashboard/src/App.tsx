import { useState } from "react";
import TrendMetrics from "./components/TrendMetrics";
import ExpertTriagePage, {
  mockCases,
  type Case,
} from "./pages/ExpertTriagePage";
import CaseDetailPage from "./pages/CaseDetailPage";
import StateHotspotMap from "./pages/StateHotspotMap";

type Page = "triage" | "map" | "analytics";

function App() {
  const [activePage, setActivePage] = useState<Page>("triage");
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [resolvedCaseIds, setResolvedCaseIds] = useState<number[]>([]);

  const activeCases = mockCases.filter(
    (item) => !resolvedCaseIds.includes(item.case_id)
  );

  const handleResolveCase = (caseId: number) => {
    setResolvedCaseIds((previous) => [...previous, caseId]);
    setSelectedCase(null);
  };

  if (selectedCase) {
    return (
      <CaseDetailPage
        caseData={selectedCase}
        onBack={() => setSelectedCase(null)}
        onResolve={handleResolveCase}
      />
    );
  }

  return (
    <div className="app">
      <header className="topbar">
  <div className="brand-section">
    

    <div>
      <h1 style={{ color: "#166534" }}>
  PikRakshak Government Dashboard
</h1>
      <p>Government Crop Health Monitoring Portal</p>
    </div>
  </div>

  

  <nav className="navigation">
    <button
      className={
        activePage === "triage"
          ? "nav-button active"
          : "nav-button"
      }
      onClick={() => setActivePage("triage")}
    >
      Expert Triage
    </button>

    <button
      className={
        activePage === "map"
          ? "nav-button active"
          : "nav-button"
      }
      onClick={() => setActivePage("map")}
    >
      State Outbreak Map
    </button>
    <button
  className={
    activePage === "analytics"
      ? "nav-button active"
      : "nav-button"
  }
  onClick={() => setActivePage("analytics")}
>
  Analytics
</button>
  </nav>
</header>

      <main>
       {activePage === "triage" ? (
  <ExpertTriagePage
    cases={activeCases}
    onSelectCase={(caseData) => setSelectedCase(caseData)}
  />
) : activePage === "map" ? (
  <StateHotspotMap />
) : (
  <TrendMetrics />
)}
      </main>
    </div>
  );
}

export default App;