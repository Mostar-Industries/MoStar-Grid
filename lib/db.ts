// lib/db.ts
import { Scroll } from '../types/moscript';
import { WooTraceLog, Note } from '../types';

/**
 * --- CRITICAL ARCHITECTURE NOTE ---
 * This file demonstrates the LOGIC for database persistence. The application is currently
 * pure client-side, and directly connecting to a database from the browser is a major
 * security vulnerability and the cause of the "No database connection string" error.
 *
 * The functions below have been modified to LOG their intended actions to the console
 * instead of making a real database call. This resolves the startup crash.
 *
 * BUILDER ACTION REQUIRED:
 * 1. Create a secure backend with API endpoints (e.g., using Vercel Serverless Functions).
 * 2. Move the commented-out database logic (the `await sql...` blocks from the previous
 *    version) into those endpoints.
 * 3. Update these functions to use `fetch` to call your new backend API endpoints.
 */

/**
 * SIMULATES saving a scroll to the 'scrolls' table.
 * In a real backend, this would connect to the Neon database via a secure API endpoint.
 * @param scroll The scroll object to save.
 */
export async function saveScroll(scroll: Scroll): Promise<void> {
    console.log(`[DB SIMULATION] Intending to save scroll to database:`, scroll);
    // This is a placeholder. In a real application, you would make a fetch call here:
    /*
    await fetch('/api/save-scroll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scroll),
    });
    */
    return Promise.resolve();
}

/**
 * SIMULATES logging a Woo trace to the 'woo_trace' table.
 * In a real backend, this would connect to the Neon database via a secure API endpoint.
 * @param trace The WooTraceLog object to save.
 */
export async function logWooTrace(trace: WooTraceLog): Promise<void> {
    console.log(`[DB SIMULATION] Intending to log Woo trace to database:`, trace);
    // This is a placeholder. In a real application, you would make a fetch call here:
    /*
    await fetch('/api/log-trace', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(trace),
    });
    */
    return Promise.resolve();
}


// --- Local API Gateway Integration ---
// NOTE: These functions now call the local Python API gateway, which is proxied by Vite.
// This avoids CORS errors and securely handles the database connection on the server-side.

export async function fetchNotes(): Promise<Note[]> {
    console.log('[Local API] Fetching notes...');
    const response = await fetch('/api/notes');
    if (!response.ok) {
        const errorText = await response.text().catch(() => 'Could not read error response.');
        throw new Error(`API Error: ${response.status} ${response.statusText}. ${errorText}`);
    }
    const data = await response.json();
    return data as Note[];
}

export async function createNote(title: string): Promise<Note | null> {
    console.log(`[Local API] Creating note with title: ${title}`);
    const response = await fetch('/api/notes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        // The python server expects `title` and `body` (not null).
        body: JSON.stringify({ title, body: ' ' }),
    });

    if (!response.ok) {
        const errorText = await response.text().catch(() => 'Could not read error response.');
        throw new Error(`API Error: ${response.status} ${response.statusText}. ${errorText}`);
    }

    const data = await response.json();
    return data as Note;
}