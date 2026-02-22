// Patta Schema Types
export interface PattaCoords {
  lat: number;
  lng: number;
}

export interface PattaSchema {
  claimant_name: string;
  father_or_spouse: string;
  caste_st: string;
  village: string;
  taluk: string;
  district: string;
  survey_or_compartment_no: string;
  sub_division: string;
  coords: PattaCoords | null;
  area: number | null;
  document_no: string;
  document_date: string;
  claim_type: string;
  raw_text: string;
  ocr_confidence: number;
}

// OCR Types
export interface OCRPage {
  pageNo: number;
  text: string;
  conf: number;
}

export interface OCRResult {
  pages: OCRPage[];
  fullText: string;
  totalConfidence: number;
}

// NER Types
export interface NERSpan {
  text: string;
  label: string;
  start: number;
  end: number;
  score: number;
}

export interface NERResult {
  spans: NERSpan[];
  locale: string;
}

// Upload Types
export interface UploadedFile {
  id: string;
  file: File;
  type: 'image' | 'pdf';
  thumbnail?: string;
  pages?: string[]; // PDF page thumbnails
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  ocrResult?: OCRResult;
  nerResult?: NERResult;
  pattaData?: PattaSchema;
  error?: string;
}

// API Types
export interface UploadResponse {
  success: boolean;
  fileId: string;
  message: string;
}

export interface ExtractResponse {
  success: boolean;
  extractedData: any;
  message: string;
}

export interface NERRequest {
  text: string;
  locale: string;
}

export interface NERResponse {
  success: boolean;
  spans: NERSpan[];
  message: string;
}

export interface PattaSaveRequest {
  pattaData: PattaSchema;
  fileId: string;
}

export interface PattaSaveResponse {
  success: boolean;
  pattaId: string;
  message: string;
}

// Configuration Types
export interface OCRConfig {
  languages: string[];
  poolSize: number;
  timeout: number;
  dpi: number;
}

export interface UploadConfig {
  maxFileSizeMB: number;
  maxPdfPages: number;
  allowedTypes: string[];
  apiBase: string;
}

// Worker Types
export interface OCRWorkerMessage {
  type: 'init' | 'process' | 'terminate' | 'progress' | 'result' | 'error';
  data?: any;
}

export interface OCRWorkerProgress {
  pageNo: number;
  progress: number;
  status: string;
}

export interface OCRWorkerResult {
  pages: OCRPage[];
  fullText: string;
  totalConfidence: number;
}






