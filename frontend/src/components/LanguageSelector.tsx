import React from 'react';
import { FaLanguage } from 'react-icons/fa';
import useLanguageStore, { SUPPORTED_LANGUAGES } from '../store/languageStore';

const LanguageSelector: React.FC = () => {
  const { currentLanguage, setLanguage } = useLanguageStore();

  const handleLanguageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = SUPPORTED_LANGUAGES.find(lang => lang.code === event.target.value);
    if (selected) {
      setLanguage(selected);
    }
  };

  return (
    <div className="flex items-center space-x-4 p-4 bg-white rounded-lg shadow-sm">
      <div className="flex items-center">
        <FaLanguage className="text-gray-500 mr-2" />
        <select
          value={currentLanguage.code}
          onChange={handleLanguageChange}
          className="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {SUPPORTED_LANGUAGES.map((language) => (
            <option key={language.code} value={language.code}>
              {language.name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default LanguageSelector; 