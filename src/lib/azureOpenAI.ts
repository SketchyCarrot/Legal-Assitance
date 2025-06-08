import { OpenAIClient, AzureKeyCredential } from '@azure/openai';
import type { AzureOpenAIConfig, LegalResponse, ConversationContext, LegalQueryRequest } from '@/types/azure';

class AzureOpenAIService {
  private client: OpenAIClient;
  private deploymentName: string;
  private static instance: AzureOpenAIService;

  private constructor(config: AzureOpenAIConfig) {
    this.client = new OpenAIClient(
      config.endpoint,
      new AzureKeyCredential(config.apiKey)
    );
    this.deploymentName = config.deploymentName;
  }

  public static getInstance(config?: AzureOpenAIConfig): AzureOpenAIService {
    if (!AzureOpenAIService.instance && config) {
      AzureOpenAIService.instance = new AzureOpenAIService(config);
    }
    return AzureOpenAIService.instance;
  }

  private getLegalSystemPrompt(jurisdiction?: string): string {
    return `You are a legal assistant AI with expertise in ${jurisdiction || 'general'} law. 
    Provide accurate, well-reasoned legal information while:
    1. Always including relevant legal disclaimers
    2. Citing specific laws and regulations when applicable
    3. Maintaining high ethical standards
    4. Identifying when human legal counsel is necessary
    5. Providing confidence levels for responses
    6. Suggesting relevant form fields for document preparation`;
  }

  private async validateResponse(response: string): Promise<boolean> {
    // Basic validation rules
    const containsDisclaimer = response.includes('DISCLAIMER') || response.includes('This is not legal advice');
    const containsConfidenceIndicator = response.includes('Confidence:');
    const hasStructuredFormat = response.includes('RESPONSE:') && response.includes('FOLLOW-UP:');
    
    return containsDisclaimer && containsConfidenceIndicator && hasStructuredFormat;
  }

  private calculateConfidence(response: string): number {
    // Implement confidence scoring based on:
    // 1. Presence of specific legal citations
    // 2. Clarity of response
    // 3. Completeness of information
    // 4. Jurisdiction match
    let score = 0.7; // Base confidence score

    if (response.includes('Section') || response.includes('Article')) score += 0.1;
    if (response.includes('case law') || response.includes('precedent')) score += 0.1;
    if (response.includes('statute') || response.includes('regulation')) score += 0.1;

    return Math.min(score, 1); // Cap at 1.0
  }

  private parseResponse(rawResponse: string): LegalResponse {
    const sections = rawResponse.split('\n\n');
    const mainContent = sections.find(s => s.startsWith('RESPONSE:'))?.replace('RESPONSE:', '').trim() || '';
    const followUp = sections.find(s => s.startsWith('FOLLOW-UP:'))?.replace('FOLLOW-UP:', '').trim().split('\n') || [];
    const disclaimer = sections.find(s => s.startsWith('DISCLAIMER:'))?.replace('DISCLAIMER:', '').trim() || '';
    const citations = sections.find(s => s.startsWith('CITATIONS:'))?.replace('CITATIONS:', '').trim().split('\n') || [];

    // Extract suggested form fields if present
    const fieldsSection = sections.find(s => s.startsWith('FORM_FIELDS:'));
    const suggestedFields: Record<string, string> = {};
    if (fieldsSection) {
      const fieldLines = fieldsSection.replace('FORM_FIELDS:', '').trim().split('\n');
      fieldLines.forEach(line => {
        const [key, value] = line.split(':').map(s => s.trim());
        if (key && value) suggestedFields[key] = value;
      });
    }

    return {
      content: mainContent,
      confidence: this.calculateConfidence(rawResponse),
      suggestedFields,
      followUpQuestions: followUp,
      legalDisclaimer: disclaimer,
      citations
    };
  }

  public async processLegalQuery(request: LegalQueryRequest): Promise<LegalResponse> {
    try {
      const messages = [
        { role: 'system', content: this.getLegalSystemPrompt(request.jurisdiction) },
        ...(request.context?.messages || []),
        { role: 'user', content: request.query }
      ];

      const response = await this.client.getChatCompletions(
        this.deploymentName,
        messages as any,
        {
          temperature: 0.3, // Lower temperature for more focused legal responses
          maxTokens: 800,
          stopSequences: ['DISCLAIMER:', 'FOLLOW-UP:', 'CITATIONS:'],
          n: 1
        }
      );

      const rawResponse = response.choices[0].message?.content || '';
      
      // Validate response format
      const isValid = await this.validateResponse(rawResponse);
      if (!isValid) {
        throw new Error('Invalid response format from Azure OpenAI');
      }

      return this.parseResponse(rawResponse);
    } catch (error) {
      console.error('Error processing legal query:', error);
      return this.getFallbackResponse(request.query);
    }
  }

  private getFallbackResponse(query: string): LegalResponse {
    return {
      content: 'I apologize, but I am unable to provide a complete response at this time. Please consult with a qualified legal professional for accurate advice.',
      confidence: 0,
      followUpQuestions: ['Would you like to rephrase your question?', 'Would you like to speak with a human legal professional?'],
      legalDisclaimer: 'This is a fallback response due to a system error. No legal advice is being provided.',
      citations: []
    };
  }
}

export default AzureOpenAIService; 