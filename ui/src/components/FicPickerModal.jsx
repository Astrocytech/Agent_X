import { useState, useEffect } from "react";

export default function FicPickerModal({ open, onClose, currentFic, onSave }) {
  const [ficDocs, setFicDocs] = useState([]);
  const [selectedFic, setSelectedFic] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    Promise.resolve().then(() => {
      if (!cancelled) setSelectedFic(currentFic || "");
    });
    fetch("/api/fic-documents")
      .then((r) => r.json())
      .then((docs) => {
        if (!cancelled) setFicDocs(docs);
      })
      .catch(() => {
        if (!cancelled) setFicDocs([]);
      });
    return () => {
      cancelled = true;
    };
  }, [open, currentFic]);

  const handleSave = () => {
    if (!selectedFic) return;
    setSaving(true);
    fetch("/api/agent-mode", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_mode: "governed", fic_document: selectedFic }),
    })
      .then((r) => r.json())
      .then((data) => {
        onSave(data);
        onClose();
      })
      .catch(() => setSaving(false));
  };

  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span>Change FIC Document</span>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
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
          <div className="modal-actions">
            <button
              className="btn btn-primary"
              disabled={!selectedFic || saving}
              onClick={handleSave}
            >
              {saving ? "Saving..." : "Apply"}
            </button>
            <button className="btn" onClick={onClose}>Cancel</button>
          </div>
        </div>
      </div>
    </div>
  );
}
