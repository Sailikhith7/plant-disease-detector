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

import type { MockCase } from "../data/mockCases";

type TrendMetricsProps = {
  cases: MockCase[];
  onResolvedClick: () => void;
};

function TrendMetrics({
  cases,
  onResolvedClick,
}: TrendMetricsProps) {
  // =========================================
  // DISEASE DISTRIBUTION
  // ORIGINAL FORMAT
  // =========================================

  const diseaseData = Object.values(
    cases.reduce(
      (acc, item) => {
        if (!acc[item.disease]) {
          acc[item.disease] = {
            disease: item.disease,
            cases: 0,
          };
        }

        acc[item.disease].cases += 1;

        return acc;
      },
      {} as Record<
        string,
        {
          disease: string;
          cases: number;
        }
      >
    )
  );

  // =========================================
  // DISTRICT DATA
  // ONE HORIZONTAL BAR PER DISTRICT
  // BAR SPLIT INTO HIGH / MEDIUM / LOW
  // =========================================

  const districtData = Object.values(
    cases.reduce(
      (acc, item) => {
        if (!acc[item.district]) {
          acc[item.district] = {
            district: item.district,
            High: 0,
            Medium: 0,
            Low: 0,
          };
        }

        if (item.severity === "High") {
          acc[item.district].High += 1;
        }

        if (item.severity === "Medium") {
          acc[item.district].Medium += 1;
        }

        if (item.severity === "Low") {
          acc[item.district].Low += 1;
        }

        return acc;
      },
      {} as Record<
        string,
        {
          district: string;
          High: number;
          Medium: number;
          Low: number;
        }
      >
    )
  );

  // =========================================
  // RISK DISTRIBUTION
  // ORIGINAL FORMAT
  // =========================================

  const riskData = [
    {
      name: "High Risk",
      value: cases.filter(
        (item) => item.severity === "High"
      ).length,
    },
    {
      name: "Medium Risk",
      value: cases.filter(
        (item) => item.severity === "Medium"
      ).length,
    },
    {
      name: "Low Risk",
      value: cases.filter(
        (item) => item.severity === "Low"
      ).length,
    },
  ];

  const riskColors = [
    "#ef4444",
    "#f59e0b",
    "#22c55e",
  ];

  // =========================================
  // SUMMARY COUNTS
  // =========================================

  const totalCases = cases.length;

  const pendingCases = cases.filter(
    (item) => item.status === "Pending Expert"
  ).length;

  const resolvedCases = cases.filter(
    (item) => item.status === "Resolved"
  ).length;

  const highRiskCases = cases.filter(
    (item) => item.severity === "High"
  ).length;

  // =========================================
  // UI
  // =========================================

  return (
    <div className="analytics-page">

      {/* HEADER */}

      <div className="analytics-header">
        <div>
          <h2>Crop Health Analytics</h2>

          <p>
            State-level disease surveillance and case monitoring.
          </p>
        </div>
      </div>

      {/* STAT CARDS */}

      <div className="stat-grid">

        <div className="stat-card">
          <span>Total Cases</span>

          <strong>{totalCases}</strong>

          <small>
            Reported incidents
          </small>
        </div>

        <div className="stat-card">
          <span>Pending Expert Review</span>

          <strong>{pendingCases}</strong>

          <small>
            Require KVK action
          </small>
        </div>

        <div
          className="stat-card clickable-stat"
          onClick={onResolvedClick}
        >
          <span>Resolved Cases</span>

          <strong>{resolvedCases}</strong>

          <small>
            Expert confirmed · Click to view records
          </small>
        </div>

        <div className="stat-card">
          <span>High Risk Cases</span>

          <strong>{highRiskCases}</strong>

          <small>
            Priority surveillance
          </small>
        </div>

      </div>

      {/* MAIN ANALYTICS */}

      <div className="analytics-grid">

        {/* =====================================
            DISEASE DISTRIBUTION
            ORIGINAL
        ====================================== */}

        <div className="chart-card">

          <div className="chart-header">

            <h3>
              Disease Distribution
            </h3>

            <p>
              Reported cases by disease
            </p>

          </div>

          <div className="chart-container">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <BarChart data={diseaseData}>

                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis
                  dataKey="disease"
                  tick={{ fontSize: 11 }}
                  interval={0}
                  angle={-25}
                  textAnchor="end"
                  height={80}
                />

                <YAxis
                  allowDecimals={false}
                />

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

        {/* =====================================
            RISK DISTRIBUTION
            ORIGINAL
        ====================================== */}

        <div className="chart-card">

          <div className="chart-header">

            <h3>
              Risk Distribution
            </h3>

            <p>
              Cases grouped by risk level
            </p>

          </div>

          <div className="chart-container pie-container">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

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

                  {riskData.map(
                    (entry, index) => (
                      <Cell
                        key={entry.name}
                        fill={riskColors[index]}
                      />
                    )
                  )}

                </Pie>

                <Tooltip />

                <Legend />

              </PieChart>

            </ResponsiveContainer>

          </div>
        </div>

        {/* =====================================
            DISTRICT-WISE CASES
            HORIZONTAL STACKED BAR
        ====================================== */}

        <div className="chart-card full-width">

          <div className="chart-header">

            <h3>
              District-wise Disease Cases
            </h3>

            <p>
              One bar per district, divided by severity
            </p>

          </div>

          <div
            className="chart-container"
            style={{ height: 420 }}
          >

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <BarChart
  data={districtData}
  margin={{
    top: 10,
    right: 30,
    left: 10,
    bottom: 20,
  }}
>

                <CartesianGrid
                  strokeDasharray="3 3"
                />

                {/* CASE COUNT ON X-AXIS */}
                <XAxis
  dataKey="district"
  interval={0}
  tick={{ fontSize: 12 }}
/>

<YAxis
  allowDecimals={false}
/>

                <Tooltip />

                <Legend />

                {/* ONE HORIZONTAL STACK */}

                <Bar
                  dataKey="High"
                  stackId="severity"
                  fill="#ef4444"
                  name="High"
                />

                <Bar
                  dataKey="Medium"
                  stackId="severity"
                  fill="#f59e0b"
                  name="Medium"
                />

                <Bar
                  dataKey="Low"
                  stackId="severity"
                  fill="#22c55e"
                  name="Low"
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