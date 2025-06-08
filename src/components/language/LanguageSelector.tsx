'use client';

import React, { useState, useEffect } from 'react';
import type { SupportedLanguage } from '@/types/bhashini';

interface LanguageSelectorProps {
  onSourceLanguageChange: (language: string) => void;
  onTargetLanguageChange: (language: string) => void;
  initialSourceLanguage?: string;
  initialTargetLanguage?: string;
  className?: string;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  onSourceLanguageChange,
  onTargetLanguageChange,
  initialSourceLanguage = 'en',
  initialTargetLanguage = 'hi',
  className = ''
}) => {
  const [languages, setLanguages] = useState<SupportedLanguage[]>([]);
  const [sourceLanguage, setSourceLanguage] = useState(initialSourceLanguage);
  const [targetLanguage, setTargetLanguage] = useState(initialTargetLanguage);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSupportedLanguages();
  }, []);

  const fetchSupportedLanguages = async () => {
    try {
      const response = await fetch('/api/translate');
      if (!response.ok) throw new Error('Failed to fetch languages');
      const data = await response.json();
      setLanguages(data);
    } catch (err) {
      setError('Failed to load languages');
      console.error('Error fetching languages:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSourceLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newSourceLang = e.target.value;
    setSourceLanguage(newSourceLang);
    onSourceLanguageChange(newSourceLang);
  };

  const handleTargetLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newTargetLang = e.target.value;
    setTargetLanguage(newTargetLang);
    onTargetLanguageChange(newTargetLang);
  };

  const swapLanguages = () => {
    setSourceLanguage(targetLanguage);
    setTargetLanguage(sourceLanguage);
    onSourceLanguageChange(targetLanguage);
    onTargetLanguageChange(sourceLanguage);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-500 p-4">
        {error}
      </div>
    );
  }

  const getLanguageDirection = (languageCode: string): 'ltr' | 'rtl' => {
    const language = languages.find(lang => lang.code === languageCode);
    return language?.direction || 'ltr';
  };

  return (
    <div className={`flex items-center gap-4 ${className}`}>
      <div className="flex-1">
        <select
          value={sourceLanguage}
          onChange={handleSourceLanguageChange}
          className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          style={{ direction: getLanguageDirection(sourceLanguage) }}
        >
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.nativeName} ({lang.name})
            </option>
          ))}
        </select>
      </div>

      <button
        onClick={swapLanguages}
        className="p-2 hover:bg-gray-100 rounded-full"
        title="Swap languages"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
          />
        </svg>
      </button>

      <div className="flex-1">
        <select
          value={targetLanguage}
          onChange={handleTargetLanguageChange}
          className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          style={{ direction: getLanguageDirection(targetLanguage) }}
        >
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.nativeName} ({lang.name})
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default LanguageSelector; 