export interface BhashiniConfig {
  apiKey: string;
  userId: string;
  apiEndpoint: string;
  ulcaApiKey: string;
}

export interface TranslationRequest {
  text: string;
  sourceLanguage: string;
  targetLanguage: string;
  domain?: string;
}

export interface TranslationResponse {
  translatedText: string;
  detectedLanguage?: string;
  confidence: number;
  alternatives?: string[];
}

export interface BatchTranslationRequest {
  texts: string[];
  sourceLanguage: string;
  targetLanguage: string;
  domain?: string;
}

export interface SupportedLanguage {
  code: string;
  name: string;
  nativeName: string;
  direction: 'ltr' | 'rtl';
}

export interface TranslationCache {
  key: string;
  sourceLanguage: string;
  targetLanguage: string;
  translatedText: string;
  timestamp: number;
  expiresIn: number;
}

export interface LanguageDetectionResult {
  detectedLanguage: string;
  confidence: number;
  alternatives: Array<{
    language: string;
    confidence: number;
  }>;
} 