import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Plus, Edit, Trash2, Home, Users, Building } from 'lucide-react';
import toast from 'react-hot-toast';
import { coreAPI } from '../../services/api';
import { Room, Department } from '../../types';

export const RoomManagement: React.FC = () => {
  const [showModal, setShowModal] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const queryClient = useQueryClient();

  const { data: rooms = [], isLoading } = useQuery<Room[]>(
    'rooms',
    () => coreAPI.getRooms().then(res => res.data.results || res.data)
  );

  const { data: departments = [] } = useQuery<Department[]>(
    'departments',
    () => coreAPI.getDepartments().then(res => res.data.results || res.data)
  );

  const createMutation = useMutation(coreAPI.createRoom, {
    onSuccess: () => {
      queryClient.invalidateQueries('rooms');
      toast.success('Salle créée avec succès');
      setShowModal(false);
    },
    onError: () => {
      toast.error('Erreur lors de la création');
    }
  });

  const updateMutation = useMutation(
    ({ id, data }: { id: number; data: any }) => coreAPI.updateRoom(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('rooms');
        toast.success('Salle modifiée avec succès');
        setShowModal(false);
        setEditingRoom(null);
      },
      onError: () => {
        toast.error('Erreur lors de la modification');
      }
    }
  );

  const deleteMutation = useMutation(coreAPI.deleteRoom, {
    onSuccess: () => {
      queryClient.invalidateQueries('rooms');
      toast.success('Salle supprimée avec succès');
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
      room_type: formData.get('room_type'),
      capacity: parseInt(formData.get('capacity') as string),
      department: parseInt(formData.get('department') as string),
      equipment: formData.get('equipment'),
      is_available: formData.get('is_available') === 'on',
    };

    if (editingRoom) {
      updateMutation.mutate({ id: editingRoom.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (id: number) => {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette salle ?')) {
      deleteMutation.mutate(id);
    }
  };

  const getRoomTypeInfo = (type: string) => {
    const types = {
      'lecture': { label: 'Cours', color: 'bg-blue-100 text-blue-800', icon: '📚' },
      'td': { label: 'TD', color: 'bg-green-100 text-green-800', icon: '✏️' },
      'lab': { label: 'TP', color: 'bg-orange-100 text-orange-800', icon: '🔬' },
      'amphitheater': { label: 'Amphi', color: 'bg-purple-100 text-purple-800', icon: '🎭' },
    };
    return types[type as keyof typeof types] || types.lecture;
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
          <h1 className="text-2xl font-bold text-gray-900">Gestion des Salles</h1>
          <p className="text-gray-600">Gérez les salles et leurs équipements</p>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => {
            setEditingRoom(null);
            setShowModal(true);
          }}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nouvelle salle
        </motion.button>
      </motion.div>

      {/* Rooms grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {rooms.map((room, index) => {
          const typeInfo = getRoomTypeInfo(room.room_type);
          
          return (
            <motion.div
              key={room.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
              className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow duration-300"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg mr-3">
                    <Home className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{room.name}</h3>
                    <p className="text-sm text-gray-500">Code: {room.code}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => {
                      setEditingRoom(room);
                      setShowModal(true);
                    }}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(room.id)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${typeInfo.color}`}>
                    {typeInfo.icon} {typeInfo.label}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    room.is_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {room.is_available ? 'Disponible' : 'Indisponible'}
                  </span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 flex items-center">
                    <Users className="w-4 h-4 mr-1" />
                    Capacité:
                  </span>
                  <span className="font-medium text-gray-900">{room.capacity} places</span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 flex items-center">
                    <Building className="w-4 h-4 mr-1" />
                    Département:
                  </span>
                  <span className="font-medium text-gray-900 text-xs">{room.department_name}</span>
                </div>
              </div>

              {room.equipment && (
                <div className="pt-3 border-t border-gray-100">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Équipements:</span> {room.equipment}
                  </p>
                </div>
              )}
            </motion.div>
          );
        })}
      </motion.div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              {editingRoom ? 'Modifier la salle' : 'Nouvelle salle'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom de la salle
                </label>
                <input
                  type="text"
                  name="name"
                  defaultValue={editingRoom?.name || ''}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="ex: Salle A101"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Code
                </label>
                <input
                  type="text"
                  name="code"
                  defaultValue={editingRoom?.code || ''}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="ex: A101"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type de salle
                </label>
                <select
                  name="room_type"
                  defaultValue={editingRoom?.room_type || ''}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Sélectionner un type</option>
                  <option value="lecture">Salle de Cours</option>
                  <option value="td">Salle de TD</option>
                  <option value="lab">Laboratoire/TP</option>
                  <option value="amphitheater">Amphithéâtre</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Capacité
                </label>
                <input
                  type="number"
                  name="capacity"
                  defaultValue={editingRoom?.capacity || 30}
                  min="1"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="30"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Département
                </label>
                <select
                  name="department"
                  defaultValue={editingRoom?.department || ''}
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
                  Équipements
                </label>
                <textarea
                  name="equipment"
                  defaultValue={editingRoom?.equipment || ''}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Projecteur, ordinateur, tableau interactif..."
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="is_available"
                  defaultChecked={editingRoom?.is_available ?? true}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-700">
                  Salle disponible
                </label>
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingRoom(null);
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
                  {editingRoom ? 'Modifier' : 'Créer'}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};