// NER Service for server-side Named Entity Recognition
import { NERResult, NERSpan } from '../types';

export class NERService {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string = '/api', apiKey: string = '') {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async extractEntities(text: string): Promise<NERResult> {
    try {
      const response = await fetch(`${this.baseUrl}/ner`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': this.apiKey ? `Bearer ${this.apiKey}` : '',
        },
        body: JSON.stringify({
          text: text,
          language: 'mixed', // Support for multiple languages
          entities: [
            'PERSON',      // Names
            'ORG',         // Organizations
            'GPE',         // Geopolitical entities (villages, districts)
            'DATE',        // Dates
            'CARDINAL',    // Numbers
            'MONEY',       // Monetary values
            'PERCENT',     // Percentages
            'QUANTITY',    // Measurements
            'LOC'          // Locations
          ]
        })
      });

      if (!response.ok) {
        throw new Error(`NER API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        text: text,
        entities: data.entities || [],
        confidence: data.confidence || 0,
        language: data.language || 'unknown',
        processing_time: data.processing_time || 0
      };

    } catch (error) {
      console.error('NER extraction failed:', error);
      
      // Fallback: return basic result with no entities
      return {
        text: text,
        entities: [],
        confidence: 0,
        language: 'unknown',
        processing_time: 0,
        error: error.message
      };
    }
  }

  async extractPattaEntities(text: string): Promise<NERResult> {
    try {
      const response = await fetch(`${this.baseUrl}/ner/patta`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': this.apiKey ? `Bearer ${this.apiKey}` : '',
        },
        body: JSON.stringify({
          text: text,
          schema: 'patta', // Use patta-specific NER model
          languages: ['en', 'hi', 'ta', 'te'] // English, Hindi, Tamil, Telugu
        })
      });

      if (!response.ok) {
        throw new Error(`Patta NER API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        text: text,
        entities: data.entities || [],
        confidence: data.confidence || 0,
        language: data.language || 'unknown',
        processing_time: data.processing_time || 0,
        patta_specific: true
      };

    } catch (error) {
      console.error('Patta NER extraction failed:', error);
      
      // Fallback to general NER
      return this.extractEntities(text);
    }
  }

  // Helper method to merge OCR words with NER entities
  mergeOCRWithNER(ocrWords: any[], nerEntities: NERSpan[]): Array<{
    text: string;
    confidence: number;
    bbox: any;
    entity?: string;
    entity_confidence?: number;
  }> {
    return ocrWords.map(word => {
      // Find matching NER entity
      const matchingEntity = nerEntities.find(entity => 
        word.bbox.x0 >= entity.start_char && 
        word.bbox.x1 <= entity.end_char
      );

      return {
        text: word.text,
        confidence: word.confidence,
        bbox: word.bbox,
        entity: matchingEntity?.label,
        entity_confidence: matchingEntity?.confidence
      };
    });
  }

  // Extract specific patta fields using NER
  extractPattaFields(nerResult: NERResult): Record<string, any> {
    const fields: Record<string, any> = {};
    
    nerResult.entities.forEach(entity => {
      const label = entity.label.toLowerCase();
      const text = entity.text.trim();
      
      switch (label) {
        case 'person':
          if (!fields.claimant_name) {
            fields.claimant_name = text;
          } else if (!fields.father_or_spouse) {
            fields.father_or_spouse = text;
          }
          break;
          
        case 'gpe':
        case 'loc':
          if (text.toLowerCase().includes('village')) {
            fields.village = text.replace(/village/gi, '').trim();
          } else if (text.toLowerCase().includes('taluk')) {
            fields.taluk = text.replace(/taluk/gi, '').trim();
          } else if (text.toLowerCase().includes('district')) {
            fields.district = text.replace(/district/gi, '').trim();
          }
          break;
          
        case 'date':
          if (!fields.document_date) {
            fields.document_date = text;
          }
          break;
          
        case 'cardinal':
          if (text.match(/^\d+$/)) {
            if (!fields.survey_or_compartment_no) {
              fields.survey_or_compartment_no = text;
            }
          }
          break;
          
        case 'quantity':
          if (text.match(/\d+\.?\d*\s*(hectares?|acres?|sq\.?\s*ft)/i)) {
            fields.area = text;
          }
          break;
      }
    });
    
    return fields;
  }
}

// Singleton instance
export const nerService = new NERService();