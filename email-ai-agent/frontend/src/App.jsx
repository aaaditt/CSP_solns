import { useCallback, useEffect, useState } from "react";
import Header from "./components/Header";
import FilterBar from "./components/FilterBar";
import EmailTable from "./components/EmailTable";
import EmailDetail from "./components/EmailDetail";
import BulkActionBar from "./components/BulkActionBar";
import SettingsPanel from "./components/SettingsPanel";
import {
  listEmails,
  getEmail,
  patchEmail,
  patchEmailsBulk,
  getStats,
  syncEmails,
  unsubscribeEmail,
  exportUrl,
} from "./api";

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
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [error, setError] = useState(null);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [settingsOpen, setSettingsOpen] = useState(false);

  function notify(message, { isError = false } = {}) {
    setToast({ message, isError });
  }

  const refresh = useCallback(async () => {
    try {
      const query = { ...filters, reviewed: filters.reviewed === "" ? undefined : filters.reviewed };
      const [emailsRes, statsRes] = await Promise.all([listEmails(query), getStats()]);
      setEmails(emailsRes.emails);
      setStats(statsRes);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    // Background sync now happens on its own schedule server-side; poll
    // periodically so newly-synced mail shows up without a manual click.
    const interval = setInterval(refresh, 60_000);
    return () => clearInterval(interval);
  }, [refresh]);

  useEffect(() => {
    if (!toast) return;
    const timeout = setTimeout(() => setToast(null), 4000);
    return () => clearTimeout(timeout);
  }, [toast]);

  useEffect(() => {
    // Selections referencing rows no longer in view (filters changed, or a
    // row got reviewed/tagged away) shouldn't linger in the bulk bar.
    setSelectedIds((prev) => {
      const visibleIds = new Set(emails.map((e) => e.id));
      const next = new Set([...prev].filter((id) => visibleIds.has(id)));
      return next.size === prev.size ? prev : next;
    });
  }, [emails]);

  function updateFilters(partial) {
    setFilters((prev) => ({ ...prev, ...partial }));
  }

  function toggleSelect(id) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleSelectAll(checked) {
    setSelectedIds(checked ? new Set(emails.map((e) => e.id)) : new Set());
  }

  async function handleSync() {
    setSyncing(true);
    try {
      const result = await syncEmails();
      if (result.status === "success") {
        notify(`Sync complete: ${result.classified} new emails classified, ${result.skipped} already seen.`);
      } else {
        notify(`Sync failed: ${result.error}`, { isError: true });
      }
      await refresh();
    } catch (err) {
      notify(`Sync failed: ${err.message}`, { isError: true });
    } finally {
      setSyncing(false);
    }
  }

  async function handleOpen(id) {
    try {
      const email = await getEmail(id);
      setSelectedEmail(email);
    } catch (err) {
      notify(`Could not open email: ${err.message}`, { isError: true });
    }
  }

  async function handleToggleReviewed(id, current) {
    try {
      await patchEmail(id, { reviewed: !current });
      if (selectedEmail?.id === id) {
        setSelectedEmail((prev) => ({ ...prev, reviewed: !current }));
      }
      await refresh();
    } catch (err) {
      notify(`Could not update email: ${err.message}`, { isError: true });
    }
  }

  async function handleTagChange(id, tag) {
    try {
      await patchEmail(id, { tag });
      if (selectedEmail?.id === id) {
        setSelectedEmail((prev) => ({ ...prev, tag }));
      }
      await refresh();
    } catch (err) {
      notify(`Could not update tag: ${err.message}`, { isError: true });
    }
  }

  async function handleUnsubscribe(email) {
    try {
      const result = await unsubscribeEmail(email.id);

      if (result.action === "completed") {
        if (result.status === "sent") {
          notify(`Unsubscribed from ${email.sender}.`);
        } else {
          notify(`Unsubscribe failed: ${result.detail}`, { isError: true });
        }
      } else if (result.action === "open_link") {
        window.open(result.url, "_blank", "noopener,noreferrer");
        await patchEmail(email.id, { unsubscribe_status: "opened" });
        notify("Opened the unsubscribe link in a new tab.");
      } else if (result.action === "open_mailto") {
        window.location.href = result.mailto;
        await patchEmail(email.id, { unsubscribe_status: "opened" });
        notify("Opened your email client to unsubscribe.");
      }

      if (selectedEmail?.id === email.id) {
        setSelectedEmail(await getEmail(email.id));
      }
      await refresh();
    } catch (err) {
      notify(`Unsubscribe failed: ${err.message}`, { isError: true });
    }
  }

  async function handleBulkMarkReviewed(reviewed) {
    try {
      const result = await patchEmailsBulk([...selectedIds], { reviewed });
      notify(`${result.updated} email(s) updated.`);
      setSelectedIds(new Set());
      await refresh();
    } catch (err) {
      notify(`Bulk update failed: ${err.message}`, { isError: true });
    }
  }

  async function handleBulkTag(tag) {
    try {
      const result = await patchEmailsBulk([...selectedIds], { tag });
      notify(`${result.updated} email(s) tagged.`);
      setSelectedIds(new Set());
      await refresh();
    } catch (err) {
      notify(`Bulk tag failed: ${err.message}`, { isError: true });
    }
  }

  function handleBulkExport() {
    window.open(exportUrl(filters, [...selectedIds]), "_blank");
  }

  return (
    <div className="app">
      <Header stats={stats} syncing={syncing} onSync={handleSync} onOpenSettings={() => setSettingsOpen(true)} />

      {error && (
        <div className="error-banner">
          Can't reach the backend ({error}). Is uvicorn running on port 8000?
        </div>
      )}
      {toast && (
        <div className={toast.isError ? "toast toast-error" : "toast"}>{toast.message}</div>
      )}

      <FilterBar filters={filters} onChange={updateFilters} />

      {selectedIds.size > 0 && (
        <BulkActionBar
          count={selectedIds.size}
          onMarkReviewed={handleBulkMarkReviewed}
          onTag={handleBulkTag}
          onExport={handleBulkExport}
          onClear={() => setSelectedIds(new Set())}
        />
      )}

      <EmailTable
        emails={emails}
        loading={loading}
        selectedIds={selectedIds}
        onToggleSelect={toggleSelect}
        onToggleSelectAll={toggleSelectAll}
        onOpen={handleOpen}
        onToggleReviewed={handleToggleReviewed}
        onTagChange={handleTagChange}
        onUnsubscribe={handleUnsubscribe}
      />

      <EmailDetail
        email={selectedEmail}
        onClose={() => setSelectedEmail(null)}
        onToggleReviewed={handleToggleReviewed}
        onTagChange={handleTagChange}
        onUnsubscribe={handleUnsubscribe}
      />

      {settingsOpen && (
        <SettingsPanel
          onClose={() => setSettingsOpen(false)}
          onSaved={() => notify("Settings saved.")}
          onError={(message) => notify(message, { isError: true })}
        />
      )}
    </div>
  );
}
