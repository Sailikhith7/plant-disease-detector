import { useMemo, useState } from "react";
import type { MockCase } from "../data/mockCases";
export type Case = MockCase;

type ExpertTriagePageProps = {
  cases: Case[];
  onSelectCase: (caseData: Case) => void;
};

function ExpertTriagePage({
    
  cases,
  onSelectCase,
}: ExpertTriagePageProps) {
    const [search, setSearch] = useState("");
const [cropFilter, setCropFilter] = useState("All");
const [districtFilter, setDistrictFilter] = useState("All");
const [severityFilter, setSeverityFilter] = useState("All");
const [sortOrder, setSortOrder] = useState("low");

const filteredCases = useMemo(() => {
  const result = cases.filter((item) => {
    const searchText = search.toLowerCase();

    const matchesSearch =
      item.farmer_name.toLowerCase().includes(searchText) ||
      item.disease.toLowerCase().includes(searchText) ||
      item.crop.toLowerCase().includes(searchText);

    const matchesCrop =
      cropFilter === "All" || item.crop === cropFilter;

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
      return a.confidence - b.confidence;
    }

    return b.confidence - a.confidence;
  });

  return result;
}, [
  cases,
  search,
  cropFilter,
  districtFilter,
  severityFilter,
  sortOrder,
]);
  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2>KVK Expert Triage</h2>
          <p>
            Review crop cases where AI confidence is below 70%.
          </p>
        </div>

        <div className="pending-card">
          <span>Pending Cases</span>
          <strong>{cases.length}</strong>
        </div>
      </div>

      <div className="table-card">
        <div className="filter-bar">
  <input
    type="text"
    placeholder="Search farmer, crop or disease..."
    value={search}
    onChange={(e) => setSearch(e.target.value)}
  />

  <select
    value={cropFilter}
    onChange={(e) => setCropFilter(e.target.value)}
  >
    <option value="All">All Crops</option>
    <option value="Cotton">Cotton</option>
    <option value="Soybean">Soybean</option>
    <option value="Onion">Onion</option>
    <option value="Sugarcane">Sugarcane</option>
  </select>

  <select
    value={districtFilter}
    onChange={(e) => setDistrictFilter(e.target.value)}
  >
    <option value="All">All Districts</option>
    <option value="Yavatmal">Yavatmal</option>
    <option value="Nanded">Nanded</option>
    <option value="Nashik">Nashik</option>
    <option value="Kolhapur">Kolhapur</option>
    <option value="Akola">Akola</option>
  </select>

  <select
    value={severityFilter}
    onChange={(e) => setSeverityFilter(e.target.value)}
  >
    <option value="All">All Severity</option>
    <option value="High">High</option>
    <option value="Medium">Medium</option>
    <option value="Low">Low</option>
  </select>

  <select
    value={sortOrder}
    onChange={(e) => setSortOrder(e.target.value)}
  >
    <option value="low">Lowest Confidence First</option>
    <option value="high">Highest Confidence First</option>
  </select>
</div>
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
            {filteredCases.map((item) => (
              <tr
  key={item.case_id}
  onClick={() => onSelectCase(item)}
  className="case-row"
>
                <td>#{item.case_id}</td>
                <td>{item.farmer_name}</td>
                <td>{item.crop}</td>
                <td>{item.disease}</td>

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

                <td>{item.district}</td>

                <td>
                  <span className={`severity ${item.severity.toLowerCase()}`}>
                    {item.severity}
                  </span>
                </td>

                <td>
                  <span className="status">{item.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ExpertTriagePage;