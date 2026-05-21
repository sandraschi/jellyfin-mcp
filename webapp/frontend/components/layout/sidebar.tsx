'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import {
  Home,
  Library,
  Film,
  Search,
  Play,
  Puzzle,
  Tv,
  Users,
  Settings,
  Brain,
  MessageSquare,
  HelpCircle,
  Activity,
} from 'lucide-react';

const navItems = [
  { href: '/', label: 'Overview', icon: Home },
  { href: '/libraries', label: 'Libraries', icon: Library },
  { href: '/media/Movies', label: 'Media Browser', icon: Film },
  { href: '/search', label: 'Search', icon: Search },
  { href: '/playback', label: 'Playback', icon: Play, dot: true },
  { href: '/plugins', label: 'Plugins', icon: Puzzle },
  { href: '/livetv', label: 'Live TV', icon: Tv },
  { href: '/users', label: 'Users', icon: Users },
  { href: '/settings', label: 'Settings', icon: Settings },
  { href: '/rag', label: 'RAG Search', icon: Brain },
  { href: '/chat', label: 'AI Chat', icon: MessageSquare },
  { href: '/help', label: 'Help', icon: HelpCircle },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-[#ffffff08] bg-jellyfin-dark">
      <div className="flex h-16 items-center gap-3 border-b border-[#ffffff08] px-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-jellyfin-purple to-jellyfin-blue">
          <Activity className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight text-white">jellyfin-mcp</h1>
          <p className="text-[10px] font-medium uppercase tracking-widest text-jellyfin-purple">
            Jellyfin++
          </p>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href ||
            (item.href !== '/' && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                'group mb-1 flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-jellyfin-purple/15 text-jellyfin-purple-light'
                  : 'text-[#8888A0] hover:bg-jellyfin-surface hover:text-white',
              )}
            >
              <Icon
                className={clsx(
                  'h-4 w-4 transition-colors',
                  isActive ? 'text-jellyfin-purple' : 'text-[#666680] group-hover:text-jellyfin-purple',
                )}
              />
              <span className="flex-1">{item.label}</span>
              {item.dot && (
                <span className="flex h-2 w-2 items-center justify-center">
                  <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-green-400" />
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-[#ffffff08] px-5 py-4">
        <div className="flex items-center gap-2 text-xs text-[#555570]">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-green-500" />
          Jellyfin++
        </div>
      </div>
    </aside>
  );
}
