import React, { useState, useRef, useEffect } from 'react';

interface TextInputProps {
  onChange?: (text: string) => void;
  placeholder?: string;
  maxLength?: number;
  defaultValue?: string;
}

const TextInput: React.FC<TextInputProps> = ({
  onChange = () => {},
  placeholder = 'Enter your text here...',
  maxLength = 1000,
  defaultValue = ''
}) => {
  const [text, setText] = useState(defaultValue);
  const [wordCount, setWordCount] = useState(0);
  const [charCount, setCharCount] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      adjustTextareaHeight();
    }
  }, [text]);

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    if (maxLength && newText.length > maxLength) return;

    setText(newText);
    onChange(newText);

    // Update word and character counts
    setCharCount(newText.length);
    setWordCount(newText.trim() === '' ? 0 : newText.trim().split(/\s+/).length);
  };

  const handleCopy = () => {
    if (text) {
      navigator.clipboard.writeText(text);
    }
  };

  const handlePaste = async () => {
    try {
      const clipboardText = await navigator.clipboard.readText();
      const newText = text + clipboardText;
      if (maxLength && newText.length > maxLength) {
        alert(`Text would exceed maximum length of ${maxLength} characters`);
        return;
      }
      setText(newText);
      onChange(newText);
    } catch (err) {
      console.error('Failed to read clipboard:', err);
    }
  };

  const formatText = (type: 'bold' | 'italic' | 'underline') => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = text.substring(start, end);
    let newText = text;

    switch (type) {
      case 'bold':
        newText = text.substring(0, start) + `**${selectedText}**` + text.substring(end);
        break;
      case 'italic':
        newText = text.substring(0, start) + `_${selectedText}_` + text.substring(end);
        break;
      case 'underline':
        newText = text.substring(0, start) + `__${selectedText}__` + text.substring(end);
        break;
    }

    setText(newText);
    onChange(newText);
  };

  return (
    <div className="p-4 border rounded-lg shadow-sm">
      {/* Toolbar */}
      <div className="flex items-center gap-2 mb-4 p-2 bg-gray-50 rounded-lg">
        <button
          onClick={() => formatText('bold')}
          className="p-2 hover:bg-gray-200 rounded"
          title="Bold"
        >
          <strong>B</strong>
        </button>
        <button
          onClick={() => formatText('italic')}
          className="p-2 hover:bg-gray-200 rounded"
          title="Italic"
        >
          <em>I</em>
        </button>
        <button
          onClick={() => formatText('underline')}
          className="p-2 hover:bg-gray-200 rounded"
          title="Underline"
        >
          <u>U</u>
        </button>
        <div className="h-6 w-px bg-gray-300 mx-2" />
        <button
          onClick={handleCopy}
          className="p-2 hover:bg-gray-200 rounded text-sm"
          title="Copy"
        >
          Copy
        </button>
        <button
          onClick={handlePaste}
          className="p-2 hover:bg-gray-200 rounded text-sm"
          title="Paste"
        >
          Paste
        </button>
      </div>

      {/* Text Area */}
      <textarea
        ref={textareaRef}
        value={text}
        onChange={handleTextChange}
        placeholder={placeholder}
        className="w-full min-h-[200px] p-3 rounded-lg border focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        style={{
          fontFamily: 'inherit',
          lineHeight: '1.5',
        }}
        dir="auto" // Enables automatic text direction based on content
        spellCheck="true"
        lang="en" // Default language, can be changed based on detected content
      />

      {/* Character and Word Count */}
      <div className="flex justify-between mt-2 text-sm text-gray-500">
        <span>{`${charCount} characters`}</span>
        <span>{`${wordCount} words`}</span>
        {maxLength && (
          <span>{`${charCount}/${maxLength} characters`}</span>
        )}
      </div>
    </div>
  );
};

export default TextInput; 