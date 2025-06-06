import React, { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/store/auth-store';
import { authAPI } from '@/lib/api/auth-api';
import type { APIKeyResponse } from '@/lib/api/auth-api';

export const ApiKeyManager: React.FC = () => {
  const { apiKeys, setApiKeys, activeApiKey, setActiveApiKey } = useAuthStore();
  const [newKeyName, setNewKeyName] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      const response = await authAPI.listApiKeys();
      setApiKeys(response.items);
    } catch (err) {
      setError('Failed to load API keys');
      console.error('Error loading API keys:', err);
    }
  };

  const createNewKey = async () => {
    if (!newKeyName.trim()) {
      setError('Please enter a name for the API key');
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      const newKey = await authAPI.createApiKey({ name: newKeyName.trim() });
      setApiKeys([...apiKeys, newKey]);
      setNewKeyName('');
      
      // Show the key to user (only time it's visible)
      alert(`Your new API key has been created:\n\n${newKey.key}\n\nPlease save this key now. You won't be able to see it again!`);
    } catch (err) {
      setError('Failed to create API key');
      console.error('Error creating API key:', err);
    } finally {
      setIsCreating(false);
    }
  };

  const deleteKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return;
    }

    try {
      await authAPI.deleteApiKey(keyId);
      setApiKeys(apiKeys.filter(key => key.id !== keyId));
      if (activeApiKey?.id === keyId) {
        setActiveApiKey(null);
      }
    } catch (err) {
      setError('Failed to delete API key');
      console.error('Error deleting API key:', err);
    }
  };

  const activateKey = async (key: APIKeyResponse) => {
    try {
      await authAPI.activateApiKey(key.id);
      const updatedKeys = apiKeys.map(k => 
        k.id === key.id ? { ...k, is_active: true } : k
      );
      setApiKeys(updatedKeys);
    } catch (err) {
      setError('Failed to activate API key');
      console.error('Error activating API key:', err);
    }
  };

  const deactivateKey = async (key: APIKeyResponse) => {
    try {
      await authAPI.deactivateApiKey(key.id);
      const updatedKeys = apiKeys.map(k => 
        k.id === key.id ? { ...k, is_active: false } : k
      );
      setApiKeys(updatedKeys);
      if (activeApiKey?.id === key.id) {
        setActiveApiKey(null);
      }
    } catch (err) {
      setError('Failed to deactivate API key');
      console.error('Error deactivating API key:', err);
    }
  };

  const selectKey = (key: APIKeyResponse) => {
    setActiveApiKey(key.is_active ? key : null);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Create New API Key</h2>
        <div className="flex gap-4">
          <input
            type="text"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            placeholder="Enter key name"
            className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isCreating}
          />
          <button
            onClick={createNewKey}
            disabled={isCreating}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {isCreating ? 'Creating...' : 'Create Key'}
          </button>
        </div>
        {error && (
          <p className="mt-2 text-sm text-red-600">{error}</p>
        )}
      </div>

      <div className="bg-white shadow-sm rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Your API Keys</h2>
        <div className="space-y-4">
          {apiKeys.length === 0 ? (
            <p className="text-gray-500">No API keys found. Create one to get started.</p>
          ) : (
            apiKeys.map(key => (
              <div
                key={key.id}
                className="border rounded-lg p-4 flex items-center justify-between"
              >
                <div className="space-y-1">
                  <h3 className="font-medium">{key.name}</h3>
                  <p className="text-sm text-gray-500">
                    Created: {new Date(key.created_at).toLocaleDateString()}
                  </p>
                  <p className="text-sm">
                    Status: <span className={key.is_active ? 'text-green-600' : 'text-red-600'}>
                      {key.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => selectKey(key)}
                    disabled={!key.is_active || activeApiKey?.id === key.id}
                    className="px-3 py-1 text-sm border rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {activeApiKey?.id === key.id ? 'Selected' : 'Select'}
                  </button>
                  <button
                    onClick={() => key.is_active ? deactivateKey(key) : activateKey(key)}
                    className="px-3 py-1 text-sm border rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {key.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                  <button
                    onClick={() => deleteKey(key.id)}
                    className="px-3 py-1 text-sm text-red-600 border border-red-200 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}; 