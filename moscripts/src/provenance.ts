// src/moscripts/provenance.ts

/** Cross-runtime HMAC-SHA256 verification (Node or WebCrypto). */
export async function verifyHMACBase64(message: string, signatureBase64: string, secret: string): Promise<boolean> {
  if (!signatureBase64 || !secret) return false;
  const expected = await hmacSha256Base64(message, secret);
  try {
    // Constant-time compare
    const a = base64ToBytes(signatureBase64);
    const b = base64ToBytes(expected);
    if (a.length !== b.length) return false;
    let diff = 0;
    for (let i = 0; i < a.length; i++) diff |= (a[i] ^ b[i]);
    return diff === 0;
  } catch {
    return false;
  }
}

function base64ToBytes(b64: string): Uint8Array {
  // Fix: Check for Buffer on the global object to avoid TypeScript errors in a browser context.
  if (typeof (globalThis as any).Buffer !== 'undefined') {
    return new Uint8Array((globalThis as any).Buffer.from(b64, 'base64'));
  }
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

async function hmacSha256Base64(message: string, secret: string): Promise<string> {
  // Web Crypto path
  const g: any = globalThis as any;
  if (g.crypto?.subtle) {
    const key = await g.crypto.subtle.importKey('raw', new TextEncoder().encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
    const sig = await g.crypto.subtle.sign('HMAC', key, new TextEncoder().encode(message));
    // Fix: Use the global 'g' object to check for and use Buffer to prevent type errors.
    return (typeof g.Buffer !== 'undefined' ? g.Buffer.from(new Uint8Array(sig)).toString('base64')
                                          : btoa(String.fromCharCode(...new Uint8Array(sig))));
  }
  // Node crypto path
  const { createHmac } = await import('node:crypto');
  const h = createHmac('sha256', secret);
  h.update(message);
  return h.digest('base64');
}