'use client';

import { HelpCircle, BookOpen, Terminal, MessageSquare, Zap, ExternalLink } from 'lucide-react';

const tools = [
  {
    name: 'jellyfin_search_library',
    description: 'Search across all libraries with semantic matching',
    example: 'Search for "Christopher Nolan movies" across your library',
  },
  {
    name: 'jellyfin_get_media_info',
    description: 'Get detailed information for a specific media item',
    example: 'Get metadata, cast, and reviews for a specific movie or show',
  },
  {
    name: 'jellyfin_play_media',
    description: 'Start playback on a specific device',
    example: 'Play Inception on Living Room TV',
  },
  {
    name: 'jellyfin_control_playback',
    description: 'Control active playback sessions',
    example: 'Pause, resume, seek, or stop the current session',
  },
  {
    name: 'jellyfin_manage_users',
    description: 'CRUD operations for Jellyfin users',
    example: 'Create a guest account with restricted media access',
  },
  {
    name: 'jellyfin_rag_search',
    description: 'Semantic search using vector embeddings',
    example: 'Find "dark atmospheric thrillers with plot twists"',
  },
  {
    name: 'jellyfin_manage_plugins',
    description: 'Install, enable, and disable plugins',
    example: 'Install the OpenSubtitles plugin for auto-downloading subtitles',
  },
  {
    name: 'jellyfin_live_tv',
    description: 'Access Live TV streams and DVR recordings',
    example: 'List all channels and schedule a recording',
  },
];

const faq = [
  {
    q: 'How do I connect jellyfin-mcp to my Jellyfin server?',
    a: 'Go to Settings and enter your Jellyfin server URL and API key. You can generate an API key from the Jellyfin dashboard under Admin Dashboard → API Keys.',
  },
  {
    q: 'What AI models are supported for the chat?',
    a: 'We support GPT-4o (OpenAI), Claude Opus 4 (Anthropic), and Llama 3 (Local via Ollama). Configure your API keys in Settings.',
  },
  {
    q: 'How does RAG search work?',
    a: 'RAG (Retrieval-Augmented Generation) indexes your media library metadata as vector embeddings. When you search, it uses semantic similarity to find relevant content beyond simple keyword matching.',
  },
  {
    q: 'What is the WebSocket connection used for?',
    a: 'The real-time WebSocket connection on the Playback Dashboard provides live session updates, play state changes, and transcode status without polling.',
  },
  {
    q: 'Can I manage multiple Jellyfin servers?',
    a: 'Currently jellyfin-mcp connects to one server at a time. Multi-server support is on the roadmap.',
  },
];

export default function HelpPage() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Help &amp; Reference</h2>
        <p className="mt-1 text-sm text-[#777790]">Documentation and tool reference for jellyfin-mcp</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-green-500/15">
              <Zap className="h-5 w-5 text-green-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Quickstart</h3>
              <p className="text-xs text-[#666680]">Get up and running in minutes</p>
            </div>
          </div>
          <ol className="ml-5 list-decimal space-y-2 text-sm text-[#999]">
            <li>Install and launch the Jellyfin server</li>
            <li>Configure your connection in Settings</li>
            <li>Set up your media libraries in the Jellyfin dashboard</li>
            <li>Use the AI Chat to ask questions about your library</li>
            <li>Manage playback from the Playback Dashboard</li>
          </ol>
        </div>

        <div className="card">
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-jellyfin-purple/15">
              <BookOpen className="h-5 w-5 text-jellyfin-purple" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Resources</h3>
              <p className="text-xs text-[#666680]">External links and documentation</p>
            </div>
          </div>
          <div className="space-y-2">
            {[
              { label: 'Jellyfin Documentation', url: 'https://jellyfin.org/docs' },
              { label: 'Jellyfin API Reference', url: 'https://api.jellyfin.org' },
              { label: 'MCP Protocol Spec', url: 'https://modelcontextprotocol.io' },
              { label: 'jellyfin-mcp GitHub', url: 'https://github.com/SandraSchipal/jellyfin-mcp' },
            ].map((link) => (
              <a
                key={link.url}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-[#999] transition-colors hover:bg-jellyfin-surface-light hover:text-white"
              >
                <ExternalLink className="h-3.5 w-3.5 text-jellyfin-purple" />
                {link.label}
              </a>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-jellyfin-blue/15">
            <Terminal className="h-5 w-5 text-jellyfin-blue" />
          </div>
          <div>
            <h3 className="font-semibold text-white">MCP Tool Reference</h3>
            <p className="text-xs text-[#666680]">{tools.length} available tools</p>
          </div>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {tools.map((tool) => (
            <div
              key={tool.name}
              className="rounded-lg border border-[#ffffff08] bg-jellyfin-darker/50 p-4 transition-colors hover:border-jellyfin-purple/15"
            >
              <code className="text-xs font-medium text-jellyfin-purple-light">{tool.name}</code>
              <p className="mt-1 text-xs text-[#999]">{tool.description}</p>
              <p className="mt-2 rounded-md bg-jellyfin-surface px-2 py-1 text-[11px] text-[#666680] font-mono">
                {tool.example}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-500/15">
            <MessageSquare className="h-5 w-5 text-amber-400" />
          </div>
          <div>
            <h3 className="font-semibold text-white">Frequently Asked Questions</h3>
          </div>
        </div>
        <div className="space-y-4">
          {faq.map((item) => (
            <div key={item.q} className="border-b border-[#ffffff06] pb-4 last:border-0 last:pb-0">
              <h4 className="text-sm font-medium text-white">{item.q}</h4>
              <p className="mt-1 text-xs leading-relaxed text-[#8888A0]">{item.a}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="card flex items-center gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-jellyfin-purple to-jellyfin-blue">
          <HelpCircle className="h-6 w-6 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-white">Need more help?</h3>
          <p className="text-sm text-[#777790]">
            Check the GitHub repository for issues, discussions, and the full documentation.
          </p>
        </div>
      </div>
    </div>
  );
}
