import { useState, useMemo } from "react";

export default function QuestionBlock({ questions, onReply, onReject }) {
  const [selections, setSelections] = useState(() =>
    questions.map(() => new Set())
  );
  const [customInputs, setCustomInputs] = useState(() =>
    questions.map(() => "")
  );
  const [submitted, setSubmitted] = useState(false);

  const handleToggle = (qIdx, label) => {
    setSelections((prev) => {
      const next = prev.map((s) => new Set(s));
      const q = questions[qIdx];
      if (q.allow_select_multiple) {
        if (next[qIdx].has(label)) next[qIdx].delete(label);
        else next[qIdx].add(label);
      } else {
        next[qIdx] = new Set([label]);
      }
      return next;
    });
  };

  const handleCustomChange = (qIdx, value) => {
    setCustomInputs((prev) => {
      const next = [...prev];
      next[qIdx] = value;
      return next;
    });
  };

  const answers = useMemo(
    () =>
      selections.map((sel, i) => {
        const ans = Array.from(sel);
        if (customInputs[i].trim()) ans.push(customInputs[i].trim());
        return ans;
      }),
    [selections, customInputs]
  );

  const allAnswered = answers.every((a) => a.length > 0);

  const handleSubmit = () => {
    if (!allAnswered) return;
    setSubmitted(true);
    onReply(answers);
  };

  if (submitted) {
    return (
      <div className="question-block answered">
        {questions.map((q, i) => (
          <div key={q.id || i} className="question-item">
            <div className="question-text">{q.text}</div>
            <div className="question-answer-summary">
              {answers[i].length > 0
                ? answers[i].map((a) => (
                    <span key={a} className="answer-chip">{a}</span>
                  ))
                : <span className="answer-skipped">(skipped)</span>}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="question-block">
      {questions.map((q, i) => (
        <div key={q.id || i} className="question-item">
          <div className="question-text">{q.text}</div>
          {q.options && q.options.length > 0 && (
            <div className="question-options">
              {q.options.map((opt) => {
                const isSelected = selections[i]?.has(opt.label);
                return (
                  <button
                    key={opt.label}
                    className={`question-option ${isSelected ? "selected" : ""}`}
                    onClick={() => handleToggle(i, opt.label)}
                  >
                    <span className="qo-label">{opt.label}</span>
                    {opt.description && (
                      <span className="qo-desc">{opt.description}</span>
                    )}
                  </button>
                );
              })}
            </div>
          )}
          {q.allow_custom && (
            <textarea
              className="question-custom"
              placeholder="Custom answer..."
              value={customInputs[i]}
              onChange={(e) => handleCustomChange(i, e.target.value)}
              rows={2}
            />
          )}
        </div>
      ))}
      <div className="question-actions">
        <button className="btn-reject" onClick={onReject}>Cancel</button>
        <button className="btn-submit" disabled={!allAnswered} onClick={handleSubmit}>
          Submit
        </button>
      </div>
    </div>
  );
}
