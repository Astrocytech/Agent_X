import { useState, useMemo } from "react";

export default function QuestionDock({ questions, onReply, onReject }) {
  const [activeTab, setActiveTab] = useState(0);
  const [selections, setSelections] = useState(() =>
    questions.map(() => new Set())
  );
  const [customInputs, setCustomInputs] = useState(() =>
    questions.map(() => "")
  );

  const handleToggleOption = (qIdx, label) => {
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

  const isComplete = answers.every((a) => a.length > 0);
  const qTabs = questions.length;
  const reviewIdx = qTabs;

  return (
    <div className="question-dock">
      <div className="question-tabs">
        {questions.map((q, i) => (
          <button
            key={q.id || i}
            className={`question-tab ${activeTab === i ? "active" : ""}`}
            onClick={() => setActiveTab(i)}
          >
            {q.display || `Question ${i + 1}`}
          </button>
        ))}
        <button
          className={`question-tab review-tab ${activeTab === reviewIdx ? "active" : ""}`}
          onClick={() => setActiveTab(reviewIdx)}
        >
          Review
        </button>
      </div>

      <div className="question-tab-content">
        {activeTab < qTabs ? (
          <div className="question-panel">
            <div className="question-text">{questions[activeTab].text}</div>
            {questions[activeTab].options && questions[activeTab].options.length > 0 && (
              <div className="question-options">
                {questions[activeTab].options.map((opt) => {
                  const isSelected = selections[activeTab]?.has(opt.label);
                  return (
                    <button
                      key={opt.label}
                      className={`question-option ${isSelected ? "selected" : ""}`}
                      onClick={() => handleToggleOption(activeTab, opt.label)}
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
            {questions[activeTab].allow_custom && (
              <textarea
                className="question-custom"
                placeholder="Custom answer..."
                value={customInputs[activeTab]}
                onChange={(e) => handleCustomChange(activeTab, e.target.value)}
                rows={3}
              />
            )}
          </div>
        ) : (
          <div className="review-panel">
            {questions.map((q, i) => (
              <div key={q.id || i} className="review-item">
                <div className="review-question">{q.text}</div>
                <div className="review-answers">
                  {answers[i].length > 0 ? (
                    answers[i].map((a) => (
                      <span key={a} className="review-answer">
                        {a}
                      </span>
                    ))
                  ) : (
                    <span className="review-unanswered">(unanswered)</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="question-actions">
        <button className="btn-reject" onClick={onReject}>
          Cancel
        </button>
        <button
          className="btn-submit"
          disabled={!isComplete}
          onClick={() => onReply(answers)}
        >
          Submit
        </button>
      </div>
    </div>
  );
}
