import React from 'react';
import { Message } from '../types/chat';
import { FaTrash, FaDownload, FaSearch } from 'react-icons/fa';

interface HistoryProps {
  conversations: {
    id: string;
    title: string;
    timestamp: string;
    messages: Message[];
  }[];
  onDeleteConversation: (id: string) => void;
  onExportConversation: (id: string) => void;
  onLoadConversation: (id: string) => void;
}

const History: React.FC<HistoryProps> = ({
  conversations,
  onDeleteConversation,
  onExportConversation,
  onLoadConversation,
}) => {
  const [searchTerm, setSearchTerm] = React.useState('');

  const filteredConversations = conversations.filter(
    (conv) =>
      conv.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      conv.messages.some((msg) =>
        msg.content.toLowerCase().includes(searchTerm.toLowerCase())
      )
  );

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search conversations..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <FaSearch className="absolute left-3 top-3 text-gray-400" />
      </div>

      {/* Conversations List */}
      <div className="space-y-4">
        {filteredConversations.map((conversation) => (
          <div
            key={conversation.id}
            className="bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-semibold text-lg">{conversation.title}</h3>
                  <p className="text-sm text-gray-500">
                    {new Date(conversation.timestamp).toLocaleString()}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => onExportConversation(conversation.id)}
                    className="p-2 text-gray-600 hover:text-blue-600 transition-colors"
                    title="Export conversation"
                  >
                    <FaDownload />
                  </button>
                  <button
                    onClick={() => onDeleteConversation(conversation.id)}
                    className="p-2 text-gray-600 hover:text-red-600 transition-colors"
                    title="Delete conversation"
                  >
                    <FaTrash />
                  </button>
                </div>
              </div>

              {/* Preview of the conversation */}
              <div className="mt-4 space-y-2">
                {conversation.messages.slice(0, 2).map((message, index) => (
                  <div
                    key={index}
                    className={`text-sm ${
                      message.sender === 'user' ? 'text-blue-600' : 'text-gray-600'
                    }`}
                  >
                    <span className="font-medium">
                      {message.sender === 'user' ? 'You' : 'Assistant'}:
                    </span>{' '}
                    {message.content.length > 100
                      ? `${message.content.substring(0, 100)}...`
                      : message.content}
                  </div>
                ))}
                {conversation.messages.length > 2 && (
                  <p className="text-sm text-gray-500">
                    ... and {conversation.messages.length - 2} more messages
                  </p>
                )}
              </div>

              {/* Load Conversation Button */}
              <button
                onClick={() => onLoadConversation(conversation.id)}
                className="mt-4 w-full bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Continue Conversation
              </button>
            </div>
          </div>
        ))}

        {filteredConversations.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            {searchTerm
              ? 'No conversations match your search'
              : 'No conversations yet'}
          </div>
        )}
      </div>
    </div>
  );
};

export default History; 