import { useState } from "react";

// District fallback coordinates across Maharashtra
const DISTRICT_COORDINATES = {
  "ahilyanagar (ahmednagar)": [19.0952, 74.7496],
  "ahmednagar": [19.0952, 74.7496],
  "akola": [20.7002, 77.0082],
  "amravati": [20.9374, 77.7796],
  "beed": [18.9891, 75.7601],
  "bhandara": [21.1667, 79.6500],
  "buldhana": [20.5312, 76.1834],
  "chandrapur": [19.9615, 79.2961],
  "chhatrapati sambhajinagar (aurangabad)": [19.8762, 75.3433],
  "aurangabad": [19.8762, 75.3433],
  "dharashiv (osmanabad)": [18.1856, 76.0416],
  "osmanabad": [18.1856, 76.0416],
  "dhule": [20.9042, 74.7749],
  "gadchiroli": [20.1849, 79.9948],
  "gondia": [21.4554, 80.1961],
  "hingoli": [19.7196, 77.1477],
  "jalgaon": [21.0077, 75.5626],
  "jalna": [19.8410, 75.8864],
  "kolhapur": [16.7050, 74.2433],
  "latur": [18.4088, 76.5604],
  "mumbai city": [18.9388, 72.8354],
  "mumbai suburban": [19.0760, 72.8777],
  "nagpur": [21.1458, 79.0882],
  "nanded": [19.1383, 77.3210],
  "nandurbar": [21.3700, 74.2400],
  "nashik": [19.9975, 73.7898],
  "palghar": [19.6967, 72.7655],
  "parbhani": [19.2686, 76.7708],
  "pune": [18.5204, 73.8567],
  "raigad": [18.5158, 73.1812],
  "ratnagiri": [16.9902, 73.3120],
  "sangli": [16.8524, 74.5815],
  "satara": [17.6805, 73.9936],
  "sindhudurg": [16.1216, 73.6934],
  "solapur": [17.6599, 75.9064],
  "thane": [19.2183, 72.9781],
  "wardha": [20.7453, 78.6022],
  "washim": [20.1110, 77.1340],
  "yavatmal": [20.3888, 78.1204],
};

function CaseDetailPage({ caseData, onBack, onResolve }) {
  const [expertDiagnosis, setExpertDiagnosis] = useState("");
  const [prescription, setPrescription] = useState("");
  const [imgError, setImgError] = useState(false);

  const handleResolve = () => {
    if (!expertDiagnosis.trim()) {
      alert("Please enter the expert diagnosis.");
      return;
    }

    if (!prescription.trim()) {
      alert("Please enter the prescription/advisory.");
      return;
    }

    onResolve(
      caseData.case_id,
      expertDiagnosis.trim(),
      prescription.trim()
    );
  };

  // =========================================
  // GPS & DISTRICT RESOLUTION
  // =========================================
  const cleanDistrict = (caseData?.district || "yavatmal").toLowerCase().trim();
  const districtCoords = DISTRICT_COORDINATES[cleanDistrict];

  const rawLat = caseData?.latitude ?? caseData?.gps_lat;
  const rawLng = caseData?.longitude ?? caseData?.gps_long;

  const latitude = districtCoords ? districtCoords[0] : (rawLat ? Number(rawLat) : 20.3888);
  const longitude = districtCoords ? districtCoords[1] : (rawLng ? Number(rawLng) : 78.1204);

  // =========================================
  // IMAGE URL FIX & NORMALIZATION
  // =========================================
  let imageUrl = caseData?.image_url || "";
  if (imageUrl && imageUrl.startsWith("http://127.0.0.1:8000")) {
    imageUrl = imageUrl.replace("http://127.0.0.1:8000", "http://localhost:8000");
  } else if (imageUrl && !imageUrl.startsWith("http")) {
    imageUrl = `http://localhost:8000${imageUrl.startsWith("/") ? "" : "/"}${imageUrl}`;
  }

  return (
    <div className="detail-page" style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      {/* BACK BUTTON */}
      <button
        className="back-button"
        onClick={onBack}
        style={{
          background: "transparent",
          border: "none",
          color: "#166534",
          fontSize: "15px",
          fontWeight: 600,
          cursor: "pointer",
          marginBottom: "16px",
          display: "inline-flex",
          alignItems: "center"
        }}
      >
        ← Back to Expert Triage
      </button>

      {/* HEADER */}
      <div className="detail-header" style={{ marginBottom: "24px" }}>
        <h2 style={{ fontSize: "24px", fontWeight: 700, color: "#0f172a", margin: 0 }}>
          Case #{caseData?.case_id}
        </h2>
        <p style={{ color: "#64748b", margin: "4px 0 0 0" }}>
          Review case details and provide expert confirmation.
        </p>
      </div>

      {/* GRID */}
      <div
        className="detail-grid"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))",
          gap: "20px",
          marginBottom: "20px"
        }}
      >
        {/* IMAGE CARD */}
        <div
          className="detail-card image-card"
          style={{
            background: "#ffffff",
            borderRadius: "12px",
            padding: "20px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
            border: "1px solid #e2e8f0"
          }}
        >
          <h3 style={{ fontSize: "16px", fontWeight: 600, marginTop: 0, marginBottom: "16px", color: "#1e293b" }}>
            📷 User Uploaded Crop Image
          </h3>

          <div
            className="case-image-container"
            style={{
              width: "100%",
              height: "260px",
              borderRadius: "8px",
              overflow: "hidden",
              backgroundColor: "#f8fafc",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              border: "1px solid #e2e8f0"
            }}
          >
            {!imgError && imageUrl ? (
              <img
                src={imageUrl}
                alt="Farmer uploaded crop"
                style={{ width: "100%", height: "100%", objectFit: "contain", background: "#111827" }}
                onError={() => setImgError(true)}
              />
            ) : (
              <div style={{ textAlign: "center", color: "#94a3b8" }}>
                <span style={{ fontSize: "36px" }}>🌿</span>
                <p style={{ margin: "6px 0 0 0", fontSize: "13px" }}>Image preview not available</p>
              </div>
            )}
          </div>

          <p className="image-caption" style={{ fontSize: "13px", color: "#64748b", marginTop: "10px", textAlign: "center" }}>
            Farmer-submitted leaf scan
          </p>
        </div>

        {/* CASE DETAILS */}
        <div
          className="detail-card"
          style={{
            background: "#ffffff",
            borderRadius: "12px",
            padding: "20px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
            border: "1px solid #e2e8f0"
          }}
        >
          <h3 style={{ fontSize: "16px", fontWeight: 600, marginTop: 0, marginBottom: "16px", color: "#1e293b" }}>
            Case Information
          </h3>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #f1f5f9", paddingBottom: "8px" }}>
              <span style={{ color: "#64748b", fontSize: "14px" }}>Farmer</span>
              <strong style={{ color: "#0f172a", fontSize: "14px" }}>{caseData?.farmer_name || "Unknown Farmer"}</strong>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #f1f5f9", paddingBottom: "8px" }}>
              <span style={{ color: "#64748b", fontSize: "14px" }}>Crop</span>
              <strong style={{ color: "#0f172a", fontSize: "14px", textTransform: "capitalize" }}>{caseData?.crop}</strong>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #f1f5f9", paddingBottom: "8px" }}>
              <span style={{ color: "#64748b", fontSize: "14px" }}>District</span>
              <strong style={{ color: "#0f172a", fontSize: "14px" }}>{caseData?.district}</strong>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #f1f5f9", paddingBottom: "8px", alignItems: "center" }}>
              <span style={{ color: "#64748b", fontSize: "14px" }}>Severity</span>
              <span
                style={{
                  background: caseData?.severity?.toLowerCase() === "high" ? "#fee2e2" : caseData?.severity?.toLowerCase() === "low" ? "#dcfce7" : "#fef3c7",
                  color: caseData?.severity?.toLowerCase() === "high" ? "#b91c1c" : caseData?.severity?.toLowerCase() === "low" ? "#166534" : "#b45309",
                  padding: "2px 10px",
                  borderRadius: "12px",
                  fontSize: "12px",
                  fontWeight: 600
                }}
              >
                {caseData?.severity || "Medium"}
              </span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #f1f5f9", paddingBottom: "8px" }}>
              <span style={{ color: "#64748b", fontSize: "14px" }}>AI Predicted Disease</span>
              <strong style={{ color: "#166534", fontSize: "14px", textTransform: "capitalize" }}>
                {caseData?.disease ? caseData.disease.replace(/_/g, " ") : "Unknown"}
              </strong>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #f1f5f9", paddingBottom: "8px" }}>
              <span style={{ color: "#64748b", fontSize: "14px" }}>AI Confidence</span>
              <strong style={{ color: "#0f172a", fontSize: "14px" }}>{caseData?.confidence}%</strong>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #f1f5f9", paddingBottom: "8px" }}>
              <span style={{ color: "#64748b", fontSize: "14px" }}>Status</span>
              <span
                style={{
                  background: caseData?.status?.toLowerCase().includes("resolve") ? "#dcfce7" : "#ede9fe",
                  color: caseData?.status?.toLowerCase().includes("resolve") ? "#166534" : "#5b21b6",
                  padding: "2px 10px",
                  borderRadius: "12px",
                  fontSize: "12px",
                  fontWeight: 600
                }}
              >
                {caseData?.status}
              </span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "#64748b", fontSize: "14px" }}>Report Date</span>
              <strong style={{ color: "#0f172a", fontSize: "14px" }}>{caseData?.date || caseData?.created_at || "Recent"}</strong>
            </div>
          </div>
        </div>
      </div>

      {/* LOCATION */}
      <div
        className="detail-card location-card"
        style={{
          background: "#ffffff",
          borderRadius: "12px",
          padding: "20px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          border: "1px solid #e2e8f0",
          marginBottom: "20px"
        }}
      >
        <h3 style={{ fontSize: "16px", fontWeight: 600, marginTop: 0, marginBottom: "12px", color: "#1e293b" }}>
          📍 Location ({caseData?.district || "Maharashtra"})
        </h3>

        <div>
          <strong style={{ fontSize: "15px", color: "#0f172a" }}>
            {latitude.toFixed(6)}, {longitude.toFixed(6)}
          </strong>
          <p style={{ fontSize: "13px", color: "#64748b", margin: "4px 0 10px 0" }}>
            GPS coordinates for {caseData?.district}, Maharashtra
          </p>

          <a
            href={`https://maps.google.com/?q=${latitude},${longitude}`}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "#2563eb", textDecoration: "none", fontWeight: 600, fontSize: "14px" }}
          >
            ↗ View on Google Maps
          </a>
        </div>
      </div>

      {/* EXPERT REVIEW */}
      <div
        className="detail-card expert-review-card"
        style={{
          background: "#ffffff",
          borderRadius: "12px",
          padding: "20px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          border: "1px solid #e2e8f0"
        }}
      >
        <h3 style={{ fontSize: "16px", fontWeight: 600, marginTop: 0, marginBottom: "6px", color: "#1e293b" }}>
          👨‍🌾 Expert Review
        </h3>
        <p style={{ fontSize: "14px", color: "#64748b", marginTop: 0, marginBottom: "16px" }}>
          Provide your expert diagnosis and recommended advisory before resolving this case.
        </p>

        <div style={{ marginBottom: "16px" }}>
          <label style={{ display: "block", fontSize: "14px", fontWeight: 600, color: "#334155", marginBottom: "6px" }}>
            Expert Diagnosis
          </label>
          <textarea
            rows={3}
            value={expertDiagnosis}
            onChange={(event) => setExpertDiagnosis(event.target.value)}
            placeholder="Enter confirmed disease diagnosis..."
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              fontSize: "14px"
            }}
          />
        </div>

        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", fontSize: "14px", fontWeight: 600, color: "#334155", marginBottom: "6px" }}>
            Prescription / Advisory
          </label>
          <textarea
            rows={4}
            value={prescription}
            onChange={(event) => setPrescription(event.target.value)}
            placeholder="Enter treatment or advisory for the farmer..."
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              fontSize: "14px"
            }}
          />
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px" }}>
          <button
            onClick={onBack}
            style={{
              padding: "10px 18px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              background: "#ffffff",
              color: "#475569",
              fontWeight: 600,
              cursor: "pointer"
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleResolve}
            style={{
              padding: "10px 20px",
              borderRadius: "8px",
              border: "none",
              background: "#166534",
              color: "#ffffff",
              fontWeight: 600,
              cursor: "pointer"
            }}
          >
            ✓ Confirm & Resolve Case
          </button>
        </div>
      </div>
    </div>
  );
}

export default CaseDetailPage;