// AdminImportExcel.tsx - Composant d'importation Excel pour admins
import React, { useState, useRef, useCallback } from "react";
import { useAuth, useAuthenticatedFetch } from "../../contexts/AuthContext";
import {
  Upload,
  FileText,
  AlertCircle,
  CheckCircle,
  Download,
  X,
  Info,
  Clock,
  RefreshCw,
  Eye,
} from "lucide-react";
import { toast } from "react-hot-toast";
import { useNavigate } from "react-router-dom";

// Types
interface ImportLog {
  id: number;
  filename: string;
  imported_by_name: string;
  import_date: string;
  status: "pending" | "success" | "failed" | "partial";
  status_display: string;
  total_rows: number;
  successful_rows: number;
  failed_rows: number;
  success_rate: number;
  processing_time: number;
  error_log?: string;
  success_log?: string;
}

const AdminImportExcel: React.FC = () => {
  const { hasPermission } = useAuth();
  const authenticatedFetch = useAuthenticatedFetch();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // États
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [importLogs, setImportLogs] = useState<ImportLog[]>([]);
  const [showLogs] = useState(true);
  const [selectedLog, setSelectedLog] = useState<ImportLog | null>(null);

  // Charger les logs au montage
  React.useEffect(() => {
    if (hasPermission("import_excel")) {
      loadImportLogs();
    } else {
      navigate("/dashboard");
      toast.error("Accès non autorisé");
    }
  }, []);

  const loadImportLogs = async () => {
    try {
      // Endpoint temporaire - fonctionnalité en développement
      console.log("Import logs - fonctionnalité en développement");
      setImportLogs([]);
      /*
      const response = await authenticatedFetch('/api/excel-import-logs/');
      if (response.ok) {
        const data = await response.json();
        setImportLogs(data.results || []);
      }
      */
    } catch (error) {
      console.error("Erreur lors du chargement des logs:", error);
    }
  };

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
      handleFileSelection(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelection = (file: File) => {
    // Vérifier le type de fichier
    const allowedTypes = [
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", // .xlsx
      "application/vnd.ms-excel", // .xls
      "application/vnd.oasis.opendocument.spreadsheet", // .ods
    ];

    if (
      !allowedTypes.includes(file.type) &&
      !file.name.endsWith(".xlsx") &&
      !file.name.endsWith(".xls")
    ) {
      toast.error("Veuillez sélectionner un fichier Excel (.xlsx ou .xls)");
      return;
    }

    // Vérifier la taille (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error("Le fichier est trop volumineux (max 10MB)");
      return;
    }

    setSelectedFile(file);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleImport = async () => {
    if (!selectedFile) {
      toast.error("Veuillez sélectionner un fichier");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    setImporting(true);

    try {
      toast.loading("Importation en cours...", { id: "import" });

      const response = await fetch("/api/import/excel/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("appget_token")}`,
        },
        body: formData,
      });

      const result = await response.json();

      if (response.ok && result.success) {
        toast.success("Importation réussie !", { id: "import" });

        // Recharger les logs
        await loadImportLogs();

        // Réinitialiser le formulaire
        setSelectedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }

        // Afficher les statistiques
        toast.success(
          `${Object.values(result.stats).reduce(
            (a: any, b: any) => a + b,
            0
          )} éléments importés`
        );
      } else {
        throw new Error(result.error || "Erreur lors de l'importation");
      }
    } catch (error: any) {
      console.error("Erreur importation:", error);
      toast.error(error.message || "Erreur lors de l'importation", {
        id: "import",
      });
    } finally {
      setImporting(false);
    }
  };

  const downloadTemplate = () => {
    // URL du template Excel (à créer)
    const templateUrl = "/static/templates/template_emploi_temps.xlsx";
    const link = document.createElement("a");
    link.href = templateUrl;
    link.download = "template_emploi_temps.xlsx";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "text-green-600 bg-green-100";
      case "failed":
        return "text-red-600 bg-red-100";
      case "partial":
        return "text-orange-600 bg-orange-100";
      case "pending":
        return "text-blue-600 bg-blue-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-5 w-5" />;
      case "failed":
        return <AlertCircle className="h-5 w-5" />;
      case "partial":
        return <AlertCircle className="h-5 w-5" />;
      case "pending":
        return <Clock className="h-5 w-5 animate-spin" />;
      default:
        return <Info className="h-5 w-5" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const LogDetailsModal = ({
    log,
    onClose,
  }: {
    log: ImportLog | null;
    onClose: () => void;
  }) => {
    if (!log) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
          <div className="flex items-center justify-between p-6 border-b">
            <h3 className="text-lg font-semibold">Détails de l'importation</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <div className="p-6 overflow-y-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">
                  Informations générales
                </h4>
                <div className="space-y-2 text-sm">
                  <div>
                    <strong>Fichier:</strong> {log.filename}
                  </div>
                  <div>
                    <strong>Importé par:</strong> {log.imported_by_name}
                  </div>
                  <div>
                    <strong>Date:</strong>{" "}
                    {new Date(log.import_date).toLocaleString("fr-FR")}
                  </div>
                  <div>
                    <strong>Temps de traitement:</strong>{" "}
                    {log.processing_time?.toFixed(2)}s
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-2">Statistiques</h4>
                <div className="space-y-2 text-sm">
                  <div>
                    <strong>Total lignes:</strong> {log.total_rows}
                  </div>
                  <div>
                    <strong>Réussies:</strong>{" "}
                    <span className="text-green-600">
                      {log.successful_rows}
                    </span>
                  </div>
                  <div>
                    <strong>Échouées:</strong>{" "}
                    <span className="text-red-600">{log.failed_rows}</span>
                  </div>
                  <div>
                    <strong>Taux de succès:</strong> {log.success_rate}%
                  </div>
                </div>
              </div>
            </div>

            {log.success_log && (
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">
                  Log de succès
                </h4>
                <pre className="bg-green-50 p-4 rounded-lg text-xs overflow-x-auto">
                  {log.success_log}
                </pre>
              </div>
            )}

            {log.error_log && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">
                  Log d'erreurs
                </h4>
                <pre className="bg-red-50 p-4 rounded-lg text-xs overflow-x-auto text-red-800">
                  {log.error_log}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="w-full px-6 lg:px-10 py-8">
        {/* En-tête */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Import Excel</h1>
          <p className="text-gray-600 mt-2">
            Importez des données d'emploi du temps depuis un fichier Excel
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
          {/* Section d'import */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              {/* Instructions */}
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Instructions
                </h2>
                <div className="prose prose-sm text-gray-600">
                  <ol>
                    <li>Téléchargez le modèle Excel ci-dessous</li>
                    <li>Remplissez vos données en respectant le format</li>
                    <li>Sélectionnez votre fichier rempli</li>
                    <li>Cliquez sur "Importer" pour traiter les données</li>
                  </ol>
                </div>

                <button
                  onClick={downloadTemplate}
                  className="mt-4 inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors duration-200"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Télécharger le modèle Excel
                </button>
              </div>

              {/* Zone de drop */}
              <div className="p-6">
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 ${
                    dragActive
                      ? "border-primary-500 bg-primary-50"
                      : "border-gray-300 hover:border-gray-400"
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  {selectedFile ? (
                    <div className="space-y-4">
                      <FileText className="h-16 w-16 text-green-500 mx-auto" />
                      <div>
                        <p className="text-lg font-medium text-gray-900">
                          {selectedFile.name}
                        </p>
                        <p className="text-sm text-gray-500">
                          {formatFileSize(selectedFile.size)} •{" "}
                          {selectedFile.type || "Excel"}
                        </p>
                      </div>
                      <div className="flex justify-center space-x-4">
                        <button
                          onClick={() => setSelectedFile(null)}
                          className="text-sm text-gray-600 hover:text-gray-800"
                        >
                          Supprimer
                        </button>
                        <button
                          onClick={() => fileInputRef.current?.click()}
                          className="text-sm text-primary-600 hover:text-primary-700"
                        >
                          Changer de fichier
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <Upload className="h-16 w-16 text-gray-400 mx-auto" />
                      <div>
                        <p className="text-lg font-medium text-gray-900">
                          Glissez votre fichier Excel ici
                        </p>
                        <p className="text-sm text-gray-500 mt-2">
                          ou
                          <button
                            onClick={() => fileInputRef.current?.click()}
                            className="text-primary-600 hover:text-primary-700 font-medium ml-1"
                          >
                            parcourez vos fichiers
                          </button>
                        </p>
                      </div>
                      <p className="text-xs text-gray-400">
                        Formats supportés: .xlsx, .xls • Taille max: 10MB
                      </p>
                    </div>
                  )}
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileInput}
                  className="hidden"
                />

                {/* Bouton d'import */}
                <div className="mt-6 flex justify-center">
                  <button
                    onClick={handleImport}
                    disabled={!selectedFile || importing}
                    className={`px-6 py-3 rounded-lg font-medium text-white transition-all duration-200 ${
                      !selectedFile || importing
                        ? "bg-gray-400 cursor-not-allowed"
                        : "bg-primary-600 hover:bg-primary-700 hover:shadow-lg transform hover:-translate-y-0.5"
                    }`}
                  >
                    {importing ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Importation en cours...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4 mr-2" />
                        Importer les données
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Informations et conseils */}
          <div className="space-y-6">
            {/* Conseils */}
            <div className="bg-blue-50 rounded-lg p-6">
              <div className="flex items-start">
                <Info className="h-6 w-6 text-blue-500 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-blue-900 mb-2">
                    Conseils d'importation
                  </h3>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>
                      • Vérifiez que tous les champs obligatoires sont remplis
                    </li>
                    <li>• Utilisez le format exact du modèle fourni</li>
                    <li>
                      • Les noms d'enseignants et salles doivent être uniques
                    </li>
                    <li>• Respectez les formats de date et heure</li>
                    <li>• Évitez les caractères spéciaux</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Statistiques rapides */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="font-medium text-gray-900 mb-4">
                Statistiques d'import
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total imports</span>
                  <span className="text-sm font-medium">
                    {importLogs.length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Réussis</span>
                  <span className="text-sm font-medium text-green-600">
                    {
                      importLogs.filter((log) => log.status === "success")
                        .length
                    }
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Échoués</span>
                  <span className="text-sm font-medium text-red-600">
                    {importLogs.filter((log) => log.status === "failed").length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Historique des imports */}
        {showLogs && (
          <div className="mt-12">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Historique des imports
              </h2>
              <button
                onClick={loadImportLogs}
                className="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Actualiser
              </button>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              {importLogs.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Aucun import effectué</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Fichier
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Statut
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Résultats
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {importLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <FileText className="h-5 w-5 text-gray-400 mr-3" />
                              <div>
                                <div className="text-sm font-medium text-gray-900">
                                  {log.filename}
                                </div>
                                <div className="text-sm text-gray-500">
                                  Par {log.imported_by_name}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(log.import_date).toLocaleString("fr-FR")}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                                log.status
                              )}`}
                            >
                              {getStatusIcon(log.status)}
                              <span className="ml-1">{log.status_display}</span>
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <div>
                              <span className="text-green-600">
                                {log.successful_rows}
                              </span>{" "}
                              /{" "}
                              <span className="text-gray-500">
                                {log.total_rows}
                              </span>
                              <span className="text-gray-400 ml-1">
                                ({log.success_rate}%)
                              </span>
                            </div>
                            {log.processing_time && (
                              <div className="text-xs text-gray-500">
                                {log.processing_time.toFixed(2)}s
                              </div>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <button
                              onClick={() => setSelectedLog(log)}
                              className="text-primary-600 hover:text-primary-900 mr-3"
                            >
                              <Eye className="h-4 w-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Modal détails */}
        <LogDetailsModal
          log={selectedLog}
          onClose={() => setSelectedLog(null)}
        />
      </div>
    </div>
  );
};

export default AdminImportExcel;
