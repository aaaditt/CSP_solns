import { useState } from "react";

export default function BulkActionBar({ count, onMarkReviewed, onTag, onExport, onClear }) {
  const [tag, setTag] = useState("");

  return (
    <div className="bulk-action-bar">
      <span>{count} selected</span>
      <button onClick={() => onMarkReviewed(true)}>Mark reviewed</button>
      <button onClick={() => onMarkReviewed(false)}>Mark unreviewed</button>
      <input
        className="tag-input"
        type="text"
        placeholder="tag..."
        value={tag}
        onChange={(e) => setTag(e.target.value)}
      />
      <button onClick={() => tag && onTag(tag)} disabled={!tag}>
        Apply tag
      </button>
      <button onClick={onExport}>Export selected</button>
      <button onClick={onClear}>Clear selection</button>
    </div>
  );
}
