import { PattaSchema, PattaCoords } from '../types';

export class PattaNormalizer {
  private patterns: Record<string, RegExp[]>;

  constructor() {
    this.patterns = {
      claimantName: [
        /(?:claimant|name|holder)[\s:]*([A-Za-z\s]+)/i,
        /([A-Za-z\s]{3,})[\s]*(?:son|daughter|of)/i,
        /(?:name)[\s:]*([A-Za-z\s]+)/i
      ],
      fatherOrSpouse: [
        /(?:son|daughter)\s+of\s+([A-Za-z\s]+)/i,
        /(?:father|mother|spouse)[\s:]*([A-Za-z\s]+)/i,
        /(?:s\/o|d\/o|w\/o)[\s:]*([A-Za-z\s]+)/i
      ],
      casteSt: [
        /(?:caste|community)[\s:]*([A-Za-z\s]+)/i,
        /(?:ST|Scheduled Tribe|SC|Scheduled Caste)/i,
        /(?:tribal|tribe)[\s:]*([A-Za-z\s]+)/i
      ],
      village: [
        /(?:village|vlg)[\s:]*([A-Za-z\s]+)/i,
        /(?:gram)[\s:]*([A-Za-z\s]+)/i,
        /(?:place)[\s:]*([A-Za-z\s]+)/i
      ],
      taluk: [
        /(?:taluk|taluka)[\s:]*([A-Za-z\s]+)/i,
        /(?:tehsil)[\s:]*([A-Za-z\s]+)/i
      ],
      district: [
        /(?:district)[\s:]*([A-Za-z\s]+)/i,
        /(?:dist)[\s:]*([A-Za-z\s]+)/i
      ],
      surveyNo: [
        /(?:survey|s\.no|sno)[\s:]*(\d+)/i,
        /(?:plot|khasra)[\s:]*(\d+)/i,
        /(?:patta)[\s:]*(\d+)/i
      ],
      subDivision: [
        /(?:sub.?division|sub.?div)[\s:]*([A-Za-z\s]+)/i,
        /(?:range)[\s:]*([A-Za-z\s]+)/i
      ],
      coordinates: [
        /(?:lat|latitude)[\s:]*(\d+\.?\d*)/i,
        /(?:lng|longitude)[\s:]*(\d+\.?\d*)/i,
        /(\d+\.?\d*)[\s]*°?[\s]*(?:N|S|E|W)/i
      ],
      area: [
        /(?:area|hectares|acres)[\s:]*(\d+\.?\d*)/i,
        /(\d+\.?\d*)[\s]*(?:hectares|acres|ha|sq\.m)/i
      ],
      documentNo: [
        /(?:document|doc|patta)[\s:]*no[\.\s:]*(\d+)/i,
        /(?:no)[\s:]*(\d+)/i
      ],
      documentDate: [
        /(?:date)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})/i,
        /(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})/i
      ],
      claimType: [
        /(?:IFR|Individual Forest Rights)/i,
        /(?:CR|Community Rights)/i,
        /(?:CFR|Community Forest Rights)/i,
        /(?:Individual|Community)[\s]*(?:Forest|Rights)/i
      ]
    };
  }

  normalize(rawText: string, ocrConfidence: number): PattaSchema {
    const normalized: PattaSchema = {
      claimant_name: '',
      father_or_spouse: '',
      caste_st: '',
      village: '',
      taluk: '',
      district: '',
      survey_or_compartment_no: '',
      sub_division: '',
      coords: null,
      area: null,
      document_no: '',
      document_date: '',
      claim_type: '',
      raw_text: rawText,
      ocr_confidence: ocrConfidence
    };

    // Extract each field
    normalized.claimant_name = this.extractClaimantName(rawText);
    normalized.father_or_spouse = this.extractFatherOrSpouse(rawText);
    normalized.caste_st = this.extractCasteSt(rawText);
    normalized.village = this.extractVillage(rawText);
    normalized.taluk = this.extractTaluk(rawText);
    normalized.district = this.extractDistrict(rawText);
    normalized.survey_or_compartment_no = this.extractSurveyNo(rawText);
    normalized.sub_division = this.extractSubDivision(rawText);
    normalized.coords = this.extractCoordinates(rawText);
    normalized.area = this.extractArea(rawText);
    normalized.document_no = this.extractDocumentNo(rawText);
    normalized.document_date = this.extractDocumentDate(rawText);
    normalized.claim_type = this.extractClaimType(rawText);

    return normalized;
  }

  private extractClaimantName(text: string): string {
    for (const pattern of this.patterns.claimantName) {
      const match = text.match(pattern);
      if (match) {
        return match[1].trim();
      }
    }
    return '';
  }

  private extractFatherOrSpouse(text: string): string {
    for (const pattern of this.patterns.fatherOrSpouse) {
      const match = text.match(pattern);
      if (match) {
        return match[1].trim();
      }
    }
    return '';
  }

  private extractCasteSt(text: string): string {
    for (const pattern of this.patterns.casteSt) {
      const match = text.match(pattern);
      if (match) {
        return match[1] ? match[1].trim() : match[0].trim();
      }
    }
    return '';
  }

  private extractVillage(text: string): string {
    for (const pattern of this.patterns.village) {
      const match = text.match(pattern);
      if (match) {
        return match[1].trim();
      }
    }
    return '';
  }

  private extractTaluk(text: string): string {
    for (const pattern of this.patterns.taluk) {
      const match = text.match(pattern);
      if (match) {
        return match[1].trim();
      }
    }
    return '';
  }

  private extractDistrict(text: string): string {
    for (const pattern of this.patterns.district) {
      const match = text.match(pattern);
      if (match) {
        return match[1].trim();
      }
    }
    return '';
  }

  private extractSurveyNo(text: string): string {
    for (const pattern of this.patterns.surveyNo) {
      const match = text.match(pattern);
      if (match) {
        return match[1].trim();
      }
    }
    return '';
  }

  private extractSubDivision(text: string): string {
    for (const pattern of this.patterns.subDivision) {
      const match = text.match(pattern);
      if (match) {
        return match[1].trim();
      }
    }
    return '';
  }

  private extractCoordinates(text: string): PattaCoords | null {
    const latMatch = text.match(/(?:lat|latitude)[\s:]*(\d+\.?\d*)/i);
    const lngMatch = text.match(/(?:lng|longitude)[\s:]*(\d+\.?\d*)/i);
    
    if (latMatch && lngMatch) {
      const lat = parseFloat(latMatch[1]);
      const lng = parseFloat(lngMatch[1]);
      
      // Basic validation for Indian coordinates
      if (lat >= 6 && lat <= 37 && lng >= 68 && lng <= 97) {
        return { lat, lng };
      }
    }
    
    return null;
  }

  private extractArea(text: string): number | null {
    for (const pattern of this.patterns.area) {
      const match = text.match(pattern);
      if (match) {
        return parseFloat(match[1]);
      }
    }
    return null;
  }

  private extractDocumentNo(text: string): string {
    for (const pattern of this.patterns.documentNo) {
      const match = text.match(pattern);
      if (match) {
        return match[1].trim();
      }
    }
    return '';
  }

  private extractDocumentDate(text: string): string {
    for (const pattern of this.patterns.documentDate) {
      const match = text.match(pattern);
      if (match) {
        return match[1].trim();
      }
    }
    return '';
  }

  private extractClaimType(text: string): string {
    for (const pattern of this.patterns.claimType) {
      const match = text.match(pattern);
      if (match) {
        const type = match[0].toUpperCase();
        if (type.includes('IFR')) return 'IFR';
        if (type.includes('CR')) return 'CR';
        if (type.includes('CFR')) return 'CFR';
        return type;
      }
    }
    return '';
  }

  // Method to merge with NER results
  mergeWithNER(normalized: PattaSchema, nerSpans: any[]): PattaSchema {
    const merged = { ...normalized };

    // Process NER spans and update fields with higher confidence
    nerSpans.forEach(span => {
      if (span.score > 0.7) { // Only use high-confidence spans
        switch (span.label) {
          case 'NAME':
            if (!merged.claimant_name || span.score > 0.8) {
              merged.claimant_name = span.text.trim();
            }
            break;
          case 'FATHER_SPOUSE':
            if (!merged.father_or_spouse || span.score > 0.8) {
              merged.father_or_spouse = span.text.trim();
            }
            break;
          case 'VILLAGE':
            if (!merged.village || span.score > 0.8) {
              merged.village = span.text.trim();
            }
            break;
          case 'TALUK':
            if (!merged.taluk || span.score > 0.8) {
              merged.taluk = span.text.trim();
            }
            break;
          case 'DISTRICT':
            if (!merged.district || span.score > 0.8) {
              merged.district = span.text.trim();
            }
            break;
          case 'SURVEY_NO':
            if (!merged.survey_or_compartment_no || span.score > 0.8) {
              merged.survey_or_compartment_no = span.text.trim();
            }
            break;
          case 'SUB_DIV':
            if (!merged.sub_division || span.score > 0.8) {
              merged.sub_division = span.text.trim();
            }
            break;
          case 'AREA':
            const area = this.parseArea(span.text);
            if (area && (!merged.area || span.score > 0.8)) {
              merged.area = area;
            }
            break;
          case 'COORDS':
            const coords = this.extractCoordinates(span.text);
            if (coords && (!merged.coords || span.score > 0.8)) {
              merged.coords = coords;
            }
            break;
          case 'CLAIM_TYPE':
            if (!merged.claim_type || span.score > 0.8) {
              merged.claim_type = span.text.trim();
            }
            break;
          case 'DOC_NO':
            if (!merged.document_no || span.score > 0.8) {
              merged.document_no = span.text.trim();
            }
            break;
          case 'DOC_DATE':
            if (!merged.document_date || span.score > 0.8) {
              merged.document_date = span.text.trim();
            }
            break;
        }
      }
    });

    return merged;
  }
}






