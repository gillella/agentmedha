import React, { useState } from 'react';
import { Database, Server, FolderOpen, Settings } from 'lucide-react';
import MCPServersPage from './MCPServersPage';
import ResourcesPage from './ResourcesPage';

type TabType = 'servers' | 'sources' | 'resources' | 'settings';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('servers');

  const tabs = [
    { id: 'servers' as TabType, label: 'MCP Servers', icon: Server },
    { id: 'sources' as TabType, label: 'Data Sources', icon: Database },
    { id: 'resources' as TabType, label: 'Data Catalog', icon: FolderOpen },
    { id: 'settings' as TabType, label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Manage data sources, connections, and system configuration
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center space-x-2 px-6 py-4 font-medium text-sm
                    border-b-2 transition-colors
                    ${isActive
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'servers' && <MCPServersPage />}

        {activeTab === 'sources' && (
          <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
            <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Data Sources</h2>
            <p className="text-gray-600 max-w-md mx-auto">
              Configure and manage your organization's data sources.
              <br />
              <span className="text-sm text-gray-500 mt-2 inline-block">Coming soon...</span>
            </p>
          </div>
        )}

        {activeTab === 'resources' && <ResourcesPage />}

        {activeTab === 'settings' && (
          <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
            <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">System Settings</h2>
            <p className="text-gray-600 max-w-md mx-auto">
              Configure system-wide settings, permissions, and data loading options.
              <br />
              <span className="text-sm text-gray-500 mt-2 inline-block">Coming soon...</span>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
