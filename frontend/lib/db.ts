// Database API client for notes
import { Note } from '../types';

const API_BASE = '/api';

export async function fetchNotes(): Promise<Note[]> {
  try {
    const response = await fetch(`${API_BASE}/notes`);
    if (!response.ok) {
      throw new Error(`Failed to fetch notes: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching notes:', error);
    return [];
  }
}

export async function createNote(title: string, content: string = ''): Promise<Note | null> {
  try {
    const response = await fetch(`${API_BASE}/notes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, content }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create note: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating note:', error);
    return null;
  }
}
