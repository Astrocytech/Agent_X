import { useMemo } from "react";

const POOL = [
  { label: "Architecture Overview", text: "Explain the layered architecture of Agent_X — what each layer owns and how they interact." },
  { label: "Governance Model", text: "How does the governance layer enforce policies on tool execution? Walk through the full chain." },
  { label: "Kernel Lifecycle", text: "Describe the phase engine in L0's kernel: prelude, decision, execution, record, finale." },
  { label: "Add a Tool", text: "What steps are needed to register a new seed tool in L0's tool_gateway?" },
  { label: "L1 Controller Flow", text: "Trace a goal from document_loader through the 14-module L1 controller pipeline to boundary_checker." },
  { label: "New Agent Profile", text: "What files and schemas must I touch to add a new L2 agent profile?" },
  { label: "Evidence Ledger", text: "How does the evidence ledger work and how does the proof suite validate checkpoint replay?" },
  { label: "Future Layer Contract", text: "What port interfaces would an L3 domain package need to satisfy based on existing contracts?" },
];

function pickRandom(arr, n) {
  const shuffled = [...arr].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, n);
}

export default function SuggestionQuestions({ onSelect }) {
  const questions = useMemo(() => pickRandom(POOL, 4), []);

  return (
    <div className="suggestion-questions">
      <div className="suggestion-header">Try asking</div>
      <div className="suggestion-grid">
        {questions.map((q) => (
          <button
            key={q.label}
            className="suggestion-card"
            onClick={() => onSelect(q.text)}
          >
            <span className="suggestion-label">{q.label}</span>
            <span className="suggestion-desc">{q.text}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
