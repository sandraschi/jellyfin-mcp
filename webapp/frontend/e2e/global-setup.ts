import { execFileSync } from 'node:child_process';
import type { FullConfig } from '@playwright/test';

function freePort(port: number) {
  if (process.platform !== 'win32') {
    return;
  }
  const script = [
    `$conns = Get-NetTCPConnection -LocalPort ${port} -ErrorAction SilentlyContinue`,
    '| Where-Object { $_.OwningProcess -gt 4 }',
    '| Select-Object -ExpandProperty OwningProcess -Unique',
    'foreach ($procId in $conns) { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue }',
  ].join(' ');

  try {
    execFileSync('powershell.exe', ['-NoProfile', '-Command', script], { stdio: 'ignore' });
  } catch {
    // port already free
  }
}

export default async function globalSetup(_config: FullConfig) {
  freePort(10934);
  freePort(10935);
  await new Promise((resolve) => setTimeout(resolve, 1500));
}
