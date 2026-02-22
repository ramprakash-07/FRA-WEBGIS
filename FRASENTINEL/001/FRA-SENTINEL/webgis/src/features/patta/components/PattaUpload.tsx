import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, AlertCircle, CheckCircle, Eye, Download } from 'lucide-react';
import { UploadedFile, OCRResult, NERResult, PattaSchema } from '../types';
import { OCRService } from '../services/ocrService';
import { PDFRasterizer } from '../services/pdfRasterizer';
import { NERService } from '../services/nerService';
import { PattaNormalizer } from '../services/pattaNormalizer';
import { PattaApiClient } from '../services/pattaApiClient';

interface PattaUploadProps {
  onPattaExtracted: (pattaData: PattaSchema) => void;
  onError: (error: string) => void;
  className?: string;
}

export const PattaUpload: React.FC<PattaUploadProps> = ({
  onPattaExtracted,
  onError,
  className = ''
}) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [extractedPatta, setExtractedPatta] = useState<PattaSchema | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const ocrService = useRef(new OCRService());
  const pdfRasterizer = useRef(new PDFRasterizer({ dpi: 150, maxPages: 20 }));
  const nerService = useRef(new NERService());
  const pattaNormalizer = useRef(new PattaNormalizer());
  const apiClient = useRef(new PattaApiClient());

  useEffect(() => {
    // Initialize services
    const initializeServices = async () => {
      try {
        await ocrService.current.initialize();
        
        // Set up progress callback
        ocrService.current.setProgressCallback((progress) => {
          setCurrentProgress(progress.progress);
        });

        // Load auth token from localStorage
        const authToken = localStorage.getItem('fra-auth-token');
        if (authToken) {
          nerService.current.setAuthToken(authToken);
          apiClient.current.setAuthToken(authToken);
        }

      } catch (error) {
        console.error('Failed to initialize services:', error);
        onError('Failed to initialize OCR service');
      }
    };

    initializeServices();
  }, [onError]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      type: file.type.startsWith('image/') ? 'image' : 'pdf',
      status: 'pending',
      progress: 0
    }));

    setFiles(prev => [...prev, ...newFiles]);
    showToast(`${acceptedFiles.length} file(s) added`, 'success');
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png'],
      'application/pdf': ['.pdf']
    },
    maxSize: 25 * 1024 * 1024, // 25MB
    multiple: true
  });

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const processFile = async (uploadedFile: UploadedFile) => {
    try {
      setIsProcessing(true);
      setFiles(prev => prev.map(f => 
        f.id === uploadedFile.id 
          ? { ...f, status: 'processing', progress: 0 }
          : f
      ));

      let ocrResult: OCRResult;
      let nerResult: NERResult | null = null;

      if (uploadedFile.type === 'pdf') {
        // Process PDF
        ocrResult = await processPDF(uploadedFile.file);
      } else {
        // Process image
        ocrResult = await processImage(uploadedFile.file);
      }

      // Extract NER
      try {
        const nerResponse = await nerService.current.extractEntitiesWithRetry(
          ocrResult.fullText,
          'en'
        );
        nerResult = { spans: nerResponse, locale: 'en' };
      } catch (error) {
        console.warn('NER extraction failed, continuing with OCR only:', error);
      }

      // Normalize to Patta schema
      const normalizedPatta = pattaNormalizer.current.normalize(
        ocrResult.fullText,
        ocrResult.totalConfidence
      );

      // Merge with NER results if available
      const finalPatta = nerResult 
        ? pattaNormalizer.current.mergeWithNER(normalizedPatta, nerResult.spans)
        : normalizedPatta;

      // Update file status
      setFiles(prev => prev.map(f => 
        f.id === uploadedFile.id 
          ? { 
              ...f, 
              status: 'completed', 
              ocrResult, 
              nerResult, 
              pattaData: finalPatta,
              progress: 100 
            }
          : f
      ));

      setExtractedPatta(finalPatta);
      onPattaExtracted(finalPatta);
      showToast('File processed successfully!', 'success');

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Processing failed';
      
      setFiles(prev => prev.map(f => 
        f.id === uploadedFile.id 
          ? { ...f, status: 'error', error: errorMessage }
          : f
      ));

      onError(errorMessage);
      showToast(`Processing failed: ${errorMessage}`, 'error');
    } finally {
      setIsProcessing(false);
      setCurrentProgress(0);
    }
  };

  const processPDF = async (file: File): Promise<OCRResult> => {
    // Rasterize PDF
    const pages = await pdfRasterizer.current.rasterizePDF(file, (progress) => {
      setCurrentProgress(progress);
    });

    // Create images from canvases
    const images = await Promise.all(
      pages.map(async (page) => {
        return await pdfRasterizer.current.createImageFromCanvas(page.canvas);
      })
    );

    // OCR all pages
    return await ocrService.current.processMultipleImages(images);
  };

  const processImage = async (file: File): Promise<OCRResult> => {
    const img = new Image();
    img.src = URL.createObjectURL(file);
    
    await new Promise((resolve, reject) => {
      img.onload = resolve;
      img.onerror = reject;
    });

    const page = await ocrService.current.processImage(img, 0);
    
    return {
      pages: [page],
      fullText: page.text,
      totalConfidence: page.conf
    };
  };

  const processAllFiles = async () => {
    const pendingFiles = files.filter(f => f.status === 'pending');
    
    for (const file of pendingFiles) {
      await processFile(file);
    }
  };

  const savePatta = async () => {
    if (!extractedPatta) {
      showToast('No patta data to save', 'error');
      return;
    }

    try {
      const fileId = files.find(f => f.status === 'completed')?.id || 'unknown';
      const response = await apiClient.current.savePatta(extractedPatta, fileId);
      
      if (response.success) {
        showToast('Patta data saved successfully!', 'success');
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Save failed';
      onError(errorMessage);
      showToast(`Save failed: ${errorMessage}`, 'error');
    }
  };

  const downloadPattaData = () => {
    if (!extractedPatta) return;

    const dataStr = JSON.stringify(extractedPatta, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `patta-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'pending':
        return <File className="w-4 h-4 text-gray-400" />;
      case 'processing':
        return <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
    }
  };

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    // Simple toast implementation
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 p-4 rounded-lg text-white z-50 ${
      type === 'success' ? 'bg-green-500' : 
      type === 'error' ? 'bg-red-500' : 'bg-blue-500'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 3000);
  };

  return (
    <div className={`w-full max-w-6xl mx-auto p-6 ${className}`}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Patta Document Digitization</h2>
        <p className="text-gray-600">
          Upload JPG, PNG, or PDF files for OCR processing and NER extraction
        </p>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors mb-6
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
        `}
      >
        <input {...getInputProps()} ref={fileInputRef} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <p className="text-lg font-medium text-gray-700 mb-2">
          {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
        </p>
        <p className="text-sm text-gray-500 mb-4">
          or click to browse files
        </p>
        <p className="text-xs text-gray-400">
          Supports JPG, PNG, PDF (max 25MB each)
        </p>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Files ({files.length})
            </h3>
            <button
              onClick={processAllFiles}
              disabled={isProcessing || files.every(f => f.status !== 'pending')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Process All Files
            </button>
          </div>

          <div className="space-y-3">
            {files.map((uploadedFile) => (
              <div
                key={uploadedFile.id}
                className="flex items-center justify-between p-4 border rounded-lg bg-white"
              >
                <div className="flex items-center space-x-3">
                  {getStatusIcon(uploadedFile.status)}
                  <div>
                    <p className="font-medium text-gray-900">
                      {uploadedFile.file.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {uploadedFile.status === 'processing' && (
                    <div className="w-32">
                      <div className="bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${uploadedFile.progress}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {uploadedFile.progress.toFixed(0)}%
                      </p>
                    </div>
                  )}

                  {uploadedFile.status === 'pending' && (
                    <button
                      onClick={() => processFile(uploadedFile)}
                      className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                    >
                      Process
                    </button>
                  )}

                  {uploadedFile.status === 'completed' && (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setShowPreview(true)}
                        className="p-1 text-gray-400 hover:text-blue-500"
                        title="Preview"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={downloadPattaData}
                        className="p-1 text-gray-400 hover:text-green-500"
                        title="Download"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  )}

                  {uploadedFile.status === 'error' && (
                    <p className="text-sm text-red-600">
                      {uploadedFile.error}
                    </p>
                  )}

                  <button
                    onClick={() => removeFile(uploadedFile.id)}
                    className="p-1 text-gray-400 hover:text-red-500"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extracted Patta Data */}
      {extractedPatta && (
        <div className="bg-white border rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Extracted Patta Data</h3>
            <div className="flex space-x-2">
              <button
                onClick={savePatta}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Save Patta
              </button>
              <button
                onClick={downloadPattaData}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Download JSON
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(extractedPatta).map(([key, value]) => {
              if (key === 'raw_text' || key === 'ocr_confidence') return null;
              
              return (
                <div key={key} className="p-3 bg-gray-50 rounded-lg">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </label>
                  <p className="text-gray-900">
                    {value || <span className="text-gray-400 italic">Not detected</span>}
                  </p>
                </div>
              );
            })}
          </div>

          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>OCR Confidence:</strong> {extractedPatta.ocr_confidence.toFixed(1)}%
            </p>
          </div>
        </div>
      )}

      {/* Progress Indicator */}
      {isProcessing && (
        <div className="fixed bottom-4 right-4 bg-white border rounded-lg p-4 shadow-lg">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span className="text-sm text-gray-600">Processing...</span>
          </div>
          <div className="mt-2 w-48 bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${currentProgress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};
