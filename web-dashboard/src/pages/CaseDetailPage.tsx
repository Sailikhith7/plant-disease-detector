import { useState } from "react";

import type { Case } from "./ExpertTriagePage";

type CaseDetailPageProps = {
  caseData: Case;
  onBack: () => void;
  onResolve: (
    caseId: number,
    expertDiagnosis: string,
    prescription: string
  ) => void;
};

function CaseDetailPage({
  caseData,
  onBack,
  onResolve,
}: CaseDetailPageProps) {
  const [expertDiagnosis, setExpertDiagnosis] = useState("");
  const [prescription, setPrescription] = useState("");

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

  return (
    <div className="detail-page">

      <button
        className="back-button"
        onClick={onBack}
      >
        ← Back to Expert Triage
      </button>

      <div className="detail-header">
        <div>
          <h2>Case #{caseData.case_id}</h2>

          <p>
            Review case details and provide expert confirmation.
          </p>
        </div>
      </div>

      <div className="detail-grid">

        {/* LEFT CARD */}
        <div className="detail-card">

          <h3>Case Information</h3>

          {/* USER IMAGE */}
          <div className="uploaded-image-placeholder">
            <div className="upload-icon">📷</div>

            <strong>User Uploaded Crop Image</strong>

            <span>
              Farmer-submitted image will appear here
            </span>
          </div>

          {/* CASE DETAILS */}
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
              <span>Severity</span>
              <strong>{caseData.severity}</strong>
            </div>

          </div>

          {/* AI PREDICTION */}
          <div className="prediction-box">

            <span>AI Predicted Disease</span>

            <strong>{caseData.disease}</strong>

            <small>
              AI Confidence: {caseData.confidence}%
            </small>

          </div>

          {/* LOCATION */}
          <div className="gps-box">

            <span>Location</span>

            <strong>
              {caseData.latitude}, {caseData.longitude}
            </strong>

            <small>
              GPS coordinates of reported case
            </small>

          </div>

        </div>

        {/* RIGHT CARD */}
        <div className="detail-card">

          <h3>Expert Review</h3>

          <label>
            Expert Diagnosis
          </label>

          <textarea
            value={expertDiagnosis}
            onChange={(e) =>
              setExpertDiagnosis(e.target.value)
            }
            placeholder="Enter the expert-confirmed diagnosis..."
          />

          <label>
            Advisory / Prescription
          </label>

          <textarea
            value={prescription}
            onChange={(e) =>
              setPrescription(e.target.value)
            }
            placeholder="Enter treatment, advisory or prescription..."
          />

          <button
            className="resolve-button"
            onClick={handleResolve}
          >
            Resolve Case
          </button>

        </div>

      </div>
    </div>
  );
}

export default CaseDetailPage;