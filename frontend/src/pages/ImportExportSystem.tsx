import React, { useState, useCallback, useRef } from 'react';
import { 
  Upload, 
  Download, 
  FileSpreadsheet,
  FileText,
  Calendar,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  X,
  FileDown
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { scheduleAPI } from '../services/api';

interface ImportResult {
  success: boolean;
  message: string;
  imported_count?: number;
  errors?: string[];
  warnings?: string[];
}

interface ExportOptions {
  format: 'excel' | 'pdf' | 'ics';
  period: string;
  includeDetails: boolean;
  departments?: string[];
  programs?: string[];
}

const ImportExportSystem: React.FC = () => {
  const { user } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'excel',
    period: 'current_month',
    includeDetails: true,
    departments: [],
    programs: []
  });
  const [importResults, setImportResults] = useState<ImportResult | null>(null);
  const [exporting, setExporting] = useState(false);

  // Gestion du drag & drop
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    // Validation du fichier
    const validTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      'text/csv'
    ];

    if (!validTypes.includes(file.type)) {
      toast.error('Format de fichier non supporté. Utilisez Excel (.xlsx) ou CSV.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB
      toast.error('Le fichier est trop volumineux (max 10MB).');
      return;
    }

    setUploading(true);
    setImportResults(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', 'schedule_import');

    try {
      const response = await scheduleAPI.importSchedules(formData);

      const result: ImportResult = response.data;
      setImportResults(result);

      if (result.success) {
        toast.success(`Import réussi ! ${result.imported_count || 0} éléments importés.`);
      } else {
        toast.error('Erreur lors de l\'import. Vérifiez les détails ci-dessous.');
      }
    } catch (error: any) {
      console.error('Erreur import:', error);
      const errorMessage = error.response?.data?.message || 'Erreur lors de l\'import du fichier';
      setImportResults({
        success: false,
        message: errorMessage,
        errors: [errorMessage]
      });
      toast.error(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      toast.loading('Téléchargement du modèle...', { duration: 1000 });
      
      const response = await scheduleAPI.downloadImportTemplate();

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'modele_emploi_temps.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('Modèle téléchargé');
    } catch (error) {
      console.error('Erreur téléchargement modèle:', error);
      toast.error('Erreur lors du téléchargement du modèle');
    }
  };

  const handleExport = async () => {
    if (!exportOptions.format) {
      toast.error('Veuillez sélectionner un format d\'export');
      return;
    }

    setExporting(true);
    
    try {
      const params = {
        format: exportOptions.format,
        period: exportOptions.period,
        include_details: exportOptions.includeDetails.toString(),
      };

      if (exportOptions.departments?.length) {
        (params as any).departments = exportOptions.departments.join(',');
      }
      if (exportOptions.programs?.length) {
        (params as any).programs = exportOptions.programs.join(',');
      }

      const response = await scheduleAPI.exportSchedules(params);

      const fileExtension = exportOptions.format === 'excel' ? 'xlsx' : 
                           exportOptions.format === 'pdf' ? 'pdf' : 'ics';
      
      const fileName = `emplois_temps_${exportOptions.period}_${new Date().toISOString().split('T')[0]}.${fileExtension}`;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success(`Emplois du temps exportés en ${exportOptions.format.toUpperCase()}`);
    } catch (error) {
      console.error('Erreur export:', error);
      toast.error('Erreur lors de l\'export');
    } finally {
      setExporting(false);
    }
  };

  const clearResults = () => {
    setImportResults(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatOptions = [
    { value: 'excel', label: 'EXCEL', icon: <FileSpreadsheet className="w-6 h-6" />, description: 'Format Excel (.xlsx)' },
    { value: 'pdf', label: 'PDF', icon: <FileText className="w-6 h-6" />, description: 'Document PDF' },
    { value: 'ics', label: 'ICS', icon: <Calendar className="w-6 h-6" />, description: 'Calendrier (.ics)' }
  ];

  const periodOptions = [
    { value: 'current_week', label: 'Cette semaine' },
    { value: 'current_month', label: 'Ce mois' },
    { value: 'current_semester', label: 'Ce semestre' },
    { value: 'current_year', label: 'Cette année' },
    { value: 'custom', label: 'Période personnalisée' }
  ];

  return (
    <div className="h-full w-full bg-gray-50 overflow-auto">
      <div className="p-6 space-y-6">
        {/* En-tête */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-2">
            <FileSpreadsheet className="w-8 h-8 text-green-600" />
            <h1 className="text-2xl font-bold text-gray-900">Import / Export Excel</h1>
          </div>
          <p className="text-gray-600">
            Importez ou exportez vos emplois du temps en masse
          </p>
          
          <div className="mt-4 flex items-center justify-end">
            <button
              onClick={handleDownloadTemplate}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2 transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Télécharger le modèle</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* Section Import */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Upload className="w-5 h-5 text-blue-600" />
                <h2 className="text-lg font-semibold text-gray-900">Importer des Données</h2>
              </div>

              {/* Zone de drop */}
              <div
                className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive 
                    ? 'border-blue-400 bg-blue-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={handleFileSelect}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  disabled={uploading}
                />

                <div className="space-y-4">
                  {uploading ? (
                    <div className="flex flex-col items-center">
                      <RefreshCw className="w-12 h-12 text-blue-600 animate-spin" />
                      <p className="text-blue-600 font-medium">Import en cours...</p>
                    </div>
                  ) : (
                    <>
                      <FileSpreadsheet className="w-16 h-16 text-gray-400 mx-auto" />
                      <div>
                        <p className="text-lg text-gray-700 font-medium">
                          Glissez-déposez un fichier Excel ou CSV ici
                        </p>
                        <p className="text-gray-500">ou cliquez pour sélectionner</p>
                      </div>
                      <p className="text-sm text-gray-400">
                        Formats supportés: .xlsx, .xls, .csv (max 10MB)
                      </p>
                    </>
                  )}
                </div>
              </div>

              {/* Résultats d'import */}
              {importResults && (
                <div className="mt-6">
                  <div className={`border rounded-lg p-4 ${
                    importResults.success 
                      ? 'border-green-200 bg-green-50' 
                      : 'border-red-200 bg-red-50'
                  }`}>
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {importResults.success ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-red-600" />
                        )}
                        <h3 className={`font-medium ${
                          importResults.success ? 'text-green-800' : 'text-red-800'
                        }`}>
                          {importResults.success ? 'Import réussi' : 'Erreur d\'import'}
                        </h3>
                      </div>
                      <button
                        onClick={clearResults}
                        className="p-1 hover:bg-gray-200 rounded"
                      >
                        <X className="w-4 h-4 text-gray-500" />
                      </button>
                    </div>
                    
                    <p className={`text-sm mb-3 ${
                      importResults.success ? 'text-green-700' : 'text-red-700'
                    }`}>
                      {importResults.message}
                    </p>

                    {importResults.success && importResults.imported_count && (
                      <p className="text-sm text-green-600">
                        <strong>{importResults.imported_count}</strong> éléments importés avec succès
                      </p>
                    )}

                    {importResults.errors && importResults.errors.length > 0 && (
                      <div className="mt-3">
                        <h4 className="text-sm font-medium text-red-800 mb-1">Erreurs:</h4>
                        <ul className="text-sm text-red-700 space-y-1">
                          {importResults.errors.slice(0, 5).map((error, index) => (
                            <li key={index} className="flex items-start space-x-1">
                              <span className="text-red-500 mt-1">•</span>
                              <span>{error}</span>
                            </li>
                          ))}
                          {importResults.errors.length > 5 && (
                            <li className="text-red-600 font-medium">
                              ... et {importResults.errors.length - 5} autres erreurs
                            </li>
                          )}
                        </ul>
                      </div>
                    )}

                    {importResults.warnings && importResults.warnings.length > 0 && (
                      <div className="mt-3">
                        <h4 className="text-sm font-medium text-yellow-800 mb-1">Avertissements:</h4>
                        <ul className="text-sm text-yellow-700 space-y-1">
                          {importResults.warnings.slice(0, 3).map((warning, index) => (
                            <li key={index} className="flex items-start space-x-1">
                              <span className="text-yellow-500 mt-1">•</span>
                              <span>{warning}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Section Export */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-2 mb-6">
                <Download className="w-5 h-5 text-green-600" />
                <h2 className="text-lg font-semibold text-gray-900">Exporter des Données</h2>
              </div>

              {/* Format d'export */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Format d'export
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {formatOptions.map((format) => (
                    <button
                      key={format.value}
                      onClick={() => setExportOptions(prev => ({...prev, format: format.value as any}))}
                      className={`p-4 border rounded-lg text-center transition-all ${
                        exportOptions.format === format.value
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex flex-col items-center space-y-2">
                        <div className={exportOptions.format === format.value ? 'text-blue-600' : 'text-gray-400'}>
                          {format.icon}
                        </div>
                        <div>
                          <p className="font-medium">{format.label}</p>
                          <p className="text-xs text-gray-500">{format.description}</p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Période */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Période
                </label>
                <select
                  value={exportOptions.period}
                  onChange={(e) => setExportOptions(prev => ({...prev, period: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {periodOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Options */}
              <div className="mb-6">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={exportOptions.includeDetails}
                    onChange={(e) => setExportOptions(prev => ({...prev, includeDetails: e.target.checked}))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">Inclure les détails complets</span>
                </label>
              </div>

              {/* Bouton d'export */}
              <button
                onClick={handleExport}
                disabled={exporting || !exportOptions.format}
                className="w-full px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center justify-center space-x-2 transition-colors"
              >
                {exporting ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    <span>Export en cours...</span>
                  </>
                ) : (
                  <>
                    <FileDown className="w-5 h-5" />
                    <span>Exporter les Données</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Informations d'aide */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            <div className="text-sm">
              <h3 className="font-medium text-blue-800 mb-1">Conseils d'utilisation</h3>
              <ul className="text-blue-700 space-y-1 list-disc list-inside">
                <li>Téléchargez d'abord le modèle Excel pour connaître le format requis</li>
                <li>Vérifiez que vos données respectent les contraintes (enseignants, salles, horaires)</li>
                <li>L'import vérifiera automatiquement les conflits avant la sauvegarde</li>
                <li>Les formats d'export sont optimisés pour différents usages (Excel = modification, PDF = impression, ICS = calendrier)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImportExportSystem;