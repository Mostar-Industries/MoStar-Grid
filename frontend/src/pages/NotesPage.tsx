import React, { useState, useEffect, useCallback } from 'react';
import { Note } from '../types';
import { fetchNotes, createNote } from '../lib/db';

const PageTitle: React.FC<{ title: string; children?: React.ReactNode }> = ({ title, children }) => (
    <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        {children && <div className="flex space-x-2">{children}</div>}
    </div>
);

const NotesPage: React.FC = () => {
    const [notes, setNotes] = useState<Note[]>([]);
    const [newNoteTitle, setNewNoteTitle] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [isCreating, setIsCreating] = useState(false);
    const [error, setError] = useState('');

    const loadNotes = useCallback(async () => {
        setIsLoading(true);
        setError('');
        try {
            const fetchedNotes = await fetchNotes();
            setNotes(fetchedNotes);
        } catch (err: any) {
            setError(`Failed to fetch notes. Please ensure the Python API server is running. Error: ${err.message}`);
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        loadNotes();
    }, [loadNotes]);

    const handleCreateNote = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newNoteTitle.trim() || isCreating) return;

        setIsCreating(true);
        setError('');
        try {
            const created = await createNote(newNoteTitle);
            if (created) {
                // To ensure chronological order, add new notes to the top
                setNotes(prev => [created, ...prev]);
                setNewNoteTitle('');
            } else {
                 throw new Error('Creation returned null.');
            }
        } catch (err: any) {
            setError(`Failed to create note. Error: ${err.message}`);
            console.error(err);
        } finally {
            setIsCreating(false);
        }
    };

    return (
        <div>
            <PageTitle title="GRID Logbook" />
            <p className="text-gray-400 mb-6 max-w-2xl">
                This page serves as the first live connection to the GRID's underlying database via a secure API.
                While other modules are simulated, this logbook demonstrates real data persistence.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-1">
                    <div className="grid-card rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-white mb-4">New Log Entry</h3>
                        <form onSubmit={handleCreateNote}>
                            <div className="mb-4">
                                <label htmlFor="note-title" className="block text-sm font-medium text-gray-300 mb-1">
                                    Title
                                </label>
                                <input
                                    id="note-title"
                                    type="text"
                                    value={newNoteTitle}
                                    onChange={(e) => setNewNoteTitle(e.target.value)}
                                    placeholder="Enter log entry..."
                                    className="w-full px-3 py-2 border border-gray-700 rounded-md bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={isCreating || !newNoteTitle.trim()}
                                className="gradient-bg w-full text-white px-4 py-2 rounded-md hover:opacity-90 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isCreating ? (
                                    <><i className="fas fa-spinner fa-spin mr-2" /> Saving...</>
                                ) : (
                                    <><i className="fas fa-plus-circle mr-2" /> Add Entry</>
                                )}
                            </button>
                        </form>
                    </div>
                </div>

                <div className="md:col-span-2">
                    <div className="grid-card rounded-lg p-6 min-h-[300px]">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-semibold text-white">Logbook History</h3>
                            <button onClick={loadNotes} disabled={isLoading} className="text-sm text-purple-400 hover:text-purple-300 disabled:opacity-50">
                                <i className={`fas fa-sync ${isLoading ? 'fa-spin' : ''} mr-2`}></i>
                                Refresh
                            </button>
                        </div>

                        {error && (
                            <div className="bg-red-900/50 border border-red-700 text-red-300 text-sm rounded-md p-3 text-center">
                                <p>{error}</p>
                            </div>
                        )}
                        
                        {isLoading ? (
                            <div className="text-center text-gray-400">
                                <i className="fas fa-spinner fa-spin mr-2" /> Loading logbook entries...
                            </div>
                        ) : !error && (
                            <ul className="space-y-3">
                                {notes.length > 0 ? notes.map((note) => (
                                    <li key={note.id} className="bg-gray-800/50 p-3 rounded-md border border-gray-700 flex justify-between items-center">
                                        <p className="text-gray-300">{note.title}</p>
                                        <span className="text-xs text-gray-500">{new Date(note.created_at).toLocaleString()}</span>
                                    </li>
                                )) : (
                                     <p className="text-center text-gray-500">No log entries found.</p>
                                )}
                            </ul>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default NotesPage;