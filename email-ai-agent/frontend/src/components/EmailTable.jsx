import { useState } from "react";
import UnsubscribeButton from "./UnsubscribeButton";

function TagInput({ value, onCommit }) {
  const [text, setText] = useState(value || "");

  return (
    <input
      className="tag-input"
      type="text"
      value={text}
      placeholder="tag..."
      onChange={(e) => setText(e.target.value)}
      onBlur={() => {
        if (text !== (value || "")) onCommit(text);
      }}
    />
  );
}

function formatDate(dateStr) {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleString();
}

function SkeletonRows() {
  return (
    <>
      {[0, 1, 2, 3, 4].map((i) => (
        <tr key={i} className="skeleton-row">
          {Array.from({ length: 7 }).map((_, col) => (
            <td key={col}>
              <div className="skeleton-block" />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

export default function EmailTable({
  emails,
  loading,
  selectedIds,
  onToggleSelect,
  onToggleSelectAll,
  onOpen,
  onToggleReviewed,
  onTagChange,
  onUnsubscribe,
}) {
  const allSelected = emails.length > 0 && emails.every((e) => selectedIds.has(e.id));

  if (!loading && emails.length === 0) {
    return <div className="empty-state">No emails match the current filters.</div>;
  }

  return (
    <table className="email-table">
      <thead>
        <tr>
          <th>
            <input
              type="checkbox"
              checked={allSelected}
              onChange={(e) => onToggleSelectAll(e.target.checked)}
              disabled={emails.length === 0}
            />
          </th>
          <th>Sender</th>
          <th>Subject</th>
          <th>Date</th>
          <th>Category</th>
          <th>Confidence</th>
          <th>Summary</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {loading && emails.length === 0 ? (
          <SkeletonRows />
        ) : (
          emails.map((e) => (
            <tr key={e.id} className={e.reviewed ? "reviewed-row" : ""}>
              <td>
                <input
                  type="checkbox"
                  checked={selectedIds.has(e.id)}
                  onChange={() => onToggleSelect(e.id)}
                />
              </td>
              <td>{e.sender}</td>
              <td className="subject-cell" onClick={() => onOpen(e.id)}>
                {e.subject}
              </td>
              <td>{formatDate(e.date)}</td>
              <td>
                <span className={`badge badge-${e.category}`}>{e.category}</span>
              </td>
              <td>
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{ width: `${Math.round((e.confidence || 0) * 100)}%` }}
                  />
                </div>
              </td>
              <td className="summary-cell">{e.summary}</td>
              <td className="actions-cell">
                <button onClick={() => onOpen(e.id)}>Open</button>
                <button onClick={() => onToggleReviewed(e.id, e.reviewed)}>
                  {e.reviewed ? "Unreview" : "Mark reviewed"}
                </button>
                <TagInput value={e.tag} onCommit={(tag) => onTagChange(e.id, tag)} />
                <UnsubscribeButton email={e} onUnsubscribe={onUnsubscribe} />
              </td>
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}
