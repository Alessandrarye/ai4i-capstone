import { useEffect, useState } from "react";

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

const STATUS_COLOR = {
  green: "var(--green)",
  yellow: "var(--amber)",
  red: "var(--red)",
};
const STATUS_LABEL = {
  green: "Healthy",
  yellow: "Watch",
  red: "Fault predicted",
};

function MachineTile({ name, reading }) {
  const color = STATUS_COLOR[reading.status] || "var(--muted)";
  const fault = reading.status === "red";
  return (
    <div
      style={{
        background: "var(--panel)",
        border: `1.5px solid ${fault ? "var(--red)" : "var(--border)"}`,
        borderRadius: 12,
        padding: 16,
        minWidth: 190,
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

const TYPE_NAME = {
  L: "Line L (Low)",
  M: "Line M (Medium)",
  H: "Line H (High)",
};

function App() {
  const [readings, setReadings] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API}/readings?limit=600`)
      .then((r) => r.json())
      .then(setReadings)
      .catch((e) => setError(e.message));
  }, []);

  const counts = { green: 0, yellow: 0, red: 0 };
  readings.forEach((r) => {
    if (r.status in counts) counts[r.status] += 1;
  });
  const total = readings.length;
  const failureRate = total ? ((counts.red / total) * 100).toFixed(1) : "0";

  // latest reading per machine type (readings come newest-first)
  const latestByType = {};
  readings.forEach((r) => {
    if (!latestByType[r.machine_type]) latestByType[r.machine_type] = r;
  });

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
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        {Object.keys(latestByType).map((type) => (
          <MachineTile
            key={type}
            name={TYPE_NAME[type] || type}
            reading={latestByType[type]}
          />
        ))}
      </div>
    </div>
  );
}

export default App;
