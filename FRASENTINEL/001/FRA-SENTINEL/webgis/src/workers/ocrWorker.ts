// OCR Web Worker for Tesseract.js processing
// This worker handles OCR processing in a separate thread to avoid blocking the UI

import Tesseract from 'tesseract.js';

// Worker message types
interface OCRJob {
  id: string;
  imageData: string; // base64 image data
  languages: string[];
  pageNumber?: number;
}

interface OCRProgress {
  id: string;
  status: 'loading' | 'recognizing' | 'completed' | 'error';
  progress: number;
  message?: string;
}

interface OCRResult {
  id: string;
  text: string;
  confidence: number;
  words: Array<{
    text: string;
    confidence: number;
    bbox: {
      x0: number;
      y0: number;
      x1: number;
      y1: number;
    };
  }>;
  pageNumber?: number;
}

// Initialize Tesseract with language packs
let tesseractWorker: Tesseract.Worker | null = null;

async function initializeTesseract() {
  if (!tesseractWorker) {
    console.log('Initializing Tesseract.js worker...');
    tesseractWorker = await Tesseract.createWorker({
      logger: (m) => {
        // Log progress for debugging
        if (m.status === 'recognizing text') {
          console.log(`OCR Progress: ${Math.round(m.progress * 100)}%`);
        }
      }
    });
    
    // Load language packs
    await tesseractWorker.loadLanguage('eng+hin+tam+tel');
    await tesseractWorker.initialize('eng+hin+tam+tel');
    
    console.log('Tesseract.js worker initialized successfully');
  }
  return tesseractWorker;
}

// Process OCR job
async function processOCR(job: OCRJob): Promise<OCRResult> {
  try {
    const worker = await initializeTesseract();
    
    // Convert base64 to image
    const image = await Tesseract.createImageFromBase64(job.imageData);
    
    // Perform OCR
    const { data } = await worker.recognize(image, {
      logger: (m) => {
        // Send progress updates
        const progress: OCRProgress = {
          id: job.id,
          status: m.status === 'recognizing text' ? 'recognizing' : 'loading',
          progress: Math.round(m.progress * 100),
          message: m.status
        };
        
        self.postMessage({
          type: 'progress',
          data: progress
        });
      }
    });
    
    // Extract word-level data
    const words = data.words.map(word => ({
      text: word.text,
      confidence: word.confidence,
      bbox: {
        x0: word.bbox.x0,
        y0: word.bbox.y0,
        x1: word.bbox.x1,
        y1: word.bbox.y1
      }
    }));
    
    const result: OCRResult = {
      id: job.id,
      text: data.text,
      confidence: data.confidence,
      words,
      pageNumber: job.pageNumber
    };
    
    return result;
    
  } catch (error) {
    console.error('OCR processing error:', error);
    throw new Error(`OCR failed: ${error.message}`);
  }
}

// Handle messages from main thread
self.addEventListener('message', async (event) => {
  const { type, data } = event.data;
  
  try {
    switch (type) {
      case 'process':
        const result = await processOCR(data);
        self.postMessage({
          type: 'result',
          data: result
        });
        break;
        
      case 'initialize':
        await initializeTesseract();
        self.postMessage({
          type: 'initialized',
          data: { success: true }
        });
        break;
        
      default:
        throw new Error(`Unknown message type: ${type}`);
    }
  } catch (error) {
    self.postMessage({
      type: 'error',
      data: {
        id: data?.id || 'unknown',
        error: error.message
      }
    });
  }
});

// Initialize on worker start
initializeTesseract().catch(console.error);