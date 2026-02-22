import React, { useState, useEffect } from 'react';
import { PattaUpload } from './components/PattaUpload';
import { PattaSchema } from './types';

export const PattaPage: React.FC = () => {
  const [extractedPatta, setExtractedPatta] = useState<PattaSchema | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Load any previously extracted data from localStorage
    const savedPatta = localStorage.getItem('fra-last-patta');
    if (savedPatta) {
      try {
        const pattaData = JSON.parse(savedPatta);
        setExtractedPatta(pattaData);
      } catch (error) {
        console.warn('Failed to load saved patta data:', error);
      }
    }
    setIsInitialized(true);
  }, []);

  const handlePattaExtracted = (pattaData: PattaSchema) => {
    setExtractedPatta(pattaData);
    // Save to localStorage for recovery
    localStorage.setItem('fra-last-patta', JSON.stringify(pattaData));
  };

  const handleError = (error: string) => {
    console.error('Patta processing error:', error);
    // You could show a toast notification here
  };

  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">FRA Patta Digitization</h1>
              <p className="text-sm text-gray-600">Upload → OCR → NER → Normalized Patta Data</p>
            </div>
            <div className="flex items-center space-x-4">
              <a href="/dashboard" className="text-gray-600 hover:text-gray-900">← Back to Dashboard</a>
              {extractedPatta && (
                <div className="text-sm text-green-600 font-medium">
                  ✓ Data Extracted
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <PattaUpload
          onPattaExtracted={handlePattaExtracted}
          onError={handleError}
        />
      </div>
    </div>
  );
};






