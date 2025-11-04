import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot, User, Sparkles, Database, Code, BarChart3, Table } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useSearchParams } from 'react-router-dom';
import DataVisualization from '../components/DataVisualization';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sql_query?: string;
  results?: any[];
  tables_used?: string[];
  visualization_suggestion?: string;
}

const QUICK_PROMPTS = [
  "Show me all users in the database",
  "How many rows are in each table?",
  "What tables are available in the database?",
  "Show me the latest 5 queries executed"
];

export default function SimpleChatPage() {
  const { accessToken } = useAuthStore();
  const [searchParams, setSearchParams] = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hi! I'm AgentMedha, your AI-powered data assistant. Ask me questions about your data, and I'll query the database for you. Try asking about users, tables, or any data insights you need!"
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const autoQuerySentRef = useRef(false); // Prevent double-sending

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);

    // Add user message
    const newMessages = [...messages, { role: 'user' as const, content: userMessage }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/query/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          question: userMessage,
          conversation_history: messages.slice(1).map(m => ({ role: m.role, content: m.content }))
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get response');
      }

      const data = await response.json();
      
      // Add assistant response with additional data
      setMessages([...newMessages, { 
        role: 'assistant', 
        content: data.answer,
        sql_query: data.sql_query,
        results: data.results,
        tables_used: data.tables_used,
        visualization_suggestion: data.visualization_suggestion
      }]);
    } catch (err) {
      console.error('Chat error:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');
      // Remove the user message if there was an error
      setMessages(messages);
    } finally {
      setLoading(false);
    }
  };

  // Handle query parameter from URL (e.g., from Data Catalog)
  useEffect(() => {
    const queryParam = searchParams.get('query');
    if (queryParam && !autoQuerySentRef.current && !loading) {
      autoQuerySentRef.current = true;
      // Clear the query param from URL
      setSearchParams({});
      // Set input and auto-send
      setInput(queryParam);
      
      // Auto-send the query after state updates
      setTimeout(async () => {
        if (!queryParam.trim()) return;

        const userMessage = queryParam.trim();
        setError(null);

        // Add user message
        const newMessages = [...messages, { role: 'user' as const, content: userMessage }];
        setMessages(newMessages);
        setLoading(true);

        try {
          const response = await fetch('http://localhost:8000/api/v1/query/query', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${accessToken}`,
            },
            body: JSON.stringify({
              question: userMessage,
              conversation_history: messages.slice(1).map(m => ({ role: m.role, content: m.content }))
            }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get response');
          }

          const data = await response.json();
          
          // Add assistant response with additional data
          setMessages([...newMessages, { 
            role: 'assistant', 
            content: data.answer,
            sql_query: data.sql_query,
            results: data.results,
            tables_used: data.tables_used
          }]);
          setInput(''); // Clear input after successful send
        } catch (err) {
          console.error('Chat error:', err);
          setError(err instanceof Error ? err.message : 'Failed to send message');
          // Remove the user message if there was an error
          setMessages(messages);
        } finally {
          setLoading(false);
        }
      }, 100);
    }
  }, [searchParams, setSearchParams, loading, accessToken, messages]);


  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleQuickPrompt = (prompt: string) => {
    setInput(prompt);
    textareaRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-[calc(100vh-128px)] bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-6 py-8 space-y-6">
        {/* Welcome Section - Only show when no user messages */}
        {messages.length === 1 && (
          <div className="max-w-4xl mx-auto mb-8">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl mb-4 shadow-lg">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to AgentMedha</h1>
              <p className="text-gray-600">Your AI-powered assistant for insights, answers, and solutions</p>
            </div>

            {/* Quick Prompts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {QUICK_PROMPTS.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickPrompt(prompt)}
                  className="text-left px-4 py-3 bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-md transition-all group"
                >
                  <div className="flex items-start space-x-2">
                    <Sparkles className="w-4 h-4 text-gray-400 group-hover:text-blue-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700 group-hover:text-gray-900">{prompt}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
            >
              <div
                className={`flex items-start space-x-3 max-w-[85%] ${
                  message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                <div
                  className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-md ${
                    message.role === 'user' 
                      ? 'bg-gradient-to-br from-blue-600 to-purple-600' 
                      : 'bg-gradient-to-br from-gray-700 to-gray-900'
                  }`}
                >
                  {message.role === 'user' ? (
                    <User className="w-5 h-5 text-white" />
                  ) : (
                    <Bot className="w-5 h-5 text-white" />
                  )}
                </div>
                <div className="flex-1">
                  <div
                    className={`px-5 py-3 rounded-2xl shadow-sm ${
                      message.role === 'user'
                        ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white'
                        : 'bg-white text-gray-900 border border-gray-200'
                    }`}
                  >
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                  </div>
                  
                  {/* Show SQL Query if present */}
                  {message.sql_query && message.role === 'assistant' && (
                    <div className="mt-3 bg-gray-900 text-gray-100 rounded-lg p-4 text-xs font-mono overflow-x-auto">
                      <div className="flex items-center space-x-2 mb-2">
                        <Code className="w-4 h-4 text-blue-400" />
                        <span className="text-blue-400 font-semibold">SQL Query</span>
                      </div>
                      <pre className="text-green-400">{message.sql_query}</pre>
                    </div>
                  )}
                  
                  {/* Show Data Visualization if present */}
                  {message.results && message.results.length > 0 && message.role === 'assistant' && (
                    <div className="mt-3">
                      <div className="bg-gray-50 px-4 py-2 rounded-t-lg border border-b-0 border-gray-200 flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Database className="w-4 h-4 text-blue-600" />
                          <span className="text-sm font-semibold text-gray-700">
                            Results ({message.results.length} rows)
                          </span>
                          {message.tables_used && message.tables_used.length > 0 && (
                            <span className="text-xs text-gray-500">
                              • Tables: {message.tables_used.join(', ')}
                            </span>
                          )}
                        </div>
                        {message.visualization_suggestion && message.visualization_suggestion !== 'table' && (
                          <div className="flex items-center space-x-1">
                            <BarChart3 className="w-4 h-4 text-purple-600" />
                            <span className="text-xs text-purple-600 font-medium">
                              {message.visualization_suggestion.replace('_', ' ')}
                            </span>
                          </div>
                        )}
                      </div>
                      <DataVisualization 
                        data={message.results.slice(0, 100)} 
                        visualizationType={message.visualization_suggestion || 'table'}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {loading && (
          <div className="max-w-4xl mx-auto">
            <div className="flex justify-start animate-fade-in">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center bg-gradient-to-br from-gray-700 to-gray-900 shadow-md">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="px-5 py-3 rounded-2xl bg-white border border-gray-200 shadow-sm">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                    <span className="text-sm text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="max-w-4xl mx-auto">
            <div className="flex justify-center">
              <div className="bg-red-50 border-2 border-red-200 text-red-800 px-5 py-4 rounded-xl max-w-lg shadow-sm">
                <p className="font-semibold mb-1">Error</p>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Section */}
      <div className="bg-white/80 backdrop-blur-sm border-t border-gray-200 px-6 py-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-3">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything... (Press Enter to send, Shift+Enter for new line)"
                className="w-full px-4 py-3 pr-12 border-2 border-gray-300 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 resize-none transition-all shadow-sm"
                rows={1}
                disabled={loading}
                style={{ maxHeight: '150px' }}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className="px-5 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl disabled:shadow-none flex items-center space-x-2"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
              <span className="font-medium">Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

