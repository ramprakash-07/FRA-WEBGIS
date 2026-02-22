import React from 'react';
import ReactDOM from 'react-dom/client';
import { UploadPage } from './features/upload/UploadPage';
import './index.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <UploadPage />
  </React.StrictMode>
);







