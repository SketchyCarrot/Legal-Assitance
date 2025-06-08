import { NextResponse } from 'next/server';
import AzureOpenAIService from '@/lib/azureOpenAI';
import type { LegalQueryRequest } from '@/types/azure';

// Initialize Azure OpenAI service
const azureOpenAI = AzureOpenAIService.getInstance({
  apiKey: process.env.AZURE_OPENAI_API_KEY || '',
  endpoint: process.env.AZURE_OPENAI_ENDPOINT || '',
  deploymentName: process.env.AZURE_OPENAI_DEPLOYMENT_NAME || '',
  apiVersion: process.env.AZURE_OPENAI_API_VERSION || '2023-05-15'
});

export async function POST(request: Request) {
  try {
    // Rate limiting check (implement if needed)
    const rateLimitHeader = request.headers.get('x-api-key');
    if (!rateLimitHeader || rateLimitHeader !== process.env.API_KEY) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Parse request body
    const body: LegalQueryRequest = await request.json();

    // Validate request
    if (!body.query) {
      return NextResponse.json({ error: 'Query is required' }, { status: 400 });
    }

    // Process query
    const response = await azureOpenAI.processLegalQuery(body);

    // Return response
    return NextResponse.json(response);
  } catch (error) {
    console.error('Error in Azure OpenAI API route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json(
    { status: 'Azure OpenAI API is running' },
    { status: 200 }
  );
} 