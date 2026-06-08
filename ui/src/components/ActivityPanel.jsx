import { useRef, useEffect, useState } from "react";

function renderActivityText(a) {
  const raw = a.text || a.input || a.output || "";
  if (typeof raw === "object" && raw !== null) {
    try { return JSON.stringify(raw, null, 2); } catch { return "[object]"; }
  }
  return String(raw);
}

function looksLikeDiff(text) {
  if (!text) return false;
  const lines = text.split("\n");
  let score = 0;
  for (const line of lines) {
    if (line.startsWith("--- ") || line.startsWith("+++ ")) score += 3;
    else if (line.startsWith("@@") && line.includes("@@")) score += 2;
    else if (line.startsWith("+") || line.startsWith("-")) score += 1;
    if (score >= 4) return true;
  }
  return false;
}

function DiffBlock({ text }) {
  const [open, setOpen] = useState(true);
  const lines = text.split("\n");
  const MAX = 200;
  const truncated = lines.length > MAX;
  const display = truncated && !open ? lines.slice(0, MAX) : lines;

  return (
    <div className="activity-diff">
      <label className="activity-diff-toggle">
        <input type="checkbox" checked={open} onChange={() => setOpen(!open)} />
        {" "}Diff ({lines.length} lines)
      </label>
      {open && (
        <pre className="activity-diff-pre">
          {display.map((line, i) => {
            let cls = "activity-diff-line";
            if (line.startsWith("--- ") || line.startsWith("+++ ")) cls += " activity-diff-file";
            else if (line.startsWith("@@")) cls += " activity-diff-hunk";
            else if (line.startsWith("+")) cls += " activity-diff-add";
            else if (line.startsWith("-")) cls += " activity-diff-rem";
            return (
              <div key={i} className={cls}>{line}</div>
            );
          })}
          {truncated && !open && (
            <div className="activity-diff-trunc">… {lines.length - MAX} more lines</div>
          )}
        </pre>
      )}
    </div>
  );
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
            const raw = renderActivityText(a);
            const isDiff = looksLikeDiff(raw);
            return (
              <div key={i} className={"activity-entry" + suffix}>
                <span className="activity-time">{a.time || ""}</span>
                {!isToolRunning && <span className="activity-type">{String(typeLabel)}</span>}
                <span className="activity-text">
                  {isDiff ? <DiffBlock text={raw} /> : raw}
                </span>
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
