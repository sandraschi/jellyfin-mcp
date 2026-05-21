'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Puzzle,
  Download,
  ToggleLeft,
  ToggleRight,
  Search,
  Package,
  Tag,
  Loader2,
  Wrench,
} from 'lucide-react';
import { fetchPlugins, fetchPluginCatalog, togglePlugin, installPlugin } from '@/utils/api';

interface InstalledPlugin {
  Name: string;
  Version: string;
  Description: string;
  Id: string;
  enabled?: boolean;
}

interface CatalogPlugin {
  Name: string;
  Version: string;
  Description: string;
  Id: string;
  Category: string;
}

export default function PluginsPage() {
  const [installed, setInstalled] = useState<InstalledPlugin[]>([]);
  const [catalog, setCatalog] = useState<CatalogPlugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<'installed' | 'catalog'>('installed');
  const [installingId, setInstallingId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  const load = useCallback(async () => {
    try {
      const [inst, cat] = await Promise.all([
        fetchPlugins(),
        fetchPluginCatalog(),
      ]);
      setInstalled(inst as InstalledPlugin[]);
      setCatalog(cat as CatalogPlugin[]);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load plugins');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleToggle = async (pluginId: string, currentEnabled: boolean) => {
    try {
      await togglePlugin(pluginId, !currentEnabled);
      setInstalled((prev) =>
        prev.map((p) => (p.Id === pluginId ? { ...p, enabled: !currentEnabled } : p)),
      );
    } catch {
      // silently fail
    }
  };

  const handleInstall = async (pluginId: string) => {
    setInstallingId(pluginId);
    try {
      await installPlugin(pluginId);
      load();
    } catch {
      // silently fail
    } finally {
      setInstallingId(null);
    }
  };

  const categories = [...new Set(catalog.map((p) => p.Category).filter(Boolean))];
  const filteredCatalog = catalog.filter((p) => {
    const matchesSearch = p.Name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.Description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !categoryFilter || p.Category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Plugins</h2>
          <p className="mt-1 text-sm text-[#777790]">Manage Jellyfin++ extensions</p>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="flex items-center gap-1 rounded-lg border border-[#ffffff10] bg-jellyfin-surface p-1">
        <button
          onClick={() => setTab('installed')}
          className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
            tab === 'installed'
              ? 'bg-jellyfin-purple/20 text-jellyfin-purple-light'
              : 'text-[#777790] hover:text-white'
          }`}
        >
          <Package className="mr-2 inline-block h-4 w-4" />
          Installed ({installed.length})
        </button>
        <button
          onClick={() => setTab('catalog')}
          className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
            tab === 'catalog'
              ? 'bg-jellyfin-purple/20 text-jellyfin-purple-light'
              : 'text-[#777790] hover:text-white'
          }`}
        >
          <Download className="mr-2 inline-block h-4 w-4" />
          Catalog ({catalog.length})
        </button>
      </div>

      {loading && (
        <div className="animate-pulse space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card">
              <div className="h-5 w-48 rounded bg-jellyfin-surface-light" />
              <div className="mt-2 h-3 w-96 rounded bg-jellyfin-surface-light" />
            </div>
          ))}
        </div>
      )}

      {tab === 'installed' && !loading && (
        <div className="space-y-3">
          {installed.map((plugin) => (
            <div key={plugin.Id} className="card flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <Wrench className="h-4 w-4 text-jellyfin-purple" />
                  <h3 className="font-medium text-white">{plugin.Name}</h3>
                  <span className="rounded-md bg-jellyfin-surface-light px-2 py-0.5 text-[11px] text-[#8888A0]">
                    v{plugin.Version}
                  </span>
                </div>
                <p className="mt-1 text-xs text-[#666680]">{plugin.Description}</p>
              </div>
              <button
                onClick={() => handleToggle(plugin.Id, !!plugin.enabled)}
                className={`rounded-lg p-2 transition-colors ${
                  plugin.enabled
                    ? 'text-green-400 hover:bg-green-500/10'
                    : 'text-[#555570] hover:bg-jellyfin-surface-light hover:text-white'
                }`}
              >
                {plugin.enabled ? (
                  <ToggleRight className="h-5 w-5" />
                ) : (
                  <ToggleLeft className="h-5 w-5" />
                )}
              </button>
            </div>
          ))}
          {installed.length === 0 && (
            <div className="card flex flex-col items-center py-16">
              <Puzzle className="mb-3 h-10 w-10 text-[#444460]" />
              <p className="text-sm text-[#666680]">No plugins installed</p>
              <p className="mt-1 text-xs text-[#555570]">Browse the catalog to install plugins</p>
            </div>
          )}
        </div>
      )}

      {tab === 'catalog' && !loading && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#666680]" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search plugins..."
                className="input-field pl-10"
              />
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setCategoryFilter(categoryFilter === cat ? '' : cat)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                    categoryFilter === cat
                      ? 'bg-jellyfin-purple/20 text-jellyfin-purple-light'
                      : 'text-[#777790] hover:bg-jellyfin-surface hover:text-white'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            {filteredCatalog.map((plugin) => {
              const isInstalled = installed.some((p) => p.Id === plugin.Id);
              return (
                <div key={plugin.Id} className="card flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <Tag className="h-4 w-4 text-jellyfin-blue" />
                      <h3 className="font-medium text-white">{plugin.Name}</h3>
                      <span className="rounded-md bg-jellyfin-surface-light px-2 py-0.5 text-[11px] text-[#8888A0]">
                        v{plugin.Version}
                      </span>
                      {plugin.Category && (
                        <span className="badge badge-blue">{plugin.Category}</span>
                      )}
                    </div>
                    <p className="mt-1 text-xs text-[#666680]">{plugin.Description}</p>
                  </div>
                  <button
                    onClick={() => handleInstall(plugin.Id)}
                    disabled={isInstalled || installingId === plugin.Id}
                    className={`btn-primary inline-flex items-center gap-2 text-sm ${
                      isInstalled ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    {installingId === plugin.Id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Download className="h-4 w-4" />
                    )}
                    {isInstalled ? 'Installed' : 'Install'}
                  </button>
                </div>
              );
            })}
            {filteredCatalog.length === 0 && (
              <div className="card flex flex-col items-center py-16">
                <Puzzle className="mb-3 h-10 w-10 text-[#444460]" />
                <p className="text-sm text-[#666680]">No plugins match your search</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
