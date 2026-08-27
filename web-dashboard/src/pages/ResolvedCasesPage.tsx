import { useMemo, useState } from "react";
import type { MockCase } from "../data/mockCases";

type ResolvedCasesPageProps = {
  cases: MockCase[];
  onBack: () => void;
};

function ResolvedCasesPage({
  cases,
  onBack,
}: ResolvedCasesPageProps) {
  const [search, setSearch] = useState("");
  const [cropFilter, setCropFilter] = useState("All");
  const [districtFilter, setDistrictFilter] =
    useState("All");
  const [diseaseFilter, setDiseaseFilter] =
    useState("All");

  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const [selectedCase, setSelectedCase] =
    useState<MockCase | null>(null);

  const resolvedCases = useMemo(() => {
    return cases.filter((item) => {
      // Only RESOLVED cases
      if (item.status !== "Resolved") {
        return false;
      }

      const searchText = search.toLowerCase();

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

      const matchesDisease =
        diseaseFilter === "All" ||
        item.disease === diseaseFilter;

      const matchesFromDate =
        !fromDate ||
        (item.resolution_date &&
          item.resolution_date >= fromDate);

      const matchesToDate =
        !toDate ||
        (item.resolution_date &&
          item.resolution_date <= toDate);

      return (
        matchesSearch &&
        matchesCrop &&
        matchesDistrict &&
        matchesDisease &&
        matchesFromDate &&
        matchesToDate
      );
    });
  }, [
    cases,
    search,
    cropFilter,
    districtFilter,
    diseaseFilter,
    fromDate,
    toDate,
  ]);

  return (
    <div className="resolved-page">

      {/* HEADER */}
      <div className="resolved-header">

        <div>
          <button
            className="back-button"
            onClick={onBack}
          >
            ← Back to Analytics
          </button>

          <h2>Resolved Case Records</h2>

          <p>
            Review expert-confirmed crop health
            cases and their resolution history.
          </p>
        </div>

        <div className="resolved-count-card">
          <span>Resolved Cases</span>
          <strong>
            {resolvedCases.length}
          </strong>
        </div>

      </div>

      {/* MAIN CARD */}
      <div className="resolved-card">

        {/* FILTERS */}
        <div className="resolved-filters">

          <input
            type="text"
            placeholder="Search farmer, crop or disease..."
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
          />

          <select
            value={cropFilter}
            onChange={(e) =>
              setCropFilter(e.target.value)
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
          </select>

          <select
            value={districtFilter}
            onChange={(e) =>
              setDistrictFilter(e.target.value)
            }
          >
            <option value="All">
              All Districts
            </option>

            <option value="Amravati">
              Amravati
            </option>

            <option value="Latur">
              Latur
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
          </select>

          <select
            value={diseaseFilter}
            onChange={(e) =>
              setDiseaseFilter(e.target.value)
            }
          >
            <option value="All">
              All Diseases
            </option>

            <option value="Pink Bollworm">
              Pink Bollworm
            </option>

            <option value="Rust">
              Rust
            </option>

            <option value="Purple Blotch">
              Purple Blotch
            </option>

            <option value="Leaf Spot">
              Leaf Spot
            </option>

            <option value="Leaf Curl">
              Leaf Curl
            </option>
          </select>

          <div className="date-filter">
            <label>From Date</label>

            <input
              type="date"
              value={fromDate}
              onChange={(e) =>
                setFromDate(e.target.value)
              }
            />
          </div>

          <div className="date-filter">
            <label>To Date</label>

            <input
              type="date"
              value={toDate}
              onChange={(e) =>
                setToDate(e.target.value)
              }
            />
          </div>

        </div>

        {/* RESET FILTERS */}
        <button
          className="clear-filters"
          onClick={() => {
            setSearch("");
            setCropFilter("All");
            setDistrictFilter("All");
            setDiseaseFilter("All");
            setFromDate("");
            setToDate("");
          }}
        >
          Clear Filters
        </button>

        {/* DETAIL VIEW */}
        {selectedCase ? (
          <div className="resolved-detail">

            <button
              className="back-button"
              onClick={() =>
                setSelectedCase(null)
              }
            >
              ← Back to resolved cases
            </button>

            <h3>
              Case #{selectedCase.case_id}
            </h3>

            <div className="resolved-detail-grid">

              <div>
                <span>Farmer</span>
                <strong>
                  {selectedCase.farmer_name}
                </strong>
              </div>

              <div>
                <span>Crop</span>
                <strong>
                  {selectedCase.crop}
                </strong>
              </div>

              <div>
                <span>Disease</span>
                <strong>
                  {selectedCase.disease}
                </strong>
              </div>

              <div>
                <span>District</span>
                <strong>
                  {selectedCase.district}
                </strong>
              </div>

              <div>
                <span>AI Confidence</span>
                <strong>
                  {selectedCase.confidence}%
                </strong>
              </div>

              <div>
                <span>Severity</span>
                <strong>
                  {selectedCase.severity}
                </strong>
              </div>

              <div>
                <span>Status</span>
                <strong>Resolved</strong>
              </div>

              <div>
                <span>Resolved On</span>
                <strong>
                  {selectedCase.resolution_date
                    ? new Date(
                        selectedCase.resolution_date
                      ).toLocaleDateString(
                        "en-IN",
                        {
                          day: "2-digit",
                          month: "short",
                          year: "numeric",
                        }
                      )
                    : "Not available"}
                </strong>
              </div>

            </div>

            <div className="resolution-section">
              <h4>Expert Diagnosis</h4>

              <p>
                {selectedCase.expert_diagnosis ||
                  "No diagnosis recorded."}
              </p>
            </div>

            <div className="resolution-section">
              <h4>
                Advisory / Prescription
              </h4>

              <p>
                {selectedCase.prescription ||
                  "No prescription recorded."}
              </p>
            </div>

          </div>
        ) : (
          /* TABLE */
          <div className="resolved-table-wrapper">

            <table>

              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Farmer</th>
                  <th>Crop</th>
                  <th>Disease</th>
                  <th>District</th>
                  <th>Confidence</th>
                  <th>Resolved On</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>

                {resolvedCases.map(
                  (item) => (
                    <tr
                      key={item.case_id}
                      className="resolved-row"
                      onClick={() =>
                        setSelectedCase(item)
                      }
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
                        {item.district}
                      </td>

                      <td>
                        {item.confidence}%
                      </td>

                      <td>
                        {item.resolution_date
                          ? new Date(
                              item.resolution_date
                            ).toLocaleDateString(
                              "en-IN",
                              {
                                day: "2-digit",
                                month: "short",
                                year: "numeric",
                              }
                            )
                          : "-"}
                      </td>

                      <td>
                        <span className="status resolved-status">
                          Resolved
                        </span>
                      </td>

                    </tr>
                  )
                )}

              </tbody>

            </table>

            {resolvedCases.length === 0 && (
              <div className="empty-state">
                No resolved cases match
                your filters.
              </div>
            )}

          </div>
        )}

      </div>
    </div>
  );
}

export default ResolvedCasesPage;