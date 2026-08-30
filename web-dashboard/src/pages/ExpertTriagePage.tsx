import { useMemo, useState } from "react";
import type { MockCase } from "../data/mockCases";

export type Case = MockCase;

type ExpertTriagePageProps = {
  cases: Case[];
  onSelectCase: (caseData: Case) => void;
  onApproveAll: (caseIds: (number | string)[]) => void;
};

const CONFIDENCE_THRESHOLD = 75;

function ExpertTriagePage({
  cases,
  onSelectCase,
  onApproveAll,
}: ExpertTriagePageProps) {
  const [search, setSearch] = useState("");
  const [cropFilter, setCropFilter] = useState("All");
  const [districtFilter, setDistrictFilter] =
    useState("All");
  const [severityFilter, setSeverityFilter] =
    useState("All");
  const [sortOrder, setSortOrder] =
    useState("low");

  // =====================================================
  // PENDING EXPERT CASES
  //
  // < 75% confidence
  // AND NOT already resolved
  // AND NOT approved for analytics
  // =====================================================

  const pendingCases = useMemo(() => {
    return cases.filter((item) => {
      const isLowConfidence =
        item.confidence < CONFIDENCE_THRESHOLD;

      const isResolved =
        item.status === "Resolved";

      const isApproved =
        item.status === "Approved for Analytics";

      return (
        isLowConfidence &&
        !isResolved &&
        !isApproved
      );
    });
  }, [cases]);

  // =====================================================
  // AI AUTO-RESOLVED CASES
  //
  // >= 75% confidence
  // AND NOT already approved for analytics
  //
  // IMPORTANT:
  // Once approved, it will NOT appear here again.
  // =====================================================

  const autoResolvedCases = useMemo(() => {
    return cases.filter((item) => {
      const isHighConfidence =
        item.confidence >= CONFIDENCE_THRESHOLD;

      const isApproved =
        item.status ===
        "Approved for Analytics";

      const isResolved =
        item.status === "Resolved";

      return (
        isHighConfidence &&
        !isApproved &&
        !isResolved
      );
    });
  }, [cases]);

  // =====================================================
  // FILTER PENDING CASES
  // =====================================================

  const filteredPendingCases = useMemo(() => {
    const result = pendingCases.filter((item) => {
      const searchText =
        search.toLowerCase();

      const matchesSearch =
        item.farmer_name
          .toLowerCase()
          .includes(searchText) ||
        item.disease
          .toLowerCase()
          .includes(searchText) ||
        item.crop
          .toLowerCase()
          .includes(searchText);

      const matchesCrop =
        cropFilter === "All" ||
        item.crop === cropFilter;

      const matchesDistrict =
        districtFilter === "All" ||
        item.district === districtFilter;

      const matchesSeverity =
        severityFilter === "All" ||
        item.severity === severityFilter;

      return (
        matchesSearch &&
        matchesCrop &&
        matchesDistrict &&
        matchesSeverity
      );
    });

    result.sort((a, b) => {
      if (sortOrder === "low") {
        return (
          a.confidence -
          b.confidence
        );
      }

      return (
        b.confidence -
        a.confidence
      );
    });

    return result;
  }, [
    pendingCases,
    search,
    cropFilter,
    districtFilter,
    severityFilter,
    sortOrder,
  ]);

  // =====================================================
  // APPROVE ALL
  // =====================================================

  function handleApproveAll() {
    const caseIds =
      autoResolvedCases.map(
        (item) => item.case_id
      );

    if (caseIds.length === 0) {
      return;
    }

    onApproveAll(caseIds);
  }

  return (
    <div className="page-container">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="page-header">

        <div>
          <h2>
            KVK Expert Triage
          </h2>

          <p>
            Review low-confidence cases and
            approve high-confidence AI
            resolutions.
          </p>
        </div>

        <div className="pending-card">

          <span>
            Pending Cases
          </span>

          <strong>
            {pendingCases.length}
          </strong>

        </div>

      </div>


      {/* =================================================
          PENDING EXPERT REVIEW
      ================================================= */}

      <div className="table-card">

        <div
          style={{
            padding:
              "24px 24px 0",
          }}
        >

          <h3
            style={{
              margin: 0,
              marginBottom:
                "6px",
            }}
          >
            Pending Expert Review
          </h3>

          <p
            style={{
              margin: 0,
              color: "#64748b",
            }}
          >
            Cases with AI confidence below
            75% require expert verification.
          </p>

        </div>


        {/* FILTER BAR */}

        <div className="filter-bar">

          <input
            type="text"
            placeholder="Search farmer, crop or disease..."
            value={search}
            onChange={(e) =>
              setSearch(
                e.target.value
              )
            }
          />


          <select
            value={cropFilter}
            onChange={(e) =>
              setCropFilter(
                e.target.value
              )
            }
          >

            <option value="All">
              All Crops
            </option>

            <option value="Cotton">
              Cotton
            </option>

            <option value="Soybean">
              Soybean
            </option>

            <option value="Onion">
              Onion
            </option>

            <option value="Sugarcane">
              Sugarcane
            </option>

            <option value="Tomato">
              Tomato
            </option>

            <option value="Grapes">
              Grapes
            </option>

            <option value="Orange">
              Orange
            </option>

          </select>


          <select
            value={districtFilter}
            onChange={(e) =>
              setDistrictFilter(
                e.target.value
              )
            }
          >

            <option value="All">
              All Districts
            </option>

            <option value="Amravati">
              Amravati
            </option>

            <option value="Akola">
              Akola
            </option>

            <option value="Nagpur">
              Nagpur
            </option>

            <option value="Pune">
              Pune
            </option>

            <option value="Sangli">
              Sangli
            </option>

            <option value="Wardha">
              Wardha
            </option>

            <option value="Yavatmal">
              Yavatmal
            </option>

            <option value="Nanded">
              Nanded
            </option>

            <option value="Nashik">
              Nashik
            </option>

            <option value="Kolhapur">
              Kolhapur
            </option>

          </select>


          <select
            value={severityFilter}
            onChange={(e) =>
              setSeverityFilter(
                e.target.value
              )
            }
          >

            <option value="All">
              All Severity
            </option>

            <option value="High">
              High
            </option>

            <option value="Medium">
              Medium
            </option>

            <option value="Low">
              Low
            </option>

          </select>


          <select
            value={sortOrder}
            onChange={(e) =>
              setSortOrder(
                e.target.value
              )
            }
          >

            <option value="low">
              Lowest Confidence First
            </option>

            <option value="high">
              Highest Confidence First
            </option>

          </select>

        </div>


        {/* PENDING TABLE */}

        <table>

          <thead>
            <tr>
              <th>Case ID</th>
              <th>Farmer</th>
              <th>Crop</th>
              <th>Predicted Disease</th>
              <th>Confidence</th>
              <th>District</th>
              <th>Severity</th>
              <th>Status</th>
            </tr>
          </thead>


          <tbody>

            {filteredPendingCases.map(
              (item) => (

                <tr
                  key={item.case_id}
                  onClick={() =>
                    onSelectCase(item)
                  }
                  className="case-row"
                >

                  <td>
                    #{item.case_id}
                  </td>

                  <td>
                    {item.farmer_name}
                  </td>

                  <td>
                    {item.crop}
                  </td>

                  <td>
                    {item.disease}
                  </td>

                  <td>

                    <span
                      className={
                        item.confidence < 70
                          ? "confidence warning"
                          : "confidence safe"
                      }
                    >
                      {item.confidence}%
                    </span>

                  </td>

                  <td>
                    {item.district}
                  </td>

                  <td>

                    <span
                      className={`severity ${item.severity.toLowerCase()}`}
                    >
                      {item.severity}
                    </span>

                  </td>

                  <td>

                    <span className="status">
                      Pending Expert
                    </span>

                  </td>

                </tr>

              )
            )}


            {filteredPendingCases.length ===
              0 && (

              <tr>

                <td
                  colSpan={8}
                  style={{
                    textAlign:
                      "center",
                    padding:
                      "32px",
                    color:
                      "#64748b",
                  }}
                >
                  No pending expert cases.
                </td>

              </tr>

            )}

          </tbody>

        </table>

      </div>


      {/* =================================================
          AI AUTO-RESOLVED
          BELOW PENDING SECTION
      ================================================= */}

      {autoResolvedCases.length > 0 && (

        <div
          className="table-card"
          style={{
            marginTop:
              "24px",
          }}
        >

          {/* SECTION HEADER */}

          <div
            style={{
              display:
                "flex",
              justifyContent:
                "space-between",
              alignItems:
                "center",
              gap:
                "20px",
              padding:
                "24px",
            }}
          >

            <div>

              <h3
                style={{
                  margin: 0,
                  marginBottom:
                    "6px",
                }}
              >
                AI Auto-Resolved
              </h3>

              <p
                style={{
                  margin: 0,
                  color:
                    "#64748b",
                }}
              >
                Cases with confidence
                of 75% or higher.
                Review and approve
                them before analytics.
              </p>

            </div>


            <button
              type="button"
              onClick={
                handleApproveAll
              }
              disabled={
                autoResolvedCases.length ===
                0
              }
              style={{
                border: "none",
                borderRadius:
                  "10px",
                padding:
                  "12px 24px",
                fontWeight: 700,
                cursor:
                  "pointer",
                background:
                  "#166534",
                color:
                  "#ffffff",
                whiteSpace:
                  "nowrap",
              }}
            >
              Approve All
            </button>

          </div>


          {/* AUTO-RESOLVED TABLE */}

          <table>

            <thead>

              <tr>
                <th>Case ID</th>
                <th>Farmer</th>
                <th>Crop</th>
                <th>Predicted Disease</th>
                <th>Confidence</th>
                <th>District</th>
                <th>Severity</th>
                <th>Status</th>
              </tr>

            </thead>


            <tbody>

              {autoResolvedCases.map(
                (item) => (

                  <tr
                    key={item.case_id}
                    onClick={() =>
                      onSelectCase(item)
                    }
                    className="case-row"
                  >

                    <td>
                      #{item.case_id}
                    </td>

                    <td>
                      {item.farmer_name}
                    </td>

                    <td>
                      {item.crop}
                    </td>

                    <td>
                      {item.disease}
                    </td>

                    <td>

                      <span className="confidence safe">
                        {item.confidence}%
                      </span>

                    </td>

                    <td>
                      {item.district}
                    </td>

                    <td>

                      <span
                        className={`severity ${item.severity.toLowerCase()}`}
                      >
                        {item.severity}
                      </span>

                    </td>

                    <td>

                      <span className="status">
                        AI Auto-Resolved
                      </span>

                    </td>

                  </tr>

                )
              )}

            </tbody>

          </table>

        </div>

      )}

    </div>
  );
}

export default ExpertTriagePage;