import React, { useState, useEffect } from 'react';
import { notificationApi } from '@/lib/notifications/notification-api';
import type { NotificationPreference } from '@/lib/notifications/notification-api';

interface NotificationPreferencesFormProps {
  onClose?: () => void;
}

export const NotificationPreferencesForm: React.FC<NotificationPreferencesFormProps> = ({
  onClose,
}) => {
  const [preferences, setPreferences] = useState<NotificationPreference[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPreferences = async () => {
      try {
        const prefs = await notificationApi.getPreferences();
        setPreferences(prefs);
      } catch (error) {
        setError('Failed to load preferences');
        console.error('Failed to load preferences:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPreferences();
  }, []);

  const handleToggleChannel = async (pref: NotificationPreference) => {
    try {
      const updated = await notificationApi.updatePreference(pref.id, {
        enabled: !pref.enabled,
      });
      setPreferences(preferences.map(p => p.id === updated.id ? updated : p));
    } catch (error) {
      console.error('Failed to update preference:', error);
    }
  };

  const handlePriorityChange = async (pref: NotificationPreference, priority: NotificationPreference['min_priority']) => {
    try {
      const updated = await notificationApi.updatePreference(pref.id, {
        min_priority: priority,
      });
      setPreferences(preferences.map(p => p.id === updated.id ? updated : p));
    } catch (error) {
      console.error('Failed to update preference:', error);
    }
  };

  if (loading) {
    return <div className="p-4 text-center">Loading preferences...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-600">{error}</div>;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Notification Preferences</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            ×
          </button>
        )}
      </div>

      <div className="space-y-6">
        {preferences.map((pref) => (
          <div key={pref.id} className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={pref.enabled}
                    onChange={() => handleToggleChannel(pref)}
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
                <span className="ml-3 text-sm font-medium text-gray-900 capitalize">
                  {pref.channel} Notifications
                </span>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Minimum Priority
                </label>
                <select
                  value={pref.min_priority}
                  onChange={(e) => handlePriorityChange(pref, e.target.value as NotificationPreference['min_priority'])}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  disabled={!pref.enabled}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              {pref.channel === 'webhook' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Webhook URL
                  </label>
                  <input
                    type="url"
                    value={pref.webhook_url || ''}
                    onChange={async (e) => {
                      try {
                        const updated = await notificationApi.updatePreference(pref.id, {
                          webhook_url: e.target.value,
                        });
                        setPreferences(preferences.map(p => p.id === updated.id ? updated : p));
                      } catch (error) {
                        console.error('Failed to update webhook URL:', error);
                      }
                    }}
                    className="mt-1 block w-full shadow-sm sm:text-sm focus:ring-indigo-500 focus:border-indigo-500 border-gray-300 rounded-md"
                    placeholder="https://your-webhook-url.com"
                    disabled={!pref.enabled}
                  />
                </div>
              )}

              {pref.channel === 'email' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={pref.email_address || ''}
                    onChange={async (e) => {
                      try {
                        const updated = await notificationApi.updatePreference(pref.id, {
                          email_address: e.target.value,
                        });
                        setPreferences(preferences.map(p => p.id === updated.id ? updated : p));
                      } catch (error) {
                        console.error('Failed to update email address:', error);
                      }
                    }}
                    className="mt-1 block w-full shadow-sm sm:text-sm focus:ring-indigo-500 focus:border-indigo-500 border-gray-300 rounded-md"
                    placeholder="your@email.com"
                    disabled={!pref.enabled}
                  />
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}; 