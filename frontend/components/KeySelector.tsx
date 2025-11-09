import React, { useState, useEffect, useCallback } from 'react';
import Button from './Button';
import { AI_STUDIO_BILLING_DOCS_URL } from '../constants';

interface KeySelectorProps {
  onKeySelected: (hasKey: boolean) => void;
}

const KeySelector: React.FC<KeySelectorProps> = ({ onKeySelected }) => {
  const [keyStatus, setKeyStatus] = useState<'checking' | 'not_selected' | 'selected'>('checking');
  const [error, setError] = useState<string | null>(null);

  const checkApiKey = useCallback(async () => {
    if (typeof window.aistudio === 'undefined' || typeof window.aistudio.hasSelectedApiKey !== 'function') {
      setError('window.aistudio API is not available. Please ensure you are running in the correct environment or have it mocked.');
      setKeyStatus('not_selected'); // Assume not selected if API is missing
      onKeySelected(false);
      return;
    }

    setKeyStatus('checking');
    try {
      const hasKey = await window.aistudio.hasSelectedApiKey();
      setKeyStatus(hasKey ? 'selected' : 'not_selected');
      onKeySelected(hasKey);
    } catch (err: any) {
      setError(`Error checking API key: ${err.message}`);
      setKeyStatus('not_selected');
      onKeySelected(false);
    }
  }, [onKeySelected]);

  const openKeySelection = useCallback(async () => {
    if (typeof window.aistudio === 'undefined' || typeof window.aistudio.openSelectKey !== 'function') {
      setError('window.aistudio API is not available. Cannot open key selection dialog.');
      return;
    }

    setError(null);
    try {
      await window.aistudio.openSelectKey();
      // As per guidance: assume success after opening dialog.
      // A slight delay might be needed for the environment to update `process.env.API_KEY`
      // For this implementation, we will trust the `onKeySelected(true)` here.
      setKeyStatus('selected');
      onKeySelected(true);
    } catch (err: any) {
      setError(`Error opening key selection: ${err.message}`);
      // If the dialog failed to open, the key is still not selected
      setKeyStatus('not_selected');
      onKeySelected(false);
    }
  }, [onKeySelected]);

  useEffect(() => {
    checkApiKey();
  }, [checkApiKey]);

  if (keyStatus === 'checking') {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-card rounded-lg shadow-custom">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
        <p className="text-lg text-textSecondary">Checking API Key status...</p>
      </div>
    );
  }

  if (keyStatus === 'selected') {
    return null; // Key is selected, render nothing, parent component can proceed.
  }

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-card rounded-lg shadow-custom text-center space-y-4">
      <h2 className="text-2xl font-bold text-primary">Gemini API Key Required</h2>
      <p className="text-textSecondary">
        To use the advanced Gemini features, please select or provide an API key.
        This key is managed securely by the environment and is not stored in your browser.
      </p>
      <Button onClick={openKeySelection} size="large">
        Select Gemini API Key
      </Button>
      <p className="text-sm text-textSecondary">
        Learn more about API key management and billing:&nbsp;
        <a href={`https://${AI_STUDIO_BILLING_DOCS_URL}`} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
          Billing Documentation
        </a>
      </p>
      {error && <p className="text-red-500 mt-4">{error}</p>}
    </div>
  );
};

export default KeySelector;
