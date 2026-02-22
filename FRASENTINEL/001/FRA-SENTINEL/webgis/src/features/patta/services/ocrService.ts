// OCR Service for managing Tesseract.js Web Worker
import { OCRResult, OCRProgress } from '../features/patta/types';

export class OCRService {
  private worker: Worker | null = null;
  private jobId = 0;
  private callbacks = new Map<string, {
    onProgress?: (progress: OCRProgress) => void;
    onResult?: (result: OCRResult) => void;
    onError?: (error: Error) => void;
  }>();

  constructor() {
    this.initializeWorker();
  }

  private async initializeWorker() {
    try {
      // Create Web Worker from the OCR worker file
      this.worker = new Worker('/src/workers/ocrWorker.js', { type: 'module' });
      
      this.worker.onmessage = (event) => {
        const { type, data } = event.data;
        
        switch (type) {
          case 'initialized':
            console.log('OCR Worker initialized successfully');
            break;
            
          case 'progress':
            const callback = this.callbacks.get(data.id);
            if (callback?.onProgress) {
              callback.onProgress(data);
            }
            break;
            
          case 'result':
            const resultCallback = this.callbacks.get(data.id);
            if (resultCallback?.onResult) {
              resultCallback.onResult(data);
            }
            this.callbacks.delete(data.id);
            break;
            
          case 'error':
            const errorCallback = this.callbacks.get(data.id);
            if (errorCallback?.onError) {
              errorCallback.onError(new Error(data.error));
            }
            this.callbacks.delete(data.id);
            break;
        }
      };

      this.worker.onerror = (error) => {
        console.error('OCR Worker error:', error);
        // Notify all pending callbacks of the error
        this.callbacks.forEach(callback => {
          if (callback.onError) {
            callback.onError(new Error('Worker error'));
          }
        });
        this.callbacks.clear();
      };

      // Initialize the worker
      this.worker.postMessage({ type: 'initialize' });
      
    } catch (error) {
      console.error('Failed to initialize OCR worker:', error);
      throw new Error('OCR service unavailable');
    }
  }

  async processImage(
    imageData: string, // base64 image data
    languages: string[] = ['eng', 'hin', 'tam', 'tel'],
    pageNumber?: number,
    onProgress?: (progress: OCRProgress) => void,
    onResult?: (result: OCRResult) => void,
    onError?: (error: Error) => void
  ): Promise<OCRResult> {
    if (!this.worker) {
      throw new Error('OCR worker not initialized');
    }

    const jobId = `ocr_${++this.jobId}_${Date.now()}`;
    
    // Store callbacks
    this.callbacks.set(jobId, {
      onProgress,
      onResult,
      onError
    });

    // Send job to worker
    this.worker.postMessage({
      type: 'process',
      data: {
        id: jobId,
        imageData,
        languages,
        pageNumber
      }
    });

    // Return a promise that resolves when the job completes
    return new Promise((resolve, reject) => {
      const callback = this.callbacks.get(jobId);
      if (callback) {
        callback.onResult = (result) => {
          resolve(result);
        };
        callback.onError = (error) => {
          reject(error);
        };
      }
    });
  }

  async processPDF(
    pdfFile: File,
    onProgress?: (progress: OCRProgress) => void,
    onPageComplete?: (result: OCRResult) => void
  ): Promise<OCRResult[]> {
    try {
      // Import PDF.js dynamically
      const pdfjsLib = await import('pdfjs-dist');
      
      // Set worker source
      pdfjsLib.GlobalWorkerOptions.workerSrc = '/node_modules/pdfjs-dist/build/pdf.worker.min.js';
      
      // Load PDF
      const arrayBuffer = await pdfFile.arrayBuffer();
      const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
      
      const results: OCRResult[] = [];
      
      // Process each page
      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        
        // Render page to canvas
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        const viewport = page.getViewport({ scale: 2.0 }); // 150 DPI equivalent
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        
        await page.render({
          canvasContext: context!,
          viewport: viewport
        }).promise;
        
        // Convert canvas to base64
        const imageData = canvas.toDataURL('image/png');
        
        // Process with OCR
        const result = await this.processImage(
          imageData,
          ['eng', 'hin', 'tam', 'tel'],
          pageNum,
          onProgress,
          onPageComplete
        );
        
        results.push(result);
      }
      
      return results;
      
    } catch (error) {
      console.error('PDF processing error:', error);
      throw new Error(`PDF processing failed: ${error.message}`);
    }
  }

  // Cleanup method
  destroy() {
    if (this.worker) {
      this.worker.terminate();
      this.worker = null;
    }
    this.callbacks.clear();
  }
}

// Singleton instance
export const ocrService = new OCRService();