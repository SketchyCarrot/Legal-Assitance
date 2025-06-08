import type {
  BhashiniConfig,
  TranslationRequest,
  TranslationResponse,
  BatchTranslationRequest,
  LanguageDetectionResult,
  TranslationCache,
  SupportedLanguage
} from '@/types/bhashini';

class BhashiniService {
  private static instance: BhashiniService;
  private config: BhashiniConfig;
  private cache: Map<string, TranslationCache>;
  private readonly CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 24 hours

  private constructor(config: BhashiniConfig) {
    this.config = config;
    this.cache = new Map();
  }

  public static getInstance(config?: BhashiniConfig): BhashiniService {
    if (!BhashiniService.instance && config) {
      BhashiniService.instance = new BhashiniService(config);
    }
    return BhashiniService.instance;
  }

  private generateCacheKey(text: string, sourceLanguage: string, targetLanguage: string): string {
    return `${sourceLanguage}:${targetLanguage}:${text}`;
  }

  private getCachedTranslation(key: string): TranslationResponse | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    // Check if cache has expired
    if (Date.now() - cached.timestamp > cached.expiresIn) {
      this.cache.delete(key);
      return null;
    }

    return {
      translatedText: cached.translatedText,
      confidence: 1, // Cached translations are considered highly confident
    };
  }

  private setCachedTranslation(
    key: string,
    sourceLanguage: string,
    targetLanguage: string,
    translatedText: string
  ): void {
    this.cache.set(key, {
      key,
      sourceLanguage,
      targetLanguage,
      translatedText,
      timestamp: Date.now(),
      expiresIn: this.CACHE_EXPIRY
    });
  }

  public async detectLanguage(text: string): Promise<LanguageDetectionResult> {
    try {
      const response = await fetch(`${this.config.apiEndpoint}/language-detection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`,
          'User-ID': this.config.userId
        },
        body: JSON.stringify({ text })
      });

      if (!response.ok) {
        throw new Error(`Language detection failed: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        detectedLanguage: data.language,
        confidence: data.confidence,
        alternatives: data.alternatives || []
      };
    } catch (error) {
      console.error('Language detection error:', error);
      throw error;
    }
  }

  public async translateText(request: TranslationRequest): Promise<TranslationResponse> {
    const cacheKey = this.generateCacheKey(request.text, request.sourceLanguage, request.targetLanguage);
    
    // Check cache first
    const cached = this.getCachedTranslation(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${this.config.apiEndpoint}/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`,
          'User-ID': this.config.userId,
          'ULCA-API-Key': this.config.ulcaApiKey
        },
        body: JSON.stringify({
          ...request,
          domain: request.domain || 'general'
        })
      });

      if (!response.ok) {
        throw new Error(`Translation failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Cache the successful translation
      this.setCachedTranslation(
        cacheKey,
        request.sourceLanguage,
        request.targetLanguage,
        data.translatedText
      );

      return {
        translatedText: data.translatedText,
        confidence: data.confidence || 1,
        alternatives: data.alternatives,
        detectedLanguage: data.detectedLanguage
      };
    } catch (error) {
      console.error('Translation error:', error);
      throw error;
    }
  }

  public async translateBatch(request: BatchTranslationRequest): Promise<TranslationResponse[]> {
    try {
      const translations = await Promise.all(
        request.texts.map(text =>
          this.translateText({
            text,
            sourceLanguage: request.sourceLanguage,
            targetLanguage: request.targetLanguage,
            domain: request.domain
          })
        )
      );

      return translations;
    } catch (error) {
      console.error('Batch translation error:', error);
      throw error;
    }
  }

  public async validateTranslation(
    originalText: string,
    translatedText: string,
    sourceLanguage: string,
    targetLanguage: string
  ): Promise<number> {
    try {
      const response = await fetch(`${this.config.apiEndpoint}/validate-translation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`,
          'User-ID': this.config.userId
        },
        body: JSON.stringify({
          originalText,
          translatedText,
          sourceLanguage,
          targetLanguage
        })
      });

      if (!response.ok) {
        throw new Error(`Translation validation failed: ${response.statusText}`);
      }

      const data = await response.json();
      return data.quality || 0;
    } catch (error) {
      console.error('Translation validation error:', error);
      throw error;
    }
  }

  public getSupportedLanguages(): SupportedLanguage[] {
    return [
      { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', direction: 'ltr' },
      { code: 'en', name: 'English', nativeName: 'English', direction: 'ltr' },
      { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', direction: 'ltr' },
      { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', direction: 'ltr' },
      { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', direction: 'ltr' },
      { code: 'mr', name: 'Marathi', nativeName: 'मराठी', direction: 'ltr' },
      { code: 'ur', name: 'Urdu', nativeName: 'اردو', direction: 'rtl' },
      { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', direction: 'ltr' },
      { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', direction: 'ltr' },
      { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', direction: 'ltr' },
      { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', direction: 'ltr' },
      { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ', direction: 'ltr' }
    ];
  }
}

export default BhashiniService; 