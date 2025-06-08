'use client';

import { useState } from 'react';
import LegalChatWindow from './LegalChatWindow';

export default function HomePage() {
  const [showChat, setShowChat] = useState(false);

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
      {/* Background Patterns */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-[500px] h-[500px] bg-blue-100/30 rounded-full -top-48 -right-24 blur-3xl"></div>
        <div className="absolute w-[500px] h-[500px] bg-blue-100/30 rounded-full -bottom-48 -left-24 blur-3xl"></div>
        <div className="absolute inset-0 bg-white/50 backdrop-blur-3xl"></div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Hero Section */}
        <section className="min-h-[80vh] flex items-center justify-center px-4 py-20">
          <div className="max-w-4xl mx-auto text-center">
            <div className="mb-8 relative">
              <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg blur opacity-20"></div>
              <h1 className="relative text-5xl sm:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600">
                Legal <span className="text-blue-600">Saathi</span>
              </h1>
            </div>
            <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
              Your AI-powered legal assistant for Indian law. Get instant guidance on your legal matters with accurate citations and practical advice.
            </p>
            
            <button
              onClick={() => setShowChat(true)}
              className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl overflow-hidden transition-all duration-300 hover:scale-105 hover:shadow-lg"
            >
              <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-blue-600 to-blue-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <span className="relative flex items-center">
                <span className="mr-3 text-2xl">⚖️</span>
                Start Legal Consultation
              </span>
            </button>
            
            <div className="mt-4 text-sm text-gray-500">
              Free • Instant • Confidential
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="py-20 px-4 bg-white/80 backdrop-blur-sm">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
              How We Can Help
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <FeatureCard
                icon="⚡"
                title="Instant Answers"
                description="Get immediate responses to your legal questions with relevant citations"
              />
              <FeatureCard
                icon="📚"
                title="Legal Knowledge"
                description="Access comprehensive information about Indian laws and regulations"
              />
              <FeatureCard
                icon="🔒"
                title="Private & Secure"
                description="Your conversations are confidential and protected"
              />
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-20 px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
              Simple Process
            </h2>
            <div className="flex flex-col md:flex-row items-center justify-between gap-8">
              <ProcessStep
                icon="💬"
                title="Ask"
                description="Describe your legal concern"
              />
              <div className="hidden md:block text-gray-300 text-2xl">→</div>
              <ProcessStep
                icon="🤖"
                title="Analyze"
                description="AI processes your query"
              />
              <div className="hidden md:block text-gray-300 text-2xl">→</div>
              <ProcessStep
                icon="✅"
                title="Resolve"
                description="Get clear legal guidance"
              />
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-8 px-4 bg-gray-50/80 backdrop-blur-sm">
          <div className="max-w-6xl mx-auto text-center text-gray-600">
            <p>© 2024 Legal Saathi • AI-Powered Legal Assistant</p>
          </div>
        </footer>
      </div>

      {/* Chat Window */}
      {showChat && <LegalChatWindow />}
    </main>
  );
}

function FeatureCard({ icon, title, description }: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="group p-6 bg-white rounded-2xl shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-1">
      <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
        <span className="text-2xl">{icon}</span>
      </div>
      <h3 className="text-lg font-semibold mb-2 text-gray-900">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}

function ProcessStep({ icon, title, description }: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="flex-1 text-center group">
      <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
        <span className="text-2xl">{icon}</span>
      </div>
      <h3 className="font-semibold mb-2 text-gray-900">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
} 