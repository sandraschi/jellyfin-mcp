'use client';

import { useState, useEffect, useCallback } from 'react';
import { Users, UserPlus, Trash2, Shield, User } from 'lucide-react';
import { fetchUsers, createUser, deleteUser } from '@/utils/api';

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newUser, setNewUser] = useState({ name: '', password: '' });
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await fetchUsers();
      setUsers(data as any[]);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleCreate = async () => {
    if (!newUser.name) return;
    setCreating(true);
    try {
      await createUser(newUser);
      setNewUser({ name: '', password: '' });
      setShowCreate(false);
      load();
    } catch (err: any) {
      setError(err.message || 'Failed to create user');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (userId: string) => {
    try {
      await deleteUser(userId);
      load();
    } catch (err: any) {
      setError(err.message || 'Failed to delete user');
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Users</h2>
          <p className="mt-1 text-sm text-[#777790]">{users.length} users</p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="btn-primary inline-flex items-center gap-2 text-sm"
        >
          <UserPlus className="h-4 w-4" />
          Create User
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      {showCreate && (
        <div className="card space-y-4">
          <h3 className="font-medium text-white">Create New User</h3>
          <div className="flex gap-3">
            <input
              type="text"
              value={newUser.name}
              onChange={(e) => setNewUser((p) => ({ ...p, name: e.target.value }))}
              placeholder="Username"
              className="input-field flex-1"
            />
            <input
              type="password"
              value={newUser.password}
              onChange={(e) => setNewUser((p) => ({ ...p, password: e.target.value }))}
              placeholder="Password"
              className="input-field flex-1"
            />
            <button
              onClick={handleCreate}
              disabled={creating || !newUser.name}
              className="btn-primary"
            >
              {creating ? 'Creating...' : 'Create'}
            </button>
          </div>
        </div>
      )}

      {loading && (
        <div className="animate-pulse space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-lg bg-jellyfin-surface-light" />
                <div className="space-y-2">
                  <div className="h-4 w-32 rounded bg-jellyfin-surface-light" />
                  <div className="h-3 w-20 rounded bg-jellyfin-surface-light" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && (
        <div className="space-y-3">
          {users.map((user: any) => (
            <div key={user.Id || user.Name} className="card flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-jellyfin-purple/15">
                  <User className="h-5 w-5 text-jellyfin-purple" />
                </div>
                <div>
                  <p className="font-medium text-white">{user.Name}</p>
                  <div className="flex items-center gap-2 text-xs text-[#666680]">
                    <Shield className="h-3 w-3" />
                    {user.Policy?.IsAdministrator ? 'Admin' : 'User'}
                    {user.LastActivityDate && (
                      <span>· Last active: {user.LastActivityDate}</span>
                    )}
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleDelete(user.Id)}
                className="rounded-lg p-2 text-[#555570] transition-colors hover:bg-red-500/10 hover:text-red-400"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
          {users.length === 0 && (
            <div className="card flex flex-col items-center py-16">
              <Users className="mb-3 h-10 w-10 text-[#444460]" />
              <p className="text-sm text-[#666680]">No users found</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
