export default function EmailDetail({ email, onClose, onToggleReviewed, onTagChange }) {
  if (!email) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          &times;
        </button>
        <h2>{email.subject}</h2>
        <p className="modal-meta">
          {email.sender} &lt;{email.sender_email}&gt; &mdash;{" "}
          {email.date ? new Date(email.date).toLocaleString() : ""}
        </p>
        <p className="modal-meta">
          <span className={`badge badge-${email.category}`}>{email.category}</span>{" "}
          confidence {Math.round((email.confidence || 0) * 100)}%
        </p>
        <p className="modal-summary">{email.summary}</p>

        <div className="modal-actions">
          <button onClick={() => onToggleReviewed(email.id, email.reviewed)}>
            {email.reviewed ? "Unreview" : "Mark reviewed"}
          </button>
          <input
            className="tag-input"
            type="text"
            defaultValue={email.tag || ""}
            placeholder="tag..."
            onBlur={(e) => onTagChange(email.id, e.target.value)}
          />
        </div>

        <hr />

        {email.error ? (
          <p className="error-banner">
            Could not load the full body live ({email.error}). Showing the stored snippet
            instead:
          </p>
        ) : null}
        <pre className="email-body">{email.full_body ?? email.body_snippet}</pre>
      </div>
    </div>
  );
}
