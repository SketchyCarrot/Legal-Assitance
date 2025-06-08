export interface AzureOpenAIConfig {
  apiKey: string;
  endpoint: string;
  deploymentName: string;
  apiVersion: string;
}

export interface LegalResponse {
  content: string;
  confidence: number;
  suggestedFields?: Record<string, string>;
  followUpQuestions?: string[];
  legalDisclaimer?: string;
  citations?: string[];
}

export interface ConversationContext {
  messages: {
    role: 'system' | 'user' | 'assistant';
    content: string;
  }[];
  metadata?: {
    jurisdiction?: string;
    legalDomain?: string;
    clientInfo?: Record<string, any>;
  };
}

export interface LegalQueryRequest {
  query: string;
  context?: ConversationContext;
  jurisdiction?: string;
  language?: string;
} 