import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Plus, Edit, Trash2, Building, Users } from 'lucide-react';
import toast from 'react-hot-toast';
import { coreAPI } from '../../services/api';
import { Department } from '../../types';

export const DepartmentManagement: React.FC = () => {
  const [showModal, setShowModal] = useState(false);
  const [editingDepartment, setEditingDepartment] = useState<Department | null>(null);
  const queryClient = useQueryClient();

  const { data: departments = [], isLoading } = useQuery<Department[]>(
    'departments',
    () => coreAPI.getDepartments().then(res => res.data.results || res.data)
  );

  const createMutation = useMutation(coreAPI.createDepartment, {
    onSuccess: () => {
      queryClient.invalidateQueries('departments');
      toast.success('Département créé avec succès');
      setShowModal(false);
    },
    onError: () => {
      toast.error('Erreur lors de la création');
    }
  });

  const updateMutation = useMutation(
    ({ id, data }: { id: number; data: any }) => coreAPI.updateDepartment(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('departments');
        toast.success('Département modifié avec succès');
        setShowModal(false);
        setEditingDepartment(null);
      },
      onError: () => {
        toast.error('Erreur lors de la modification');
      }
    }
  );

  const deleteMutation = useMutation(coreAPI.deleteDepartment, {
    onSuccess: () => {
      queryClient.invalidateQueries('departments');
      toast.success('Département supprimé avec succès');
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
      description: formData.get('description'),
    };

    if (editingDepartment) {
      updateMutation.mutate({ id: editingDepartment.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (id: number) => {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce département ?')) {
      deleteMutation.mutate(id);
    }
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
          <h1 className="text-2xl font-bold text-gray-900">Gestion des Départements</h1>
          <p className="text-gray-600">Créez et gérez les départements de la faculté</p>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => {
            setEditingDepartment(null);
            setShowModal(true);
          }}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nouveau département
        </motion.button>
      </motion.div>

      {/* Departments grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {departments.map((department, index) => (
          <motion.div
            key={department.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * index }}
            className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg mr-3">
                  <Building className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{department.name}</h3>
                  <p className="text-sm text-gray-500">Code: {department.code}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => {
                    setEditingDepartment(department);
                    setShowModal(true);
                  }}
                  className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(department.id)}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Filières:</span>
                <span className="font-medium text-gray-900">{department.programs_count}</span>
              </div>
              {department.head_name && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Chef:</span>
                  <span className="font-medium text-gray-900">{department.head_name}</span>
                </div>
              )}
            </div>
            
            {department.description && (
              <p className="text-sm text-gray-600 mt-4 line-clamp-3">
                {department.description}
              </p>
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
              {editingDepartment ? 'Modifier le département' : 'Nouveau département'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom du département
                </label>
                <input
                  type="text"
                  name="name"
                  defaultValue={editingDepartment?.name || ''}
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
                  defaultValue={editingDepartment?.code || ''}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="ex: INFO"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  name="description"
                  defaultValue={editingDepartment?.description || ''}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Description du département..."
                />
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingDepartment(null);
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
                  {editingDepartment ? 'Modifier' : 'Créer'}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};