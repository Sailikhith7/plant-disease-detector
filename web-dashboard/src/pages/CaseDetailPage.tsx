import { useState } from "react";
import type { Case } from "./ExpertTriagePage";

type CaseDetailPageProps = {
  caseData: Case;
  onBack: () => void;
  onResolve: (caseId: number) => void;
};

function CaseDetailPage({
  caseData,
  onBack,
  onResolve,
}: CaseDetailPageProps) {
  const [diagnosis, setDiagnosis] = useState("");
  const [prescription, setPrescription] = useState("");
  const [resolved, setResolved] = useState(false);

  const handleResolve = () => {
  if (!diagnosis.trim() || !prescription.trim()) {
    alert("Please enter diagnosis and prescription.");
    return;
  }

  onResolve(caseData.case_id);
  setResolved(true);
};
  return (
    <div className="detail-page">
      <button className="back-button" onClick={onBack}>
        ← Back to Expert Queue
      </button>

      <div className="detail-header">
        <div>
          <h2>Case #{caseData.case_id}</h2>
          <p>Expert review and case resolution</p>
        </div>

        {resolved && (
          <span className="resolved-badge">
            ✓ Case Resolved
          </span>
        )}
      </div>

      <div className="detail-grid">
        {/* LEFT SIDE */}
        <div className="detail-card">
          <h3>Case Information</h3>

          <div className="info-grid">
            <div>
              <span>Farmer</span>
              <strong>{caseData.farmer_name}</strong>
            </div>

            <div>
              <span>Crop</span>
              <strong>{caseData.crop}</strong>
            </div>

            <div>
              <span>District</span>
              <strong>{caseData.district}</strong>
            </div>

            <div>
              <span>Case ID</span>
              <strong>#{caseData.case_id}</strong>
            </div>
          </div>

          <div className="image-placeholder">
            <div className="image-icon">🌿</div>
            <p>Crop Leaf Image</p>
            <small>High-resolution farmer upload</small>
          </div>

          <div className="gps-box">
            <span>GPS Location</span>
            <strong>20.3888° N, 78.1204° E</strong>
            <small>{caseData.district}, Maharashtra</small>
          </div>
        </div>

        {/* RIGHT SIDE */}
        <div className="detail-card">
          <h3>AI Prediction</h3>

          <div className="prediction-box">
            <span>Predicted Disease</span>
            <strong>{caseData.disease}</strong>

            <span>AI Confidence</span>
            <strong className="prediction-confidence">
              {caseData.confidence}%
            </strong>
          </div>

          <h3 className="form-heading">Expert Diagnosis</h3>

          <label htmlFor="diagnosis">
            Confirmed Diagnosis
          </label>

          <textarea
            id="diagnosis"
            value={diagnosis}
            onChange={(e) => setDiagnosis(e.target.value)}
            placeholder="Enter expert-confirmed diagnosis..."
          />

          <label htmlFor="prescription">
            Advisory / Prescription
          </label>

          <textarea
            id="prescription"
            value={prescription}
            onChange={(e) => setPrescription(e.target.value)}
            placeholder="Enter treatment or management advice..."
          />

          <button
            className="resolve-button"
            onClick={handleResolve}
            disabled={resolved}
          >
            {resolved ? "Case Resolved ✓" : "Resolve Case"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default CaseDetailPage;