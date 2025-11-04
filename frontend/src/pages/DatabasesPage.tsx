import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Plus,
  Database,
  Trash2,
  Edit,
  TestTube,
  Shield,
  CheckCircle2,
  XCircle,
  Clock,
  Globe,
  Lock,
  Users,
  Loader2,
  X,
  Sparkles,
} from 'lucide-react'
import { databaseApi } from '../services/api'
import { useAuthStore } from '../store/authStore'

interface DatabaseConnection {
  id: number
  name: string
  display_name?: string
  description?: string
  keywords?: string[]
  database_type: string
  is_shared: boolean
  access_level: string
  allowed_roles?: string[]
  allowed_users?: number[]
  connection_status: string
  is_active: boolean
  last_tested?: string
  created_at: string
  updated_at: string
}

export default function DatabasesPage() {
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingConnection, setEditingConnection] = useState<DatabaseConnection | null>(
    null
  )
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const { isAdmin } = useAuthStore()

  // Admin-only guard
  useEffect(() => {
    if (!isAdmin()) {
      navigate('/')
    }
  }, [isAdmin, navigate])

  // Fetch connections
  const { data: connections, isLoading } = useQuery({
    queryKey: ['databases'],
    queryFn: databaseApi.list,
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: databaseApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['databases'] })
    },
  })

  // Test connection mutation
  const testMutation = useMutation({
    mutationFn: databaseApi.test,
  })

  const handleDelete = (id: number, name: string) => {
    if (confirm(`Are you sure you want to delete "${name}"?`)) {
      deleteMutation.mutate(id)
    }
  }

  const handleTest = async (id: number) => {
    try {
      const result = await testMutation.mutateAsync(id)
      alert(result.message)
      queryClient.invalidateQueries({ queryKey: ['databases'] })
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Test failed')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle2 className="h-4 w-4 text-green-600" />
      case 'unhealthy':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getAccessIcon = (level: string) => {
    switch (level) {
      case 'public':
        return <Globe className="h-3.5 w-3.5" />
      case 'restricted':
        return <Users className="h-3.5 w-3.5" />
      default:
        return <Lock className="h-3.5 w-3.5" />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-8 py-8">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-3 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl shadow-lg shadow-blue-500/20">
                  <Database className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">Data Sources</h1>
                  <div className="flex items-center gap-2 mt-1">
                    <Shield className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-600">
                      Admin Panel
                    </span>
                  </div>
                </div>
              </div>
              <p className="text-gray-600 mt-2 max-w-2xl">
                Configure organization-wide data sources for your team. Add keywords to enable
                AI-powered discovery.
              </p>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-5 py-3 rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30 hover:-translate-y-0.5"
            >
              <Plus className="h-5 w-5" />
              <span className="font-medium">Add Data Source</span>
            </button>
          </div>

          {/* Stats */}
          {connections && (
            <div className="grid grid-cols-4 gap-4 mt-6">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
                <div className="text-2xl font-bold text-blue-900">
                  {connections.length}
                </div>
                <div className="text-sm text-blue-700 font-medium mt-1">
                  Total Sources
                </div>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border border-green-100">
                <div className="text-2xl font-bold text-green-900">
                  {connections.filter((c: DatabaseConnection) => c.connection_status === 'healthy').length}
                </div>
                <div className="text-sm text-green-700 font-medium mt-1">Healthy</div>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-100">
                <div className="text-2xl font-bold text-purple-900">
                  {connections.filter((c: DatabaseConnection) => c.is_shared).length}
                </div>
                <div className="text-sm text-purple-700 font-medium mt-1">Shared</div>
              </div>
              <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-4 border border-amber-100">
                <div className="text-2xl font-bold text-amber-900">
                  {connections.filter((c: DatabaseConnection) => c.access_level === 'public').length}
                </div>
                <div className="text-sm text-amber-700 font-medium mt-1">
                  Public Access
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-8 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
          </div>
        ) : connections && connections.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {connections.map((conn: DatabaseConnection) => (
              <div
                key={conn.id}
                className="group bg-white rounded-2xl border border-gray-200 overflow-hidden hover:shadow-xl hover:shadow-gray-200/50 transition-all duration-300"
              >
                {/* Card Header */}
                <div className="p-6 border-b border-gray-100">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start gap-4 flex-1">
                      <div className="p-3 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl group-hover:from-blue-100 group-hover:to-indigo-100 transition-colors">
                        <Database className="h-6 w-6 text-blue-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                          {conn.display_name || conn.name}
                        </h3>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(conn.connection_status)}
                          <span
                            className={`text-sm font-medium ${
                              conn.connection_status === 'healthy'
                                ? 'text-green-600'
                                : conn.connection_status === 'unhealthy'
                                ? 'text-red-600'
                                : 'text-gray-500'
                            }`}
                          >
                            {conn.connection_status.charAt(0).toUpperCase() +
                              conn.connection_status.slice(1)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Description */}
                  {conn.description && (
                    <p className="text-sm text-gray-600 line-clamp-2 mb-4">
                      {conn.description}
                    </p>
                  )}

                  {/* Tags Row */}
                  <div className="flex items-center gap-2 flex-wrap">
                    {/* Database Type */}
                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-xs font-medium">
                      <Sparkles className="h-3 w-3" />
                      {conn.database_type}
                    </span>

                    {/* Sharing Status */}
                    {conn.is_shared ? (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg text-xs font-medium">
                        <Globe className="h-3 w-3" />
                        Shared
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 text-gray-600 rounded-lg text-xs font-medium">
                        <Lock className="h-3 w-3" />
                        Private
                      </span>
                    )}

                    {/* Access Level */}
                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-purple-50 text-purple-700 rounded-lg text-xs font-medium capitalize">
                      {getAccessIcon(conn.access_level)}
                      {conn.access_level}
                    </span>
                  </div>

                  {/* Keywords */}
                  {conn.keywords && conn.keywords.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-100">
                      {conn.keywords.slice(0, 4).map((keyword, idx) => (
                        <span
                          key={idx}
                          className="px-2.5 py-1 bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 rounded-md text-xs font-medium"
                        >
                          {keyword}
                        </span>
                      ))}
                      {conn.keywords.length > 4 && (
                        <span className="px-2.5 py-1 bg-gray-100 text-gray-600 rounded-md text-xs font-medium">
                          +{conn.keywords.length - 4} more
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Card Footer - Actions */}
                <div className="px-6 py-4 bg-gray-50 flex items-center gap-2">
                  <button
                    onClick={() => handleTest(conn.id)}
                    disabled={testMutation.isPending}
                    className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-colors disabled:opacity-50"
                  >
                    {testMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <TestTube className="h-4 w-4" />
                    )}
                    Test
                  </button>
                  <button
                    onClick={() => setEditingConnection(conn)}
                    className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-colors"
                  >
                    <Edit className="h-4 w-4" />
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(conn.id, conn.display_name || conn.name)}
                    disabled={deleteMutation.isPending}
                    className="flex items-center gap-2 px-4 py-2 bg-white border border-red-200 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 hover:border-red-300 transition-colors disabled:opacity-50 ml-auto"
                  >
                    <Trash2 className="h-4 w-4" />
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="inline-flex p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl mb-6">
              <Database className="h-16 w-16 text-blue-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              No Data Sources Yet
            </h3>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Add your first data source to enable users to discover and query data through
              natural language.
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-500/25 font-medium"
            >
              <Plus className="h-5 w-5" />
              Add Your First Data Source
            </button>
          </div>
        )}
      </div>

      {/* Add/Edit Modal */}
      {(showAddModal || editingConnection) && (
        <DatabaseConnectionModal
          connection={editingConnection}
          onClose={() => {
            setShowAddModal(false)
            setEditingConnection(null)
          }}
        />
      )}
    </div>
  )
}

// Modal Component (keeping it compact for now, can be enhanced further)
function DatabaseConnectionModal({
  connection,
  onClose,
}: {
  connection: DatabaseConnection | null
  onClose: () => void
}) {
  const [formData, setFormData] = useState({
    name: connection?.name || '',
    display_name: connection?.display_name || '',
    description: connection?.description || '',
    keywords: connection?.keywords?.join(', ') || '',
    database_type: connection?.database_type || 'postgresql',
    connection_string: '',
    is_shared: connection?.is_shared ?? true,
    access_level: connection?.access_level || 'public',
    allowed_roles: connection?.allowed_roles?.join(', ') || '',
  })
  const [error, setError] = useState('')
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: connection
      ? (data: any) => databaseApi.update(connection.id, data)
      : databaseApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['databases'] })
      onClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to save data source')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    const payload = {
      ...formData,
      keywords: formData.keywords
        ? formData.keywords
            .split(',')
            .map((k) => k.trim())
            .filter(Boolean)
        : undefined,
      allowed_roles: formData.allowed_roles
        ? formData.allowed_roles
            .split(',')
            .map((r) => r.trim())
            .filter(Boolean)
        : undefined,
    }

    mutation.mutate(payload)
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-8 py-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {connection ? 'Edit Data Source' : 'Add Data Source'}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Configure connection and access control settings
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-8 space-y-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-6">
            {/* Name */}
            <div className="col-span-2 sm:col-span-1">
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Internal Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="sales_db"
                required
              />
            </div>

            {/* Display Name */}
            <div className="col-span-2 sm:col-span-1">
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Display Name
              </label>
              <input
                type="text"
                value={formData.display_name}
                onChange={(e) =>
                  setFormData({ ...formData, display_name: e.target.value })
                }
                className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Sales Database"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="Customer orders, products, and revenue data"
              rows={3}
            />
          </div>

          {/* Keywords */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Keywords (comma-separated)
            </label>
            <input
              type="text"
              value={formData.keywords}
              onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="sales, orders, revenue, customers"
            />
            <p className="text-xs text-gray-500 mt-2">
              Used by AI to discover relevant data sources
            </p>
          </div>

          <div className="grid grid-cols-2 gap-6">
            {/* Database Type */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Database Type *
              </label>
              <select
                value={formData.database_type}
                onChange={(e) =>
                  setFormData({ ...formData, database_type: e.target.value })
                }
                className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                required
              >
                <option value="postgresql">PostgreSQL</option>
                <option value="mysql">MySQL</option>
                <option value="snowflake">Snowflake</option>
                <option value="bigquery">BigQuery</option>
              </select>
            </div>

            {/* Access Level */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Access Level
              </label>
              <select
                value={formData.access_level}
                onChange={(e) =>
                  setFormData({ ...formData, access_level: e.target.value })
                }
                className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              >
                <option value="public">Public (All Users)</option>
                <option value="restricted">Restricted (Specific Roles)</option>
                <option value="private">Private (Admin Only)</option>
              </select>
            </div>
          </div>

          {/* Connection String */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Connection String *
            </label>
            <input
              type="password"
              value={formData.connection_string}
              onChange={(e) =>
                setFormData({ ...formData, connection_string: e.target.value })
              }
              className="w-full px-4 py-3 border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all font-mono text-sm"
              placeholder="postgresql://user:pass@host:port/db"
              required={!connection}
            />
            <p className="text-xs text-gray-500 mt-2">
              {connection
                ? 'Leave empty to keep existing credentials'
                : 'Will be encrypted before storage'}
            </p>
          </div>

          {/* Share Toggle */}
          <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-xl border border-blue-100">
            <input
              type="checkbox"
              id="is_shared"
              checked={formData.is_shared}
              onChange={(e) =>
                setFormData({ ...formData, is_shared: e.target.checked })
              }
              className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <label htmlFor="is_shared" className="text-sm font-medium text-gray-900">
              Share with organization
            </label>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3 pt-6">
            <button
              type="submit"
              disabled={mutation.isPending}
              className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-6 rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-500/25 font-medium disabled:opacity-50"
            >
              {mutation.isPending ? (
                <span className="flex items-center justify-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Saving...
                </span>
              ) : connection ? (
                'Update Data Source'
              ) : (
                'Create Data Source'
              )}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors font-medium text-gray-700"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
