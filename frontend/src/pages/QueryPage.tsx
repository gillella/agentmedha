import { useState, useEffect, useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  Send,
  Database,
  Sparkles,
  Loader2,
  ArrowRight,
  CheckCircle2,
  Zap,
  Code,
  ChevronDown,
  ChevronUp,
  Download,
  BarChart3,
  ThumbsUp,
  ThumbsDown,
} from 'lucide-react'
import axios from 'axios'
import { useAuthStore } from '../store/authStore'
import DataVisualization from '../components/DataVisualization'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  message_type?: 'discovery' | 'query_result' | 'clarification' | 'error' | 'info'
  dataSources?: DataSource[]
  sqlQuery?: string
  sqlExplanation?: string
  results?: any[]
  resultCount?: number
  visualization?: VisualizationConfig
  suggestedActions?: string[]
  contextStats?: ContextStats
  errorCode?: string
  timestamp: Date
}

interface DataSource {
  id: number
  name: string
  display_name: string
  description: string | null
  database_type: string
  keywords: string[] | null
  connection_status: string
}

interface VisualizationConfig {
  type: string
  title?: string
  suggested?: boolean
}

interface ContextStats {
  query_tokens: number
  context_tokens: number
  total_tokens: number
  cache_hit: boolean
}

export default function QueryPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [selectedDataSource, setSelectedDataSource] = useState<DataSource | null>(null)
  const [expandedSql, setExpandedSql] = useState<Record<string, boolean>>({})
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const { accessToken } = useAuthStore()

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Add welcome message on mount
  useEffect(() => {
    const welcomeMessage: Message = {
      id: 'welcome',
      role: 'assistant',
      content:
        "👋 Hi! I'm **AgentMedha**, your AI-powered data assistant.\n\nI can help you discover and query your organization's data sources. Just tell me what you're looking for!",
      message_type: 'info',
      timestamp: new Date(),
    }
    setMessages([welcomeMessage])
  }, [])

  // Auto-focus input
  useEffect(() => {
    inputRef.current?.focus()
  }, [selectedDataSource])

  // Query mutation using new endpoint
  const queryMutation = useMutation({
    mutationFn: async (message: string) => {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/chat/query`,
        {
          message,
          session_id: sessionId,
          data_source_id: selectedDataSource?.id,
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        }
      )
      return response.data
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || queryMutation.isPending) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue('')

    try {
      const result = await queryMutation.mutateAsync(inputValue)

      // Update session ID if new
      if (result.session_id && !sessionId) {
        setSessionId(result.session_id)
      }

      // Create assistant message from result
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.content,
        message_type: result.message_type,
        dataSources: result.data_sources,
        sqlQuery: result.sql_query,
        sqlExplanation: result.sql_explanation,
        results: result.results,
        resultCount: result.result_count,
        visualization: result.visualization,
        suggestedActions: result.suggested_actions,
        contextStats: result.context_stats,
        errorCode: result.error_code,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ Sorry, I encountered an error: ${
          error.response?.data?.detail || error.message
        }`,
        message_type: 'error',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    }
  }

  const handleDataSourceSelect = (source: DataSource) => {
    setSelectedDataSource(source)

    const selectionMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: `Selected: ${source.display_name}`,
      timestamp: new Date(),
    }

    const responseMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: `Perfect! I've connected to **${source.display_name}**.\n\nNow you can ask me questions like:\n• "Show me the top 10 records"\n• "What's the total count?"\n• "Show me recent entries"`,
      message_type: 'info',
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, selectionMessage, responseMessage])
  }

  const handleSuggestedAction = (action: string) => {
    setInputValue(action)
    inputRef.current?.focus()
  }

  const toggleSqlExpanded = (messageId: string) => {
    setExpandedSql((prev) => ({
      ...prev,
      [messageId]: !prev[messageId],
    }))
  }

  const exportResults = (results: any[], format: 'json' | 'csv') => {
    if (!results || results.length === 0) return

    let content: string
    let filename: string
    let mimeType: string

    if (format === 'json') {
      content = JSON.stringify(results, null, 2)
      filename = `results_${Date.now()}.json`
      mimeType = 'application/json'
    } else {
      // CSV export
      const headers = Object.keys(results[0])
      const csvRows = [
        headers.join(','),
        ...results.map((row) =>
          headers.map((h) => JSON.stringify(row[h] ?? '')).join(',')
        ),
      ]
      content = csvRows.join('\n')
      filename = `results_${Date.now()}.csv`
      mimeType = 'text/csv'
    }

    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  const renderMessage = (message: Message) => {
    if (message.role === 'user') {
      return (
        <div className="flex justify-end">
          <div className="max-w-[70%]">
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-2xl rounded-tr-sm px-5 py-3 shadow-lg">
              <p className="text-sm leading-relaxed">{message.content}</p>
            </div>
            <p className="text-xs text-gray-400 mt-1.5 text-right">
              {message.timestamp.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
          </div>
        </div>
      )
    }

    // Assistant message
    return (
      <div className="flex justify-start">
        <div className="max-w-[85%]">
          <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm">
            {/* Message content */}
            <div className="text-sm leading-relaxed text-gray-700 space-y-2">
              {message.content.split('\n').map((line, idx) => {
                // Bold text
                if (line.includes('**')) {
                  const parts = line.split('**')
                  return (
                    <p key={idx}>
                      {parts.map((part, i) =>
                        i % 2 === 1 ? (
                          <strong key={i} className="font-semibold text-gray-900">
                            {part}
                          </strong>
                        ) : (
                          part
                        )
                      )}
                    </p>
                  )
                }
                // Bullet points
                if (line.startsWith('•') || line.startsWith('-')) {
                  return (
                    <p key={idx} className="flex items-start gap-2 ml-2">
                      <span className="text-blue-600 mt-0.5">•</span>
                      <span>{line.substring(1).trim()}</span>
                    </p>
                  )
                }
                // Regular text
                return line ? <p key={idx}>{line}</p> : <br key={idx} />
              })}
            </div>

            {/* SQL Query Display */}
            {message.sqlQuery && (
              <div className="mt-4 border border-gray-200 rounded-lg overflow-hidden">
                <button
                  onClick={() => toggleSqlExpanded(message.id)}
                  className="w-full flex items-center justify-between px-4 py-2 bg-gray-50 hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <Code className="h-4 w-4 text-gray-600" />
                    <span className="text-sm font-medium text-gray-700">
                      SQL Query
                    </span>
                  </div>
                  {expandedSql[message.id] ? (
                    <ChevronUp className="h-4 w-4 text-gray-600" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-600" />
                  )}
                </button>
                {expandedSql[message.id] && (
                  <div className="p-4 bg-gray-900 text-gray-100">
                    <pre className="text-xs font-mono overflow-x-auto">
                      {message.sqlQuery}
                    </pre>
                    {message.sqlExplanation && (
                      <p className="mt-3 text-xs text-gray-400 border-t border-gray-700 pt-3">
                        {message.sqlExplanation}
                      </p>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Results Table */}
            {message.results && message.results.length > 0 && (
              <div className="mt-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Database className="h-4 w-4 text-gray-600" />
                    <span className="text-sm font-medium text-gray-700">
                      Results ({message.resultCount || message.results.length})
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => exportResults(message.results!, 'csv')}
                      className="flex items-center gap-1 px-2 py-1 text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
                    >
                      <Download className="h-3 w-3" />
                      CSV
                    </button>
                    <button
                      onClick={() => exportResults(message.results!, 'json')}
                      className="flex items-center gap-1 px-2 py-1 text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
                    >
                      <Download className="h-3 w-3" />
                      JSON
                    </button>
                  </div>
                </div>

                {/* Table */}
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="overflow-x-auto max-h-96">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          {Object.keys(message.results[0]).map((key) => (
                            <th
                              key={key}
                              className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider whitespace-nowrap"
                            >
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {message.results.slice(0, 50).map((row, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            {Object.values(row).map((val: any, i) => (
                              <td
                                key={i}
                                className="px-4 py-2 text-sm text-gray-900 whitespace-nowrap"
                              >
                                {val === null || val === undefined
                                  ? '-'
                                  : String(val)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {message.results.length > 50 && (
                    <div className="px-4 py-2 bg-gray-50 text-xs text-gray-600 text-center">
                      Showing first 50 of {message.resultCount || message.results.length}{' '}
                      results
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Visualization */}
            {message.visualization && message.results && message.results.length > 0 && (
              <div className="mt-4">
                <div className="flex items-center gap-2 mb-3">
                  <BarChart3 className="h-4 w-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">
                    Visualization
                  </span>
                  {message.visualization.suggested && (
                    <span className="text-xs text-gray-500">(suggested)</span>
                  )}
                </div>
                <DataVisualization
                  data={message.results}
                  type={message.visualization.type}
                  title={message.visualization.title}
                />
              </div>
            )}

            {/* Data Sources Grid (for discovery messages) */}
            {message.dataSources && message.dataSources.length > 0 && (
              <div className="mt-4 space-y-2">
                {message.dataSources.map((source) => (
                  <button
                    key={source.id}
                    onClick={() => handleDataSourceSelect(source)}
                    className="w-full text-left group relative overflow-hidden"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                    <div className="relative bg-white m-[1px] rounded-xl p-4 border border-gray-200 group-hover:border-transparent transition-all">
                      <div className="flex items-start gap-4">
                        <div className="mt-1 p-2.5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg group-hover:from-blue-100 group-hover:to-indigo-100 transition-colors">
                          <Database className="h-5 w-5 text-blue-600" />
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex-1">
                              <h4 className="font-semibold text-gray-900 text-base mb-1 group-hover:text-blue-600 transition-colors">
                                {source.display_name}
                              </h4>
                              {source.description && (
                                <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                                  {source.description}
                                </p>
                              )}
                            </div>
                            <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all flex-shrink-0" />
                          </div>

                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-100 text-gray-700 rounded-md text-xs font-medium">
                              <Zap className="h-3 w-3" />
                              {source.database_type}
                            </span>
                            {source.keywords?.slice(0, 3).map((keyword, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-md text-xs font-medium"
                              >
                                {keyword}
                              </span>
                            ))}
                            {source.connection_status === 'healthy' && (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-50 text-green-700 rounded-md text-xs font-medium">
                                <CheckCircle2 className="h-3 w-3" />
                                Ready
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Suggested Actions */}
            {message.suggestedActions && message.suggestedActions.length > 0 && (
              <div className="mt-4">
                <p className="text-xs text-gray-500 mb-2">💡 Suggested follow-ups:</p>
                <div className="flex flex-wrap gap-2">
                  {message.suggestedActions.map((action, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSuggestedAction(action)}
                      className="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-xs font-medium transition-colors"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Context Stats (for debugging) */}
            {message.contextStats && (
              <div className="mt-4 pt-3 border-t border-gray-100">
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>
                    Tokens: {message.contextStats.context_tokens}
                  </span>
                  {message.contextStats.cache_hit && (
                    <span className="inline-flex items-center gap-1 text-green-600">
                      <CheckCircle2 className="h-3 w-3" />
                      Cached
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
          <p className="text-xs text-gray-400 mt-1.5">
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gradient-to-br from-gray-50 via-white to-blue-50">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header with selected data source */}
        {selectedDataSource && (
          <div className="bg-white border-b border-gray-200 px-6 py-3">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
                <Database className="h-4 w-4 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="text-xs text-gray-500 font-medium">Connected to</p>
                <p className="text-sm font-semibold text-gray-900">
                  {selectedDataSource.display_name}
                </p>
              </div>
              {sessionId && (
                <span className="text-xs text-gray-500">
                  Session: {sessionId}
                </span>
              )}
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-green-50 text-green-700 rounded-full text-xs font-medium">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                Active
              </span>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-8">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message) => (
              <div key={message.id}>{renderMessage(message)}</div>
            ))}

            {queryMutation.isPending && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm">
                  <div className="flex items-center gap-3">
                    <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
                    <span className="text-sm text-gray-600">
                      Processing your query...
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 px-6 py-6">
          <div className="max-w-4xl mx-auto">
            <form onSubmit={handleSubmit} className="relative">
              <div className="relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={
                    selectedDataSource
                      ? 'Ask a question about your data...'
                      : 'What data are you looking for?'
                  }
                  className="w-full pl-6 pr-14 py-4 bg-gray-50 border border-gray-200 rounded-2xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-sm"
                  disabled={queryMutation.isPending}
                />
                <button
                  type="submit"
                  disabled={queryMutation.isPending || !inputValue.trim()}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2.5 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/20"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </form>

            {/* Suggestions */}
            {!selectedDataSource && (
              <div className="mt-3 flex items-center gap-2 overflow-x-auto pb-2">
                <span className="text-xs text-gray-500 font-medium whitespace-nowrap">
                  Try:
                </span>
                {[
                  'Show me sales data',
                  'Customer information',
                  'Financial reports',
                ].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputValue(suggestion)}
                    className="flex-shrink-0 px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-xs text-gray-600 hover:border-blue-300 hover:text-blue-600 hover:bg-blue-50 transition-all"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Enhanced Sidebar */}
      <div className="hidden xl:block w-80 bg-white border-l border-gray-200 overflow-y-auto">
        <div className="p-6 space-y-6">
          {/* Header */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="h-5 w-5 text-blue-600" />
              <h2 className="font-bold text-gray-900">AgentMedha</h2>
            </div>
            <p className="text-sm text-gray-600">
              Your AI-powered data assistant
            </p>
          </div>

          {/* How to Use */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <span className="text-blue-600">💡</span>
              How to Use
            </h3>
            <ol className="space-y-2 text-sm text-gray-700">
              {[
                'Ask about the data you need',
                'Select a data source',
                'Ask your question',
                'Get instant results!',
              ].map((step, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-5 h-5 bg-blue-600 text-white rounded-full text-xs flex items-center justify-center font-medium">
                    {idx + 1}
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>

          {/* Example Queries */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <span>📊</span>
              Example Queries
            </h3>
            <div className="space-y-2">
              {[
                { q: 'Show me total revenue', icon: '💰' },
                { q: 'Top 10 customers', icon: '👥' },
                { q: 'Sales by region', icon: '📈' },
                { q: 'Recent orders', icon: '📦' },
              ].map((example, idx) => (
                <button
                  key={idx}
                  onClick={() => setInputValue(example.q)}
                  className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{example.icon}</span>
                    <span className="text-sm text-gray-700 group-hover:text-gray-900">
                      "{example.q}"
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Session Info */}
          {sessionId && (
            <div className="pt-4 border-t border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span>🔍</span>
                Current Session
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Session ID</span>
                  <span className="font-medium text-gray-900">{sessionId}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Messages</span>
                  <span className="font-medium text-gray-900">
                    {messages.length - 1}
                  </span>
                </div>
                {selectedDataSource && (
                  <div className="flex items-center gap-2 mt-3 p-2 bg-green-50 rounded-lg">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span className="text-xs text-green-700 font-medium">
                      Data source connected
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
