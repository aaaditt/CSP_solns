import { useEffect, useState } from "react";
import { exportUrl } from "../api";

const CATEGORIES = [
  "streaming",
  "saas",
  "hosting",
  "domain",
  "telecom",
  "gym",
  "newsletter",
  "finance",
  "other",
  "not_subscription",
];

export default function FilterBar({ filters, onChange }) {
  const [searchInput, setSearchInput] = useState(filters.search);

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (searchInput !== filters.search) {
        onChange({ search: searchInput });
      }
    }, 300);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput]);

  return (
    <div className="filter-bar">
      <label className="filter-toggle">
        <input
          type="checkbox"
          checked={filters.subscription_only}
          onChange={(e) => onChange({ subscription_only: e.target.checked })}
        />
        Subscriptions only
      </label>

      <select
        value={filters.category}
        onChange={(e) => onChange({ category: e.target.value })}
      >
        <option value="">All categories</option>
        {CATEGORIES.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      <select
        value={filters.reviewed}
        onChange={(e) => onChange({ reviewed: e.target.value })}
      >
        <option value="">All</option>
        <option value="false">Unreviewed</option>
        <option value="true">Reviewed</option>
      </select>

      <input
        className="search-input"
        type="text"
        placeholder="Search sender or subject..."
        value={searchInput}
        onChange={(e) => setSearchInput(e.target.value)}
      />

      <a className="export-link" href={exportUrl(filters)} download>
        Export CSV
      </a>
    </div>
  );
}
