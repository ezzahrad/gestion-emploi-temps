// main.tsx - Point d'entrée de l'application React
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Configuration du strict mode pour le développement
const isDevelopment = import.meta.env.DEV;

// Fonction pour initialiser l'application
const initializeApp = () => {
  const rootElement = document.getElementById('root');
  
  if (!rootElement) {
    throw new Error('Element racine non trouvé');
  }

  const root = ReactDOM.createRoot(rootElement);
  
  if (isDevelopment) {
    // Mode strict activé en développement pour détecter les problèmes
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  } else {
    // Mode production sans strict mode pour les performances
    root.render(<App />);
  }
};

// Initialiser l'application
initializeApp();

// Hot Module Replacement (HMR) pour Vite
if (import.meta.hot) {
  import.meta.hot.accept();
}
