import React, { useState, useRef, useEffect } from 'react';
import {
    MessageCircle, Send, X, Minimize2, Maximize2, Sparkles,
    Brain, Zap, RefreshCw, ChevronDown, User, Bot
} from 'lucide-react';
import { mayaApi } from '../../services/mayaApi';

/**
 * Maya AI Assistant Chat Panel
 * A floating chat interface for interacting with Maya
 */
const MayaAssistant = ({ 
    isOpen, 
    onClose, 
    onMinimize,
    isMinimized = false,
    emailContext = null,
    onDraftGenerated = null
}) => {
    const [messages, setMessages] = useState([
        {
            id: 'welcome',
            role: 'assistant',
            content: "Hi! I'm Maya, your intelligent email assistant. 🌟\n\nI can help you:\n• Triage your inbox by priority\n• Draft responses\n• Summarize emails\n• Learn your preferences\n\nWhat would you like to do?",
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId] = useState(() => `session_${Date.now()}`);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Focus input when opened
    useEffect(() => {
        if (isOpen && !isMinimized) {
            inputRef.current?.focus();
        }
    }, [isOpen, isMinimized]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage = {
            id: `user_${Date.now()}`,
            role: 'user',
            content: input.trim(),
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await mayaApi.chat(
                userMessage.content,
                sessionId,
                emailContext
            );

            const assistantMessage = {
                id: `assistant_${Date.now()}`,
                role: 'assistant',
                content: response.response,
                timestamp: new Date()
            };

            setMessages(prev => [...prev, assistantMessage]);

            // Check if response contains a draft
            if (response.response.includes('Draft Response:') && onDraftGenerated) {
                const draftMatch = response.response.match(/Draft Response:\n\n([\s\S]*?)(?:\n\n\*|$)/);
                if (draftMatch) {
                    onDraftGenerated(draftMatch[1]);
                }
            }
        } catch (error) {
            const errorMessage = {
                id: `error_${Date.now()}`,
                role: 'assistant',
                content: `Sorry, I encountered an error: ${error.message}. Please try again.`,
                timestamp: new Date(),
                isError: true
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const quickActions = [
        { label: "What's urgent?", action: "What's urgent in my inbox?" },
        { label: "Summarize unread", action: "Summarize my unread emails" },
        { label: "Triage inbox", action: "Triage my inbox by priority" },
        { label: "Daily digest", action: "Give me my daily email digest" },
    ];

    const handleQuickAction = (action) => {
        setInput(action);
        setTimeout(() => handleSend(), 100);
    };

    if (!isOpen) return null;

    if (isMinimized) {
        return (
            <div 
                className="maya-assistant-minimized"
                onClick={onMinimize}
            >
                <div className="maya-mini-avatar">
                    <Sparkles size={20} />
                </div>
                <span>Maya</span>
                <div className="maya-mini-badge">AI</div>
            </div>
        );
    }

    return (
        <div className="maya-assistant-panel">
            {/* Header */}
            <div className="maya-header">
                <div className="maya-header-left">
                    <div className="maya-avatar">
                        <Sparkles size={20} />
                    </div>
                    <div className="maya-header-info">
                        <h3>Maya</h3>
                        <span className="maya-status">
                            <span className="status-dot online"></span>
                            AI Email Assistant
                        </span>
                    </div>
                </div>
                <div className="maya-header-actions">
                    <button onClick={onMinimize} className="maya-btn-icon" title="Minimize">
                        <Minimize2 size={16} />
                    </button>
                    <button onClick={onClose} className="maya-btn-icon" title="Close">
                        <X size={16} />
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="maya-messages">
                {messages.map((msg) => (
                    <div 
                        key={msg.id} 
                        className={`maya-message ${msg.role} ${msg.isError ? 'error' : ''}`}
                    >
                        <div className="message-avatar">
                            {msg.role === 'assistant' ? (
                                <Bot size={16} />
                            ) : (
                                <User size={16} />
                            )}
                        </div>
                        <div className="message-content">
                            <div className="message-text">{msg.content}</div>
                            <div className="message-time">
                                {msg.timestamp.toLocaleTimeString([], { 
                                    hour: '2-digit', 
                                    minute: '2-digit' 
                                })}
                            </div>
                        </div>
                    </div>
                ))}
                
                {isLoading && (
                    <div className="maya-message assistant loading">
                        <div className="message-avatar">
                            <Bot size={16} />
                        </div>
                        <div className="message-content">
                            <div className="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                )}
                
                <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            {messages.length <= 2 && (
                <div className="maya-quick-actions">
                    {quickActions.map((action, idx) => (
                        <button 
                            key={idx}
                            className="quick-action-btn"
                            onClick={() => handleQuickAction(action.action)}
                        >
                            <Zap size={12} />
                            {action.label}
                        </button>
                    ))}
                </div>
            )}

            {/* Input */}
            <div className="maya-input-area">
                <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask Maya anything about your emails..."
                    rows={1}
                    disabled={isLoading}
                />
                <button 
                    className="maya-send-btn"
                    onClick={handleSend}
                    disabled={!input.trim() || isLoading}
                >
                    <Send size={18} />
                </button>
            </div>
        </div>
    );
};

export default MayaAssistant;

