import React, { useState, useRef, useEffect, useCallback } from "react";
import "./App.css";
import ActivityPanel from "./components/ActivityPanel";

/* ------------------------------------------------------------------ */
/*  Menu data                                                          */
/* ------------------------------------------------------------------ */

const MENUS = {
  Session: [
    { label: "New Session", shortcut: "Ctrl+X N", id: "newSession" },
    null,
    { label: "Open Session...", shortcut: "Ctrl+O", id: "openSession" },
    null,
    { label: "Import Session", disabled: true },
    { label: "Export Session", disabled: true },
    null,
    { label: "Jump to Message", shortcut: "Ctrl+X G", disabled: true },
    { label: "Fork Session", disabled: true },
    { label: "Compact Session", shortcut: "Ctrl+X C", disabled: true },
    { label: "Undo Previous Message", shortcut: "Ctrl+X U", disabled: true },
    null,
    { label: "Hide Sidebar", shortcut: "Ctrl+X B", disabled: true },
    { label: "Disable Code Concealment", shortcut: "Ctrl+X H", disabled: true },
    { label: "Show Timestamps", disabled: true },
    { label: "Collapse Thinking", disabled: true },
    { label: "Hide Tool Details", disabled: true },
    { label: "Toggle Session Scrollbar", disabled: true },
    { label: "Show Generic Tool Output", disabled: true },
    null,
    { label: "Copy Last Assistant Message", shortcut: "Ctrl+X Y", disabled: true },
    { label: "Copy Session Transcript", disabled: true },
  ],
  Prompt: [
    { label: "Skills", disabled: true },
    { label: "Stash Pop", disabled: true },
    { label: "Stash List", disabled: true },
  ],
  Agent: [
    { label: "Switch Model", shortcut: "Ctrl+X M", disabled: true },
    { label: "Switch Agent", shortcut: "Ctrl+X A", disabled: true },
    { label: "Toggle MCPs", disabled: true },
    { label: "Variant Cycle", shortcut: "Ctrl+T", disabled: true },
  ],
  Provider: [{ label: "Connect Provider", disabled: true }],
  System: [
    { label: "View Status", shortcut: "Ctrl+X S", disabled: true },
    { label: "Switch Theme", shortcut: "Ctrl+X T", disabled: true },
    { label: "Switch to Light Mode", disabled: true },
    { label: "Lock Theme Mode", disabled: true },
    null,
    { label: "Open Docs", disabled: true },
    null,
    { label: "Exit the App", shortcut: "Ctrl+X Q", disabled: true },
    null,
    { label: "Toggle Debug Panel", disabled: true },
    { label: "Toggle Console", disabled: true },
    { label: "Write Heap Snapshot", disabled: true },
    { label: "Disable Terminal Title", disabled: true },
    { label: "Disable Animations", disabled: true },
    { label: "Disable File Context", disabled: true },
    { label: "Disable Diff Wrapping", disabled: true },
    { label: "Disable Paste Summary", disabled: true },
    { label: "Disable Session Directory Filtering", disabled: true },
    null,
    { label: "Install Plugin", disabled: true },
  ],
  VCS: [{ label: "Open Diff Viewer", disabled: true }],
  Help: [{ label: "About", id: "about" }],
};

const MENU_ORDER = [
  "Session",
  "Prompt",
  "Agent",
  "Provider",
  "System",
  "VCS",
  "Help",
];

/* ------------------------------------------------------------------ */
/*  Markdown → HTML (minimal)                                          */
/* ------------------------------------------------------------------ */

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
    setConfirm(null);
    setEditing(null);
    fetchSessions();
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
                    <button className="btn btn-open" onClick={() => { onSelect(s); onClose(); }}>Open</button>
                    <button className="btn btn-rename" onClick={() => startRename(s)}>Rename</button>
                    <button className="btn btn-delete" onClick={() => handleDelete(s.run_id)}>Delete</button>
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

/* ------------------------------------------------------------------ */
/*  Message bubble                                                     */
/* ------------------------------------------------------------------ */

function Message({ role, text }) {
  const html = mdToHtml(text);
  const isUser = role === "user";
  return (
    <div className={`msg msg-${role}`}>
      <div className={`msg-label msg-label-${role}`}>
        {isUser ? "You" : "Assistant"}
      </div>
      <div className="msg-body" dangerouslySetInnerHTML={{ __html: html }} />
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
  } catch {}
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
  } catch {}
  return null;
}

export default function App() {
  const [messages, setMessages] = useState(() => {
    const saved = loadState();
    return saved ? saved.messages : [];
  });
  const [streaming, setStreaming] = useState(false);
  const [input, setInput] = useState("");
  const [openMenu, setOpenMenu] = useState(null);
  const [showSessionModal, setShowSessionModal] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const menuRef = useRef(null);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const abortRef = useRef(null);
  const [activities, setActivities] = useState(() => {
    const saved = loadState();
    return saved ? saved.activities : [];
  });
  const [statusInfo, setStatusInfo] = useState({ model: "", session_id: "", provider: "", session_name: "" });
  const [editingName, setEditingName] = useState(false);
  const nameInputRef = useRef(null);

  /* resizable activity panel width */
  const [activityWidth, setActivityWidth] = useState(() => {
    try {
      const saved = localStorage.getItem("agentx_activity_width");
      return saved ? parseInt(saved, 10) : 420;
    } catch { return 420; }
  });
  const [dragging, setDragging] = useState(false);
  const dragStartX = useRef(0);
  const dragStartWidth = useRef(0);

  const onHandleMouseDown = useCallback((e) => {
    e.preventDefault();
    setDragging(true);
    dragStartX.current = e.clientX;
    dragStartWidth.current = activityWidth;
  }, [activityWidth]);

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
        try { localStorage.setItem("agentx_activity_width", String(w)); } catch {}
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
      .then(setStatusInfo)
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
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  const handleMenuAction = useCallback((id) => {
    setOpenMenu(null);
    switch (id) {
      case "newSession":
        fetch("/api/session/new", { method: "POST" })
          .then((r) => r.json())
          .then(() => {
            setMessages([]);
            setActivities([]);
            fetchStatus();
          })
          .catch(() => {});
        break;
      case "openSession":
        setShowSessionModal(true);
        break;
      case "about":
        setShowAbout(true);
        break;
    }
  }, []);

  const loadSession = useCallback((s) => {
    setShowSessionModal(false);
    setActivities([]);
    try {
      localStorage.setItem("agentx_chat_state_backup", JSON.stringify({ messages, activities }));
    } catch {}
    fetch(`/api/sessions/${s.run_id}/messages`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((msgs) => {
        setMessages(msgs);
        if (!msgs || msgs.length === 0) {
          setActivities([{ type: "info", text: "No messages in this session.", time: new Date().toLocaleTimeString() }]);
        }
      })
      .catch((err) => {
        setActivities([{ type: "error", text: `Failed to load session: ${err.message}`, time: new Date().toLocaleTimeString() }]);
      });
    fetchStatus();
  }, [messages, activities, fetchStatus]);

  const sendMessage = useCallback(() => {
    const text = input.trim();
    if (!text || streaming) return;
    setInput("");
    setActivities([]);

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

    (async () => {
      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
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
                setMessages((prev) => {
                  const copy = [...prev];
                  const last = copy[copy.length - 1];
                  if (last && last.role === "assistant") {
                    copy[copy.length - 1] = {
                      ...last,
                      text: last.text + (event.text || ""),
                    };
                  }
                  return copy;
                });
              } else if (event.type === "error") {
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
  }, [input, streaming]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
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
            </div>
          </div>
          <div className="chat-area">
            <div className="chat-header">
            {editingName ? (
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
              {messages.map((m, i) => (
                <Message key={i} role={m.role} text={m.text} />
              ))}
              <div ref={chatEndRef} />
            </div>

            {/* ── Input bar ─────────────────────────────────── */}
            <div className="input-bar">
              <textarea
                ref={inputRef}
                className="input-box"
                placeholder="Type a message... (Enter to send, Shift+Enter for newline)"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={2}
              />
              <div className="input-actions">
                <button
                  className="stop-btn"
                  disabled={!streaming}
                  onClick={() => {
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
                  onClick={sendMessage}
                  disabled={streaming || !input.trim()}
                >
                  &#9654;
                </button>
              </div>
            </div>
          </div>
          <div className={`resize-handle${dragging ? " active" : ""}`} onMouseDown={onHandleMouseDown} />
          <div className="activity-panel-wrap" style={{ width: activityWidth }}>
            <ActivityPanel activities={activities} streaming={streaming} />
          </div>
        </div>

        {/* ── Modals ────────────────────────────────────── */}
        <SessionModal
          open={showSessionModal}
          onClose={() => setShowSessionModal(false)}
          onSelect={loadSession}
          onStatusRefresh={fetchStatus}
        />
        <AboutModal open={showAbout} onClose={() => setShowAbout(false)} />
      </div>
    </ErrorBoundary>
  );
}
