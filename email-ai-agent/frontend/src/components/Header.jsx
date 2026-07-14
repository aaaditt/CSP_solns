function StatChip({ label, value }) {
  return (
    <div className="stat-chip">
      <span className="stat-value">{value ?? "-"}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

export default function Header({ stats, syncing, onSync, onOpenSettings }) {
  return (
    <header className="header">
      <div className="header-top">
        <h1>Email AI Agent</h1>
        <div className="header-actions">
          <button className="settings-button" onClick={onOpenSettings}>
            Settings
          </button>
          <button className="sync-button" onClick={onSync} disabled={syncing}>
            {syncing ? "Syncing..." : "Sync"}
          </button>
        </div>
      </div>
      {stats && (
        <div className="stat-chips">
          <StatChip label="Subscriptions" value={stats.total_subscriptions} />
          <StatChip label="Unreviewed" value={stats.unreviewed} />
          {stats.last_sync && (
            <StatChip
              label="Last sync"
              value={
                stats.last_sync.status === "success"
                  ? `${stats.last_sync.emails_classified} classified`
                  : stats.last_sync.status
              }
            />
          )}
        </div>
      )}
    </header>
  );
}
