// Stubs for @google/genai imports when package is not available

export class GoogleGenAI {
  constructor(config?: any) {}
  
  getGenerativeModel(config: any) {
    return {
      generateContent: async (prompt: string) => {
        return {
          response: {
            text: () => `Generated content for: ${prompt}`,
          },
        };
      },
    };
  }
}

export interface Chat {
  sendMessage: (message: string) => Promise<any>;
}

export interface LiveServerMessage {
  type: string;
  data?: any;
}
