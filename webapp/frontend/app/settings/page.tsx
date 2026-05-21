'use client';

import { useState, useEffect, useCallback } from 'react';
import { Settings, Save, Key, Link, Brain, Server, RefreshCw } from 'lucide-react';
import { fetchSettings, updateSettings } from '@/utils/api';

export default function SettingsPage() {
  const [settings, setSettingsForm] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await fetchSettings();
      setSettingsForm(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await updateSettings(settings);
      setSaved(true);
      setError(null);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const update = (key: string, value: string) => {
    setSettingsForm((prev) => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-8">
        <div className="h-7 w-32 rounded bg-jellyfin-surface-light" />
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card space-y-3">
            <div className="h-4 w-24 rounded bg-jellyfin-surface-light" />
            <div className="h-10 w-full rounded bg-jellyfin-surface-light" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Settings</h2>
          <p className="mt-1 text-sm text-[#777790]">Configure jellyfin-mcp connections</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary inline-flex items-center gap-2 text-sm"
        >
          {saving ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          {saving ? 'Saving...' : 'Save'}
        </button>
      </div>

      {saved && (
        <div className="rounded-xl border border-green-500/20 bg-green-500/5 px-4 py-3 text-sm text-green-400">
          Settings saved successfully
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="space-y-6">
        <div className="card space-y-5">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-jellyfin-purple/15">
              <Server className="h-5 w-5 text-jellyfin-purple" />
            </div>
            <h3 className="font-semibold text-white">Jellyfin Server</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-[#777790]">
                <Link className="mr-1.5 inline-block h-3.5 w-3.5" />
                Jellyfin URL
              </label>
              <input
                type="text"
                value={settings.jellyfinUrl || ''}
                onChange={(e) => update('jellyfinUrl', e.target.value)}
                placeholder="http://localhost:8096"
                className="input-field"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-[#777790]">
                <Key className="mr-1.5 inline-block h-3.5 w-3.5" />
                API Key
              </label>
              <input
                type="password"
                value={settings.apiKey || ''}
                onChange={(e) => update('apiKey', e.target.value)}
                placeholder="Enter your Jellyfin API key"
                className="input-field"
              />
            </div>
          </div>
        </div>

        <div className="card space-y-5">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-jellyfin-blue/15">
              <Brain className="h-5 w-5 text-jellyfin-blue" />
            </div>
            <h3 className="font-semibold text-white">LLM &amp; RAG Configuration</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-[#777790]">
                LLM Provider
              </label>
              <select
                value={settings.llmProvider || ''}
                onChange={(e) => update('llmProvider', e.target.value)}
                className="input-field"
              >
                <option value="">Select provider</option>
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="local">Local (Ollama)</option>
              </select>
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-[#777790]">
                LLM API Key
              </label>
              <input
                type="password"
                value={settings.llmApiKey || ''}
                onChange={(e) => update('llmApiKey', e.target.value)}
                placeholder="LLM provider API key"
                className="input-field"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-[#777790]">
                LLM Model
              </label>
              <input
                type="text"
                value={settings.llmModel || ''}
                onChange={(e) => update('llmModel', e.target.value)}
                placeholder="gpt-4o / claude-opus-4 / llama3"
                className="input-field"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-[#777790]">
                RAG Chunk Size
              </label>
              <input
                type="number"
                value={settings.ragChunkSize || 500}
                onChange={(e) => update('ragChunkSize', e.target.value)}
                placeholder="500"
                className="input-field"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-[#777790]">
                RAG Chunk Overlap
              </label>
              <input
                type="number"
                value={settings.ragChunkOverlap || 50}
                onChange={(e) => update('ragChunkOverlap', e.target.value)}
                placeholder="50"
                className="input-field"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
