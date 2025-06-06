import React from 'react';
import { ApiKeyManager } from '@/components/ApiKeyManager';

export const Settings: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-8">Settings</h1>
      
      <div className="space-y-8">
        <section>
          <h2 className="text-xl font-semibold mb-4">API Keys</h2>
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <p className="text-gray-600 mb-6">
                API keys are used to authenticate your requests to the incident tracking system.
                Create and manage your API keys here. Remember to keep your API keys secure and
                never share them with others.
              </p>
              <ApiKeyManager />
            </div>
          </div>
        </section>

        {/* Add other settings sections here */}
      </div>
    </div>
  );
}; 