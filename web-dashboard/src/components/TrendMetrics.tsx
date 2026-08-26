import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const diseaseData = [
  { disease: "Pink Bollworm", cases: 12 },
  { disease: "Purple Blotch", cases: 10 },
  { disease: "Rust", cases: 8 },
  { disease: "Leaf Spot", cases: 6 },
  { disease: "Leaf Curl", cases: 4 },
];

const districtData = [
  { district: "Yavatmal", cases: 12 },
  { district: "Nashik", cases: 10 },
  { district: "Nanded", cases: 8 },
  { district: "Kolhapur", cases: 6 },
  { district: "Pune", cases: 4 },
];

const riskData = [
  { name: "High Risk", value: 8 },
  { name: "Medium Risk", value: 14 },
  { name: "Low Risk", value: 8 },
];

const riskColors = ["#ef4444", "#f59e0b", "#22c55e"];

function TrendMetrics() {
  const totalCases = 30;
  const pendingCases = 12;
  const resolvedCases = 18;
  const highRiskCases = 8;

  return (
    <div className="analytics-page">
      <div className="analytics-header">
        <div>
          <h2>Crop Health Analytics</h2>
          <p>
            State-level disease surveillance and case monitoring.
          </p>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <span>Total Cases</span>
          <strong>{totalCases}</strong>
          <small>Reported incidents</small>
        </div>

        <div className="stat-card">
          <span>Pending Expert Review</span>
          <strong>{pendingCases}</strong>
          <small>Require KVK action</small>
        </div>

        <div className="stat-card">
          <span>Resolved Cases</span>
          <strong>{resolvedCases}</strong>
          <small>Expert confirmed</small>
        </div>

        <div className="stat-card">
          <span>High Risk Cases</span>
          <strong>{highRiskCases}</strong>
          <small>Priority surveillance</small>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="chart-card">
          <div className="chart-header">
            <h3>Disease Distribution</h3>
            <p>Reported cases by disease</p>
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={diseaseData}>
                <CartesianGrid strokeDasharray="3 3" />

                <XAxis
                  dataKey="disease"
                  tick={{ fontSize: 11 }}
                  interval={0}
                  angle={-25}
                  textAnchor="end"
                  height={80}
                />

                <YAxis />

                <Tooltip />

                <Bar
                  dataKey="cases"
                  fill="#166534"
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <h3>Risk Distribution</h3>
            <p>Cases grouped by risk level</p>
          </div>

          <div className="chart-container pie-container">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {riskData.map((entry, index) => (
                    <Cell
                      key={entry.name}
                      fill={riskColors[index]}
                    />
                  ))}
                </Pie>

                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card full-width">
          <div className="chart-header">
            <h3>District-wise Disease Cases</h3>
            <p>Reported incidents across monitored districts</p>
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={districtData}>
                <CartesianGrid strokeDasharray="3 3" />

                <XAxis dataKey="district" />

                <YAxis />

                <Tooltip />

                <Bar
                  dataKey="cases"
                  fill="#2563eb"
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TrendMetrics;