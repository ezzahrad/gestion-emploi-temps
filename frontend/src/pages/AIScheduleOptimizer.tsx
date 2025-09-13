// Temporary proxy: this file is the page. If a deeper path exists, replace later.
import React from "react";

const AIScheduleOptimizer: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="w-full px-6 lg:px-10 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Optimisation IA</h1>
          <p className="text-gray-600 mt-2">
            Configurez vos contraintes et lancez l'optimisation.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-2">Contraintes</h2>
            <p className="text-gray-600 text-sm">Section démo.</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-2">Résultats</h2>
            <p className="text-gray-600 text-sm">Section démo.</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-2">Historique</h2>
            <p className="text-gray-600 text-sm">Section démo.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIScheduleOptimizer;
