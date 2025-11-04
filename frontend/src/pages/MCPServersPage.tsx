import React, { useState, useEffect } from 'react';
import {
  Database,
  Github,
  Folder,
  Plus,
  Trash2,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle,
  Settings,
  Search,
} from 'lucide-react';
import AddMCPServerModal from '../components/AddMCPServerModal';
import { useAuthStore } from '../store/authStore';

interface MCPServer {
  id: string;
  name: string;
  description: string;
  server_type: string;
  status: 'active' | 'inactive' | 'error';
  last_connected_at: string | null;
  error_message: string | null;
  resource_count: number;
  created_at: string;
}

const SERVER_TYPE_ICONS: Record<string, React.ReactNode> = {
  github: <Github className="w-6 h-6" />,
  postgres: <Database className="w-6 h-6" />,
  filesystem: <Folder className="w-6 h-6" />,
  sqlite: <Database className="w-6 h-6" />,
};

const SERVER_TYPE_LABELS: Record<string, string> = {
  github: 'GitHub',
  postgres: 'PostgreSQL',
  filesystem: 'Filesystem',
  sqlite: 'SQLite',
};

export default function MCPServersPage() {
  const { accessToken } = useAuthStore();
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadServers();
  }, []);

  const loadServers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:8000/api/v1/mcp/servers', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load servers');
      }

      const data = await response.json();
      setServers(data);
    } catch (err) {
      console.error('Error loading servers:', err);
      setError(err instanceof Error ? err.message : 'Failed to load servers');
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async (serverId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/mcp/servers/${serverId}/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      const result = await response.json();
      
      if (result.success) {
        alert('Connection successful!');
        loadServers(); // Reload to show updated status
      } else {
        alert(`Connection failed: ${result.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error testing connection:', err);
      alert('Failed to test connection');
    }
  };

  const deleteServer = async (serverId: string, serverName: string) => {
    if (!confirm(`Are you sure you want to delete "${serverName}"?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/mcp/servers/${serverId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete server');
      }

      alert('Server deleted successfully');
      loadServers();
    } catch (err) {
      console.error('Error deleting server:', err);
      alert('Failed to delete server');
    }
  };

  const discoverResources = async (serverId: string, serverName: string) => {
    if (!confirm(`Discover resources from "${serverName}"? This may take a moment.`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/mcp/servers/${serverId}/resources?refresh=true`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to discover resources');
      }

      const resources = await response.json();
      alert(`Discovered ${resources.length} resources!`);
      loadServers(); // Reload to show updated resource count
    } catch (err) {
      console.error('Error discovering resources:', err);
      alert('Failed to discover resources');
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">MCP Servers</h1>
          <p className="text-gray-600 mt-2">
            Manage data source connections through Model Context Protocol servers
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Add Server</span>
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
          <p className="font-semibold">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      )}

      {/* Empty State */}
      {!loading && servers.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No MCP Servers Yet
          </h3>
          <p className="text-gray-600 mb-4">
            Add your first MCP server to connect data sources
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-5 h-5" />
            <span>Add Server</span>
          </button>
        </div>
      )}

      {/* Server Grid */}
      {!loading && servers.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {servers.map((server) => (
            <div
              key={server.id}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow"
            >
              {/* Server Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                    {SERVER_TYPE_ICONS[server.server_type] || <Database className="w-6 h-6" />}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{server.name}</h3>
                    <p className="text-sm text-gray-600">
                      {SERVER_TYPE_LABELS[server.server_type] || server.server_type}
                    </p>
                  </div>
                </div>
                
                {/* Status Badge */}
                <div>
                  {server.status === 'active' && (
                    <div className="flex items-center space-x-1 text-green-600 bg-green-50 px-2 py-1 rounded">
                      <CheckCircle className="w-4 h-4" />
                      <span className="text-xs font-medium">Active</span>
                    </div>
                  )}
                  {server.status === 'inactive' && (
                    <div className="flex items-center space-x-1 text-gray-600 bg-gray-50 px-2 py-1 rounded">
                      <AlertCircle className="w-4 h-4" />
                      <span className="text-xs font-medium">Inactive</span>
                    </div>
                  )}
                  {server.status === 'error' && (
                    <div className="flex items-center space-x-1 text-red-600 bg-red-50 px-2 py-1 rounded">
                      <XCircle className="w-4 h-4" />
                      <span className="text-xs font-medium">Error</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Description */}
              {server.description && (
                <p className="text-sm text-gray-600 mb-4">{server.description}</p>
              )}

              {/* Error Message */}
              {server.error_message && (
                <div className="bg-red-50 border border-red-200 rounded p-2 mb-4">
                  <p className="text-xs text-red-800">{server.error_message}</p>
                </div>
              )}

              {/* Stats */}
              <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                <span>{server.resource_count} resources</span>
                {server.last_connected_at && (
                  <span className="text-xs">
                    Last: {new Date(server.last_connected_at).toLocaleDateString()}
                  </span>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2 pt-4 border-t border-gray-200">
                <button
                  onClick={() => testConnection(server.id)}
                  className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-blue-50 text-blue-600 rounded hover:bg-blue-100 transition-colors text-sm"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Test</span>
                </button>
                <button
                  onClick={() => discoverResources(server.id, server.name)}
                  className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-green-50 text-green-600 rounded hover:bg-green-100 transition-colors text-sm"
                  title="Discover Resources"
                >
                  <Search className="w-4 h-4" />
                  <span>Discover</span>
                </button>
                <button
                  className="flex items-center justify-center p-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                  title="Settings"
                >
                  <Settings className="w-4 h-4" />
                </button>
                <button
                  onClick={() => deleteServer(server.id, server.name)}
                  className="flex items-center justify-center p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Server Modal */}
      {showAddModal && (
        <AddMCPServerModal
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false);
            loadServers();
          }}
        />
      )}
    </div>
  );
}

