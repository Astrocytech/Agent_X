import { useState } from "react";

const ACTION_LABELS = {
  read: "Read File",
  edit: "Edit File",
  bash: "Run Command",
  glob: "Search Files",
  grep: "Search Content",
  list: "List Directory",
  webfetch: "Fetch URL",
  delete: "Delete File",
};

export default function PermissionDock({ action, resources, metadata, save, onReply }) {
  const [mode, setMode] = useState(null);
  const [message, setMessage] = useState("");

  const label = ACTION_LABELS[action] || action;
  const resourceText = (resources || []).join(", ");

  const renderBody = () => {
    switch (action) {
      case "read":
        return <div className="perm-line">Reading file: <code>{resourceText}</code></div>;
      case "edit":
        return <div className="perm-line">Editing file: <code>{resourceText}</code></div>;
      case "bash":
        return (
          <div className="perm-line">
            <div>Running command:</div>
            <pre><code>{resourceText}</code></pre>
          </div>
        );
      case "glob":
        return <div className="perm-line">Searching pattern: <code>{resourceText}</code></div>;
      case "grep":
        return <div className="perm-line">Searching content: <code>{resourceText}</code></div>;
      case "list":
        return <div className="perm-line">Listing directory: <code>{resourceText}</code></div>;
      case "webfetch":
        return <div className="perm-line">Fetching URL: <code>{resourceText}</code></div>;
      case "delete":
        return <div className="perm-line perm-line-delete">Deleting: <code>{resourceText}</code></div>;
      default:
        return <div className="perm-line">Action: <code>{action}</code> on <code>{resourceText}</code></div>;
    }
  };

  if (mode === "once" || mode === "always") {
    return null;
  }

  return (
    <div className="permission-dock">
      <div className="permission-header">
        <span className="permission-label">{label}</span>
      </div>

      <div className="permission-body">
        {renderBody()}
      </div>

      {mode === "reject" && (
        <textarea
          className="permission-message"
          placeholder="Reason for rejection (sent to the LLM)..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={2}
        />
      )}

      <div className="permission-actions">
        {mode === null && (
          <>
            <button
              className="perm-btn perm-btn-once"
              onClick={() => {
                setMode("once");
                onReply("once");
              }}
            >
              Allow Once
            </button>
            <button
              className="perm-btn perm-btn-always"
              onClick={() => {
                setMode("always");
                onReply("always");
              }}
            >
              Allow Always
            </button>
            <button className="perm-btn perm-btn-reject" onClick={() => setMode("reject")}>
              Reject
            </button>
          </>
        )}
        {mode === "reject" && (
          <>
            <button className="perm-btn perm-btn-cancel" onClick={() => setMode(null)}>
              Back
            </button>
            <button
              className="perm-btn perm-btn-reject-send"
              onClick={() => onReply("reject", message)}
            >
              Send Rejection
            </button>
          </>
        )}
      </div>
    </div>
  );
}
