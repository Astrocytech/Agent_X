import { useRef, useEffect, useState } from "react";

/* ── Event type normalizer ────────────────────────────── */

function normalizeType(raw) {
  if (!raw) return "";
  const t = String(raw).toLowerCase();
  if (["tool", "tool_call", "tool_use"].includes(t)) return "Tool";
  if (["reasoning", "think", "thinking"].includes(t)) return "Thinking";
  if (t === "error") return "Error";
  if (t === "info") return "Info";
  if (t === "agent") return "Agent";
  if (t === "todo") return "Todo";
  return raw;
}

function formatActivityLabel(event) {
  const label = normalizeType(event.type);
  if (event.status === "running") return label + " Running";
  if (event.status === "completed") return label + " Done";
  if (event.status === "error") return label + " Error";
  return label;
}

/* ── Raw text renderer ───────────────────────────────── */

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

/* ── Badge component ─────────────────────────────────── */

function SubagentBadge({ status }) {
  let label = "Active";
  let cls = "badge-active";
  if (status === "running") { label = "Running"; cls = "badge-running"; }
  else if (status === "completed") { label = "Done"; cls = "badge-done"; }
  else if (status === "error") { label = "Error"; cls = "badge-error"; }
  return <span className={`activity-subagent-badge ${cls}`}>{label}</span>;
}

/* ── Deduplicate subagents ───────────────────────────── */

function mergeEntries(a, b) {
  const merged = { ...a, ...b };
  merged.session_id = b.session_id || a.session_id;
  merged.status = b.status || a.status;
  return merged;
}

function dedupeSubagents(subagents) {
  /*
    Keep distinct rows by session_id.
    Rows without session_id are grouped by name|description (fallback group).
    If a fallback group shares name|description with a session-keyed row,
    merge the fallback into that session row.
    Status resolution: latest event wins inside a merged row.
  */
  const bySession = new Map();
  const fallbackGroups = new Map();

  for (const sa of subagents) {
    if (sa.session_id) {
      const prev = bySession.get(sa.session_id);
      bySession.set(sa.session_id, prev ? mergeEntries(prev, sa) : { ...sa });
    } else {
      const key = `${sa.name || ""}|${sa.description || ""}`;
      const prev = fallbackGroups.get(key);
      fallbackGroups.set(key, prev ? mergeEntries(prev, sa) : { ...sa });
    }
  }

  for (const [fKey, fallback] of fallbackGroups) {
    let merged = false;
    for (const [sId, sessionEntry] of bySession) {
      const sKey = `${sessionEntry.name || ""}|${sessionEntry.description || ""}`;
      if (sKey === fKey) {
        bySession.set(sId, mergeEntries(fallback, sessionEntry));
        merged = true;
        break;
      }
    }
    if (!merged) {
      bySession.set(fKey, fallback);
    }
  }

  return Array.from(bySession.values());
}

/* ── Main component ──────────────────────────────────── */

export default function ActivityPanel({ activities, streaming, subagents, activeSession, onSelectSubagent, hideToolDetails }) {
  const endRef = useRef(null);
  const [logPreferenceSet, setLogPreferenceSet] = useState(() => {
    try { return localStorage.getItem("agentx_log_collapsed") !== null; } catch { return false; }
  });
  const [logCollapsed, setLogCollapsed] = useState(() => {
    try {
      const saved = localStorage.getItem("agentx_log_collapsed");
      if (saved !== null) return saved === "true";
    } catch {
      /* ignore unavailable storage */
    }
    return subagents.length > 0;
  });

  /* Auto-collapse when subagents appear and user hasn't set a preference */
  useEffect(() => {
    if (logPreferenceSet) return;
    let cancelled = false;
    Promise.resolve().then(() => {
      if (!cancelled) setLogCollapsed(subagents.length > 0);
    });
    return () => {
      cancelled = true;
    };
  }, [subagents, logPreferenceSet]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activities, streaming, subagents, activeSession]);

  const done = !streaming && activities.length > 0;

  /* Deduplicate and summarise */
  const uniqueSubagents = dedupeSubagents(subagents);
  const runningCount = uniqueSubagents.filter(s => s.status === "running").length;
  const doneCount = uniqueSubagents.filter(s => s.status === "completed").length;
  const errorCount = uniqueSubagents.filter(s => s.status === "error").length;
  const hasSubagents = uniqueSubagents.length > 0;

  return (
    <div className="activity-panel">
      <div className="activity-header">Activity</div>

      {/* ── Summary bar ──────────────────────────────── */}
      {hasSubagents ? (
        <div className="activity-summary">
          <span className="summary-count running">{runningCount} running</span>
          <span className="summary-sep">·</span>
          <span className="summary-count done">{doneCount} done</span>
          <span className="summary-sep">·</span>
          <span className="summary-count error">{errorCount} errors</span>
        </div>
      ) : streaming ? (
        <div className="activity-summary">
          <span className="summary-count running">1 running</span>
        </div>
      ) : null}

      {/* ── Agents zone ──────────────────────────────── */}
      {hasSubagents && (
        <div className="activity-agents-zone">
          <div className="activity-agents-header">Agents</div>
          <div className="activity-agents-list">
            {uniqueSubagents.map((sa) => {
              const isActive = activeSession === sa.session_id;
              const isRunning = sa.status === "running";
              const isError = sa.status === "error";
              const hasSession = !!sa.session_id;
              return (
                <div
                  key={sa.session_id || `${sa.name}|${sa.description}`}
                  className={`activity-subagent-entry${isActive ? " active" : ""}${!hasSession ? " no-session" : ""}`}
                  onClick={hasSession ? () => onSelectSubagent && onSelectSubagent(sa.session_id) : undefined}
                >
                  <div className="activity-subagent-icon">{isRunning ? "●" : "▶"}</div>
                  <div className="activity-subagent-name">{sa.name || "Subagent"}</div>
                  <div className="activity-subagent-badge-col">
                    <SubagentBadge status={isRunning ? "running" : isError ? "error" : "completed"} />
                  </div>
                  {hasSession && <div className="activity-subagent-chevron">›</div>}
                  {sa.description && (
                    <div className="activity-subagent-desc" title={sa.description}>
                      {sa.description.length > 40 ? sa.description.slice(0, 40) + "..." : sa.description}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Event Log zone (collapsible) ──────────────── */}
      <div className="activity-log-zone">
        <div className="activity-log-header" onClick={() => {
          const next = !logCollapsed;
          setLogCollapsed(next);
          setLogPreferenceSet(true);
          try { localStorage.setItem("agentx_log_collapsed", String(next)); } catch {
            /* ignore unavailable storage */
          }
        }}>
          <span className="activity-log-arrow">{logCollapsed ? "\u25B8" : "\u25BE"}</span>
          Event Log
          <span className="activity-log-count">{activities.length}</span>
        </div>
        {!logCollapsed && (
          <div className="activity-log-body">
            <div className="activity-list">
              {activities.length === 0 ? (
                <div className="activity-empty">Awaiting activity...</div>
              ) : (
                activities.map((a, i) => {
                  if (!a || typeof a !== "object") return null;
                  const isToolRunning = a.type === "tool" && a.status === "running";
                  const isTool = a.type === "tool" || a.type === "tool_call" || a.type === "tool_use";
                  const typeLabel = isToolRunning ? "" : formatActivityLabel(a);
                  const suffix = a.type && typeof a.type === "string" ?
                    (a.type === "tool" ? " activity-tool" : " activity-" + a.type) : "";
                  const raw = renderActivityText(a);
                  const isDiff = looksLikeDiff(raw);
                  const showFull = !hideToolDetails || !isTool;
                  return (
                    <div key={i} className={"activity-entry" + suffix}>
                      <span className="activity-time">{a.time || ""}</span>
                      {!isToolRunning && <span className="activity-type">{String(typeLabel)}</span>}
                      <span className="activity-text">
                        {showFull ? (isDiff ? <DiffBlock text={raw} /> : raw) : (a.tool_name || a.text || "tool")}
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
        )}
      </div>
    </div>
  );
}
