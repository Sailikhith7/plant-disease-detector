type Case = {
  case_id: number;
  farmer_name: string;
  crop: string;
  disease: string;
  confidence: number;
  district: string;
  severity: "High" | "Medium" | "Low";
  status: "Pending Expert";
};

const mockCases: Case[] = [
  {
    case_id: 101,
    farmer_name: "Ramesh Patil",
    crop: "Cotton",
    disease: "Pink Bollworm",
    confidence: 56,
    district: "Yavatmal",
    severity: "High",
    status: "Pending Expert",
  },
  {
    case_id: 102,
    farmer_name: "Suresh Shinde",
    crop: "Soybean",
    disease: "Rust",
    confidence: 62,
    district: "Nanded",
    severity: "Medium",
    status: "Pending Expert",
  },
  {
    case_id: 103,
    farmer_name: "Mahesh Jadhav",
    crop: "Onion",
    disease: "Purple Blotch",
    confidence: 43,
    district: "Nashik",
    severity: "High",
    status: "Pending Expert",
  },
  {
    case_id: 104,
    farmer_name: "Ganesh More",
    crop: "Sugarcane",
    disease: "Leaf Spot",
    confidence: 68,
    district: "Kolhapur",
    severity: "Medium",
    status: "Pending Expert",
  },
  {
    case_id: 105,
    farmer_name: "Vijay Pawar",
    crop: "Cotton",
    disease: "Leaf Curl",
    confidence: 51,
    district: "Akola",
    severity: "High",
    status: "Pending Expert",
  },
];

function ExpertTriagePage() {
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
          <strong>{mockCases.length}</strong>
        </div>
      </div>

      <div className="table-card">
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
            {mockCases.map((item) => (
              <tr key={item.case_id}>
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