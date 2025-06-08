import React, { useState, useRef, useEffect } from 'react';
import { Message } from '../types/chat';
import { FaMicrophone, FaPaperPlane, FaCog, FaHistory, FaQuestionCircle } from 'react-icons/fa';
import LanguageSelector from './LanguageSelector';
import useLanguageStore from '../store/languageStore';
import { BhashiniService } from '../services/bhashiniService';

interface ChatInterfaceProps {
  onSendMessage: (message: string) => void;
  onStartRecording: () => void;
  onStopRecording: () => void;
  messages: Message[];
  isRecording: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onSendMessage,
  onStartRecording,
  onStopRecording,
  messages,
  isRecording,
}) => {
  const [input, setInput] = useState('');
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [isTranslating, setIsTranslating] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'history' | 'settings' | 'help'>('chat');
  const { sourceLanguage, targetLanguage } = useLanguageStore();
  const bhashiniService = new BhashiniService();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      let messageToSend = input;
      setInput('');

      // If source language is not English, translate to English before sending
      if (sourceLanguage.code !== 'en') {
        setIsTranslating(true);
        try {
          const translation = await bhashiniService.translateText(
            input,
            sourceLanguage,
            { code: 'en', name: 'English', bhashiniCode: 'en' }
          );
          messageToSend = translation.translatedText;
        } catch (error) {
          console.error('Translation error:', error);
        } finally {
          setIsTranslating(false);
        }
      }

      onSendMessage(messageToSend);
    }
  };

  const handleRecording = () => {
    if (isRecording) {
      onStopRecording();
    } else {
      onStartRecording();
    }
  };

  const translateMessage = async (message: Message): Promise<Message> => {
    if (message.sender === 'assistant' && targetLanguage.code !== 'en') {
      try {
        const translation = await bhashiniService.translateText(
          message.content,
          { code: 'en', name: 'English', bhashiniCode: 'en' },
          targetLanguage
        );
        return {
          ...message,
          content: translation.translatedText,
          originalContent: message.content,
        };
      } catch (error) {
        console.error('Translation error:', error);
      }
    }
    return message;
  };

  const renderMessages = () => {
    return messages.map(async (message, index) => {
      const translatedMessage = await translateMessage(message);
      return (
        <div
          key={index}
          className={`flex ${
            message.sender === 'user' ? 'justify-end' : 'justify-start'
          } mb-4`}
        >
          <div
            className={`max-w-[70%] rounded-lg p-4 ${
              message.sender === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            <p className="text-sm">{translatedMessage.content}</p>
            {translatedMessage.originalContent && (
              <p className="text-xs mt-2 opacity-70">
                Original: {translatedMessage.originalContent}
              </p>
            )}
            <span className="text-xs opacity-70 mt-1 block">
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          </div>
        </div>
      );
    });
  };

  const renderSidebar = () => (
    <div className="w-64 bg-gray-800 text-white h-full flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">Legal Assistant</h1>
      </div>
      <nav className="flex-1 p-4">
        <button
          onClick={() => setActiveTab('chat')}
          className={`w-full text-left p-3 rounded-lg mb-2 flex items-center ${
            activeTab === 'chat' ? 'bg-blue-600' : 'hover:bg-gray-700'
          }`}
        >
          <FaPaperPlane className="mr-3" /> Chat
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`w-full text-left p-3 rounded-lg mb-2 flex items-center ${
            activeTab === 'history' ? 'bg-blue-600' : 'hover:bg-gray-700'
          }`}
        >
          <FaHistory className="mr-3" /> History
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          className={`w-full text-left p-3 rounded-lg mb-2 flex items-center ${
            activeTab === 'settings' ? 'bg-blue-600' : 'hover:bg-gray-700'
          }`}
        >
          <FaCog className="mr-3" /> Settings
        </button>
        <button
          onClick={() => setActiveTab('help')}
          className={`w-full text-left p-3 rounded-lg mb-2 flex items-center ${
            activeTab === 'help' ? 'bg-blue-600' : 'hover:bg-gray-700'
          }`}
        >
          <FaQuestionCircle className="mr-3" /> Help
        </button>
      </nav>
    </div>
  );

  return (
    <div className="flex h-screen bg-white">
      {isSidebarOpen && renderSidebar()}
      <div className="flex-1 flex flex-col">
        <div className="border-b border-gray-200">
          <LanguageSelector />
        </div>
        <div className="flex-1 overflow-y-auto p-6 bg-white">
          {activeTab === 'chat' && (
            <>
              {renderMessages()}
              <div ref={messagesEndRef} />
            </>
          )}
          {activeTab === 'history' && (
            <div className="p-4">
              <h2 className="text-2xl font-bold mb-4">Conversation History</h2>
              {/* Add history view here */}
            </div>
          )}
          {activeTab === 'settings' && (
            <div className="p-4">
              <h2 className="text-2xl font-bold mb-4">Settings</h2>
              {/* Add settings view here */}
            </div>
          )}
          {activeTab === 'help' && (
            <div className="p-4">
              <h2 className="text-2xl font-bold mb-4">Help</h2>
              {/* Add help content here */}
            </div>
          )}
        </div>
        <div className="border-t border-gray-200 p-4 bg-white">
          <form onSubmit={handleSubmit} className="flex items-center space-x-4">
            <button
              type="button"
              onClick={handleRecording}
              className={`p-3 rounded-full ${
                isRecording
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              disabled={isTranslating}
            >
              <FaMicrophone className={isRecording ? 'animate-pulse' : ''} />
            </button>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Type your message in ${sourceLanguage.name}...`}
              className="flex-1 p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isTranslating}
            />
            <button
              type="submit"
              className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              disabled={isTranslating}
            >
              {isTranslating ? 'Translating...' : <FaPaperPlane />}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface; 