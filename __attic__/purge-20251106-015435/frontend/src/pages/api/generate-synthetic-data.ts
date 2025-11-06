export const config = { runtime: 'edge' };

export default async function handler(req: Request) {
	// Accept POST only
	if (req.method !== 'POST') {
		return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers: { 'Content-Type': 'application/json' } });
	}

	try {
		const body = await req.json();
		const backend = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:7000';
		const res = await fetch(`${backend.replace(/\/$/, '')}/api/generate-synthetic-data`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(body),
		});

		const data = await res.text();
		return new Response(data, { status: res.status, headers: { 'Content-Type': res.headers.get('content-type') || 'application/json' } });
	} catch (err: any) {
		return new Response(JSON.stringify({ error: err.message || 'proxy error' }), { status: 500, headers: { 'Content-Type': 'application/json' } });
	}
}
