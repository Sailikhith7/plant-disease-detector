import { useState } from "react";

import type { Case } from "./ExpertTriagePage";

type CaseDetailPageProps = {
  caseData: Case;
  onBack: () => void;
  onResolve: (
    caseId: string | number,
    expertDiagnosis: string,
    prescription: string
  ) => void;
};

function CaseDetailPage({
  caseData,
  onBack,
  onResolve,
}: CaseDetailPageProps) {
  const [expertDiagnosis, setExpertDiagnosis] =
    useState("");

  const [prescription, setPrescription] =
    useState("");

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
  // GPS VALUES
  // =========================================

  const latitude =
    caseData.gps_lat ??
    (caseData as any).lat ??
    (caseData as any).latitude;

  const longitude =
    caseData.gps_long ??
    (caseData as any).lng ??
    (caseData as any).longitude;

  const hasLocation =
    latitude !== undefined &&
    latitude !== null &&
    longitude !== undefined &&
    longitude !== null &&
    latitude !== "" &&
    longitude !== "";

  // =========================================
  // IMAGE
  // =========================================

  const imageUrl =
    caseData.image_url ||
    "/uploads/sample_leaf.jpg";

  return (
    <div className="detail-page">

      {/* =====================================
          BACK BUTTON
      ====================================== */}

      <button
        className="back-button"
        onClick={onBack}
      >
        ← Back to Expert Triage
      </button>

      {/* =====================================
          HEADER
      ====================================== */}

      <div className="detail-header">

        <div>
          <h2>
            Case #{caseData.case_id}
          </h2>

          <p>
            Review case details and provide
            expert confirmation.
          </p>
        </div>

      </div>

      {/* =====================================
          CASE INFORMATION
      ====================================== */}

      <div className="detail-grid">

        {/* ===================================
            IMAGE
        ==================================== */}

        <div className="detail-card image-card">

          <h3>
            📷 User Uploaded Crop Image
          </h3>

          <div className="case-image-container">

            <img
              src={imageUrl}
              alt="Farmer uploaded crop"
              className="case-image"
              onError={(event) => {
                event.currentTarget.style.display =
                  "none";
              }}
            />

          </div>

          <p className="image-caption">
            Farmer-submitted image will appear here
          </p>

        </div>

        {/* ===================================
            CASE DETAILS
        ==================================== */}

        <div className="detail-card">

          <h3>
            Case Information
          </h3>

          <div className="information-grid">

            <div className="info-item">
              <span>Farmer</span>
              <strong>
                {caseData.farmer_name}
              </strong>
            </div>

            <div className="info-item">
              <span>Crop</span>
              <strong>
                {caseData.crop}
              </strong>
            </div>

            <div className="info-item">
              <span>District</span>
              <strong>
                {caseData.district}
              </strong>
            </div>

            <div className="info-item">
              <span>Severity</span>

              <strong>
                <span
                  className={`severity ${
                    caseData.severity.toLowerCase()
                  }`}
                >
                  {caseData.severity}
                </span>
              </strong>
            </div>

            <div className="info-item">

              <span>
                AI Predicted Disease
              </span>

              <strong>
                {caseData.disease}
              </strong>

            </div>

            <div className="info-item">

              <span>
                AI Confidence
              </span>

              <strong>
                {caseData.confidence}%
              </strong>

            </div>

            <div className="info-item">

              <span>
                Status
              </span>

              <strong>
                {caseData.status}
              </strong>

            </div>

            <div className="info-item">

              <span>
                Report Date
              </span>

              <strong>
                {caseData.date || "N/A"}
              </strong>

            </div>

          </div>

        </div>

      </div>

      {/* =====================================
          LOCATION
      ====================================== */}

      <div className="detail-card location-card">

        <h3>
          📍 Location
        </h3>

        {hasLocation ? (

          <div>

            <strong>
              {Number(latitude).toFixed(6)},{" "}
              {Number(longitude).toFixed(6)}
            </strong>

            <p>
              GPS coordinates of reported case
            </p>

            <a
              href={`https://www.google.com/maps?q=${latitude},${longitude}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              View on Google Maps
            </a>

          </div>

        ) : (

          <div>

            <strong>
              Location unavailable
            </strong>

            <p>
              GPS coordinates were not provided
              for this case.
            </p>

          </div>

        )}

      </div>

      {/* =====================================
          EXPERT REVIEW
      ====================================== */}

      <div className="detail-card expert-review-card">

        <h3>
          👨‍🌾 Expert Review
        </h3>

        <p>
          Provide your expert diagnosis and
          recommended advisory before resolving
          this case.
        </p>

        {/* DIAGNOSIS */}

        <div className="form-group">

          <label>
            Expert Diagnosis
          </label>

          <textarea
            rows={4}
            value={expertDiagnosis}
            onChange={(event) =>
              setExpertDiagnosis(
                event.target.value
              )
            }
            placeholder="Enter confirmed disease diagnosis..."
          />

        </div>

        {/* PRESCRIPTION */}

        <div className="form-group">

          <label>
            Prescription / Advisory
          </label>

          <textarea
            rows={5}
            value={prescription}
            onChange={(event) =>
              setPrescription(
                event.target.value
              )
            }
            placeholder="Enter treatment or advisory for the farmer..."
          />

        </div>

        {/* ACTIONS */}

        <div className="detail-actions">

          <button
            className="cancel-button"
            onClick={onBack}
          >
            Cancel
          </button>

          <button
            className="resolve-button"
            onClick={handleResolve}
          >
            ✓ Confirm & Resolve Case
          </button>

        </div>

      </div>

    </div>
  );
}

export default CaseDetailPage;

