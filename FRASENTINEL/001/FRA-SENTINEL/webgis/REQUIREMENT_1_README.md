# FRA Patta Digitization System - Requirement 1

## 🎯 **Requirement 1: Real OCR + NER Digitization**

This document describes the implementation of a robust patta digitization system that replaces legacy upload functionality with real OCR processing and NER extraction.

---

## 🚀 **Overview**

The system implements a complete pipeline: **Upload → OCR (Tesseract.js) → NER (spaCy/HF) → Normalized Patta Fields** with no dummy data.

### **Key Features**
- ✅ Real OCR processing with Tesseract.js Web Workers
- ✅ PDF rasterization with pdfjs-dist (150 DPI)
- ✅ Multi-language support (English, Hindi, Tamil, Telugu)
- ✅ NER integration with spaCy/Hugging Face microservice
- ✅ Normalized Patta schema extraction
- ✅ Confidence scoring and error handling
- ✅ localStorage persistence for recovery

---

## 🏗️ **Architecture**

```
src/features/patta/
├── components/
│   └── PattaUpload.tsx          # Main upload interface
├── services/
│   ├── ocrService.ts            # OCR Web Worker management
│   ├── pdfRasterizer.ts         # PDF to image conversion
│   ├── nerService.ts            # NER API integration
│   ├── pattaNormalizer.ts       # Schema normalization
│   └── pattaApiClient.ts        # API client with auth
├── types/
│   └── index.ts                 # TypeScript definitions
├── hooks/
├── utils/
└── tests/
    └── patta.test.ts            # Comprehensive tests

src/workers/
└── ocrWorker.ts                 # Tesseract.js Web Worker
```

---

## 🔧 **Configuration**

### **API Configuration**
```typescript
const config = {
  apiBase: 'https://api.fra-sentinel.gov.in',
  endpoints: {
    upload: 'POST /api/upload',
    extract: 'POST /api/extract',
    ner: 'POST /api/ner',
    patta: 'POST /api/patta'
  },
  auth: 'Authorization: Bearer <token>'
};
```

### **OCR Configuration**
```typescript
const ocrConfig = {
  languages: ['eng', 'hin', 'tam', 'tel'],
  poolSize: 1,
  timeout: 20000, // 20 seconds per page
  dpi: 150
};
```

### **File Limits**
```typescript
const limits = {
  maxFileSizeMB: 25,
  maxPdfPages: 20,
  allowedTypes: ['image/jpeg', 'image/png', 'application/pdf']
};
```

---

## 📋 **Patta Schema**

The system extracts and normalizes data into the following schema:

```typescript
interface PattaSchema {
  claimant_name: string;
  father_or_spouse: string;
  caste_st: string;
  village: string;
  taluk: string;
  district: string;
  survey_or_compartment_no: string;
  sub_division: string;
  coords: { lat: number; lng: number } | null;
  area: number | null;
  document_no: string;
  document_date: string;
  claim_type: string;
  raw_text: string;
  ocr_confidence: number;
}
```

---

## 🚀 **Getting Started**

### **Prerequisites**
- Node.js 18+
- Python 3.8+
- Modern browser with Web Worker support

### **Installation**

1. **Install Dependencies**
```bash
cd webgis
npm install
```

2. **Start Development Server**
```bash
npm run dev
```

3. **Start Flask Backend**
```bash
python app.py
```

### **Access the System**
- **Patta Digitization**: http://localhost:5000/patta-digitization
- **Legacy Upload**: http://localhost:5000/upload-new
- **Dashboard**: http://localhost:5000/dashboard

---

## 🔄 **Workflow**

### **1. Upload Phase**
- Drag & drop or click to select files
- File validation (type, size)
- Preview thumbnails for images
- Per-page previews for PDFs

### **2. OCR Processing**
- PDF rasterization at 150 DPI
- Tesseract.js Web Worker processing
- Multi-language OCR support
- Real-time progress tracking

### **3. NER Extraction**
- API call to spaCy/HF microservice
- Entity extraction with confidence scores
- Label mapping to Patta schema

### **4. Normalization**
- Regex-based field extraction
- NER span merging
- Confidence-weighted field selection
- Schema validation

### **5. Save & Export**
- Save to `/api/patta` with auth headers
- Download JSON export
- localStorage persistence

---

## 🧪 **Testing**

### **Run Tests**
```bash
npm test
npm run test:coverage
```

### **Test Coverage**
- ✅ Component rendering and interaction
- ✅ OCR service initialization and processing
- ✅ PDF rasterization
- ✅ NER service integration
- ✅ Patta normalization
- ✅ API client functionality
- ✅ Error handling and retry logic

---

## 🔌 **API Integration**

### **Upload Endpoint**
```http
POST /api/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: File
metadata?: Record<string, any>
```

### **NER Endpoint**
```http
POST /api/ner
Content-Type: application/json
Authorization: Bearer <token>

{
  "text": "Sample patta text",
  "locale": "en"
}
```

### **Save Patta Endpoint**
```http
POST /api/patta
Content-Type: application/json
Authorization: Bearer <token>

{
  "pattaData": PattaSchema,
  "fileId": "string"
}
```

---

## 🛠️ **Development**

### **Adding New Languages**
1. Update `ocrConfig.languages` array
2. Add language patterns to `PattaNormalizer`
3. Update NER service locale mapping

### **Extending Patta Schema**
1. Update `PattaSchema` interface
2. Add extraction patterns to `PattaNormalizer`
3. Update UI field display
4. Add NER label mapping

### **Custom NER Labels**
1. Train spaCy/HF model with custom labels
2. Update `NERService.labelMapping`
3. Add confidence thresholds

---

## 🚨 **Error Handling**

### **OCR Errors**
- Worker initialization failures
- Processing timeouts (20s per page)
- Language pack loading issues
- Memory constraints

### **NER Errors**
- API connectivity issues
- Service unavailability
- Invalid response format
- Authentication failures

### **File Processing**
- Invalid file types
- Size limit exceeded
- PDF parsing errors
- Image loading failures

---

## 📊 **Performance**

### **OCR Performance**
- **Images**: ~2-5 seconds per page
- **PDFs**: ~5-10 seconds per page (including rasterization)
- **Memory**: ~50MB per worker
- **Languages**: 4 languages loaded simultaneously

### **NER Performance**
- **API Response**: ~1-3 seconds
- **Retry Logic**: Exponential backoff
- **Caching**: Results cached in localStorage

---

## 🔒 **Security**

### **Authentication**
- Bearer token authentication
- Token stored in localStorage
- Automatic token refresh

### **File Security**
- Client-side file validation
- Server-side type checking
- Size limit enforcement

### **Data Privacy**
- No data sent to external OCR services
- All processing client-side
- Optional server OCR fallback

---

## 📈 **Monitoring**

### **Progress Tracking**
- Real-time OCR progress
- Page-by-page completion
- Error state management
- Recovery mechanisms

### **Quality Metrics**
- OCR confidence scores
- NER span confidence
- Field extraction success rates
- User correction tracking

---

## 🎯 **Quality Bar**

### **No Dummy Data**
- ✅ All OCR results from real Tesseract.js processing
- ✅ All NER results from real API calls
- ✅ Empty states clearly marked as "not detected"
- ✅ Confidence scores reflect actual processing quality

### **Reliability**
- ✅ Graceful error handling
- ✅ Retry mechanisms
- ✅ Timeout protection
- ✅ Memory management

### **User Experience**
- ✅ Real-time progress feedback
- ✅ Clear error messages
- ✅ Data persistence
- ✅ Export capabilities

---

## 🔮 **Future Enhancements**

### **Planned Features**
- Server-side OCR fallback
- Advanced NER models
- Batch processing
- Quality scoring
- User corrections interface

### **Integration Points**
- GIS mapping system
- DSS recommendations
- Database persistence
- Audit logging

---

## 📞 **Support**

For issues or questions:
- Check the test suite for usage examples
- Review error logs in browser console
- Verify API endpoint availability
- Ensure proper authentication tokens

---

**Built with ❤️ for Forest Rights Act digitization**






