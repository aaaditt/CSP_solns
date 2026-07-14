import { useEffect, useState } from "react";
import { getSettings, patchSettings } from "../api";

export default function SettingsPanel({ onClose, onSaved, onError }) {
  const [settings, setSettings] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getSettings()
      .then(setSettings)
      .catch((err) => onError(`Could not load settings: ${err.message}`));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSave() {
    setSaving(true);
    try {
      const saved = await patchSettings({
        sync_interval_minutes: Number(settings.sync_interval_minutes),
        sync_max_emails: Number(settings.sync_max_emails),
        background_sync_enabled: settings.background_sync_enabled,
      });
      setSettings(saved);
      onSaved();
    } catch (err) {
      onError(`Could not save settings: ${err.message}`);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          &times;
        </button>
        <h2>Settings</h2>

        {!settings ? (
          <p className="modal-meta">Loading...</p>
        ) : (
          <div className="settings-form">
            <label className="settings-field">
              <span>Background sync</span>
              <input
                type="checkbox"
                checked={settings.background_sync_enabled}
                onChange={(e) => setSettings({ ...settings, background_sync_enabled: e.target.checked })}
              />
            </label>

            <label className="settings-field">
              <span>Sync interval (minutes)</span>
              <input
                type="number"
                min={5}
                max={1440}
                value={settings.sync_interval_minutes}
                onChange={(e) => setSettings({ ...settings, sync_interval_minutes: e.target.value })}
              />
            </label>

            <label className="settings-field">
              <span>Max emails per sync</span>
              <input
                type="number"
                min={1}
                max={100}
                value={settings.sync_max_emails}
                onChange={(e) => setSettings({ ...settings, sync_max_emails: e.target.value })}
              />
            </label>

            <p className="modal-meta">
              Gmail credentials and the Gemini API key stay in the backend&apos;s .env file and
              are never editable here.
            </p>

            <div className="modal-actions">
              <button onClick={handleSave} disabled={saving}>
                {saving ? "Saving..." : "Save"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
