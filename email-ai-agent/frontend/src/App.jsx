import { useCallback, useEffect, useState } from "react";
import Header from "./components/Header";
import FilterBar from "./components/FilterBar";
import EmailTable from "./components/EmailTable";
import EmailDetail from "./components/EmailDetail";
import { listEmails, getEmail, patchEmail, getStats, syncEmails } from "./api";

const DEFAULT_FILTERS = {
  subscription_only: true,
  category: "",
  reviewed: "",
  search: "",
  sort: "date_desc",
};

export default function App() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [emails, setEmails] = useState([]);
  const [stats, setStats] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [toast, setToast] = useState(null);
  const [error, setError] = useState(null);
  const [selectedEmail, setSelectedEmail] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const query = { ...filters, reviewed: filters.reviewed === "" ? undefined : filters.reviewed };
      const [emailsRes, statsRes] = await Promise.all([listEmails(query), getStats()]);
      setEmails(emailsRes.emails);
      setStats(statsRes);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }, [filters]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!toast) return;
    const timeout = setTimeout(() => setToast(null), 4000);
    return () => clearTimeout(timeout);
  }, [toast]);

  function updateFilters(partial) {
    setFilters((prev) => ({ ...prev, ...partial }));
  }

  async function handleSync() {
    setSyncing(true);
    try {
      const result = await syncEmails();
      setToast(
        result.status === "success"
          ? `Sync complete: ${result.classified} new emails classified, ${result.skipped} already seen.`
          : `Sync failed: ${result.error}`
      );
      await refresh();
    } catch (err) {
      setToast(`Sync failed: ${err.message}`);
    } finally {
      setSyncing(false);
    }
  }

  async function handleOpen(id) {
    try {
      const email = await getEmail(id);
      setSelectedEmail(email);
    } catch (err) {
      setToast(`Could not open email: ${err.message}`);
    }
  }

  async function handleToggleReviewed(id, current) {
    await patchEmail(id, { reviewed: !current });
    if (selectedEmail?.id === id) {
      setSelectedEmail((prev) => ({ ...prev, reviewed: !current }));
    }
    await refresh();
  }

  async function handleTagChange(id, tag) {
    await patchEmail(id, { tag });
    if (selectedEmail?.id === id) {
      setSelectedEmail((prev) => ({ ...prev, tag }));
    }
    await refresh();
  }

  return (
    <div className="app">
      <Header stats={stats} syncing={syncing} onSync={handleSync} />

      {error && (
        <div className="error-banner">
          Can't reach the backend ({error}). Is uvicorn running on port 8000?
        </div>
      )}
      {toast && <div className="toast">{toast}</div>}

      <FilterBar filters={filters} onChange={updateFilters} />

      <EmailTable
        emails={emails}
        onOpen={handleOpen}
        onToggleReviewed={handleToggleReviewed}
        onTagChange={handleTagChange}
      />

      <EmailDetail
        email={selectedEmail}
        onClose={() => setSelectedEmail(null)}
        onToggleReviewed={handleToggleReviewed}
        onTagChange={handleTagChange}
      />
    </div>
  );
}
