import React, { useState, useEffect } from 'react';
import { Card, Button, Modal, Loading } from '../ui';
import { 
  Bell, Settings, Check, Trash2, Filter, Search,
  X, AlertCircle, Info, CheckCircle, Clock 
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import enhancedAPI from '../../services/enhancedAPI';
import { NotificationEnhanced, NotificationSettings } from '../../types';

interface NotificationCenterProps {
  isDropdown?: boolean;
  maxItems?: number;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({ 
  isDropdown = false, 
  maxItems = 50 
}) => {
  const [notifications, setNotifications] = useState<NotificationEnhanced[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    loadNotifications();
    loadUnreadCount();
  }, [filter]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const params = {
        limit: maxItems,
        ...(filter !== 'all' && { notification_type: filter }),
        ...(searchQuery && { search: searchQuery })
      };
      
      const response = await enhancedAPI.notifications.getNotifications(params);
      setNotifications(response.data);
    } catch (error) {
      console.error('Erreur chargement notifications:', error);
      toast.error('Erreur lors du chargement des notifications');
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const response = await enhancedAPI.notifications.getUnreadCount();
      setUnreadCount(response.data.count);
    } catch (error) {
      console.error('Erreur comptage non lues:', error);
    }
  };

  const markAsRead = async (id: number) => {
    try {
      await enhancedAPI.notifications.markAsRead(id);
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === id ? { ...notif, is_read: true } : notif
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Erreur marquage lu:', error);
      toast.error('Erreur lors du marquage');
    }
  };

  const markAllAsRead = async () => {
    try {
      await enhancedAPI.notifications.markAllAsRead();
      setNotifications(prev => 
        prev.map(notif => ({ ...notif, is_read: true }))
      );
      setUnreadCount(0);
      toast.success('Toutes les notifications marquées comme lues');
    } catch (error) {
      console.error('Erreur marquage toutes lues:', error);
      toast.error('Erreur lors du marquage');
    }
  };

  const deleteNotification = async (id: number) => {
    try {
      await enhancedAPI.notifications.deleteNotification(id);
      setNotifications(prev => prev.filter(notif => notif.id !== id));
      toast.success('Notification supprimée');
    } catch (error) {
      console.error('Erreur suppression:', error);
      toast.error('Erreur lors de la suppression');
    }
  };

  const handleNotificationClick = async (notification: NotificationEnhanced) => {
    // Marquer comme lue si pas déjà lu
    if (!notification.is_read) {
      await markAsRead(notification.id);
    }

    // Naviguer vers l'action si URL fournie
    if (notification.action_url) {
      window.location.href = notification.action_url;
    }
  };

  const filteredNotifications = notifications.filter(notif => {
    if (searchQuery) {
      return notif.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
             notif.message.toLowerCase().includes(searchQuery.toLowerCase());
    }
    return true;
  });

  if (loading) {
    return <Loading message="Chargement des notifications..." />;
  }

  return (
    <div className={`${isDropdown ? 'w-80' : 'max-w-4xl mx-auto'}`}>
      {/* Header */}
      {!isDropdown && (
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Centre de Notifications</h1>
            <p className="text-gray-600">
              {unreadCount > 0 ? `${unreadCount} notification(s) non lue(s)` : 'Toutes les notifications sont lues'}
            </p>
          </div>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              onClick={() => setShowSettings(true)}
            >
              <Settings className="w-4 h-4 mr-2" />
              Paramètres
            </Button>
            {unreadCount > 0 && (
              <Button
                onClick={markAllAsRead}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Check className="w-4 h-4 mr-2" />
                Tout marquer lu
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Filtres et recherche */}
      {!isDropdown && (
        <Card className="p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Rechercher dans les notifications..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">Toutes</option>
                <option value="schedule_change">Emploi du temps</option>
                <option value="grade">Notes</option>
                <option value="absence">Absences</option>
                <option value="pdf_export">Exports PDF</option>
                <option value="system">Système</option>
              </select>
            </div>
          </div>
        </Card>
      )}

      {/* Liste des notifications */}
      <div className="space-y-2">
        {filteredNotifications.length === 0 ? (
          <Card className="p-8 text-center">
            <Bell className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p className="text-gray-500">Aucune notification</p>
            {searchQuery && (
              <p className="text-sm text-gray-400 mt-1">
                Aucun résultat pour "{searchQuery}"
              </p>
            )}
          </Card>
        ) : (
          filteredNotifications.map((notification) => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              onClick={() => handleNotificationClick(notification)}
              onMarkRead={() => markAsRead(notification.id)}
              onDelete={() => deleteNotification(notification.id)}
              isCompact={isDropdown}
            />
          ))
        )}
      </div>

      {/* Modal paramètres */}
      {showSettings && (
        <NotificationSettingsModal
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  );
};

const NotificationItem: React.FC<{
  notification: NotificationEnhanced;
  onClick: () => void;
  onMarkRead: () => void;
  onDelete: () => void;
  isCompact?: boolean;
}> = ({ notification, onClick, onMarkRead, onDelete, isCompact = false }) => {
  const getPriorityIcon = () => {
    switch (notification.priority) {
      case 'urgent':
      case 'critical':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'high':
        return <AlertCircle className="w-4 h-4 text-orange-500" />;
      case 'medium':
        return <Info className="w-4 h-4 text-blue-500" />;
      default:
        return <CheckCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <Card 
      className={`p-4 cursor-pointer transition-all duration-200 hover:shadow-md ${
        !notification.is_read ? 'bg-blue-50 border-l-4 border-l-blue-500' : 'bg-white'
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            {getPriorityIcon()}
            <span className="text-xs text-gray-500">
              {enhancedAPI.helpers.notifications.getNotificationIcon(notification.notification_type)}
            </span>
            <h3 className={`text-sm font-medium truncate ${
              !notification.is_read ? 'text-gray-900' : 'text-gray-600'
            }`}>
              {notification.title}
            </h3>
            {!notification.is_read && (
              <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0" />
            )}
          </div>
          
          <p className={`text-sm ${
            !notification.is_read ? 'text-gray-700' : 'text-gray-500'
          } ${isCompact ? 'line-clamp-2' : ''}`}>
            {notification.message}
          </p>
          
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-gray-400">
              {enhancedAPI.helpers.notifications.formatTimeAgo(notification.created_at)}
            </span>
            
            {notification.action_text && (
              <span className="text-xs text-blue-600 font-medium">
                {notification.action_text}
              </span>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-1 ml-4">
          {!notification.is_read && (
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                onMarkRead();
              }}
              title="Marquer comme lu"
            >
              <Check className="w-4 h-4" />
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            title="Supprimer"
            className="text-red-500 hover:text-red-700"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
};

const NotificationSettingsModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
}> = ({ isOpen, onClose }) => {
  const [settings, setSettings] = useState<NotificationSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen]);

  const loadSettings = async () => {
    try {
      const response = await enhancedAPI.notifications.getMySettings();
      setSettings(response.data);
    } catch (error) {
      console.error('Erreur chargement paramètres:', error);
      toast.error('Erreur lors du chargement des paramètres');
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    if (!settings) return;

    try {
      setSaving(true);
      await enhancedAPI.notifications.updateMySettings(settings);
      toast.success('Paramètres sauvegardés');
      onClose();
    } catch (error) {
      console.error('Erreur sauvegarde paramètres:', error);
      toast.error('Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = (key: keyof NotificationSettings, value: any) => {
    if (!settings) return;
    setSettings({ ...settings, [key]: value });
  };

  if (loading) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="Paramètres de notification">
        <Loading message="Chargement des paramètres..." />
      </Modal>
    );
  }

  if (!settings) {
    return null;
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Paramètres de notification">
      <div className="space-y-6">
        {/* Canaux globaux */}
        <div>
          <h3 className="text-lg font-medium mb-4">Canaux de notification</h3>
          <div className="space-y-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.email_notifications}
                onChange={(e) => updateSetting('email_notifications', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2">Notifications par email</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.push_notifications}
                onChange={(e) => updateSetting('push_notifications', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2">Notifications push</span>
            </label>
          </div>
        </div>

        {/* Types de notifications */}
        <div>
          <h3 className="text-lg font-medium mb-4">Types de notifications</h3>
          <div className="space-y-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.schedule_changes}
                onChange={(e) => updateSetting('schedule_changes', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2">Changements d'emploi du temps</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.grade_updates}
                onChange={(e) => updateSetting('grade_updates', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2">Mises à jour des notes</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.absence_reminders}
                onChange={(e) => updateSetting('absence_reminders', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2">Rappels d'absences</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.pdf_exports}
                onChange={(e) => updateSetting('pdf_exports', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2">Exports PDF</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.system_announcements}
                onChange={(e) => updateSetting('system_announcements', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2">Annonces système</span>
            </label>
          </div>
        </div>

        {/* Horaires */}
        <div>
          <h3 className="text-lg font-medium mb-4">Horaires</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Heures silencieuses - Début
              </label>
              <input
                type="time"
                value={settings.quiet_hours_start}
                onChange={(e) => updateSetting('quiet_hours_start', e.target.value)}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Heures silencieuses - Fin
              </label>
              <input
                type="time"
                value={settings.quiet_hours_end}
                onChange={(e) => updateSetting('quiet_hours_end', e.target.value)}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <label className="flex items-center mt-3">
            <input
              type="checkbox"
              checked={settings.weekend_notifications}
              onChange={(e) => updateSetting('weekend_notifications', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2">Notifications le week-end</span>
          </label>
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            Annuler
          </Button>
          <Button
            onClick={saveSettings}
            loading={saving}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Sauvegarder
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default NotificationCenter;
