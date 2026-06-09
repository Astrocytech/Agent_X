import { useState, useEffect } from "react";

export default function AgentModeModal({ open, onClose, currentMode, currentFic, onSave }) {
  const [step, setStep] = useState("pick");
  const [mode, setMode] = useState("general");
  const [ficDocs, setFicDocs] = useState([]);
  const [selectedFic, setSelectedFic] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    Promise.resolve().then(() => {
      if (cancelled) return;
      setStep("pick");
      setMode(currentMode || "general");
      setSelectedFic(currentFic || "");
      setFicDocs([]);
    });
    return () => {
      cancelled = true;
    };
  }, [open, currentMode, currentFic]);

  const fetchFicDocs = () => {
    fetch("/api/fic-documents")
      .then((r) => r.json())
      .then(setFicDocs)
      .catch(() => setFicDocs([]));
  };

  const handleModeSelect = (m) => {
    setMode(m);
    if (m === "governed") {
      fetchFicDocs();
      setStep("pick-fic");
    } else {
      setSelectedFic("");
      setStep("review");
    }
  };

  const handleSave = () => {
    setSaving(true);
    const fic_document = mode === "governed" ? selectedFic : "";
    fetch("/api/agent-mode", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_mode: mode, fic_document }),
    })
      .then((r) => r.json())
      .then((data) => {
        onSave(data);
        onClose();
      })
      .catch(() => setSaving(false));
  };

  const handleBack = () => {
    setStep("pick");
    setMode("general");
    setSelectedFic("");
  };

  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span>{step === "pick-fic" ? "Select FIC Document" : "Set Agent Mode"}</span>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
          {step === "pick" && (
            <div className="agent-mode-cards">
              <div
                className={`agent-mode-card${mode === "general" ? " active" : ""}`}
                onClick={() => handleModeSelect("general")}
              >
                <div className="agent-mode-card-title">General</div>
                <div className="agent-mode-card-ceiling">P9 — Unrestricted</div>
                <div className="agent-mode-card-desc">
                  Full tool access. No FIC workflow required.
                  Suitable for everyday development tasks.
                </div>
              </div>
              <div
                className={`agent-mode-card${mode === "governed" ? " active" : ""}`}
                onClick={() => handleModeSelect("governed")}
              >
                <div className="agent-mode-card-title">Governed</div>
                <div className="agent-mode-card-ceiling">P7 — FIC-Governed</div>
                <div className="agent-mode-card-desc">
                  FIC workflow enforced. Tool access governed by
                  coding_agent profile. Completion evidence required.
                </div>
              </div>
            </div>
          )}

          {step === "pick-fic" && (
            <div className="fic-picker-section">
              <button className="btn btn-back fic-back" onClick={handleBack}>
                &larr; Back to mode selection
              </button>
              {ficDocs.length === 0 ? (
                <p className="fic-empty">No FIC documents found in L1/docs/.</p>
              ) : (
                <div className="fic-doc-list">
                  {ficDocs.map((doc, i) => (
                    <div
                      key={i}
                      className={`fic-doc-item${selectedFic === doc.path ? " active" : ""}`}
                      onClick={() => setSelectedFic(doc.path)}
                    >
                      <div className="fic-doc-name">{doc.name}</div>
                      <div className="fic-doc-path">{doc.path}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {step === "review" && (
            <div className="agent-mode-review">
              <div className="review-row">
                <span className="review-label">Mode</span>
                <span className="review-value">{mode === "general" ? "General (P9)" : "Governed (P7)"}</span>
              </div>
              {mode === "governed" && selectedFic && (
                <div className="review-row">
                  <span className="review-label">FIC Document</span>
                  <span className="review-value">{selectedFic}</span>
                </div>
              )}
            </div>
          )}

          {step === "pick-fic" && mode === "governed" && (
            <div className="modal-actions">
              <button
                className="btn btn-primary"
                disabled={!selectedFic || saving}
                onClick={handleSave}
              >
                {saving ? "Saving..." : "Apply Governed Mode"}
              </button>
              <button className="btn" onClick={onClose}>Cancel</button>
            </div>
          )}

          {step === "review" && mode === "general" && (
            <div className="modal-actions">
              <button
                className="btn btn-primary"
                disabled={saving}
                onClick={handleSave}
              >
                {saving ? "Saving..." : "Apply General Mode"}
              </button>
              <button className="btn" onClick={onClose}>Cancel</button>
            </div>
          )}

          {step === "pick" && (
            <div className="modal-actions">
              <button className="btn" onClick={onClose}>Cancel</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
