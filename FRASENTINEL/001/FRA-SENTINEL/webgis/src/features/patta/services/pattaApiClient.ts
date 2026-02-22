// Real API Client for Patta Digitization System
import { UploadedFile, PattaSchema, OCRResult, NERResult } from '../types';

export interface UploadResponse {
  success: boolean;
  file_id: string;
  filename: string;
  size: number;
  message?: string;
}

export interface ExtractResponse {
  success: boolean;
  ocr_result: OCRResult;
  ner_result: NERResult;
  patta_data: PattaSchema;
  message?: string;
}

export interface SaveResponse {
  success: boolean;
  patta_id: string;
  message?: string;
}

export class PattaAPIClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string = '/api', apiKey: string = '') {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private getHeaders(includeAuth: boolean = true): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (includeAuth && this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    return headers;
  }

  // Upload file to server
  async uploadFile(file: File): Promise<UploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', 'patta_document');

      const response = await fetch(`${this.baseUrl}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': this.apiKey ? `Bearer ${this.apiKey}` : '',
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('File upload error:', error);
      throw new Error(`Upload failed: ${error.message}`);
    }
  }

  // Extract data from uploaded file
  async extractData(fileId: string): Promise<ExtractResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/extract`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          file_id: fileId,
          extract_ocr: true,
          extract_ner: true,
          languages: ['eng', 'hin', 'tam', 'tel']
        })
      });

      if (!response.ok) {
        throw new Error(`Extraction failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('Data extraction error:', error);
      throw new Error(`Extraction failed: ${error.message}`);
    }
  }

  // Save extracted patta data
  async savePatta(pattaData: PattaSchema): Promise<SaveResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/patta`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          patta_data: pattaData,
          source: 'ocr_ner_extraction',
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`Save failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('Save patta error:', error);
      throw new Error(`Save failed: ${error.message}`);
    }
  }

  // Get patta by ID
  async getPatta(pattaId: string): Promise<PattaSchema> {
    try {
      const response = await fetch(`${this.baseUrl}/patta/${pattaId}`, {
        method: 'GET',
        headers: this.getHeaders()
      });

      if (!response.ok) {
        throw new Error(`Get patta failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data.patta_data;

    } catch (error) {
      console.error('Get patta error:', error);
      throw new Error(`Get patta failed: ${error.message}`);
    }
  }

  // Update patta data
  async updatePatta(pattaId: string, pattaData: Partial<PattaSchema>): Promise<SaveResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/patta/${pattaId}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify({
          patta_data: pattaData,
          updated_at: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`Update failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('Update patta error:', error);
      throw new Error(`Update failed: ${error.message}`);
    }
  }

  // Delete patta
  async deletePatta(pattaId: string): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/patta/${pattaId}`, {
        method: 'DELETE',
        headers: this.getHeaders()
      });

      if (!response.ok) {
        throw new Error(`Delete failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('Delete patta error:', error);
      throw new Error(`Delete failed: ${error.message}`);
    }
  }

  // List all pattas
  async listPattas(limit: number = 50, offset: number = 0): Promise<{
    pattas: PattaSchema[];
    total: number;
    has_more: boolean;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/pattas?limit=${limit}&offset=${offset}`, {
        method: 'GET',
        headers: this.getHeaders()
      });

      if (!response.ok) {
        throw new Error(`List pattas failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('List pattas error:', error);
      throw new Error(`List pattas failed: ${error.message}`);
    }
  }

  // Search pattas
  async searchPattas(query: string, filters?: {
    village?: string;
    district?: string;
    claim_type?: string;
  }): Promise<{
    pattas: PattaSchema[];
    total: number;
  }> {
    try {
      const searchParams = new URLSearchParams({
        q: query,
        ...filters
      });

      const response = await fetch(`${this.baseUrl}/pattas/search?${searchParams}`, {
        method: 'GET',
        headers: this.getHeaders()
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('Search pattas error:', error);
      throw new Error(`Search failed: ${error.message}`);
    }
  }

  // Health check
  async healthCheck(): Promise<{
    status: 'healthy' | 'unhealthy';
    services: {
      ocr: boolean;
      ner: boolean;
      database: boolean;
    };
    message?: string;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: this.getHeaders(false)
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('Health check error:', error);
      return {
        status: 'unhealthy',
        services: {
          ocr: false,
          ner: false,
          database: false
        },
        message: error.message
      };
    }
  }
}

// Singleton instance
export const pattaAPIClient = new PattaAPIClient();