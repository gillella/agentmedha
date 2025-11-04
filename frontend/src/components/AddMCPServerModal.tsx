import React, { useState } from 'react';
import {
  X,
  Github,
  Database,
  Folder,
  Check,
  Loader2,
  AlertCircle,
  HardDrive,
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';

interface ServerType {
  type: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  requiredFields: Field[];
  optionalFields: Field[];
}

interface Field {
  name: string;
  label: string;
  type: 'text' | 'password' | 'number';
  placeholder?: string;
  defaultValue?: string;
}

const SERVER_TYPES: ServerType[] = [
  {
    type: 'github',
    name: 'GitHub',
    description: 'Connect to GitHub repositories for code and documentation',
    icon: <Github className="w-8 h-8" />,
    requiredFields: [
      { name: 'token', label: 'Personal Access Token', type: 'password', placeholder: 'ghp_...' },
    ],
    optionalFields: [
      { name: 'owner', label: 'Repository Owner', type: 'text', placeholder: 'username or org' },
      { name: 'repo', label: 'Repository Name', type: 'text', placeholder: 'repo-name' },
    ],
  },
  {
    type: 'postgres',
    name: 'PostgreSQL',
    description: 'Connect to PostgreSQL databases for data queries',
    icon: <Database className="w-8 h-8" />,
    requiredFields: [
      { name: 'host', label: 'Host', type: 'text', placeholder: 'localhost' },
      { name: 'port', label: 'Port', type: 'number', defaultValue: '5432' },
      { name: 'database', label: 'Database', type: 'text', placeholder: 'mydatabase' },
      { name: 'username', label: 'Username', type: 'text', placeholder: 'postgres' },
      { name: 'password', label: 'Password', type: 'password' },
    ],
    optionalFields: [
      { name: 'schema', label: 'Schema', type: 'text', placeholder: 'public' },
    ],
  },
  {
    type: 'filesystem',
    name: 'Filesystem',
    description: 'Access local or mounted filesystems',
    icon: <Folder className="w-8 h-8" />,
    requiredFields: [
      { name: 'path', label: 'Base Path', type: 'text', placeholder: '/path/to/directory' },
    ],
    optionalFields: [
      { name: 'allowed_extensions', label: 'Allowed Extensions', type: 'text', placeholder: '.txt,.md,.json' },
    ],
  },
  {
    type: 'sqlite',
    name: 'SQLite',
    description: 'Connect to SQLite database files',
    icon: <HardDrive className="w-8 h-8" />,
    requiredFields: [
      { name: 'database_path', label: 'Database Path', type: 'text', placeholder: '/path/to/database.db' },
    ],
    optionalFields: [],
  },
];

interface AddMCPServerModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export default function AddMCPServerModal({ onClose, onSuccess }: AddMCPServerModalProps) {
  const { accessToken } = useAuthStore();
  const [step, setStep] = useState<'select' | 'configure'>('select');
  const [selectedType, setSelectedType] = useState<ServerType | null>(null);
  const [serverName, setServerName] = useState('');
  const [description, setDescription] = useState('');
  const [config, setConfig] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<{ success: boolean; message?: string } | null>(null);

  const handleSelectType = (type: ServerType) => {
    setSelectedType(type);
    setStep('configure');
    // Initialize config with default values
    const initialConfig: Record<string, string> = {};
    [...type.requiredFields, ...type.optionalFields].forEach(field => {
      if (field.defaultValue) {
        initialConfig[field.name] = field.defaultValue;
      }
    });
    setConfig(initialConfig);
  };

  const handleConfigChange = (fieldName: string, value: string) => {
    setConfig(prev => ({ ...prev, [fieldName]: value }));
  };

  const validateForm = (): boolean => {
    if (!serverName.trim()) {
      setError('Server name is required');
      return false;
    }

    if (!selectedType) {
      setError('Server type not selected');
      return false;
    }

    // Check required fields
    for (const field of selectedType.requiredFields) {
      if (!config[field.name] || !config[field.name].trim()) {
        setError(`${field.label} is required`);
        return false;
      }
    }

    return true;
  };

  const handleTestConnection = async () => {
    if (!validateForm()) return;

    setTesting(true);
    setTestResult(null);
    setError(null);

    try {
      // For Phase 2, we'll just validate the config structure
      // Real connection testing will come when we integrate actual MCP clients
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      
      setTestResult({
        success: true,
        message: 'Configuration looks valid!'
      });
    } catch (err) {
      setTestResult({
        success: false,
        message: err instanceof Error ? err.message : 'Connection test failed'
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/mcp/servers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          name: serverName,
          description: description || undefined,
          server_type: selectedType!.type,
          config: config,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create server');
      }

      onSuccess();
    } catch (err) {
      console.error('Error creating server:', err);
      setError(err instanceof Error ? err.message : 'Failed to create server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Add MCP Server</h2>
            <p className="text-sm text-gray-600 mt-1">
              {step === 'select' ? 'Choose a server type' : `Configure ${selectedType?.name} server`}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {step === 'select' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {SERVER_TYPES.map((type) => (
                <button
                  key={type.type}
                  onClick={() => handleSelectType(type)}
                  className="text-left p-6 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all group"
                >
                  <div className="flex items-start space-x-4">
                    <div className="p-3 bg-blue-100 rounded-lg text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                      {type.icon}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg text-gray-900 mb-1">
                        {type.name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {type.description}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}

          {step === 'configure' && selectedType && (
            <div className="space-y-6">
              {/* Basic Info */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">Basic Information</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Server Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={serverName}
                    onChange={(e) => setServerName(e.target.value)}
                    placeholder="My PostgreSQL Server"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description (Optional)
                  </label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Production database for customer data"
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Connection Details */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">Connection Details</h3>
                
                {selectedType.requiredFields.map((field) => (
                  <div key={field.name}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {field.label} <span className="text-red-500">*</span>
                    </label>
                    <input
                      type={field.type}
                      value={config[field.name] || ''}
                      onChange={(e) => handleConfigChange(field.name, e.target.value)}
                      placeholder={field.placeholder}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                ))}

                {selectedType.optionalFields.length > 0 && (
                  <>
                    <h4 className="text-sm font-medium text-gray-600 mt-4">Optional Settings</h4>
                    {selectedType.optionalFields.map((field) => (
                      <div key={field.name}>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {field.label}
                        </label>
                        <input
                          type={field.type}
                          value={config[field.name] || ''}
                          onChange={(e) => handleConfigChange(field.name, e.target.value)}
                          placeholder={field.placeholder}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    ))}
                  </>
                )}
              </div>

              {/* Test Result */}
              {testResult && (
                <div className={`p-4 rounded-lg ${
                  testResult.success 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-start space-x-2">
                    {testResult.success ? (
                      <Check className="w-5 h-5 text-green-600 mt-0.5" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                    )}
                    <div>
                      <p className={`font-medium ${
                        testResult.success ? 'text-green-900' : 'text-red-900'
                      }`}>
                        {testResult.success ? 'Test Passed' : 'Test Failed'}
                      </p>
                      {testResult.message && (
                        <p className={`text-sm mt-1 ${
                          testResult.success ? 'text-green-700' : 'text-red-700'
                        }`}>
                          {testResult.message}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start space-x-2">
                    <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-red-900">Error</p>
                      <p className="text-sm text-red-700 mt-1">{error}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
          <div>
            {step === 'configure' && (
              <button
                onClick={() => {
                  setStep('select');
                  setSelectedType(null);
                  setError(null);
                  setTestResult(null);
                }}
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                ← Back to server types
              </button>
            )}
          </div>
          
          <div className="flex items-center space-x-3">
            {step === 'configure' && (
              <button
                onClick={handleTestConnection}
                disabled={testing || loading}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {testing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Testing...</span>
                  </>
                ) : (
                  <span>Test Connection</span>
                )}
              </button>
            )}
            
            <button
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
            
            {step === 'configure' && (
              <button
                onClick={handleSubmit}
                disabled={loading || testing}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Creating...</span>
                  </>
                ) : (
                  <span>Create Server</span>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

