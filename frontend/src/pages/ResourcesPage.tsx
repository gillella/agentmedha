import React, { useState, useEffect } from 'react';
import { Table, Database, FileText, Folder, Search, Filter, Eye, Code, BarChart3, RefreshCw } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

interface MCPResource {
  id: string;
  server_id: string;
  resource_type: string;
  name: string;
  uri: string;
  metadata: any;
  created_at: string;
  updated_at: string;
}

interface MCPServer {
  id: string;
  name: string;
  server_type: string;
}

interface ResourceWithStats {
  resource: MCPResource;
  rowCount?: number;
  columnCount?: number;
  lastQueried?: string;
}

export default function ResourcesPage() {
  const { accessToken } = useAuthStore();
  const navigate = useNavigate();
  const [resources, setResources] = useState<MCPResource[]>([]);
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedServer, setSelectedServer] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  useEffect(() => {
    loadData();
  }, [accessToken]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load servers
      const serversResponse = await fetch('http://localhost:8000/api/v1/mcp/servers', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!serversResponse.ok) {
        throw new Error('Failed to load servers');
      }

      const serversData = await serversResponse.json();
      setServers(serversData);

      // Load all resources from all servers
      const allResources: MCPResource[] = [];
      for (const server of serversData) {
        try {
          const resourcesResponse = await fetch(
            `http://localhost:8000/api/v1/mcp/servers/${server.id}/resources`,
            {
              headers: {
                'Authorization': `Bearer ${accessToken}`,
              },
            }
          );

          if (resourcesResponse.ok) {
            const resourcesData = await resourcesResponse.json();
            allResources.push(...resourcesData);
          }
        } catch (err) {
          console.error(`Failed to load resources for server ${server.name}:`, err);
        }
      }

      setResources(allResources);
      setError(null);
    } catch (err) {
      console.error('Error loading data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load resources');
    } finally {
      setLoading(false);
    }
  };

  const getResourceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'table':
        return <Table className="w-5 h-5 text-blue-600 group-hover:text-white transition-colors" />;
      case 'database':
        return <Database className="w-5 h-5 text-blue-600 group-hover:text-white transition-colors" />;
      case 'file':
        return <FileText className="w-5 h-5 text-blue-600 group-hover:text-white transition-colors" />;
      case 'folder':
        return <Folder className="w-5 h-5 text-blue-600 group-hover:text-white transition-colors" />;
      default:
        return <FileText className="w-5 h-5 text-blue-600 group-hover:text-white transition-colors" />;
    }
  };

  const filteredResources = resources.filter((resource) => {
    const matchesSearch = resource.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         resource.uri.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesServer = selectedServer === 'all' || resource.server_id === selectedServer;
    const matchesType = selectedType === 'all' || resource.resource_type === selectedType;
    return matchesSearch && matchesServer && matchesType;
  });

  const resourceTypes = Array.from(new Set(resources.map(r => r.resource_type)));

  const getServerName = (serverId: string) => {
    const server = servers.find(s => s.id === serverId);
    return server?.name || 'Unknown Server';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading resources...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6 max-w-md">
          <p className="text-red-800 font-semibold mb-2">Error</p>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  const handleQueryResource = (resourceName: string) => {
    // Navigate to chat with pre-filled query
    navigate(`/chat?query=Tell me about the ${resourceName} table`);
  };

  // Group resources by server for better organization
  const groupedResources = filteredResources.reduce((acc, resource) => {
    const serverName = getServerName(resource.server_id);
    if (!acc[serverName]) {
      acc[serverName] = [];
    }
    acc[serverName].push(resource);
    return acc;
  }, {} as Record<string, MCPResource[]>);

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Data Catalog</h2>
            <p className="text-gray-600">
              Explore and query {resources.length} discovered tables and resources
            </p>
          </div>
          <button
            onClick={loadData}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Total Resources</p>
              <p className="text-3xl font-bold mt-1">{resources.length}</p>
            </div>
            <Database className="w-12 h-12 opacity-20" />
          </div>
        </div>
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Tables</p>
              <p className="text-3xl font-bold mt-1">{resources.filter(r => r.resource_type === 'table').length}</p>
            </div>
            <Table className="w-12 h-12 opacity-20" />
          </div>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Servers</p>
              <p className="text-3xl font-bold mt-1">{servers.length}</p>
            </div>
            <Database className="w-12 h-12 opacity-20" />
          </div>
        </div>
        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm font-medium">Resource Types</p>
              <p className="text-3xl font-bold mt-1">{resourceTypes.length}</p>
            </div>
            <Folder className="w-12 h-12 opacity-20" />
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search tables, views, or resources..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={selectedServer}
            onChange={(e) => setSelectedServer(e.target.value)}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white min-w-[200px]"
          >
            <option value="all">All Servers</option>
            {servers.map((server) => (
              <option key={server.id} value={server.id}>
                {server.name}
              </option>
            ))}
          </select>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white min-w-[150px]"
          >
            <option value="all">All Types</option>
            {resourceTypes.map((type) => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Resources */}
      {filteredResources.length === 0 ? (
        <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border-2 border-dashed border-gray-300 p-16 text-center">
          <Database className="w-20 h-20 text-gray-400 mx-auto mb-6" />
          <h3 className="text-2xl font-bold text-gray-900 mb-3">No Resources Found</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            {resources.length === 0
              ? 'Discover resources from your MCP servers to start exploring your data.'
              : 'Try adjusting your search or filters to find what you\'re looking for.'}
          </p>
          {resources.length === 0 && (
            <button
              onClick={() => navigate('/admin')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go to MCP Servers
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedResources).map(([serverName, serverResources]) => (
            <div key={serverName} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              {/* Server Header */}
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <Database className="w-5 h-5 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">{serverName}</h3>
                  <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                    {serverResources.length} resources
                  </span>
                </div>
              </div>

              {/* Resource Cards Grid */}
              <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {serverResources.map((resource) => (
                  <div
                    key={resource.id}
                    className="group bg-gradient-to-br from-white to-gray-50 rounded-lg border-2 border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all p-5 cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-600 transition-colors">
                          {getResourceIcon(resource.resource_type)}
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                            {resource.name}
                          </h4>
                          <span className="text-xs text-gray-500 uppercase tracking-wide">
                            {resource.resource_type}
                          </span>
                        </div>
                      </div>
                    </div>

                    {resource.metadata?.description && (
                      <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                        {resource.metadata.description}
                      </p>
                    )}

                    {/* Quick Actions */}
                    <div className="flex items-center space-x-2 pt-4 border-t border-gray-200">
                      <button
                        onClick={() => handleQueryResource(resource.name)}
                        className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-600 hover:text-white transition-colors text-sm font-medium"
                      >
                        <BarChart3 className="w-4 h-4" />
                        <span>Query</span>
                      </button>
                      <button
                        className="flex items-center justify-center px-3 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                        title="View Schema"
                      >
                        <Code className="w-4 h-4" />
                      </button>
                      <button
                        className="flex items-center justify-center px-3 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                        title="Preview Data"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

