import Image from 'next/image'

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold text-primary mb-4">
          Welcome to Legal Saathi
        </h1>
        <p className="text-xl text-secondary">
          Your AI-powered legal assistant
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {/* Input Methods */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Multi-modal Input</h2>
          <ul className="space-y-2">
            <li>✓ Voice Recognition</li>
            <li>✓ Text Input</li>
            <li>✓ Image Upload</li>
          </ul>
        </div>

        {/* Legal AI */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Legal AI Assistant</h2>
          <ul className="space-y-2">
            <li>✓ Legal Document Analysis</li>
            <li>✓ Case Law Research</li>
            <li>✓ Legal Advice Generation</li>
          </ul>
        </div>

        {/* Form Automation */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Form Automation</h2>
          <ul className="space-y-2">
            <li>✓ Auto Form Filling</li>
            <li>✓ Document Generation</li>
            <li>✓ Multi-language Support</li>
          </ul>
        </div>
      </div>

      <div className="mt-12 text-center">
        <button className="bg-primary text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-opacity-90 transition-colors">
          Get Started
        </button>
      </div>
    </div>
  )
} 