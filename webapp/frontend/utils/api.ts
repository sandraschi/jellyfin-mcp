/** Empty in dev (Next rewrites); direct backend URL in Tauri production build. */
export const API_BASE =
  process.env.NODE_ENV === 'development' ? '' : 'http://127.0.0.1:10934';

const BASE = `${API_BASE}/api`;

interface LibraryItem {
  id: string;
  name: string;
  type: string;
  itemCount: number;
}

interface MediaItem {
  Id: string;
  Name: string;
  Type: string;
  ProductionYear?: number;
  CommunityRating?: number;
  RunTimeTicks?: number;
}

interface Session {
  Id: string;
  UserName: string;
  Client: string;
  DeviceName: string;
  NowPlayingItem?: MediaItem;
  PlayState: {
    PositionTicks?: number;
    CanSeek: boolean;
    IsPaused: boolean;
    IsMuted: boolean;
    VolumeLevel: number;
    PlayMethod: string;
  };
}

interface PluginInfo {
  Name: string;
  Version: string;
  Description: string;
  Id: string;
}

interface PluginCatalogEntry extends PluginInfo {
  Category: string;
  IsPremium: boolean;
  TargetAbi: string;
}

interface SystemInfo {
  Version: string;
  OperatingSystem: string;
  Id: string;
  ServerName: string;
}

async function fetchAPI(path: string, options?: RequestInit) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `API error: ${res.status}`);
  }
  const json = await res.json();
  if (
    json &&
    typeof json === 'object' &&
    !Array.isArray(json) &&
    'success' in json &&
    'data' in json
  ) {
    return json.data;
  }
  return json;
}

function asItemArray<T>(data: unknown): T[] {
  if (Array.isArray(data)) {
    return data;
  }
  if (data && typeof data === 'object' && 'Items' in data) {
    const items = (data as { Items?: T[] }).Items;
    return Array.isArray(items) ? items : [];
  }
  return [];
}

export async function fetchSystemInfo(): Promise<SystemInfo> {
  return fetchAPI('/server/info');
}

export async function fetchLibraries(): Promise<LibraryItem[]> {
  return fetchAPI('/libraries') || [];
}

export async function fetchLibraryItems(libraryId: string): Promise<MediaItem[]> {
  return fetchAPI(`/libraries/${libraryId}/items`) || [];
}

export async function fetchMedia(
  type: string,
  params?: Record<string, string>,
): Promise<{ Items: MediaItem[]; TotalRecordCount: number }> {
  const query = new URLSearchParams(params).toString();
  return fetchAPI(`/media/${type}${query ? `?${query}` : ''}`);
}

export async function fetchSearch(query: string): Promise<MediaItem[]> {
  return fetchAPI(`/search?query=${encodeURIComponent(query)}`) || [];
}

export async function fetchSessions(): Promise<Session[]> {
  return fetchAPI('/playback/sessions') || [];
}

export async function sendPlaybackCommand(
  sessionId: string,
  command: string,
  seekPositionTicks?: number,
) {
  return fetchAPI(`/sessions/${sessionId}/command`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      command,
      ...(seekPositionTicks ? { seekPositionTicks } : {}),
    }),
  });
}

export async function fetchPlugins(): Promise<PluginInfo[]> {
  return fetchAPI('/plugins') || [];
}

export async function fetchPluginCatalog(): Promise<PluginCatalogEntry[]> {
  return fetchAPI('/plugins/catalog') || [];
}

export async function togglePlugin(pluginId: string, enabled: boolean) {
  return fetchAPI(`/plugins/${pluginId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enabled }),
  });
}

export async function installPlugin(pluginId: string) {
  return fetchAPI(`/plugins/${pluginId}/install`, { method: 'POST' });
}

export async function fetchLiveTvChannels() {
  return asItemArray(await fetchAPI('/livetv/channels'));
}

export async function fetchEpgGuide() {
  return asItemArray(await fetchAPI('/livetv/guide'));
}

export async function fetchRecordings() {
  return asItemArray(await fetchAPI('/livetv/recordings'));
}

export async function fetchUsers() {
  return fetchAPI('/users') || [];
}

export async function createUser(userData: Record<string, unknown>) {
  return fetchAPI('/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  });
}

export async function updateUser(userId: string, userData: Record<string, unknown>) {
  return fetchAPI(`/users/${userId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  });
}

export async function deleteUser(userId: string) {
  return fetchAPI(`/users/${userId}`, { method: 'DELETE' });
}

export async function fetchSettings() {
  return fetchAPI('/settings') || {};
}

export async function updateSettings(settings: Record<string, unknown>) {
  return fetchAPI('/settings', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
}

export async function fetchRagStatus() {
  return fetchAPI('/rag/status');
}

export async function syncRag() {
  return fetchAPI('/rag/sync', { method: 'POST' });
}

export async function searchRag(query: string) {
  return fetchAPI(`/rag/search?query=${encodeURIComponent(query)}`);
}

export async function fetchChatHistory() {
  return fetchAPI('/chat/history') || [];
}

export async function sendChatMessage(message: string, model?: string) {
  return fetchAPI('/chat/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, model }),
  });
}

export async function fetchHelpTopics() {
  return fetchAPI('/help/topics') || [];
}

export async function fetchRecentActivity(): Promise<
  { id: string; type: string; title: string; timestamp: string }[]
> {
  return fetchAPI('/activity/recent') || [];
}

export async function runScan() {
  return fetchAPI('/libraries/scan', { method: 'POST' });
}

export async function refreshMetadata() {
  return fetchAPI('/libraries/refresh-metadata', { method: 'POST' });
}

export { fetchAPI };
export type { LibraryItem, MediaItem, Session, PluginInfo, SystemInfo };
