import { useEffect, useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";

const API = "http://localhost:8000";

function KpiCard({ label, value, accent }) {
  return (
    <div
      style={{
        background: "var(--panel)",
        border: "1px solid var(--border)",
        borderRadius: 14,
        padding: "18px 20px",
        flex: 1,
        minWidth: 160,
      }}
    >
      <div
        style={{
          color: "var(--muted)",
          fontSize: 13,
          textTransform: "uppercase",
          letterSpacing: 0.5,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 34,
          fontWeight: 700,
          marginTop: 6,
          color: accent || "var(--text)",
        }}
      >
        {value}
      </div>
    </div>
  );
}

const STATUS_COLOR = { green: "#2fb86b", yellow: "#f2b94b", red: "#ef4b5b" };
const STATUS_LABEL = {
  green: "Healthy",
  yellow: "Watch",
  red: "Fault predicted",
};
const STATUS_RANK = { green: 0, yellow: 1, red: 2 };

function MachineTile({ name, reading }) {
  const color = STATUS_COLOR[reading.status] || "var(--muted)";
  const fault = reading.status === "red";
  return (
    <div
      style={{
        background: fault ? "rgba(239,75,91,0.08)" : "var(--panel)",
        border: `1.5px solid ${fault ? "var(--red)" : "var(--border)"}`,
        borderRadius: 12,
        padding: 16,
        minWidth: 190,
        boxShadow: fault ? "0 0 18px rgba(239,75,91,0.35)" : "none",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <span
          style={{
            width: 14,
            height: 14,
            borderRadius: "50%",
            background: color,
            display: "inline-block",
          }}
        />
        <span style={{ fontWeight: 600 }}>{name}</span>
      </div>
      <div style={{ marginTop: 10, color, fontWeight: 600, fontSize: 14 }}>
        {STATUS_LABEL[reading.status] || reading.status}
      </div>
      <div
        style={{
          marginTop: 8,
          color: "var(--muted)",
          fontSize: 12,
          lineHeight: 1.6,
        }}
      >
        <div>Tool wear: {reading.tool_wear_min} min</div>
        <div>Torque: {reading.torque_nm} Nm</div>
        <div>Risk: {(reading.score * 100).toFixed(1)}%</div>
      </div>
    </div>
  );
}

function Panel({ title, children }) {
  return (
    <div
      style={{
        background: "var(--panel)",
        border: "1px solid var(--border)",
        borderRadius: 14,
        padding: 20,
        flex: 1,
        minWidth: 320,
      }}
    >
      <h3
        style={{
          margin: "0 0 12px",
          fontSize: 15,
          color: "var(--muted)",
          textTransform: "uppercase",
          letterSpacing: 0.5,
        }}
      >
        {title}
      </h3>
      {children}
    </div>
  );
}

const TYPE_NAME = {
  L: "Line L (Low)",
  M: "Line M (Medium)",
  H: "Line H (High)",
};

function App() {
  const [readings, setReadings] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = () => {
      fetch(`${API}/readings?limit=600`)
        .then((r) => r.json())
        .then(setReadings)
        .catch((e) => setError(e.message));
    };
    load();
    const timer = setInterval(load, 3000);
    return () => clearInterval(timer);
  }, []);

  const counts = { green: 0, yellow: 0, red: 0 };
  readings.forEach((r) => {
    if (r.status in counts) counts[r.status] += 1;
  });
  const total = readings.length;
  const failureRate = total ? ((counts.red / total) * 100).toFixed(1) : "0";

  const worstByType = {};
  readings.forEach((r) => {
    const current = worstByType[r.machine_type];
    const rank = STATUS_RANK[r.status] ?? -1;
    if (!current || rank > (STATUS_RANK[current.status] ?? -1)) {
      worstByType[r.machine_type] = r;
    }
  });

  const pieData = [
    { name: "Healthy", value: counts.green, color: STATUS_COLOR.green },
    { name: "Watch", value: counts.yellow, color: STATUS_COLOR.yellow },
    { name: "Fault", value: counts.red, color: STATUS_COLOR.red },
  ].filter((d) => d.value > 0);

  return (
    <div>
      <header style={{ marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 28 }}>Shop Floor Monitor</h1>
        <p style={{ margin: "4px 0 0", color: "var(--muted)" }}>
          Affordable Predictive Maintenance for Small Machine Shops
        </p>
      </header>

      {error && <p style={{ color: "var(--red)" }}>Error: {error}</p>}

      <div
        style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 32 }}
      >
        <KpiCard label="Readings" value={total} accent="var(--accent)" />
        <KpiCard label="Healthy" value={counts.green} accent="var(--green)" />
        <KpiCard label="Warning" value={counts.yellow} accent="var(--amber)" />
        <KpiCard label="Critical" value={counts.red} accent="var(--red)" />
        <KpiCard
          label="Failure Rate"
          value={`${failureRate}%`}
          accent="var(--red)"
        />
      </div>

      <h2 style={{ fontSize: 18, marginBottom: 14 }}>Machine Floor</h2>
      <div
        style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 32 }}
      >
        {Object.keys(worstByType).map((type) => (
          <MachineTile
            key={type}
            name={TYPE_NAME[type] || type}
            reading={worstByType[type]}
          />
        ))}
      </div>

      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <Panel title="Status Breakdown">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                innerRadius={70}
                outerRadius={100}
                paddingAngle={2}
              >
                {pieData.map((d) => (
                  <Cell key={d.name} fill={d.color} stroke="none" />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "#131c2e",
                  border: "1px solid #243249",
                  borderRadius: 8,
                  color: "#e7eef7",
                }}
              />
              <Legend wrapperStyle={{ color: "#8ea0b8" }} />
            </PieChart>
          </ResponsiveContainer>
        </Panel>
      </div>
    </div>
  );
}

export default App;
