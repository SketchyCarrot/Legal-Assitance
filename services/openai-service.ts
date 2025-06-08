import OpenAI from 'openai';
import { Message } from '@/types/chat';

export class OpenAIService {
  private client: OpenAI;

  constructor() {
    if (!process.env.AZURE_OPENAI_API_KEY) {
      throw new Error('AZURE_OPENAI_API_KEY is not set');
    }
    if (!process.env.AZURE_OPENAI_ENDPOINT) {
      throw new Error('AZURE_OPENAI_ENDPOINT is not set');
    }
    if (!process.env.AZURE_OPENAI_MODEL_NAME) {
      throw new Error('AZURE_OPENAI_MODEL_NAME is not set');
    }

    this.client = new OpenAI({
      apiKey: process.env.AZURE_OPENAI_API_KEY,
      baseURL: `${process.env.AZURE_OPENAI_ENDPOINT}/openai/deployments/${process.env.AZURE_OPENAI_MODEL_NAME}`,
      defaultQuery: { 'api-version': '2024-02-15-preview' },
      defaultHeaders: { 'api-key': process.env.AZURE_OPENAI_API_KEY }
    });
  }

  async getLegalResponse(messages: Message[]): Promise<string> {
    try {
      const systemMessage = {
        role: 'system',
        content: `You are an expert legal assistant focusing on Indian law. Format your responses using markdown for better readability:

1. Use headers (## or ###) for main sections
2. Use bullet points or numbered lists for steps and key points
3. Use **bold** for emphasis on important terms
4. Use > for quoting legal sections
5. Use \`inline code\` for section numbers and legal references
6. Use --- for separating major sections if needed

Your responses should include:
1. Always cite relevant sections of Indian laws (IPC, CrPC, specific acts) when applicable
2. Provide practical steps with legal backing
3. Explain legal terms in simple language
4. Mention time limits for legal actions if any
5. Provide information about legal remedies and rights

When a user introduces themselves and states their concern:
1. Address them by name
2. Acknowledge their concern
3. Ask relevant follow-up questions to gather important details
4. Provide initial guidance based on the information available

Be empathetic while maintaining professionalism.

Example format:
### Initial Assessment
[Your assessment here]

### Relevant Laws
> [Quote relevant section]
\`Section XXX\` of [Law] states...

### Recommended Steps
1. First step
2. Second step
   * Important note
   * Additional detail

### Timeline
* Filing deadline: X days
* Response period: Y days

### Additional Resources
* [Resource 1]
* [Resource 2]`
      };

      const completion = await this.client.chat.completions.create({
        messages: [systemMessage, ...messages],
        temperature: 0.7,
        max_tokens: 800,
        top_p: 0.95,
        stream: false
      });

      const responseContent = completion.choices[0]?.message?.content;
      if (!responseContent) {
        throw new Error('No response content from OpenAI');
      }

      return responseContent;
    } catch (error) {
      console.error('OpenAI API Error:', error);
      if (error instanceof Error) {
        if (error.message.includes('API key')) {
          throw new Error('Authentication failed with Azure OpenAI. Please check your API key.');
        }
        if (error.message.includes('deployment')) {
          throw new Error('Invalid Azure OpenAI deployment configuration. Please check your endpoint and model name.');
        }
      }
      throw new Error('Failed to get response from Azure OpenAI. Please try again later.');
    }
  }
} 