import { useRef, useEffect } from "react";

function renderActivityText(a) {
  const raw = a.text || a.input || a.output || "";
  if (typeof raw === "object" && raw !== null) {
    try { return JSON.stringify(raw, null, 2); } catch { return "[object]"; }
  }
  return String(raw);
}

export default function ActivityPanel({ activities, streaming }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activities, streaming]);

  const done = !streaming && activities.length > 0;

  return (
    <div className="activity-panel">
      <div className="activity-header">Activity</div>
      <div className="activity-list">
        {activities.length === 0 ? (
          <div className="activity-empty">Awaiting activity...</div>
        ) : (
          activities.map((a, i) => {
            if (!a || typeof a !== "object") return null;
            const isToolRunning = a.type === "tool" && a.status === "running";
            const typeLabel = isToolRunning ? "" : a.type || "";
            const suffix = a.type && typeof a.type === "string" ? (a.type === "tool" ? " activity-tool" : " activity-" + a.type) : "";
            return (
              <div key={i} className={"activity-entry" + suffix}>
                <span className="activity-time">{a.time || ""}</span>
                {!isToolRunning && <span className="activity-type">{String(typeLabel)}</span>}
                <span className="activity-text">{renderActivityText(a)}</span>
              </div>
            );
          })
        )}
        {done && (
          <div className="activity-entry activity-done">
            <span className="activity-time" />
            <span className="activity-type activity-type-done">Finished</span>
            <span className="activity-text">All tasks complete.</span>
          </div>
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}
