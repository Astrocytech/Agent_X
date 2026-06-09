import React, { useState, useRef, useEffect, useCallback } from "react";
import "./App.css";
import ActivityPanel from "./components/ActivityPanel";
import QuestionBlock from "./components/QuestionBlock";
import PermissionBlock from "./components/PermissionBlock";
import AgentModeModal from "./components/AgentModeModal";
import FicPickerModal from "./components/FicPickerModal";
import GovernanceBanner from "./components/GovernanceBanner";
import SuggestionQuestions from "./components/SuggestionQuestions";

/* ------------------------------------------------------------------ */
/*  Menu data                                                          */
/* ------------------------------------------------------------------ */

const MENUS = {
  Session: [
    { label: "New Session", shortcut: "Ctrl+X N", id: "newSession" },
    null,
    { label: "Open Session...", shortcut: "Ctrl+O", id: "openSession" },
    null,
    { label: "Import Session", id: "importSession" },
    { label: "Export Session", id: "exportSession" },
    null,
    { label: "Jump to Message", shortcut: "Ctrl+X G", id: "jumpToMessage" },
    { label: "Undo Previous Message", shortcut: "Ctrl+Z", id: "undoMessage" },
    null,
    { label: "Hide Sidebar", shortcut: "Ctrl+X B", id: "hideSidebar" },
    { label: "Show Timestamps", id: "showTimestamps" },
    { label: "Collapse Thinking", id: "collapseThinking" },
    { label: "Hide Tool Details", id: "hideToolDetails" },
    null,
    { label: "Copy Last Assistant Message", shortcut: "Ctrl+X Y", id: "copyLastMessage" },
    { label: "Copy Session Transcript", id: "copyTranscript" },
  ],
  Agent: [
    { label: "Switch Model", shortcut: "Ctrl+X M", id: "switchModel" },
    null,
    { label: "Set Mode...", id: "setAgentMode" },
    { label: "Change FIC...", id: "changeFic" },
  ],
  System: [
    { label: "View Status", shortcut: "Ctrl+X S", id: "viewStatus" },
    { label: "Switch Theme", shortcut: "Ctrl+X T", id: "switchTheme" },
    null,
    { label: "Open Docs", id: "openDocs" },
  ],
  Help: [{ label: "About", id: "about" }],
};

const MENU_ORDER = [
  "Session",
  "Agent",
  "System",
  "Help",
];

/* ------------------------------------------------------------------ */
/*  Markdown → HTML (minimal)                                          */
/* ------------------------------------------------------------------ */

function joinText(existing, incoming) {
  if (!incoming) return existing || "";
  if (!existing) return incoming;
  const last = existing[existing.length - 1];
  if (".!?".includes(last) && incoming[0] !== " ") {
    return existing + " " + incoming;
  }
  return existing + incoming;
}

function mdToHtml(text) {
  if (!text) return "";
  const escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  const withCode = escaped.replace(
    /```(\w*)\n([\s\S]*?)```/g,
    (_, lang, code) => `<pre><code class="lang-${lang}">${code.trim()}</code></pre>`
  );
  const withInline = withCode.replace(
    /`([^`]+)`/g,
    "<code>$1</code>"
  );
  const paragraphs = withInline
    .split(/\n\n+/)
    .map((p) => `<p>${p.replace(/\n/g, "<br>")}</p>`)
    .join("");
  return paragraphs;
}

/* ------------------------------------------------------------------ */
/*  Icon components                                                    */
/* ------------------------------------------------------------------ */

const IconOpen = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
  </svg>
);

const IconRename = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
  </svg>
);

const IconDelete = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6"/>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
    <line x1="10" y1="11" x2="10" y2="17"/>
    <line x1="14" y1="11" x2="14" y2="17"/>
  </svg>
);

/* ------------------------------------------------------------------ */
/*  Session list modal                                                 */
/* ------------------------------------------------------------------ */

function SessionModal({ open, onClose, onSelect, onStatusRefresh }) {
  const [sessions, setSessions] = useState([]);
  const [confirm, setConfirm] = useState(null);
  const [editing, setEditing] = useState(null);
  const [editValue, setEditValue] = useState("");

  const fetchSessions = useCallback(() => {
    fetch("/api/sessions")
      .then((r) => r.json())
      .then(setSessions)
      .catch(() => setSessions([]));
  }, []);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    Promise.resolve().then(() => {
      if (cancelled) return;
      setConfirm(null);
      setEditing(null);
    });
    fetchSessions();
    return () => {
      cancelled = true;
    };
  }, [open, fetchSessions]);

  const handleDelete = (runId) => {
    setConfirm({ type: "delete", runId });
  };

  const confirmDelete = () => {
    if (!confirm || confirm.type !== "delete") return;
    fetch(`/api/sessions/${confirm.runId}`, { method: "DELETE" })
      .then(() => { setConfirm(null); fetchSessions(); })
      .catch(() => setConfirm(null));
  };

  const handleClearAll = () => {
    setConfirm({ type: "clearAll", step: 1 });
  };

  const confirmClearAll = () => {
    if (!confirm || confirm.type !== "clearAll") return;
    if (confirm.step === 1) {
      setConfirm({ type: "clearAll", step: 2 });
    } else {
      fetch("/api/sessions", { method: "DELETE" })
        .then(() => { setConfirm(null); fetchSessions(); })
        .catch(() => setConfirm(null));
    }
  };

  const cancelConfirm = () => setConfirm(null);

  const startRename = (s) => {
    setEditing(s.run_id);
    setEditValue(s.session_name || "");
  };

  const saveRename = (runId) => {
    const name = editValue.trim();
    if (!name) { setEditing(null); return; }
    fetch(`/api/sessions/${runId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_name: name }),
    })
      .then(() => { setEditing(null); fetchSessions(); if (onStatusRefresh) onStatusRefresh(); })
      .catch(() => setEditing(null));
  };

  const handleRenameKey = (e, runId) => {
    if (e.key === "Enter") saveRename(runId);
    if (e.key === "Escape") setEditing(null);
  };

  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span>Open Session</span>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
        {sessions.length === 0 ? (
          <p style={{ padding: 16, color: "#888" }}>No previous sessions found.</p>
        ) : (
          <table className="session-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Session Name</th>
                <th>Session ID</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s) => (
                <tr key={s.run_id} className="session-row">
                  <td>{s.date}</td>
                  <td className="session-name-cell">
                    {editing === s.run_id ? (
                      <input
                        className="rename-input"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onBlur={() => saveRename(s.run_id)}
                        onKeyDown={(e) => handleRenameKey(e, s.run_id)}
                        autoFocus
                      />
                    ) : (
                      <span className="session-name-text">{s.session_name}</span>
                    )}
                  </td>
                  <td className="session-id-cell">{s.short_id || ""}</td>
                  <td className="session-actions">
                    <button className="btn btn-icon btn-open" title="Open session" onClick={() => { onSelect(s); onClose(); }}><IconOpen /></button>
                    <button className="btn btn-icon btn-rename" title="Rename session" onClick={() => startRename(s)}><IconRename /></button>
                    <button className="btn btn-icon btn-delete" title="Delete session" onClick={() => handleDelete(s.run_id)}><IconDelete /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        </div>
        <div className="modal-footer">
          {sessions.length > 0 && (
            <button className="btn btn-clear" onClick={handleClearAll}>Clear All</button>
          )}
          <button className="btn" onClick={onClose}>Cancel</button>
        </div>
      </div>

      {confirm && (
        <div className="confirm-overlay" onClick={cancelConfirm}>
          <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
            {confirm.type === "delete" && (
              <>
                <p>Delete this session?</p>
                <div className="confirm-actions">
                  <button className="btn btn-delete" onClick={confirmDelete}>Delete</button>
                  <button className="btn" onClick={cancelConfirm}>Cancel</button>
                </div>
              </>
            )}
            {confirm.type === "clearAll" && confirm.step === 1 && (
              <>
                <p>Clear all sessions? This cannot be undone.</p>
                <div className="confirm-actions">
                  <button className="btn btn-delete" onClick={confirmClearAll}>Yes, clear all</button>
                  <button className="btn" onClick={cancelConfirm}>Cancel</button>
                </div>
              </>
            )}
            {confirm.type === "clearAll" && confirm.step === 2 && (
              <>
                <p>Are you absolutely sure? All sessions will be permanently deleted.</p>
                <div className="confirm-actions">
                  <button className="btn btn-delete" onClick={confirmClearAll}>Yes, delete everything</button>
                  <button className="btn" onClick={cancelConfirm}>Cancel</button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  About modal                                                        */
/* ------------------------------------------------------------------ */

function AboutModal({ open, onClose }) {
  if (!open) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-sm" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">About Agent_X Chat</div>
        <div style={{ padding: "16px 20px", lineHeight: 1.8 }}>
          <p><strong>Agent_X Chat</strong></p>
          <p>An interactive AI chat interface.</p>
        </div>
        <div className="modal-footer">
          <button className="btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function StatusModal({ open, onClose, statusInfo }) {
  if (!open) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-sm" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">Status</div>
        <div style={{ padding: "16px 20px", lineHeight: 1.8 }}>
          <div className="status-row"><span className="status-label">Provider</span><span className="status-value" style={{ marginTop: 2 }}>{statusInfo.provider || "—"}</span></div>
          <div className="status-row" style={{ marginTop: 10 }}><span className="status-label">Model</span><span className="status-value" style={{ marginTop: 2 }}>{statusInfo.model || "—"}</span></div>
          <div className="status-row" style={{ marginTop: 10 }}><span className="status-label">Session ID</span><span className="status-value" style={{ marginTop: 2 }}>{statusInfo.session_id || "—"}</span></div>
          <div className="status-row" style={{ marginTop: 10 }}><span className="status-label">Session Name</span><span className="status-value" style={{ marginTop: 2 }}>{statusInfo.session_name || "—"}</span></div>
        </div>
        <div className="modal-footer">
          <button className="btn" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}

function ModelModal({ open, onClose, currentModel, currentProvider, onSwitch }) {
  const [models, setModels] = useState([]);
  const [search, setSearch] = useState("");
  const [switching, setSwitching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [modelInput, setModelInput] = useState("");

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    Promise.resolve().then(() => {
      if (cancelled) return;
      setSearch("");
      setModelInput("");
      setLoading(true);
    });
    fetch("/api/models")
      .then((r) => r.json())
      .then((data) => {
        if (!cancelled) setModels(data.models || []);
      })
      .catch(() => {
        if (!cancelled) setModels([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [open]);

  const filtered = search
    ? models.filter((m) =>
        `${m.provider}/${m.id}`.toLowerCase().includes(search.toLowerCase()) ||
        m.name?.toLowerCase().includes(search.toLowerCase())
      )
    : models;

  const grouped = {};
  for (const m of filtered) {
    if (!grouped[m.provider]) grouped[m.provider] = [];
    grouped[m.provider].push(m);
  }

  const isCurrent = (m) => m.id === currentModel && m.provider === currentProvider;

  if (!open) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span>Switch Model</span>
          <span className="modal-subtitle">{currentProvider || "—"} / {currentModel || "—"}</span>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div style={{ padding: "8px 12px", borderBottom: "1px solid #e0e2e6" }}>
          <input
            className="chat-name-input" style={{ width: "100%" }}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search models..."
            autoFocus
          />
        </div>
        <div className="modal-body model-list-body">
          {loading ? (
            <p style={{ padding: 16, color: "#888" }}>Loading models...</p>
          ) : Object.keys(grouped).length === 0 ? (
            <p style={{ padding: 16, color: "#888" }}>No models found.</p>
          ) : (
            Object.entries(grouped).map(([provider, ms]) => (
              <div key={provider}>
                <div className="model-group-header">{provider}</div>
                {ms.map((m) => (
                  <div
                    key={`${m.provider}/${m.id}`}
                    className={`model-row${isCurrent(m) ? " active" : ""}`}
                    onClick={() => {
                      if (!isCurrent(m) && !switching) onSwitch(m.id, m.provider, setSwitching, onClose);
                    }}
                  >
                    <span className="model-name">{m.name || m.id}</span>
                    <span className="model-id">{m.id}</span>
                    {isCurrent(m) && <span className="model-check">&#10003;</span>}
                  </div>
                ))}
              </div>
            ))
          )}
        </div>
        <div className="modal-footer" style={{ flexDirection: "column", gap: 8 }}>
          <div style={{ display: "flex", gap: 8, width: "100%" }}>
            <input
              className="chat-name-input" style={{ flex: 1 }}
              value={modelInput}
              onChange={(e) => setModelInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") onSwitch(modelInput, "", setSwitching, onClose); }}
              disabled={switching}
              placeholder="Or type a custom model ID..."
            />
            <button className="btn" style={{ background: "#4a6fa5", color: "#fff", borderColor: "#4a6fa5", whiteSpace: "nowrap" }} onClick={() => onSwitch(modelInput, "", setSwitching, onClose)} disabled={switching || !modelInput.trim()}>
              {switching ? "Switching..." : "Switch"}
            </button>
          </div>
          <button className="btn" onClick={onClose} disabled={switching} style={{ width: "100%" }}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function TimelineModal({ open, onClose, messages, onJump }) {
  if (!open) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span>Jump to Message</span>
          <span className="modal-subtitle">{messages.length} messages</span>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body timeline-body">
          {messages.length === 0 ? (
            <p style={{ padding: 16, color: "#888" }}>No messages.</p>
          ) : (
            <table className="session-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Role</th>
                  <th>Message</th>
                </tr>
              </thead>
              <tbody>
                {messages.map((m, i) => (
                  <tr key={i} className="timeline-row" onClick={() => { onJump(i); onClose(); }}>
                    <td className="timeline-num">{i + 1}</td>
                    <td><span className={`tl-role tl-role-${m.role}`}>{m.role}</span></td>
                    <td className="timeline-text">{(m.text || "").slice(0, 120)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn" onClick={onClose}>Cancel</button>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Message bubble                                                     */
/* ------------------------------------------------------------------ */

function formatTimestamp(ts) {
  if (!ts) return "";
  try {
    const d = new Date(ts);
    const now = new Date();
    const isToday = d.toDateString() === now.toDateString();
    const time = d.toLocaleTimeString(undefined, { timeStyle: "short" });
    if (isToday) return time;
    return `${time} · ${d.toLocaleDateString()}`;
  } catch { return ""; }
}

function Message({ role, text, index, reasoning, timestamp, showTimestamps, thinkingMode, questionData, permissionData, onQuestionReply, onQuestionReject, onPermissionReply, mode }) {
  const html = mdToHtml(text);
  const isUser = role === "user";
  return (
    <div className={`msg msg-${role}`} data-message-index={index}>
      <div className={`msg-label msg-label-${role}`}>
        {isUser ? "You" : "Assistant"}
        {showTimestamps && timestamp && (
          <span className="msg-timestamp"> · {formatTimestamp(timestamp)}</span>
        )}
      </div>
      {reasoning && thinkingMode === "show" && (
        <details className="thinking-block" open>
          <summary className="thinking-summary">Thinking</summary>
          <div className="thinking-body" dangerouslySetInnerHTML={{ __html: mdToHtml(reasoning) }} />
        </details>
      )}
      <div className="msg-body" dangerouslySetInnerHTML={{ __html: html }} />
      {questionData && !questionData.answered && (
        <QuestionBlock
          questions={questionData.questions}
          onReply={(answers) => onQuestionReply(answers)}
          onReject={onQuestionReject}
        />
      )}
      {questionData && questionData.answered && (
        <div className="question-block answered">
          {questionData.questions.map((q, i) => (
            <div key={q.id || i} className="question-item">
              <div className="question-text">{q.text}</div>
              <div className="question-answer-summary">
                {questionData.answers && questionData.answers[i] && questionData.answers[i].length > 0
                  ? questionData.answers[i].map((a) => <span key={a} className="answer-chip">{a}</span>)
                  : <span className="answer-skipped">(skipped)</span>}
              </div>
            </div>
          ))}
        </div>
      )}
      {permissionData && !permissionData.resolved && (
        <PermissionBlock
          action={permissionData.action}
          resources={permissionData.resources}
          metadata={permissionData.metadata}
          save={permissionData.save}
          onReply={(reply, message) => onPermissionReply(permissionData.requestId, reply, message)}
          planMode={mode === "plan"}
        />
      )}
      {permissionData && permissionData.resolved && (
        <div className="permission-block resolved">
          <div className="perm-resolved-label">
            {permissionData.resolution === "once" ? "Allowed once" : permissionData.resolution === "always" ? "Always allowed" : "Rejected"}{permissionData.message ? ": " + permissionData.message : ""}
          </div>
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main App                                                           */
/* ------------------------------------------------------------------ */

/* ── Error boundary ───────────────────────────────────────────── */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }
  static getDerivedStateFromError(error) {
    console.error("ErrorBoundary caught:", error);
    return { error };
  }
  render() {
    if (this.state.error) {
      const msg = (this.state.error && (this.state.error.message || this.state.error.stack || String(this.state.error))) || "Unknown error";
      return React.createElement("div", { style: { padding: 20, color: "#c00", fontFamily: "monospace", whiteSpace: "pre-wrap" } },
        "Render error: " + msg
      );
    }
    return this.props.children;
  }
}

/* ── localStorage helpers ────────────────────────────────────── */
const STORAGE_KEY = "agentx_chat_state";
function saveState(messages, activities) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ messages, activities }));
  } catch {
    /* ignore storage quota/privacy failures */
  }
}
function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && Array.isArray(parsed.messages) && Array.isArray(parsed.activities)) {
        return parsed;
      }
    }
  } catch {
    /* ignore malformed or unavailable storage */
  }
  return null;
}

export default function App() {
  const [messages, setMessages] = useState(() => {
    const saved = loadState();
    return saved ? saved.messages : [];
  });
  const [streaming, setStreaming] = useState(false);
  const [input, setInput] = useState("");
  const [historyIndex, setHistoryIndex] = useState(null);
  const [draftInput, setDraftInput] = useState("");
  const [openMenu, setOpenMenu] = useState(null);
  const [showSessionModal, setShowSessionModal] = useState(false);
  const [showTimeline, setShowTimeline] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const menuRef = useRef(null);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const abortRef = useRef(null);
  const cancelledRef = useRef(false);
  const [activities, setActivities] = useState(() => {
    const saved = loadState();
    return saved ? saved.activities : [];
  });
  const [statusInfo, setStatusInfo] = useState({ model: "", session_id: "", provider: "", session_name: "" });
  const [loadedSessionId, setLoadedSessionId] = useState(null);
  const [editingName, setEditingName] = useState(false);
  const nameInputRef = useRef(null);
  const importFileRef = useRef(null);

  /* resizable activity panel width */
  const [subagents, setSubagents] = useState([]);
  const [activeSubagentId, setActiveSubagentId] = useState(null);
  const [subagentMessages, setSubagentMessages] = useState(null);

  const [activityWidth, setActivityWidth] = useState(() => {
    try {
      const saved = localStorage.getItem("agentx_activity_width");
      return saved ? parseInt(saved, 10) : 420;
    } catch { return 420; }
  });
  const [dragging, setDragging] = useState(false);
  const dragStartX = useRef(0);
  const dragStartWidth = useRef(0);

  /* resizable chat input height */
  const [inputHeight, setInputHeight] = useState(() => {
    try {
      const saved = localStorage.getItem("agentx_input_height");
      const parsed = saved ? parseInt(saved, 10) : 160;
      return Math.max(80, Math.min(600, parsed));
    } catch { return 160; }
  });
  const [inputDragging, setInputDragging] = useState(false);
  const inputDragStartY = useRef(0);
  const inputDragStartHeight = useRef(0);

  const [hideToolDetails, setHideToolDetails] = useState(() => {
    const v = localStorage.getItem("agentx_tool_details");
    return v !== null ? v === "true" : true;
  });
  const [showTimestamps, setShowTimestamps] = useState(() => localStorage.getItem("agentx_timestamps") === "show");
  const [thinkingMode, setThinkingMode] = useState(() => localStorage.getItem("agentx_thinking_mode") || "hide");
  const [sidebarPref, setSidebarPref] = useState(() => localStorage.getItem("agentx_sidebar") || "auto");
  const [theme, setTheme] = useState(() => localStorage.getItem("agentx_theme") || "light");
  const [mode, setMode] = useState(() => localStorage.getItem("agentx_mode") || "build");
  const [questionRequest, setQuestionRequest] = useState(null);
  const [pendingPermissions, setPendingPermissions] = useState([]);
  const [todos, setTodos] = useState([]);
  const [showStatus, setShowStatus] = useState(false);
  const [showModelModal, setShowModelModal] = useState(false);
  const [agentMode, setAgentMode] = useState("general");
  const [ficDocument, setFicDocument] = useState("");
  const [governanceInfo, setGovernanceInfo] = useState(null);
  const [showAgentModeModal, setShowAgentModeModal] = useState(false);
  const [showFicPicker, setShowFicPicker] = useState(false);
  const leaderRef = useRef(null);

  const sidebarVisible = sidebarPref === "auto";

  useEffect(() => {
    document.body.setAttribute("data-theme", theme);
  }, [theme]);

  const onHandleMouseDown = useCallback((e) => {
    e.preventDefault();
    setDragging(true);
    dragStartX.current = e.clientX;
    dragStartWidth.current = activityWidth;
  }, [activityWidth]);

  const onInputHandleMouseDown = useCallback((e) => {
    e.preventDefault();
    setInputDragging(true);
    inputDragStartY.current = e.clientY;
    inputDragStartHeight.current = inputHeight;
  }, [inputHeight]);

  useEffect(() => {
    if (!dragging) return;
    document.body.style.userSelect = "none";
    const onMove = (e) => {
      const newWidth = dragStartWidth.current - (e.clientX - dragStartX.current);
      const clamped = Math.max(280, Math.min(800, newWidth));
      setActivityWidth(clamped);
    };
    const onUp = () => {
      setDragging(false);
      document.body.style.userSelect = "";
      setActivityWidth((w) => {
        try { localStorage.setItem("agentx_activity_width", String(w)); } catch {
          /* ignore storage quota/privacy failures */
        }
        return w;
      });
    };
    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
    return () => {
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseup", onUp);
      document.body.style.userSelect = "";
    };
  }, [dragging]);

  useEffect(() => {
    if (!inputDragging) return;
    const onMove = (e) => {
      const newHeight = inputDragStartHeight.current - (e.clientY - inputDragStartY.current);
      const clamped = Math.max(80, Math.min(600, newHeight));
      setInputHeight(clamped);
    };
    const onUp = () => {
      setInputDragging(false);
      setInputHeight((h) => {
        try { localStorage.setItem("agentx_input_height", String(h)); } catch {
          /* ignore storage quota/privacy failures */
        }
        return h;
      });
    };
    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
    return () => {
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseup", onUp);
    };
  }, [inputDragging]);

  /* persist state on changes */
  useEffect(() => {
    saveState(messages, activities);
  }, [messages, activities]);

  /* auto-scroll */
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /* fetch status info */
  const fetchStatus = useCallback(() => {
    fetch("/api/status")
      .then((r) => r.json())
      .then((info) => {
        setStatusInfo(info);
        if (info.agent_mode) setAgentMode(info.agent_mode);
        if (info.fic_document !== undefined) setFicDocument(info.fic_document);
      })
      .catch(() => {});
    fetch("/api/todos")
      .then((r) => r.json())
      .then(setTodos)
      .catch(() => {});
    fetch("/api/agent-mode")
      .then((r) => r.json())
      .then(setGovernanceInfo)
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  useEffect(() => {
    if (editingName && nameInputRef.current) {
      nameInputRef.current.focus();
      nameInputRef.current.select();
    }
  }, [editingName]);

  const saveName = () => {
    const name = nameInputRef.current?.value?.trim();
    if (!name) { setEditingName(false); return; }
    const sid = statusInfo.session_id;
    if (!sid) { setEditingName(false); return; }
    fetch(`/api/sessions/${sid}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_name: name }),
    })
      .then((r) => r.json())
      .then(() => {
        setEditingName(false);
        fetchStatus();
      })
      .catch(() => setEditingName(false));
  };

  const handleNameKey = (e) => {
    if (e.key === "Enter") { e.preventDefault(); saveName(); }
    if (e.key === "Escape") { e.preventDefault(); setEditingName(false); }
  };

  /* close menu on outside click */
  useEffect(() => {
    if (!openMenu) return;
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpenMenu(null);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [openMenu]);

  /* keyboard shortcuts */
  const menuActionRef = useRef(null);
  const leaderTimeoutRef = useRef(null);
  useEffect(() => {
    const handler = (e) => {
      const mod = e.ctrlKey || e.metaKey;
      if (mod && e.key.toLowerCase() === "o") {
        e.preventDefault();
        setShowSessionModal(true);
        return;
      }
      if (mod && e.key.toLowerCase() === "c" && window.getSelection().toString()) {
        return;
      }
      if (mod && e.key.toLowerCase() === "z") {
        e.preventDefault();
        menuActionRef.current("undoMessage");
        return;
      }
      /* Ctrl+X leader key */
      if (mod && e.key.toLowerCase() === "x") {
        e.preventDefault();
        leaderRef.current = true;
        if (leaderTimeoutRef.current) clearTimeout(leaderTimeoutRef.current);
        leaderTimeoutRef.current = setTimeout(() => { leaderRef.current = false; }, 2000);
        return;
      }
      if (leaderRef.current) {
        leaderRef.current = false;
        if (leaderTimeoutRef.current) clearTimeout(leaderTimeoutRef.current);
        const key = e.key.toLowerCase();
        const map = {
          b: "hideSidebar", m: "switchModel",
          n: "newSession", s: "viewStatus", t: "switchTheme",
          y: "copyLastMessage", g: "jumpToMessage",
        };
        if (map[key]) {
          e.preventDefault();
          menuActionRef.current(map[key]);
        }
      }
    };
    document.addEventListener("keydown", handler);
    return () => {
      document.removeEventListener("keydown", handler);
      if (leaderTimeoutRef.current) clearTimeout(leaderTimeoutRef.current);
    };
  }, []);

  const handleMenuAction = useCallback((id) => {
    setOpenMenu(null);
    switch (id) {
      case "newSession":
        fetch("/api/session/new", { method: "POST" })
          .then((r) => {
            if (!r.ok) throw new Error("Failed to create new session");
            return r.json();
          })
          .then(() => {
            cancelledRef.current = true;
            abortRef.current?.abort();
            setStreaming(false);
            setMessages([]);
            setActivities([]);
            setLoadedSessionId(null);
            fetchStatus();
          })
          .catch((err) => {
            setActivities((prev) => [...prev, { type: "error", text: `New session failed: ${err.message}`, time: new Date().toLocaleTimeString() }]);
          });
        break;
      case "openSession":
        setShowSessionModal(true);
        break;
      case "about":
        setShowAbout(true);
        break;
      case "exportSession":
        {
          if (messages.length === 0) return;
          const data = {
            version: 1,
            session_name: statusInfo.session_name || "Session",
            exported_at: new Date().toISOString(),
            messages: messages.map(({ role, text }) => ({ role, text })),
          };
          const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `session-${statusInfo.session_id || "export"}.json`;
          a.click();
          URL.revokeObjectURL(url);
        }
        break;
      case "importSession":
        importFileRef.current?.click();
        break;
      case "jumpToMessage":
        setShowTimeline(true);
        break;
      case "hideToolDetails": {
        const next = !hideToolDetails;
        localStorage.setItem("agentx_tool_details", next);
        setHideToolDetails(next);
        break;
      }
      case "showTimestamps": {
        const next = showTimestamps ? "hide" : "show";
        localStorage.setItem("agentx_timestamps", next);
        setShowTimestamps(!showTimestamps);
        break;
      }
      case "collapseThinking": {
        const next = thinkingMode === "show" ? "hide" : "show";
        localStorage.setItem("agentx_thinking_mode", next);
        setThinkingMode(next);
        break;
      }
      case "hideSidebar": {
        const next = sidebarPref === "auto" ? "hide" : "auto";
        localStorage.setItem("agentx_sidebar", next);
        setSidebarPref(next);
        break;
      }
      case "switchTheme": {
        const next = theme === "light" ? "dark" : "light";
        localStorage.setItem("agentx_theme", next);
        setTheme(next);
        break;
      }
      case "viewStatus":
        setShowStatus(true);
        break;
      case "switchModel":
        setShowModelModal(true);
        break;
      case "setAgentMode":
        setShowAgentModeModal(true);
        break;
      case "changeFic":
        setShowFicPicker(true);
        break;
      case "openDocs":
        window.open("https://opencode.ai/docs", "_blank");
        break;
      case "copyLastMessage": {
        const last = [...messages].reverse().find((m) => m.role === "assistant");
        if (last) {
          navigator.clipboard.writeText(last.text.trim()).then(() => {
            setActivities((prev) => [...prev, { type: "info", text: "Message copied to clipboard!", time: new Date().toLocaleTimeString() }]);
          }).catch(() => {});
        }
        break;
      }
      case "copyTranscript": {
        const lines = [
          `# ${statusInfo.session_name || "Session"}`,
          `**Session ID:** ${statusInfo.session_id || "—"}`,
          `**Created:** ${new Date().toLocaleString()}`,
          "",
          "---",
          "",
        ];
        for (const m of messages) {
          lines.push(`## ${m.role === "user" ? "User" : "Assistant"}`);
          lines.push("");
          lines.push(m.text || "");
          if (m.reasoning && thinkingMode === "show") {
            lines.push("");
            lines.push("_Thinking:_");
            lines.push("");
            lines.push(m.reasoning);
          }
          lines.push("");
          lines.push("---");
          lines.push("");
        }
        navigator.clipboard.writeText(lines.join("\n")).then(() => {
          setActivities((prev) => [...prev, { type: "info", text: "Transcript copied to clipboard!", time: new Date().toLocaleTimeString() }]);
        }).catch(() => {});
        break;
      }
      case "undoMessage": {
        if (streaming) {
          setActivities((prev) => [...prev, { type: "error", text: "Stop the current response before undoing.", time: new Date().toLocaleTimeString() }]);
          break;
        }
        const sid = loadedSessionId || statusInfo.session_id;
        if (!sid || messages.length === 0) break;
        const lastUserIdx = [...messages].reverse().findIndex((m) => m.role === "user");
        if (lastUserIdx < 0) break;
        const idx = messages.length - 1 - lastUserIdx;
        cancelledRef.current = true;
        abortRef.current?.abort();
        setStreaming(false);
        fetch(`/api/sessions/${sid}/revert`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message_index: idx }),
        })
          .then(async (r) => {
            if (!r.ok) {
              const errBody = await r.json().catch(() => ({}));
              throw new Error(errBody.error || `HTTP ${r.status}`);
            }
            return r.json();
          })
          .then((result) => {
            setMessages(result.messages || []);
            setInput(result.restored_message || "");
            setActivities([]);
            setSubagents([]);
            setActiveSubagentId(null);
            setSubagentMessages(null);
            setTodos([]);
          })
          .catch((err) => {
            setActivities((prev) => [...prev, { type: "error", text: `Undo failed: ${err.message}`, time: new Date().toLocaleTimeString() }]);
          });
        break;
      }
    }
  }, [messages, statusInfo, importFileRef, fetchStatus, hideToolDetails, showTimestamps, thinkingMode, sidebarPref, theme, streaming, loadedSessionId]);
  menuActionRef.current = handleMenuAction;

  const jumpToMessage = useCallback((index) => {
    const el = document.querySelector(`[data-message-index="${index}"]`);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  const handleImportFile = useCallback((e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const data = JSON.parse(ev.target.result);
        const msgs = data.messages || [];
        if (!Array.isArray(msgs) || msgs.length === 0) {
          setActivities([{ type: "error", text: "No messages found in import file.", time: new Date().toLocaleTimeString() }]);
          return;
        }
        const valid = msgs.every((m) => m.role && m.text);
        if (!valid) {
          setActivities([{ type: "error", text: "Invalid message format in import file.", time: new Date().toLocaleTimeString() }]);
          return;
        }
        setActivities([{ type: "info", text: "Importing session...", time: new Date().toLocaleTimeString() }]);
        fetch("/api/sessions/import", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_name: data.session_name || "Imported Session",
            messages: msgs,
          }),
        })
          .then((r) => r.json())
          .then((result) => {
            if (result.error) throw new Error(result.error);
            setMessages(msgs.map(({ role, text }) => ({ role, text })));
            fetchStatus();
            setActivities([{ type: "info", text: `Imported "${result.session_name}"`, time: new Date().toLocaleTimeString() }]);
          })
          .catch((err) => {
            setActivities([{ type: "error", text: `Import failed: ${err.message}`, time: new Date().toLocaleTimeString() }]);
          });
      } catch (err) {
        setActivities([{ type: "error", text: `Invalid file: ${err.message}`, time: new Date().toLocaleTimeString() }]);
      }
    };
    reader.readAsText(file);
    e.target.value = "";
  }, [fetchStatus]);

  const selectSubagent = useCallback((sessionId) => {
    if (!sessionId) {
      setActiveSubagentId(null);
      setSubagentMessages(null);
      return;
    }
    setActiveSubagentId(sessionId);
    setSubagentMessages(null);
    setActivities((prev) => [
      ...prev,
      { type: "info", text: `Loading subagent session...`, time: new Date().toLocaleTimeString() },
    ]);
    fetch(`/api/sessions/${sessionId}/subagent-messages`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((msgs) => {
        setSubagentMessages(msgs || []);
        setActivities((prev) => {
          const copy = prev.filter((a) => a.text !== "Loading subagent session...");
          copy.push({ type: "info", text: `Subagent session loaded (${(msgs || []).length} messages)`, time: new Date().toLocaleTimeString() });
          return copy;
        });
      })
      .catch((err) => {
        setSubagentMessages([]);
        setActivities((prev) => [
          ...prev,
          { type: "error", text: `Failed to load subagent: ${err.message}`, time: new Date().toLocaleTimeString() },
        ]);
      });
  }, []);

  const loadSession = useCallback((s) => {
    setShowSessionModal(false);
    setActivities([]);
    try {
      localStorage.setItem("agentx_chat_state_backup", JSON.stringify({ messages, activities }));
    } catch {
      /* ignore storage quota/privacy failures */
    }
    fetch(`/api/sessions/${s.run_id}/messages`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((msgs) => {
        setMessages(msgs);
        setLoadedSessionId(s.run_id);
        if (!msgs || msgs.length === 0) {
          setActivities([{ type: "info", text: "No messages in this session.", time: new Date().toLocaleTimeString() }]);
        }
      })
      .catch((err) => {
        setActivities([{ type: "error", text: `Failed to load session: ${err.message}`, time: new Date().toLocaleTimeString() }]);
      });
    fetchStatus();
  }, [messages, activities, fetchStatus]);

  const handleQuestionReply = useCallback(async (answers) => {
    if (!questionRequest) return;
    const requestId = questionRequest.request_id;
    try {
      await fetch(`/api/questions/${requestId}/reply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers }),
      });
      setQuestionRequest(null);
      setMessages((prev) => prev.map((m) => {
        if (m.questionData && m.questionData.requestId === requestId) {
          return { ...m, questionData: { ...m.questionData, answered: true, answers } };
        }
        return m;
      }));
    } catch { /* ignore */ }
  }, [questionRequest]);

  const handleQuestionReject = useCallback(() => {
    if (!questionRequest) return;
    const requestId = questionRequest.request_id;
    cancelledRef.current = true;
    abortRef.current?.abort();
    setStreaming(false);
    setQuestionRequest(null);
    setMessages((prev) => prev.map((m) => {
      if (m.questionData && m.questionData.requestId === requestId) {
        return { ...m, questionData: { ...m.questionData, answered: true, rejected: true } };
      }
      return m;
    }));

    fetch(`/api/questions/${requestId}/reject`, { method: "POST" })
      .catch(() => {})
      .finally(() => {
        fetch("/api/chat/cancel", { method: "POST" }).catch(() => {});
      });
  }, [questionRequest]);

  const handlePermissionReply = useCallback(async (requestId, reply, message = "") => {
    try {
      await fetch(`/api/permissions/${requestId}/reply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reply, message }),
      });
      setPendingPermissions((prev) => prev.filter((p) => p.request_id !== requestId));
      setMessages((prev) => prev.map((m) => {
        if (m.permissionData && m.permissionData.requestId === requestId) {
          return { ...m, permissionData: { ...m.permissionData, resolved: true, resolution: reply, message } };
        }
        return m;
      }));
    } catch { /* ignore */ }
  }, []);

  const sendMessage = useCallback((prefill) => {
    const text = (typeof prefill === "string" ? prefill : input).trim();
    if (!text || streaming) return;
    setInput("");
    setHistoryIndex(null);
    setDraftInput("");
    setActivities([]);
    setSubagents([]);
    setActiveSubagentId(null);
    setSubagentMessages(null);
    cancelledRef.current = false;

    setMessages((prev) => [...prev, { role: "user", text }]);

    const controller = new AbortController();
    abortRef.current = controller;
    setStreaming(true);
    setMessages((prev) => [...prev, { role: "assistant", text: "" }]);

    const timeoutMs = 0;
    let timeoutId;
    if (timeoutMs > 0) {
      timeoutId = setTimeout(() => {
        controller.abort();
        setMessages((prev) => {
          const copy = [...prev];
          const last = copy[copy.length - 1];
          if (last && last.role === "assistant" && last.text === "") {
            copy[copy.length - 1] = {
              role: "assistant",
              text: "[No response within 60s — provider may be unavailable]",
            };
          }
          return copy;
        });
        setStreaming(false);
      }, timeoutMs);
    }

    const currentMode = mode;

    (async () => {
      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: text,
            mode: currentMode,
            session_id: loadedSessionId || statusInfo.session_id,
            messages: messages
              .filter((m) => (m.role === "user" || m.role === "assistant") && m.text?.trim())
              .map(({ role, text }) => ({ role, content: text })),
          }),
          signal: controller.signal,
        });

        if (!response.ok) {
          const errText = await response.text().catch(() => response.statusText);
          throw new Error(`${response.status} ${errText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("Response body is not readable");

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const data = line.slice(6);
              if (data === "[DONE]") { reader.cancel(); return; }
            try {
              const event = JSON.parse(data);
              if (event.type === "text" && event.author === "user") continue;
              if (event.type === "text") {
                if (cancelledRef.current) continue;
                setMessages((prev) => {
                  const copy = [...prev];
                  const last = copy[copy.length - 1];
                  if (last && last.role === "assistant") {
                    copy[copy.length - 1] = {
                      ...last,
                      text: joinText(last.text, event.text || ""),
                    };
                  }
                  return copy;
                });
              } else if (event.type === "error") {
                if (cancelledRef.current) continue;
                setMessages((prev) => {
                  const copy = [...prev];
                  const last = copy[copy.length - 1];
                  if (last && last.role === "assistant" && last.text === "") {
                    copy[copy.length - 1] = {
                      role: "assistant",
                      text: `[Error: ${event.text}]`,
                    };
                  }
                  return copy;
                });
                setActivities((prev) => [
                  ...prev,
                  { type: "error", text: event.text, time: new Date().toLocaleTimeString() },
                ]);
              } else if (event.type === "subagent") {
                setSubagents((prev) => {
                  const idx = prev.findIndex((s) => s.session_id === (event.session_id || event.description));
                  if (idx >= 0) {
                    const copy = [...prev];
                    copy[idx] = { ...copy[idx], ...event, time: new Date().toLocaleTimeString() };
                    return copy;
                  }
                  return [...prev, { ...event, time: new Date().toLocaleTimeString() }];
                });
              } else if (event.type === "question") {
                setQuestionRequest(event);
                setMessages((prev) => {
                  const copy = [...prev];
                  const last = copy[copy.length - 1];
                  if (last && last.role === "assistant") {
                    copy[copy.length - 1] = { ...last, questionData: { requestId: event.request_id, questions: event.questions || [], answered: false } };
                  } else {
                    copy.push({ role: "assistant", text: "", questionData: { requestId: event.request_id, questions: event.questions || [], answered: false } });
                  }
                  return copy;
                });
              } else if (event.type === "question_cleared") {
                setQuestionRequest(null);
                setMessages((prev) => prev.map((m) => {
                  if (m.questionData && m.questionData.requestId === event.request_id && !m.questionData.answered) {
                    return { ...m, questionData: { ...m.questionData, answered: true } };
                  }
                  return m;
                }));
              } else if (event.type === "permission") {
                setPendingPermissions((prev) => [...prev, event]);
                setMessages((prev) => {
                  const copy = [...prev];
                  const last = copy[copy.length - 1];
                  if (last && last.role === "assistant") {
                    copy[copy.length - 1] = { ...last, permissionData: { requestId: event.request_id, action: event.action, resources: event.resources || [], metadata: event.metadata || {}, save: event.save || [], resolved: false } };
                  } else {
                    copy.push({ role: "assistant", text: "", permissionData: { requestId: event.request_id, action: event.action, resources: event.resources || [], metadata: event.metadata || {}, save: event.save || [], resolved: false } });
                  }
                  return copy;
                });
              } else if (event.type === "permission_cleared") {
                setPendingPermissions((prev) => prev.filter((p) => p.request_id !== event.request_id));
                setMessages((prev) => prev.map((m) => {
                  if (m.permissionData && m.permissionData.requestId === event.request_id && !m.permissionData.resolved) {
                    return { ...m, permissionData: { ...m.permissionData, resolved: true } };
                  }
                  return m;
                }));
              } else if (event.type === "todo") {
                setTodos(event.todos || []);
              } else {
                setActivities((prev) => [
                  ...prev,
                  { ...event, time: new Date().toLocaleTimeString() },
                ]);
              }
            } catch {
              /* skip malformed JSON */
            }
          }
        }
      } catch (err) {
        if (err.name !== "AbortError") {
          setMessages((prev) => {
            const copy = [...prev];
            const last = copy[copy.length - 1];
            if (last && last.role === "assistant" && last.text === "") {
              copy[copy.length - 1] = {
                role: "assistant",
                text: `[Error: ${err.message}]`,
              };
            } else {
              copy.push({ role: "assistant", text: `[Error: ${err.message}]` });
            }
            return copy;
          });
        }
      } finally {
        clearTimeout(timeoutId);
        setStreaming(false);
        abortRef.current = null;
      }
    })();
  }, [input, streaming, mode, loadedSessionId]);

  const userPromptHistory = messages
    .filter((m) => m.role === "user" && m.text)
    .map((m) => m.text);

  const handleKeyDown = (e) => {
    const el = e.currentTarget;

    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
      return;
    }

    if (e.key === "ArrowUp") {
      const atStart = el.selectionStart === 0 && el.selectionEnd === 0;

      if (!atStart) {
        e.preventDefault();
        el.setSelectionRange(0, 0);
        return;
      }

      if (userPromptHistory.length === 0) return;

      e.preventDefault();

      setHistoryIndex((prev) => {
        const next = prev === null
          ? userPromptHistory.length - 1
          : Math.max(0, prev - 1);

        if (prev === null) setDraftInput(input);
        setInput(userPromptHistory[next]);
        requestAnimationFrame(() => {
          if (inputRef.current) {
            const len = inputRef.current.value.length;
            inputRef.current.setSelectionRange(len, len);
          }
        });
        return next;
      });

      return;
    }

    if (e.key === "ArrowDown") {
      const atEnd = el.selectionStart === input.length && el.selectionEnd === input.length;

      if (!atEnd) {
        e.preventDefault();
        el.setSelectionRange(input.length, input.length);
        return;
      }

      if (historyIndex === null) return;

      e.preventDefault();

      setHistoryIndex((prev) => {
        if (prev === null) return null;

        const next = prev + 1;

        if (next >= userPromptHistory.length) {
          setInput(draftInput);
          setDraftInput("");
          requestAnimationFrame(() => {
            if (inputRef.current) {
              const len = inputRef.current.value.length;
              inputRef.current.setSelectionRange(len, len);
            }
          });
          return null;
        }

        setInput(userPromptHistory[next]);
        requestAnimationFrame(() => {
          if (inputRef.current) {
            const len = inputRef.current.value.length;
            inputRef.current.setSelectionRange(len, len);
          }
        });
        return next;
      });
    }
  };

  return (
    <ErrorBoundary>
      <div className="app">
        {/* ── Menu bar ──────────────────────────────────── */}
        <div className="menubar" ref={menuRef}>
          {MENU_ORDER.map((name) => (
            <div
              key={name}
              className={`menu-trigger ${openMenu === name ? "active" : ""}`}
              onMouseDown={() => setOpenMenu(openMenu === name ? null : name)}
            >
              {name}
              {openMenu === name && (
                <div className="menu-dropdown">
                  {MENUS[name].map((item, i) =>
                    item === null ? (
                      <div key={i} className="menu-sep" />
                    ) : (
                      <div
                        key={i}
                        className={`menu-item ${item.disabled ? "disabled" : ""}`}
                  onMouseDown={(e) => e.stopPropagation()}
                          onClick={() => {
                            if (!item.disabled) handleMenuAction(item.id);
                          }}
                      >
                        <span>{item.label}</span>
                        {item.shortcut && (
                          <span className="menu-shortcut">{item.shortcut}</span>
                        )}
                      </div>
                    )
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* ── Main content ──────────────────────────────── */}
        <div className="main-content">
          <div className="status-panel">
            <div className="status-header">Status</div>
            <div className="status-body">
              <div className="status-row">
                <span className="status-label">Provider</span>
                <span className="status-value">{statusInfo.provider || "—"}</span>
              </div>
              <div className="status-row">
                <span className="status-label">Model</span>
                <span className="status-value">{statusInfo.model || "—"}</span>
              </div>
              <div className="status-row">
                <span className="status-label">Session</span>
                <span className="status-value">{statusInfo.session_id || "—"}</span>
              </div>
              <div className="status-row">
                <span className="status-label">Agent</span>
                <span className="status-value">
                  {agentMode === "governed" ? "Governed (P7)" : "General (P9)"}
                </span>
              </div>
              {agentMode === "governed" && ficDocument && (
                <div className="status-row">
                  <span className="status-label">FIC</span>
                  <span className="status-value status-fic-name">{ficDocument.split("/").pop()}</span>
                </div>
              )}
              {todos.length > 0 && (
                <div className="todo-section">
                  <div className="todo-header">
                    <span>Todos</span>
                    <span className="todo-count">{todos.filter(t => t.status !== "completed").length}</span>
                  </div>
                  {todos.map((todo, i) => (
                    <div key={i} className={`todo-item todo-${todo.status}`}>
                      <span className={`todo-status todo-status-${todo.status}`}>
                        {todo.status === "completed" ? "\u2713" : todo.status === "in_progress" ? "\u25D4" : todo.status === "cancelled" ? "\u2014" : "\u25CB"}
                      </span>
                      <span className="todo-content">{todo.content}</span>
                      {todo.priority && todo.priority !== "medium" && (
                        <span className={`todo-priority todo-priority-${todo.priority}`}>{todo.priority}</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          <div className="chat-area">
            <div className="chat-header">
            {activeSubagentId ? (
              <div className="chat-name-display">
                <button className="btn btn-back" onClick={() => selectSubagent(null)}>
                  &#8592; Back
                </button>
                <span className="chat-name-text">Subagent: {activeSubagentId.slice(0, 20)}...</span>
              </div>
            ) : editingName ? (
              <div className="chat-name-edit">
                <input
                  ref={nameInputRef}
                  className="chat-name-input"
                  defaultValue={statusInfo.session_name || "Session"}
                  onKeyDown={handleNameKey}
                  onBlur={saveName}
                />
              </div>
            ) : (
              <div className="chat-name-display" onClick={() => setEditingName(true)}>
                <span className="chat-name-text">{statusInfo.session_name || "Session"}</span>
                <span className="chat-name-hint">click to rename</span>
              </div>
            )}
          </div>
            <div className="messages">
              {activeSubagentId ? (
                subagentMessages === null ? (
                  <div className="msg msg-assistant">
                    <div className="msg-label msg-label-assistant">Subagent</div>
                    <div className="msg-body">Loading subagent session...</div>
                  </div>
                ) : subagentMessages.length === 0 ? (
                  <div className="msg msg-assistant">
                    <div className="msg-label msg-label-assistant">Subagent</div>
                    <div className="msg-body">No messages in this subagent session.</div>
                  </div>
                ) : (
                  subagentMessages.map((m, i) => (
                    <Message key={i} index={i} role={m.role} text={m.text} reasoning={m.reasoning} timestamp={m.timestamp} showTimestamps={showTimestamps} thinkingMode={thinkingMode} mode={mode} />
                  ))
                )
              ) : messages.length === 0 ? (
                <SuggestionQuestions onSelect={(text) => sendMessage(text)} />
              ) : (
                messages.map((m, i) => (
                  <Message key={i} index={i} role={m.role} text={m.text} reasoning={m.reasoning} timestamp={m.timestamp} showTimestamps={showTimestamps} thinkingMode={thinkingMode} questionData={m.questionData} permissionData={m.permissionData} onQuestionReply={handleQuestionReply} onQuestionReject={handleQuestionReject} onPermissionReply={handlePermissionReply} mode={mode} />
                ))
              )}
              <div ref={chatEndRef} />
            </div>

            <div className={`resize-handle-h${inputDragging ? " active" : ""}`} onMouseDown={onInputHandleMouseDown} />
            <div className="input-area" style={{ height: inputHeight }}>

            {/* ── Mode toggle ──────────────────────────────── */}
            <div className="mode-bar">
              <button
                className={`mode-btn mode-btn-plan${mode === "plan" ? " active" : ""}`}
                onClick={() => {
                  localStorage.setItem("agentx_mode", "plan");
                  setMode("plan");
                }}
              >
                Plan
              </button>
              <button
                className={`mode-btn mode-btn-build${mode === "build" ? " active" : ""}`}
                onClick={() => {
                  localStorage.setItem("agentx_mode", "build");
                  setMode("build");
                }}
              >
                Build
              </button>
              <span className="mode-label">{mode === "plan" ? "Read-only analysis" : "Full tool access"}</span>
              <span className={`agent-badge agent-badge-${agentMode}`}>
                {agentMode === "governed" ? "Governed" : "General"}
              </span>
            </div>

            <GovernanceBanner governanceInfo={governanceInfo} />

            {/* ── Input bar ─────────────────────────────────── */}
            <div className="input-bar">
              <textarea
                ref={inputRef}
                className="input-box"
                placeholder="Type a message... (Enter to send, Shift+Enter for newline)"
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  setHistoryIndex(null);
                  setDraftInput("");
                }}
                onKeyDown={handleKeyDown}
                rows={2}
                disabled={!!questionRequest || pendingPermissions.length > 0}
              />
              <div className="input-actions">
                <button
                  className="stop-btn"
                  disabled={!streaming}
                  onClick={() => {
                    fetch("/api/chat/cancel", { method: "POST" }).catch(() => {});
                    cancelledRef.current = true;
                    abortRef.current?.abort();
                    setMessages((prev) => {
                      const copy = [...prev];
                      const last = copy[copy.length - 1];
                      if (last && last.role === "assistant" && last.text === "") {
                        copy[copy.length - 1] = {
                          role: "assistant",
                          text: "*[Stopped]*",
                        };
                      }
                      return copy;
                    });
                  }}
                >
                  &#9632;
                </button>
                <button
                  className="send-btn"
                  onClick={() => sendMessage()}
                  disabled={streaming || !input.trim()}
                >
                  &#9654;
                </button>
              </div>
            </div>
            </div>
          </div>
          <div className={`resize-handle${dragging ? " active" : ""}`} onMouseDown={onHandleMouseDown} />
          {sidebarVisible && (
            <div className="activity-panel-wrap" style={{ width: activityWidth }}>
              <ActivityPanel
                activities={activities}
                streaming={streaming}
                subagents={subagents}
                activeSession={activeSubagentId}
                onSelectSubagent={selectSubagent}
                hideToolDetails={hideToolDetails}
              />
            </div>
          )}
        </div>

        {/* ── Modals ────────────────────────────────────── */}
        <SessionModal
          open={showSessionModal}
          onClose={() => setShowSessionModal(false)}
          onSelect={loadSession}
          onStatusRefresh={fetchStatus}
        />
        <TimelineModal
          open={showTimeline}
          onClose={() => setShowTimeline(false)}
          messages={activeSubagentId ? (subagentMessages || []) : messages}
          onJump={jumpToMessage}
        />
        <StatusModal open={showStatus} onClose={() => setShowStatus(false)} statusInfo={statusInfo} />
        <ModelModal
          open={showModelModal}
          onClose={() => setShowModelModal(false)}
          currentModel={statusInfo.model}
          currentProvider={statusInfo.provider}
          onSwitch={(model, provider, setSwitching, close) => {
            setSwitching(true);
            const payload = { model };
            if (provider) payload.provider = provider;
            fetch("/api/model/switch", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload),
            })
              .then((r) => {
                if (!r.ok) throw new Error("Switch failed");
                return r.json();
              })
              .then(() => {
                setActivities((prev) => [...prev, { type: "info", text: `Switched model to ${model}`, time: new Date().toLocaleTimeString() }]);
                fetchStatus();
                close();
              })
              .catch((err) => {
                setActivities((prev) => [...prev, { type: "error", text: `Switch failed: ${err.message}`, time: new Date().toLocaleTimeString() }]);
              })
              .finally(() => setSwitching(false));
          }}
        />
        <AgentModeModal
          open={showAgentModeModal}
          onClose={() => setShowAgentModeModal(false)}
          currentMode={agentMode}
          currentFic={ficDocument}
          onSave={(info) => {
            setAgentMode(info.agent_mode);
            setFicDocument(info.fic_document || "");
            setGovernanceInfo(info);
            setStatusInfo((prev) => ({
              ...prev,
              agent_mode: info.agent_mode,
              fic_document: info.fic_document || "",
              ceiling: info.ceiling,
            }));
          }}
        />
        <FicPickerModal
          open={showFicPicker}
          onClose={() => setShowFicPicker(false)}
          currentFic={ficDocument}
          onSave={(info) => {
            setAgentMode(info.agent_mode);
            setFicDocument(info.fic_document || "");
            setGovernanceInfo(info);
            setStatusInfo((prev) => ({
              ...prev,
              agent_mode: info.agent_mode,
              fic_document: info.fic_document || "",
              ceiling: info.ceiling,
            }));
          }}
        />
        <AboutModal open={showAbout} onClose={() => setShowAbout(false)} />
        <input
          ref={importFileRef}
          type="file"
          accept=".json"
          style={{ display: "none" }}
          onChange={handleImportFile}
        />
      </div>
    </ErrorBoundary>
  );
}
