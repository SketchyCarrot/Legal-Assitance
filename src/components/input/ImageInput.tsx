import React, { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { createWorker } from 'tesseract.js';
import Image from 'next/image';

interface ImageInputProps {
  onImageUpload?: (file: File) => void;
  onOCRComplete?: (text: string) => void;
  maxFileSize?: number; // in bytes
  acceptedFileTypes?: string[];
}

const ImageInput: React.FC<ImageInputProps> = ({
  onImageUpload = () => {},
  onOCRComplete = () => {},
  maxFileSize = 5 * 1024 * 1024, // 5MB default
  acceptedFileTypes = ['image/jpeg', 'image/png', 'application/pdf']
}) => {
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string>('');
  const workerRef = useRef<any>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file size
    if (file.size > maxFileSize) {
      setError(`File size must be less than ${maxFileSize / (1024 * 1024)}MB`);
      return;
    }

    // Create preview
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
    setError('');
    onImageUpload(file);

    // Process OCR if it's an image
    if (file.type.startsWith('image/')) {
      await processOCR(file);
    }

    return () => URL.revokeObjectURL(objectUrl);
  }, [maxFileSize, onImageUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  });

  const processOCR = async (file: File) => {
    try {
      setIsProcessing(true);
      setProgress(0);

      // Initialize Tesseract worker
      if (!workerRef.current) {
        workerRef.current = await createWorker({
          logger: (m) => {
            if (m.status === 'recognizing text') {
              setProgress(parseInt(m.progress * 100));
            }
          },
        });
      }

      const worker = workerRef.current;
      await worker.loadLanguage('eng');
      await worker.initialize('eng');
      
      const { data: { text } } = await worker.recognize(file);
      onOCRComplete(text);
      setIsProcessing(false);
      setProgress(100);
    } catch (err) {
      console.error('OCR Error:', err);
      setError('Failed to process image text. Please try again.');
      setIsProcessing(false);
    }
  };

  // Cleanup worker on unmount
  React.useEffect(() => {
    return () => {
      if (workerRef.current) {
        workerRef.current.terminate();
      }
    };
  }, []);

  return (
    <div className="p-4 border rounded-lg shadow-sm">
      {/* Drag & Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-500'}`}
      >
        <input {...getInputProps()} />
        <div className="space-y-2">
          <div className="text-4xl mb-2">📄</div>
          {isDragActive ? (
            <p>Drop the file here...</p>
          ) : (
            <>
              <p>Drag & drop an image here, or click to select</p>
              <p className="text-sm text-gray-500">
                Supported formats: JPG, PNG, PDF (max {maxFileSize / (1024 * 1024)}MB)
              </p>
            </>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Preview */}
      {previewUrl && (
        <div className="mt-4">
          <h4 className="font-medium mb-2">Preview:</h4>
          <div className="relative aspect-video w-full max-w-md mx-auto">
            <Image
              src={previewUrl}
              alt="Preview"
              fill
              className="object-contain rounded-lg"
            />
          </div>
        </div>
      )}

      {/* Processing Status */}
      {isProcessing && (
        <div className="mt-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent" />
            <span>Processing OCR...</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Mobile Camera Capture */}
      <button
        onClick={() => document.querySelector('input[type="file"]')?.click()}
        className="mt-4 w-full py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium"
      >
        📸 Take Photo
      </button>
    </div>
  );
};

export default ImageInput; 