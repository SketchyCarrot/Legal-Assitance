'use client';

import { VoiceInput, TextInput, ImageInput } from '@/components/input';

export default function InputDemo() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Input Methods Demo</h1>
      
      <div className="space-y-8">
        {/* Voice Input Section */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">Voice Input</h2>
          <VoiceInput
            onTranscriptChange={(transcript) => {
              console.log('Voice transcript:', transcript);
            }}
          />
        </section>

        {/* Text Input Section */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">Text Input</h2>
          <TextInput
            onChange={(text) => {
              console.log('Text input:', text);
            }}
            placeholder="Type your legal query here..."
            maxLength={2000}
          />
        </section>

        {/* Image Input Section */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">Image Upload & OCR</h2>
          <ImageInput
            onImageUpload={(file) => {
              console.log('Image uploaded:', file);
            }}
            onOCRComplete={(text) => {
              console.log('OCR text:', text);
            }}
          />
        </section>
      </div>
    </div>
  );
} 