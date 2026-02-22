import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PattaUpload } from '../components/PattaUpload';
import { PattaNormalizer } from '../services/pattaNormalizer';
import { NERService } from '../services/nerService';
import { PattaApiClient } from '../services/pattaApiClient';

// Mock dependencies
vi.mock('react-dropzone', () => ({
  useDropzone: () => ({
    getRootProps: () => ({}),
    getInputProps: () => ({}),
    isDragActive: false
  })
}));

vi.mock('../services/ocrService', () => ({
  OCRService: vi.fn().mockImplementation(() => ({
    initialize: vi.fn().mockResolvedValue(undefined),
    setProgressCallback: vi.fn(),
    processImage: vi.fn().mockResolvedValue({
      pageNo: 0,
      text: 'Sample OCR text',
      conf: 85
    }),
    processMultipleImages: vi.fn().mockResolvedValue({
      pages: [{ pageNo: 0, text: 'Sample OCR text', conf: 85 }],
      fullText: 'Sample OCR text',
      totalConfidence: 85
    })
  }))
}));

vi.mock('../services/pdfRasterizer', () => ({
  PDFRasterizer: vi.fn().mockImplementation(() => ({
    rasterizePDF: vi.fn().mockResolvedValue([
      {
        pageNo: 1,
        canvas: document.createElement('canvas'),
        thumbnail: 'data:image/jpeg;base64,test'
      }
    ]),
    createImageFromCanvas: vi.fn().mockResolvedValue(new Image())
  }))
}));

describe('PattaUpload Component', () => {
  let mockOnPattaExtracted: vi.Mock;
  let mockOnError: vi.Mock;

  beforeEach(() => {
    mockOnPattaExtracted = vi.fn();
    mockOnError = vi.fn();
  });

  it('renders upload component correctly', () => {
    render(
      <PattaUpload
        onPattaExtracted={mockOnPattaExtracted}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('Patta Document Digitization')).toBeInTheDocument();
    expect(screen.getByText('Upload JPG, PNG, or PDF files for OCR processing and NER extraction')).toBeInTheDocument();
  });

  it('shows file validation message', () => {
    render(
      <PattaUpload
        onPattaExtracted={mockOnPattaExtracted}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('Supports JPG, PNG, PDF (max 25MB each)')).toBeInTheDocument();
  });
});

describe('PattaNormalizer', () => {
  let normalizer: PattaNormalizer;

  beforeEach(() => {
    normalizer = new PattaNormalizer();
  });

  it('normalizes basic patta text correctly', () => {
    const sampleText = `
      Claimant Name: John Doe
      Son of: Robert Doe
      Village: Sample Village
      District: Sample District
      Area: 2.5 hectares
      Survey No: 123
    `;

    const result = normalizer.normalize(sampleText, 85);

    expect(result.claimant_name).toBe('John Doe');
    expect(result.father_or_spouse).toBe('Robert Doe');
    expect(result.village).toBe('Sample Village');
    expect(result.district).toBe('Sample District');
    expect(result.area).toBe(2.5);
    expect(result.survey_or_compartment_no).toBe('123');
    expect(result.raw_text).toBe(sampleText);
    expect(result.ocr_confidence).toBe(85);
  });

  it('extracts coordinates correctly', () => {
    const sampleText = 'Latitude: 21.8225 Longitude: 75.6102';
    const result = normalizer.normalize(sampleText, 90);

    expect(result.coords).toEqual({ lat: 21.8225, lng: 75.6102 });
  });

  it('identifies claim type correctly', () => {
    const sampleText = 'Individual Forest Rights Application';
    const result = normalizer.normalize(sampleText, 80);

    expect(result.claim_type).toBe('IFR');
  });

  it('handles empty or missing fields gracefully', () => {
    const sampleText = 'Some random text without structured data';
    const result = normalizer.normalize(sampleText, 70);

    expect(result.claimant_name).toBe('');
    expect(result.village).toBe('');
    expect(result.coords).toBeNull();
    expect(result.area).toBeNull();
  });
});

describe('NERService', () => {
  let nerService: NERService;

  beforeEach(() => {
    nerService = new NERService('https://api.fra-sentinel.gov.in');
    // Mock fetch
    global.fetch = vi.fn();
  });

  it('extracts entities successfully', async () => {
    const mockResponse = {
      success: true,
      spans: [
        { text: 'John Doe', label: 'NAME', start: 0, end: 8, score: 0.95 },
        { text: 'Sample Village', label: 'VILLAGE', start: 10, end: 23, score: 0.88 }
      ]
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    });

    const result = await nerService.extractEntities('John Doe from Sample Village');

    expect(result).toHaveLength(2);
    expect(result[0].text).toBe('John Doe');
    expect(result[0].label).toBe('NAME');
    expect(result[1].text).toBe('Sample Village');
    expect(result[1].label).toBe('VILLAGE');
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error'
    });

    await expect(nerService.extractEntities('test text')).rejects.toThrow('NER API error: 500 Internal Server Error');
  });

  it('retries on failure', async () => {
    const mockResponse = {
      success: true,
      spans: [{ text: 'John Doe', label: 'NAME', start: 0, end: 8, score: 0.95 }]
    };

    (global.fetch as any)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

    const result = await nerService.extractEntitiesWithRetry('John Doe', 'en', 3);

    expect(result).toHaveLength(1);
    expect(result[0].text).toBe('John Doe');
  });
});

describe('PattaApiClient', () => {
  let apiClient: PattaApiClient;

  beforeEach(() => {
    apiClient = new PattaApiClient('https://api.fra-sentinel.gov.in');
    global.fetch = vi.fn();
  });

  it('validates file correctly', () => {
    const validFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' });
    const largeFile = new File(['x'.repeat(30 * 1024 * 1024)], 'large.jpg', { type: 'image/jpeg' });

    expect(apiClient.validateFile(validFile).valid).toBe(true);
    expect(apiClient.validateFile(invalidFile).valid).toBe(false);
    expect(apiClient.validateFile(largeFile).valid).toBe(false);
  });

  it('uploads file successfully', async () => {
    const mockResponse = {
      success: true,
      fileId: 'test-file-id',
      message: 'File uploaded successfully'
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    });

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const result = await apiClient.uploadFile(file);

    expect(result.success).toBe(true);
    expect(result.fileId).toBe('test-file-id');
  });

  it('saves patta data successfully', async () => {
    const mockResponse = {
      success: true,
      pattaId: 'patta-123',
      message: 'Patta saved successfully'
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    });

    const pattaData = {
      claimant_name: 'John Doe',
      village: 'Sample Village',
      raw_text: 'Sample text',
      ocr_confidence: 85
    };

    const result = await apiClient.savePatta(pattaData, 'file-123');

    expect(result.success).toBe(true);
    expect(result.pattaId).toBe('patta-123');
  });

  it('retries failed requests', async () => {
    const mockResponse = { success: true, data: 'test' };

    (global.fetch as any)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

    const result = await apiClient.retryRequest(async () => {
      const response = await fetch('/test');
      return response.json();
    }, 3);

    expect(result.success).toBe(true);
  });
});






