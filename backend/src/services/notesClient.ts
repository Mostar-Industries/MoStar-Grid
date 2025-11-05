/**
 * Notes API Client
 * Uses environment-driven API base URL
 */

import { API_BASE } from '../lib/env';

export type Note = {
  id: number;
  title: string;
  body: string;
  created_at: string;
};

/**
 * Fetch all notes from the API
 */
export async function getNotes(): Promise<Note[]> {
  const res = await fetch(`${API_BASE}/notes`);
  if (!res.ok) {
    throw new Error(`GET ${API_BASE}/notes failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

/**
 * Create a new note
 */
export async function createNote(title: string, body: string): Promise<Note> {
  const res = await fetch(`${API_BASE}/notes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, body }),
  });
  if (!res.ok) {
    throw new Error(`POST ${API_BASE}/notes failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

/**
 * Delete a note by ID
 */
export async function deleteNote(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/notes/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error(`DELETE ${API_BASE}/notes/${id} failed: ${res.status} ${res.statusText}`);
  }
}

/**
 * Update a note
 */
export async function updateNote(id: number, title: string, body: string): Promise<Note> {
  const res = await fetch(`${API_BASE}/notes/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, body }),
  });
  if (!res.ok) {
    throw new Error(`PUT ${API_BASE}/notes/${id} failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}
