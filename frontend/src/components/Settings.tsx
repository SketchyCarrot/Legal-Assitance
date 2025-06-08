import React from 'react';
import { FaMoon, FaSun, FaLanguage, FaFont } from 'react-icons/fa';

interface SettingsProps {
  theme: 'light' | 'dark';
  fontSize: 'small' | 'medium' | 'large';
  language: string;
  onThemeChange: (theme: 'light' | 'dark') => void;
  onFontSizeChange: (size: 'small' | 'medium' | 'large') => void;
  onLanguageChange: (language: string) => void;
}

const Settings: React.FC<SettingsProps> = ({
  theme,
  fontSize,
  language,
  onThemeChange,
  onFontSizeChange,
  onLanguageChange,
}) => {
  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi' },
    { code: 'bn', name: 'Bengali' },
    { code: 'ta', name: 'Tamil' },
    { code: 'te', name: 'Telugu' },
    { code: 'mr', name: 'Marathi' },
    { code: 'gu', name: 'Gujarati' },
    { code: 'kn', name: 'Kannada' },
    { code: 'ml', name: 'Malayalam' },
    { code: 'pa', name: 'Punjabi' },
  ];

  return (
    <div className="space-y-8">
      {/* Theme Setting */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center">
          <FaMoon className="mr-2" /> Theme
        </h3>
        <div className="flex space-x-4">
          <button
            onClick={() => onThemeChange('light')}
            className={`flex items-center px-4 py-2 rounded-lg ${
              theme === 'light'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
          >
            <FaSun className="mr-2" /> Light
          </button>
          <button
            onClick={() => onThemeChange('dark')}
            className={`flex items-center px-4 py-2 rounded-lg ${
              theme === 'dark'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
          >
            <FaMoon className="mr-2" /> Dark
          </button>
        </div>
      </div>

      {/* Font Size Setting */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center">
          <FaFont className="mr-2" /> Font Size
        </h3>
        <div className="flex space-x-4">
          {['small', 'medium', 'large'].map((size) => (
            <button
              key={size}
              onClick={() => onFontSizeChange(size as 'small' | 'medium' | 'large')}
              className={`px-4 py-2 rounded-lg ${
                fontSize === size
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              }`}
            >
              {size.charAt(0).toUpperCase() + size.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Language Setting */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center">
          <FaLanguage className="mr-2" /> Language
        </h3>
        <select
          value={language}
          onChange={(e) => onLanguageChange(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>

      {/* Save Button */}
      <button
        className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors"
      >
        Save Settings
      </button>
    </div>
  );
};

export default Settings; 