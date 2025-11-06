// Media utilities for audio/video processing

export function createBlob(data: any, mimeType: string): Blob {
  if (data instanceof Blob) {
    return data;
  }
  
  if (data instanceof ArrayBuffer) {
    return new Blob([data], { type: mimeType });
  }
  
  if (ArrayBuffer.isView(data)) {
    return new Blob([data.buffer as ArrayBuffer], { type: mimeType });
  }
  
  return new Blob([data], { type: mimeType });
}

export function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}
