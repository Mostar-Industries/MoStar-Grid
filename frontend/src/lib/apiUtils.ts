// Shared helpers for working with API responses.

/**
 * Extract a text response from a backend API payload, trying common field
 * names in priority order and falling back to `fallback` when none are present.
 */
export function extractApiResponse(
  data: Record<string, unknown>,
  fallback = "."
): string {
  const value = data.response ?? data.result ?? data.reply ?? data.answer ?? fallback;
  return typeof value === "string" ? value : JSON.stringify(value);
}
