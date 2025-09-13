import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Plus, Edit, Trash2, GraduationCap, Building } from 'lucide-react';
import toast from 'react-hot-toast';
import { coreAPI } from '../../services/api';
import { Program, Department } from '../../types';

export const ProgramManagement: React.FC = () => {
  const [showModal, setShowModal] = useState(false);
  const [editingProgram, setEditingProgram] = useState<Program | null>(null);
  const queryClient = useQueryClient();

  const { data: programs = [], isLoading } = useQuery<Program[]>(
    'programs',
    () => coreAPI.getPrograms().then(res => res.data.results || res.data)
  );

  const { data: departments = [] } = useQuery<Department[]>(
    'departments',
    () => coreAPI.getDepartments().then(res => res.data.results || res.data)
  );

  const createMutation = useMutation(coreAPI.createProgram, {
    onSuccess: () => {
      queryClient.invalidateQueries('programs');
      toast.success('Filière créée avec succès');
      setShowModal(false);
    },
    onError: () => {
      toast.error('Erreur lors de la création');
    }
  });

  const updateMutation = useMutation(
    ({ id, data }: { id: number; data: any }) => coreAPI.updateProgram(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('programs');
        toast.success('Filière modifiée avec succès');
        setShowModal(false);
        setEditingProgram(null);
      },
      onError: () => {
        toast.error('Erreur lors de la modification');
      }
    }
  );

  const deleteMutation = useMutation(coreAPI.deleteProgram, {
    onSuccess: () => {
      queryClient.invalidateQueries('programs');
      toast.success('Filière supprimée avec succès');
    },
    onError: () => {
      toast.error('Erreur lors de la suppression');
    }
  });

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const data = {
      name: formData.get('name'),
      code: formData.get('code'),
      department: parseInt(formData.get('department') as string),
      level: formData.get('level'),
      capacity: parseInt(formData.get('capacity') as string),
    };

    if (editingProgram) {
      updateMutation.mutate({ id: editingProgram.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (id: number) => {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette filière ?')) {
      deleteMutation.mutate(id);
    }
  };

  const getLevelBadgeColor = (level: string) => {
    const colors = {
      'L1': 'bg-green-100 text-green-800',
      'L2': 'bg-blue-100 text-blue-800', 
      'L3': 'bg-purple-100 text-purple-800',
      'M1': 'bg-orange-100 text-orange-800',
      'M2': 'bg-red-100 text-red-800',
    };
    return colors[level as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestion des Filières</h1>
          <p className="text-gray-600">Créez et gérez les filières de formation</p>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => {
            setEditingProgram(null);
            setShowModal(true);
          }}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nouvelle filière
        </motion.button>
      </motion.div>

      {/* Programs grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {programs.map((program, index) => (
          <motion.div
            key={program.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * index }}
            className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg mr-3">
                  <GraduationCap className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{program.name}</h3>
                  <p className="text-sm text-gray-500">Code: {program.code}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => {
                    setEditingProgram(program);
                    setShowModal(true);
                  }}
                  className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(program.id)}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div className="space-y-2 mb-4">
              <div className="flex items-center justify-between">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getLevelBadgeColor(program.level)}`}>
                  {program.level}
                </span>
                <span className="text-sm text-gray-600 flex items-center">
                  <Building className="w-4 h-4 mr-1" />
                  {program.department_name}
                </span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Étudiants:</span>
                <span className="font-medium text-gray-900">{program.students_count}</span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Capacité:</span>
                <span className="font-medium text-gray-900">{program.capacity}</span>
              </div>
            </div>

            {program.head_name && (
              <div className="pt-3 border-t border-gray-100">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Responsable:</span> {program.head_name}
                </p>
              </div>
            )}
          </motion.div>
        ))}
      </motion.div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl p-6 w-full max-w-md"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              {editingProgram ? 'Modifier la filière' : 'Nouvelle filière'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom de la filière
                </label>
                <input
                  type="text"
                  name="name"
                  defaultValue={editingProgram?.name || ''}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="ex: Informatique"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Code
                </label>
                <input
                  type="text"
                  name="code"
                  defaultValue={editingProgram?.code || ''}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="ex: INFO"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Département
                </label>
                <select
                  name="department"
                  defaultValue={editingProgram?.department || ''}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Sélectionner un département</option>
                  {departments.map(dept => (
                    <option key={dept.id} value={dept.id}>{dept.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Niveau
                </label>
                <select
                  name="level"
                  defaultValue={editingProgram?.level || ''}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Sélectionner un niveau</option>
                  <option value="L1">Licence 1</option>
                  <option value="L2">Licence 2</option>
                  <option value="L3">Licence 3</option>
                  <option value="M1">Master 1</option>
                  <option value="M2">Master 2</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Capacité
                </label>
                <input
                  type="number"
                  name="capacity"
                  defaultValue={editingProgram?.capacity || 30}
                  min="1"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="30"
                />
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingProgram(null);
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isLoading || updateMutation.isLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {editingProgram ? 'Modifier' : 'Créer'}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};