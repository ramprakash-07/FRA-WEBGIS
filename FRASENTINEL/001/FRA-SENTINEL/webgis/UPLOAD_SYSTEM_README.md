# FRA Sentinel Upload System

A modern, React-based upload system for Forest Rights Act (FRA) document processing with OCR, GeoJSON mapping, and DSS recommendations.

## 🚀 Features

### ✅ Complete Upload Pipeline
- **Drag & Drop Interface**: Modern file upload with progress tracking
- **Multi-format Support**: JPG, PNG, PDF files with validation
- **File Management**: Cancel, retry, and error handling
- **Size Limits**: Configurable file size limits (default 10MB)

### 🔍 Client-side OCR Processing
- **Tesseract.js Integration**: Web Worker-based OCR processing
- **Multi-language Support**: English, Hindi, Tamil, Telugu
- **Progress Tracking**: Real-time OCR progress with callbacks
- **PDF Processing**: Multi-page PDF extraction and stitching
- **Pre-processing**: Optional image enhancement (grayscale, threshold, deskew)

### 📊 Intelligent Data Extraction
- **Structured Parsing**: Extracts claimant names, village, coordinates, area
- **Claim Type Detection**: IFR, CR, CFR classification
- **Evidence Recognition**: Identifies supporting documents mentioned
- **Normalized Output**: Consistent JSON format for all extractions

### 🗺️ Interactive Map Editor
- **React-Leaflet Integration**: Modern mapping interface
- **Geometry Creation**: Point and polygon drawing tools
- **Coordinate Validation**: Automatic coordinate extraction and validation
- **Manual Editing**: Draw/edit boundaries with undo/clear functionality
- **GeoJSON Export**: Standard format for geometry storage

### 🎯 DSS Recommendations
- **Scheme Matching**: Intelligent government scheme recommendations
- **Eligibility Scoring**: Percentage-based eligibility assessment
- **Ministry Integration**: Ministry-wise scheme categorization
- **Export Options**: CSV and PDF export capabilities
- **Guidelines**: Step-by-step application guidelines

### ⚙️ Settings & Configuration
- **OCR Language Packs**: Configurable language support
- **Map Tile Providers**: Multiple tile source options
- **API Configuration**: Flexible backend endpoint configuration
- **Feature Flags**: Enable/disable features as needed

## 🏗️ Architecture

```
src/features/upload/
├── components/
│   ├── UploadComponent.tsx      # Main upload interface
│   ├── MapEditor.tsx          # Interactive map editor
│   ├── DSSPanel.tsx           # Recommendations display
│   └── SettingsModal.tsx      # Configuration modal
├── services/
│   ├── ocrService.ts          # Tesseract.js integration
│   ├── extractionParser.ts    # Data extraction logic
│   └── apiClient.ts          # Backend API client
├── hooks/
│   └── useUpload.ts          # Upload state management
├── types/
│   └── index.ts              # TypeScript definitions
└── tests/
    └── upload.test.ts        # Unit tests
```

## 🛠️ Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Maps**: React-Leaflet, Leaflet
- **OCR**: Tesseract.js with Web Workers
- **PDF**: pdfjs-dist for PDF processing
- **HTTP**: Axios with retry logic
- **Testing**: Vitest, React Testing Library
- **Build**: Vite
- **Backend**: Flask (Python)

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- npm or yarn

### Frontend Setup
```bash
cd webgis
npm install
npm run dev
```

### Backend Setup
```bash
pip install -r requirements.txt
python app.py
```

## 🚀 Usage

### 1. Access the Upload System
Navigate to `http://localhost:5000/upload-new`

### 2. Upload Documents
- Drag & drop files or click to browse
- Supported formats: JPG, PNG, PDF
- Maximum file size: 10MB (configurable)

### 3. OCR Processing
- Automatic text extraction using Tesseract.js
- Multi-language support (English, Hindi, Tamil, Telugu)
- Real-time progress tracking

### 4. Map Editor
- Review extracted coordinates
- Draw/edit land boundaries
- Save geometry as GeoJSON

### 5. DSS Analysis
- View government scheme recommendations
- Check eligibility scores
- Export results to CSV/PDF

## 🔧 Configuration

### OCR Settings
```typescript
const settings = {
  ocrLanguages: ['eng', 'hin', 'tam', 'tel'],
  defaultLanguage: 'eng',
  maxFileSize: 10 // MB
};
```

### API Configuration
```typescript
const apiConfig = {
  baseURL: 'http://localhost:5000',
  timeout: 30000,
  authToken: 'your-auth-token'
};
```

### Map Settings
```typescript
const mapConfig = {
  tileUrl: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  enableSatelliteLayer: false
};
```

## 📡 API Endpoints

### Upload
```http
POST /api/upload
Content-Type: multipart/form-data

file: File
metadata?: Record<string, any>
```

### Extract
```http
POST /api/extract
Content-Type: application/json

{
  "fileId": "string"
}
```

### Save Geometry
```http
POST /api/claims/{id}/geometry
Content-Type: application/json

{
  "geometry": {
    "type": "Point|Polygon",
    "coordinates": [...]
  }
}
```

### DSS Recommendations
```http
POST /api/upload/dss/recommendations
Content-Type: application/json

{
  "fields": {...},
  "geometry": {...}
}
```

## 🧪 Testing

### Run Tests
```bash
npm test
npm run test:ui
```

### Test Coverage
```bash
npm run test:coverage
```

## 🔒 Security Features

- **File Validation**: Type and size validation
- **CSRF Protection**: Token-based CSRF protection
- **Authentication**: Bearer token authentication
- **Input Sanitization**: XSS prevention
- **Rate Limiting**: API rate limiting (configurable)

## 📈 Performance

- **Web Workers**: Non-blocking OCR processing
- **Lazy Loading**: Component-based lazy loading
- **Caching**: Intelligent caching strategies
- **Compression**: File compression for uploads
- **Pagination**: Large dataset pagination

## 🌐 Internationalization

- **Multi-language OCR**: Support for regional languages
- **UI Localization**: Configurable UI language
- **RTL Support**: Right-to-left language support

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Docker Deployment
```bash
docker build -t fra-upload .
docker run -p 5000:5000 fra-upload
```

## 📝 Development

### Code Style
- ESLint + Prettier configuration
- TypeScript strict mode
- Component-based architecture
- Custom hooks for state management

### Contributing
1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Submit a pull request

## 🐛 Troubleshooting

### Common Issues

**OCR Not Working**
- Check browser compatibility
- Verify language packs are loaded
- Check console for errors

**Map Not Loading**
- Verify tile URL is accessible
- Check network connectivity
- Ensure Leaflet CSS is loaded

**API Errors**
- Check backend server status
- Verify API endpoints
- Check authentication tokens

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation wiki

---

**Built with ❤️ for Forest Rights Act digitization**

