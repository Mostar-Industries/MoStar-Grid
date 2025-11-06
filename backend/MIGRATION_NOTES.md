# Frontend Migration to /web

**Date**: November 6, 2025  
**Status**: ✅ Complete

## What Changed

Moved the React/Vite frontend from `backend/` to `/web` for cleaner project structure.

### Files Moved
- `index.html`
- `package.json`
- `vite.config.ts`
- `tsconfig.json`
- `tailwind.config.ts`
- `postcss.config.js`
- `src/` (entire frontend source)

### Project Structure (After)

```
MoStar-Grid/
├── backend/           # Python FastAPI server only
│   ├── grid_main.py
│   ├── server/
│   ├── pantheon/
│   └── ...
├── web/               # React/Vite frontend (NEW LOCATION)
│   ├── src/
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
├── docs/              # Doctrine markdown files
└── tools/             # Migration scripts
```

## New Dev Commands

### Terminal 1 - Backend (Python API)
```powershell
cd backend
python grid_main.py
```
The backend runs on **http://localhost:7000**

### Terminal 2 - Frontend (React)
```powershell
cd web
npm install
npm run dev
```
The frontend runs on **http://localhost:5173**

## Configuration

### ✅ Vite Proxy (Already Configured)
The Vite config at `web/vite.config.ts` proxies API calls:
- `/api` → `http://127.0.0.1:8000`
- `/ws` → `ws://127.0.0.1:8000`

This eliminates CORS issues during development.

### ✅ Tailwind (Already Configured)
The Tailwind config at `web/tailwind.config.ts` is correctly scoped to `/web`.

### ✅ No Import Changes Needed
No doctrine imports (`*.md?raw`) were found that needed path updates.

## Why This Change?

### Before (Pragmatic but Confusing)
- Frontend lived in `backend/` for quick dev loop
- Single location, zero CORS drama
- Confusing naming: "backend" contained frontend code

### After (Clean Separation)
- Standard project layout (industry norm)
- Clear separation of concerns
- Easier onboarding for new contributors
- Still maintains zero CORS via Vite proxy
- Still dockerless, fast dev loop

## Rollback (if needed)

The migration script automatically archives conflicts to `__attic__/frontend-move-*`.  
To rollback, reverse the file moves from `/web` back to `/backend`.

## Notes

- Backend API remains on port 7000 (was 8000, now 7000)
- Frontend dev server on port 5173
- No changes to database or API code
- All existing functionality preserved
