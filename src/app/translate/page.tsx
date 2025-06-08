'use client';

import { useState, useCallback } from 'react';
import { LanguageSelector } from '@/components/language';
import type { TranslationResponse } from '@/types/bhashini';

export default function TranslationDemo() {
  const [sourceText, setSourceText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [sourceLanguage, setSourceLanguage] = useState('en');
  const [targetLanguage, setTargetLanguage] = useState('hi');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTranslate = useCallback(async () => {
    if (!sourceText.trim()) return;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: sourceText,
          sourceLanguage,
          targetLanguage,
        }),
      });

      if (!response.ok) {
        throw new Error('Translation failed');
      }

      const data: TranslationResponse = await response.json();
      setTranslatedText(data.translatedText);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Translation error:', err);
    } finally {
      setLoading(false);
    }
  }, [sourceText, sourceLanguage, targetLanguage]);

  const handleSourceLanguageChange = (language: string) => {
    setSourceLanguage(language);
    setTranslatedText(''); // Clear translation when source language changes
  };

  const handleTargetLanguageChange = (language: string) => {
    setTargetLanguage(language);
    setTranslatedText(''); // Clear translation when target language changes
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">Translation Service</h1>

      {/* Language Selector */}
      <div className="mb-6">
        <LanguageSelector
          onSourceLanguageChange={handleSourceLanguageChange}
          onTargetLanguageChange={handleTargetLanguageChange}
          initialSourceLanguage={sourceLanguage}
          initialTargetLanguage={targetLanguage}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Source Text */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Source Text
          </label>
          <textarea
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            className="w-full h-48 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            placeholder="Enter text to translate..."
            style={{ direction: sourceLanguage === 'ur' ? 'rtl' : 'ltr' }}
          />
        </div>

        {/* Translated Text */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Translated Text
          </label>
          <div
            className={`w-full h-48 p-3 border rounded-lg bg-gray-50 overflow-auto ${
              loading ? 'animate-pulse' : ''
            }`}
            style={{ direction: targetLanguage === 'ur' ? 'rtl' : 'ltr' }}
          >
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent" />
              </div>
            ) : (
              translatedText || 'Translation will appear here...'
            )}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Translate Button */}
      <div className="mt-6 flex justify-center">
        <button
          onClick={handleTranslate}
          disabled={loading || !sourceText.trim()}
          className="px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Translating...' : 'Translate'}
        </button>
      </div>
    </div>
  );
} 