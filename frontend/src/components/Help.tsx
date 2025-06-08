import React from 'react';
import { FaQuestionCircle, FaBook, FaInfoCircle, FaHeadset } from 'react-icons/fa';

const Help: React.FC = () => {
  const faqs = [
    {
      question: 'How do I start a conversation?',
      answer: 'Simply type your legal question in the chat box at the bottom of the screen and press Enter or click the Send button. You can also use the microphone button for voice input.',
    },
    {
      question: 'What types of legal questions can I ask?',
      answer: 'You can ask questions about various legal topics including civil law, criminal law, family law, property law, and more. The assistant will provide general guidance and information.',
    },
    {
      question: 'Is my conversation private?',
      answer: 'Yes, your conversations are private and secure. We use encryption to protect your data and do not share your information with third parties.',
    },
    {
      question: 'Can I get legal documents through this assistant?',
      answer: 'Yes, the assistant can help you generate basic legal documents and forms. However, for complex legal matters, we recommend consulting with a qualified lawyer.',
    },
  ];

  const features = [
    {
      icon: <FaQuestionCircle />,
      title: 'Legal Q&A',
      description: 'Get answers to your legal questions in simple, easy-to-understand language.',
    },
    {
      icon: <FaBook />,
      title: 'Document Generation',
      description: 'Generate basic legal documents and forms with guided assistance.',
    },
    {
      icon: <FaHeadset />,
      title: 'Voice Input',
      description: 'Speak your questions using the voice input feature for hands-free interaction.',
    },
    {
      icon: <FaInfoCircle />,
      title: 'Multi-language Support',
      description: 'Get assistance in multiple Indian languages for better accessibility.',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Quick Start Guide */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold">Quick Start Guide</h2>
        <div className="bg-gray-50 p-6 rounded-lg space-y-4">
          <h3 className="font-semibold">Getting Started:</h3>
          <ol className="list-decimal list-inside space-y-2">
            <li>Type your legal question in the chat box</li>
            <li>Use the microphone button for voice input</li>
            <li>Wait for the assistant's response</li>
            <li>Follow up with additional questions if needed</li>
          </ol>
        </div>
      </section>

      {/* Features */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold">Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center space-x-3 mb-3">
                <span className="text-blue-600 text-xl">{feature.icon}</span>
                <h3 className="font-semibold">{feature.title}</h3>
              </div>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* FAQs */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold">Frequently Asked Questions</h2>
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className="bg-white p-6 rounded-lg border border-gray-200"
            >
              <h3 className="font-semibold mb-2">{faq.question}</h3>
              <p className="text-gray-600">{faq.answer}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Support */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold">Need More Help?</h2>
        <div className="bg-blue-50 p-6 rounded-lg">
          <p className="mb-4">
            If you need additional assistance or have specific questions not covered here,
            please contact our support team.
          </p>
          <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
            Contact Support
          </button>
        </div>
      </section>
    </div>
  );
};

export default Help; 