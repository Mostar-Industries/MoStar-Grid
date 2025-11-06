// src/examples/index.ts
import { MoScript } from '../moscripts/MoScript';
import { ScrollRegistry } from '../moscripts/engine';
import { runMoScript, getAuditLog, clearAuditLog } from '../moscripts/engine';

// Example scripts
const authScript: MoScript<{ username: string; password: string }, { user: string; status: 'ok' | 'deny' }> = {
  id: 'mo-user-authentication-v1',
  name: 'User Authentication Handler',
  trigger: 'onUserLoginAttempt',
  inputs: ['username', 'password'],
  async logic({ username, password }) {
    const ok = username.length > 0 && password === 's3cret';
    return { user: username, status: ok ? 'ok' : 'deny' };
  },
  voiceLine(res) {
    return `Authentication for user ${res.user} status: ${res.status}`;
  },
  sass: true
};

const echoScript: MoScript<{ text: string }, { echoed: string }> = {
  id: 'mo-echo-v1',
  name: 'Echo Message',
  trigger: 'onUserMessage',
  inputs: ['text'],
  logic({ text }) { return { echoed: text }; },
  voiceLine(r) { return `Echoed: ${r.echoed}`; },
  sass: false
};

async function main() {
  clearAuditLog();
  const reg = new ScrollRegistry();
  reg.register(authScript);
  reg.register(echoScript);

  // Unsigned call (lower score). For demo, no signature/secret provided.
  const r1 = await runMoScript(reg, 'mo-user-authentication-v1', { username: 'alice', password: 's3cret' }, {
    evidence: ['https://internal.example/policy/auth'],
    topic: 'security'
  });
  console.log('Result #1:', r1);

  // Signed call (higher score). Example signature using known secret.
  const claim = `MoScript mo-echo-v1 triggered=${echoScript.trigger} sass=${echoScript.sass}`;
  const timestamp = new Date().toISOString();
  const secret = 'demo-secret';
  const signature = await demoSign(claim + '\n' + timestamp, secret);

  const r2 = await runMoScript(reg, 'mo-echo-v1', { text: 'hi grid' }, {
    evidence: ['https://handbook.example/echo'],
    topic: 'general',
    timestamp, signature, secret
  });
  console.log('Result #2:', r2);

  console.log('\nAudit log size:', getAuditLog().length);
}

main().catch(e => console.error(e));

// Demo-only HMAC helper (mirrors provenance.ts behavior) for generating signatures.
async function demoSign(message: string, secret: string): Promise<string> {
  const g: any = globalThis as any;
  if (g.crypto?.subtle) {
    const key = await g.crypto.subtle.importKey('raw', new TextEncoder().encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
    const sig = await g.crypto.subtle.sign('HMAC', key, new TextEncoder().encode(message));
    // Fix: Use the global 'g' object to check for and use Buffer to prevent type errors.
    return (typeof g.Buffer !== 'undefined' ? g.Buffer.from(new Uint8Array(sig)).toString('base64')
                                          : btoa(String.fromCharCode(...new Uint8Array(sig))));
  } else {
    const { createHmac } = await import('node:crypto');
    const h = createHmac('sha256', secret);
    h.update(message);
    return h.digest('base64');
  }
}