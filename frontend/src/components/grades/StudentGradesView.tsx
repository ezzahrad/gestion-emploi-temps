import React, { useState, useEffect } from 'react';
import { Card, Button, Modal, Table, Loading } from '../ui';
import { BookOpen, Plus, Edit2, Eye, TrendingUp, Award, FileText } from 'lucide-react';
import { toast } from 'react-hot-toast';
import enhancedAPI from '../../services/enhancedAPI';
import { Grade, SubjectGradeSummary, StudentTranscript } from '../../types';

interface StudentGradesProps {
  studentId?: number;
  isCurrentUser?: boolean;
}

export const StudentGradesView: React.FC<StudentGradesProps> = ({ 
  studentId, 
  isCurrentUser = false 
}) => {
  const [grades, setGrades] = useState<Grade[]>([]);
  const [summaries, setSummaries] = useState<SubjectGradeSummary[]>([]);
  const [transcript, setTranscript] = useState<StudentTranscript | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState<number | null>(null);
  const [showTranscript, setShowTranscript] = useState(false);

  useEffect(() => {
    loadStudentGrades();
  }, [studentId]);

  const loadStudentGrades = async () => {
    try {
      setLoading(true);
      
      // Charger les données selon le contexte
      if (isCurrentUser) {
        const [gradesRes, summariesRes, transcriptRes] = await Promise.all([
          enhancedAPI.grades.getMyGrades(),
          enhancedAPI.grades.getMySummaries(),
          enhancedAPI.grades.getCurrentTranscript()
        ]);
        
        setGrades(gradesRes.data);
        setSummaries(summariesRes.data);
        setTranscript(transcriptRes.data);
      } else {
        // Pour les enseignants/admin consultant un étudiant spécifique
        const [gradesRes, summariesRes] = await Promise.all([
          enhancedAPI.grades.getGrades({ student: studentId }),
          enhancedAPI.grades.getSubjectSummaries({ student: studentId })
        ]);
        
        setGrades(gradesRes.data);
        setSummaries(summariesRes.data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des notes:', error);
      toast.error('Erreur lors du chargement des notes');
    } finally {
      setLoading(false);
    }
  };

  const exportTranscriptPDF = async () => {
    try {
      const exportData = {
        export_type: 'transcript',
        student_id: studentId,
        include_details: true,
        format: 'A4'
      };

      const response = await enhancedAPI.pdfExport.createExport(exportData);
      
      toast.success('Export du relevé de notes lancé !');
      
      // Surveiller le statut
      enhancedAPI.helpers.pdf.pollJobStatus(
        response.data.job_id,
        (status) => {
          if (status.status === 'completed') {
            toast.success('Relevé de notes prêt !');
            enhancedAPI.helpers.pdf.downloadAndSavePDF(
              status.job_id, 
              `releve_notes_${new Date().getTime()}.pdf`
            );
          }
        }
      );
    } catch (error) {
      console.error('Erreur export PDF:', error);
      toast.error('Erreur lors de l\'export PDF');
    }
  };

  if (loading) {
    return <Loading message="Chargement des notes..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header avec statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Moyenne générale</p>
              <p className="text-2xl font-bold text-blue-600">
                {transcript?.overall_average ? `${transcript.overall_average.toFixed(2)}/20` : 'N/A'}
              </p>
            </div>
            <Award className="w-8 h-8 text-blue-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">GPA</p>
              <p className="text-2xl font-bold text-green-600">
                {transcript?.gpa ? `${transcript.gpa.toFixed(2)}/4.0` : 'N/A'}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Crédits acquis</p>
              <p className="text-2xl font-bold text-purple-600">
                {transcript ? `${transcript.acquired_credits}/${transcript.total_credits}` : 'N/A'}
              </p>
            </div>
            <BookOpen className="w-8 h-8 text-purple-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Note lettrée</p>
              <p className="text-2xl font-bold text-orange-600">
                {transcript?.grade_letter || 'N/A'}
              </p>
            </div>
            <Award className="w-8 h-8 text-orange-500" />
          </div>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Résultats par matière</h2>
        <div className="space-x-2">
          <Button
            onClick={() => setShowTranscript(true)}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Eye className="w-4 h-4 mr-2" />
            Voir le relevé
          </Button>
          <Button
            onClick={exportTranscriptPDF}
            className="bg-green-600 hover:bg-green-700"
          >
            <FileText className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Tableau des résumés par matière */}
      <Card>
        <Table
          headers={[
            'Matière',
            'Code',
            'Crédits',
            'Moyenne',
            'Note lettrée',
            'Évaluations',
            'Actions'
          ]}
          data={summaries.map(summary => ({
            id: summary.id,
            matiere: summary.subject_name,
            code: summary.subject_code,
            credits: summary.subject_credits,
            moyenne: summary.weighted_average ? 
              `${summary.weighted_average.toFixed(2)}/20` : 'N/A',
            note_lettree: (
              <span className={`px-2 py-1 rounded text-sm font-medium ${
                getGradeLetterColor(summary.grade_letter)
              }`}>
                {summary.grade_letter}
              </span>
            ),
            evaluations: `${summary.published_evaluations}/${summary.total_evaluations}`,
            actions: (
              <Button
                size="sm"
                variant="outline"
                onClick={() => setSelectedSubject(summary.subject)}
              >
                <Eye className="w-4 h-4" />
              </Button>
            )
          }))}
        />
      </Card>

      {/* Modal détails matière */}
      {selectedSubject && (
        <SubjectGradesModal
          subjectId={selectedSubject}
          isOpen={!!selectedSubject}
          onClose={() => setSelectedSubject(null)}
          studentId={studentId}
        />
      )}

      {/* Modal relevé de notes */}
      {showTranscript && transcript && (
        <TranscriptModal
          transcript={transcript}
          isOpen={showTranscript}
          onClose={() => setShowTranscript(false)}
        />
      )}
    </div>
  );
};

const SubjectGradesModal: React.FC<{
  subjectId: number;
  isOpen: boolean;
  onClose: () => void;
  studentId?: number;
}> = ({ subjectId, isOpen, onClose, studentId }) => {
  const [grades, setGrades] = useState<Grade[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadSubjectGrades();
    }
  }, [isOpen, subjectId]);

  const loadSubjectGrades = async () => {
    try {
      const response = await enhancedAPI.grades.getGrades({
        evaluation__subject: subjectId,
        student: studentId
      });
      setGrades(response.data);
    } catch (error) {
      console.error('Erreur chargement notes matière:', error);
      toast.error('Erreur lors du chargement des notes');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Détail des notes">
      <div className="space-y-4">
        {loading ? (
          <Loading message="Chargement des notes..." />
        ) : (
          <Table
            headers={[
              'Évaluation',
              'Type',
              'Date',
              'Note',
              'Coeff.',
              'Pourcentage'
            ]}
            data={grades.map(grade => ({
              id: grade.id,
              evaluation: grade.evaluation_name,
              type: grade.evaluation_type,
              date: new Date(grade.evaluation_date).toLocaleDateString('fr-FR'),
              note: `${grade.grade_value}/${grade.max_grade}`,
              coefficient: grade.coefficient,
              pourcentage: (
                <span className={`font-medium ${
                  grade.percentage >= 60 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {grade.percentage.toFixed(1)}%
                </span>
              )
            }))}
          />
        )}
      </div>
    </Modal>
  );
};

const TranscriptModal: React.FC<{
  transcript: StudentTranscript;
  isOpen: boolean;
  onClose: () => void;
}> = ({ transcript, isOpen, onClose }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Relevé de Notes" size="large">
      <div className="space-y-6">
        {/* En-tête du relevé */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Informations de l'étudiant</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Nom :</span> {transcript.student_name}
            </div>
            <div>
              <span className="font-medium">Programme :</span> {transcript.program_name}
            </div>
            <div>
              <span className="font-medium">Niveau :</span> {transcript.level}
            </div>
            <div>
              <span className="font-medium">Année :</span> {transcript.academic_year}
            </div>
          </div>
        </div>

        {/* Résultats académiques */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Résultats académiques</h3>
          <Table
            headers={[
              'Matière',
              'Crédits',
              'Moyenne',
              'Note lettrée'
            ]}
            data={transcript.subjects?.map(subject => ({
              id: subject.subject_name,
              matiere: `${subject.subject_name} (${subject.subject_code})`,
              credits: subject.subject_credits,
              moyenne: subject.weighted_average ? 
                `${subject.weighted_average.toFixed(2)}/20` : 'N/A',
              note_lettree: (
                <span className={`px-2 py-1 rounded text-sm font-medium ${
                  getGradeLetterColor(subject.grade_letter)
                }`}>
                  {subject.grade_letter}
                </span>
              )
            })) || []}
          />
        </div>

        {/* Résumé */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-2 text-blue-800">Résumé</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Moyenne générale :</span> 
              <span className="ml-2 text-blue-600 font-bold">
                {transcript.overall_average?.toFixed(2)}/20
              </span>
            </div>
            <div>
              <span className="font-medium">GPA :</span> 
              <span className="ml-2 text-blue-600 font-bold">
                {transcript.gpa?.toFixed(2)}/4.0
              </span>
            </div>
            <div>
              <span className="font-medium">Crédits acquis :</span> 
              <span className="ml-2 text-blue-600 font-bold">
                {transcript.acquired_credits}/{transcript.total_credits}
              </span>
            </div>
            <div>
              <span className="font-medium">Note lettrée :</span> 
              <span className={`ml-2 px-2 py-1 rounded text-sm font-bold ${
                getGradeLetterColor(transcript.grade_letter)
              }`}>
                {transcript.grade_letter}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
};

// Fonction utilitaire pour les couleurs des notes
const getGradeLetterColor = (grade: string) => {
  const colors = {
    'A+': 'bg-green-100 text-green-800',
    'A': 'bg-green-100 text-green-800',
    'B+': 'bg-blue-100 text-blue-800',
    'B': 'bg-blue-100 text-blue-800',
    'C+': 'bg-yellow-100 text-yellow-800',
    'C': 'bg-yellow-100 text-yellow-800',
    'D+': 'bg-orange-100 text-orange-800',
    'D': 'bg-orange-100 text-orange-800',
    'F': 'bg-red-100 text-red-800'
  };
  return colors[grade as keyof typeof colors] || 'bg-gray-100 text-gray-800';
};

export default StudentGradesView;
