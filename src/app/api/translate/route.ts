import { NextResponse } from 'next/server';
import BhashiniService from '@/lib/bhashini';
import type { TranslationRequest, BatchTranslationRequest } from '@/types/bhashini';

// Initialize Bhashini service
const bhashini = BhashiniService.getInstance({
  apiKey: process.env.BHASHINI_API_KEY || '',
  userId: process.env.BHASHINI_USER_ID || '',
  apiEndpoint: process.env.BHASHINI_API_ENDPOINT || '',
  ulcaApiKey: process.env.BHASHINI_ULCA_API_KEY || ''
});

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { batch = false } = body;

    // Validate request
    if (batch && !Array.isArray(body.texts)) {
      return NextResponse.json(
        { error: 'Batch translation requires an array of texts' },
        { status: 400 }
      );
    }

    if (!batch && !body.text) {
      return NextResponse.json(
        { error: 'Text is required for translation' },
        { status: 400 }
      );
    }

    // Process translation
    if (batch) {
      const batchRequest: BatchTranslationRequest = {
        texts: body.texts,
        sourceLanguage: body.sourceLanguage,
        targetLanguage: body.targetLanguage,
        domain: body.domain
      };

      const translations = await bhashini.translateBatch(batchRequest);
      return NextResponse.json(translations);
    } else {
      const translationRequest: TranslationRequest = {
        text: body.text,
        sourceLanguage: body.sourceLanguage,
        targetLanguage: body.targetLanguage,
        domain: body.domain
      };

      const translation = await bhashini.translateText(translationRequest);
      return NextResponse.json(translation);
    }
  } catch (error) {
    console.error('Translation API error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Translation failed' },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const languages = bhashini.getSupportedLanguages();
    return NextResponse.json(languages);
  } catch (error) {
    console.error('Error fetching supported languages:', error);
    return NextResponse.json(
      { error: 'Failed to fetch supported languages' },
      { status: 500 }
    );
  }
} 