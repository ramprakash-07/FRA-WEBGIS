import React from 'react';
import ReactDOM from 'react-dom/client';
import { PattaPage } from './features/patta/PattaPage';
import './index.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <PattaPage />
  </React.StrictMode>
);






