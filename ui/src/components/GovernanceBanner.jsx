import React from "react";

export default function GovernanceBanner({ governanceInfo }) {
  if (!governanceInfo || governanceInfo.agent_mode !== "governed") return null;

  return (
    <div className="governance-banner">
      <div className="gov-banner-row">
        <span className="gov-badge gov-badge-fic">FIC: {governanceInfo.fic_document || "none"}</span>
        <span className="gov-badge gov-badge-ceiling">Ceiling: {governanceInfo.ceiling}</span>
        <span className="gov-badge gov-badge-phase">Phase 0 active</span>
      </div>
      <div className="gov-banner-row gov-banner-tools">
        <span className="gov-tools-label">Allowed:</span>
        <span className="gov-tools-value">{(governanceInfo.allowed_tools || []).join(", ")}</span>
      </div>
      <div className="gov-banner-row gov-banner-tools">
        <span className="gov-tools-label">Forbidden:</span>
        <span className="gov-tools-value gov-tools-forbidden">{(governanceInfo.forbidden_tools || []).join(", ")}</span>
      </div>
    </div>
  );
}
