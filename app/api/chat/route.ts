import { NextResponse } from 'next/server';
import { OpenAIService } from '@/services/openai-service';
import { Message } from '@/types/chat';

export async function POST(request: Request) {
  try {
    const { messages } = await request.json();
    const openaiService = new OpenAIService();
    
    const response = await openaiService.getLegalResponse(messages);
    
    return NextResponse.json({ message: response });
  } catch (error) {
    console.error('Chat API Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 