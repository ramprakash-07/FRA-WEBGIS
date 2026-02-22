import * as pdfjsLib from 'pdfjs-dist';

// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

export interface PDFPage {
  pageNo: number;
  canvas: HTMLCanvasElement;
  thumbnail: string;
}

export interface PDFRasterizationOptions {
  dpi: number;
  maxPages: number;
}

export class PDFRasterizer {
  private options: PDFRasterizationOptions;

  constructor(options: PDFRasterizationOptions = { dpi: 150, maxPages: 20 }) {
    this.options = options;
  }

  async rasterizePDF(file: File, onProgress?: (progress: number) => void): Promise<PDFPage[]> {
    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      
      const totalPages = Math.min(pdf.numPages, this.options.maxPages);
      const pages: PDFPage[] = [];

      for (let pageNum = 1; pageNum <= totalPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        
        // Calculate scale based on DPI
        const scale = this.options.dpi / 72; // 72 is default DPI
        const viewport = page.getViewport({ scale });

        // Create canvas
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        if (!context) {
          throw new Error('Failed to get canvas context');
        }

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        // Render page to canvas
        await page.render({
          canvasContext: context,
          viewport: viewport
        }).promise;

        // Create thumbnail (smaller version)
        const thumbnailCanvas = document.createElement('canvas');
        const thumbnailContext = thumbnailCanvas.getContext('2d');
        
        if (!thumbnailContext) {
          throw new Error('Failed to get thumbnail canvas context');
        }

        const thumbnailScale = 0.2; // 20% of original size
        thumbnailCanvas.width = canvas.width * thumbnailScale;
        thumbnailCanvas.height = canvas.height * thumbnailScale;

        thumbnailContext.drawImage(
          canvas,
          0, 0, canvas.width, canvas.height,
          0, 0, thumbnailCanvas.width, thumbnailCanvas.height
        );

        pages.push({
          pageNo: pageNum,
          canvas: canvas,
          thumbnail: thumbnailCanvas.toDataURL('image/jpeg', 0.8)
        });

        // Update progress
        if (onProgress) {
          onProgress((pageNum / totalPages) * 100);
        }
      }

      return pages;

    } catch (error) {
      throw new Error(`PDF rasterization failed: ${error.message}`);
    }
  }

  async createImageFromCanvas(canvas: HTMLCanvasElement): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error('Failed to create image from canvas'));
      img.src = canvas.toDataURL('image/png');
    });
  }

  async createImageDataFromCanvas(canvas: HTMLCanvasElement): Promise<ImageData> {
    const context = canvas.getContext('2d');
    if (!context) {
      throw new Error('Failed to get canvas context');
    }
    return context.getImageData(0, 0, canvas.width, canvas.height);
  }
}






