import React, { useState, useRef, useEffect } from 'react';
import {
    X, Minimize2, Send, Sparkles, Wand2, Hash, TrendingUp,
    Calendar, Image, Video, MessageCircle, Zap, Bot, User,
    Copy, ThumbsUp, ThumbsDown, RefreshCw
} from 'lucide-react';

// Quick action suggestions
const QUICK_ACTIONS = [
    { id: 'ideas', icon: Wand2, label: 'Generate post ideas', prompt: 'Give me 5 creative post ideas for today' },
    { id: 'hashtags', icon: Hash, label: 'Find trending hashtags', prompt: 'What are the trending hashtags in tech right now?' },
    { id: 'timing', icon: Calendar, label: 'Best posting times', prompt: 'When is the best time to post on Twitter for maximum engagement?' },
    { id: 'viral', icon: TrendingUp, label: 'Viral content tips', prompt: 'What makes content go viral on social media?' },
];

// Sample AI responses for demo
const AI_RESPONSES = {
    'Generate post ideas': `Here are 5 creative post ideas for today:

1. **Behind the Scenes** 📸
   Share a peek into your workspace or creative process

2. **Quick Tip Tuesday** 💡
   "Did you know? [share an industry insight]"

3. **Poll Your Audience** 📊
   Ask a thought-provoking question related to your niche

4. **Celebrate a Win** 🎉
   Share a recent achievement or milestone

5. **Share a Resource** 📚
   Recommend a tool, book, or article that helped you

Would you like me to expand on any of these ideas?`,
    
    'default': `I'm Aria, your AI social media assistant! I can help you:

• Generate engaging content ideas
• Find trending hashtags
• Optimize posting times
• Create compelling captions
• Analyze what works best

What would you like to work on?`
};

const AriaAssistant = ({ isOpen, onClose, selectedPlatforms }) => {
    const [messages, setMessages] = useState([
        {
            id: 'welcome',
            role: 'assistant',
            content: "Hi! I'm Aria, your AI social media assistant. 🌟\n\nI can help you create engaging content, find trending topics, and optimize your social media strategy.\n\nWhat would you like to work on today?",
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
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

    // Handle send message
    const handleSend = async () => {
        if (!input.trim() || isTyping) return;

        const userMessage = {
            id: `user_${Date.now()}`,
            role: 'user',
            content: input.trim(),
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsTyping(true);

        // Simulate AI thinking
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Generate AI response (would call actual API)
        const aiResponse = {
            id: `assistant_${Date.now()}`,
            role: 'assistant',
            content: input.toLowerCase().includes('idea') 
                ? AI_RESPONSES['Generate post ideas']
                : `Great question! Let me help you with that.\n\nBased on your request about "${input.slice(0, 50)}...", here are my suggestions:\n\n1. Consider your audience's pain points\n2. Use storytelling to connect\n3. Include a clear call-to-action\n4. Add relevant visuals\n\nWould you like me to elaborate on any of these points?`,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, aiResponse]);
        setIsTyping(false);
    };

    // Handle quick action
    const handleQuickAction = (action) => {
        setInput(action.prompt);
        setTimeout(() => handleSend(), 100);
    };

    // Handle key press
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Copy message content
    const copyMessage = (content) => {
        navigator.clipboard.writeText(content);
    };

    if (!isOpen) return null;

    if (isMinimized) {
        return (
            <div
                onClick={() => setIsMinimized(false)}
                style={{
                    position: 'fixed',
                    bottom: '20px',
                    right: '20px',
                    padding: '12px 20px',
                    background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                    borderRadius: '50px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    cursor: 'pointer',
                    boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)',
                    zIndex: 1000,
                    color: 'white',
                    fontWeight: '600',
                }}
            >
                <Sparkles size={18} />
                <span>Aria AI</span>
            </div>
        );
    }

    return (
        <div style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            width: '400px',
            height: '560px',
            background: 'linear-gradient(145deg, rgba(15, 20, 30, 0.98), rgba(10, 15, 25, 0.98))',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            borderRadius: '16px',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5), 0 0 30px rgba(139, 92, 246, 0.15)',
            zIndex: 1000,
            animation: 'slideUp 0.3s ease',
        }}>
            {/* Header */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '16px 20px',
                borderBottom: '1px solid rgba(139, 92, 246, 0.2)',
                background: 'rgba(139, 92, 246, 0.1)',
                borderRadius: '16px 16px 0 0',
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                        width: '40px',
                        height: '40px',
                        background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                    }}>
                        <Sparkles size={20} />
                    </div>
                    <div>
                        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600', color: 'white' }}>
                            Aria
                        </h3>
                        <span style={{ fontSize: '12px', color: 'var(--social-text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></span>
                            Social Media AI
                        </span>
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                        onClick={() => setIsMinimized(true)}
                        style={{
                            width: '32px',
                            height: '32px',
                            border: 'none',
                            background: 'rgba(255, 255, 255, 0.1)',
                            borderRadius: '8px',
                            color: 'var(--social-text-secondary)',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <Minimize2 size={16} />
                    </button>
                    <button
                        onClick={onClose}
                        style={{
                            width: '32px',
                            height: '32px',
                            border: 'none',
                            background: 'rgba(255, 255, 255, 0.1)',
                            borderRadius: '8px',
                            color: 'var(--social-text-secondary)',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <X size={16} />
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div style={{
                flex: 1,
                overflowY: 'auto',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
            }}>
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        style={{
                            display: 'flex',
                            gap: '10px',
                            maxWidth: '90%',
                            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                            flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                        }}
                    >
                        <div style={{
                            width: '28px',
                            height: '28px',
                            borderRadius: '8px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0,
                            background: msg.role === 'assistant' 
                                ? 'linear-gradient(135deg, #8b5cf6, #6366f1)'
                                : 'rgba(0, 217, 255, 0.2)',
                            color: msg.role === 'assistant' ? 'white' : 'var(--email-accent)',
                        }}>
                            {msg.role === 'assistant' ? <Bot size={14} /> : <User size={14} />}
                        </div>
                        <div>
                            <div style={{
                                background: msg.role === 'user' 
                                    ? 'rgba(0, 217, 255, 0.1)' 
                                    : 'rgba(255, 255, 255, 0.05)',
                                border: msg.role === 'user'
                                    ? '1px solid rgba(0, 217, 255, 0.2)'
                                    : '1px solid rgba(255, 255, 255, 0.08)',
                                padding: '12px 14px',
                                borderRadius: '12px',
                            }}>
                                <div style={{
                                    fontSize: '14px',
                                    lineHeight: '1.5',
                                    color: 'var(--social-text-primary)',
                                    whiteSpace: 'pre-wrap',
                                }}>
                                    {msg.content}
                                </div>
                            </div>
                            {msg.role === 'assistant' && (
                                <div style={{
                                    display: 'flex',
                                    gap: '8px',
                                    marginTop: '8px',
                                }}>
                                    <button
                                        onClick={() => copyMessage(msg.content)}
                                        style={{
                                            background: 'none',
                                            border: 'none',
                                            color: 'var(--social-text-muted)',
                                            cursor: 'pointer',
                                            padding: '4px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '4px',
                                            fontSize: '11px',
                                        }}
                                    >
                                        <Copy size={12} /> Copy
                                    </button>
                                    <button style={{
                                        background: 'none',
                                        border: 'none',
                                        color: 'var(--social-text-muted)',
                                        cursor: 'pointer',
                                        padding: '4px',
                                    }}>
                                        <ThumbsUp size={12} />
                                    </button>
                                    <button style={{
                                        background: 'none',
                                        border: 'none',
                                        color: 'var(--social-text-muted)',
                                        cursor: 'pointer',
                                        padding: '4px',
                                    }}>
                                        <ThumbsDown size={12} />
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {isTyping && (
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                        <div style={{
                            width: '28px',
                            height: '28px',
                            borderRadius: '8px',
                            background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                        }}>
                            <Bot size={14} />
                        </div>
                        <div style={{
                            background: 'rgba(255, 255, 255, 0.05)',
                            padding: '12px 14px',
                            borderRadius: '12px',
                            display: 'flex',
                            gap: '4px',
                        }}>
                            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#8b5cf6', animation: 'pulse 1s infinite' }}></span>
                            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#8b5cf6', animation: 'pulse 1s infinite 0.2s' }}></span>
                            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#8b5cf6', animation: 'pulse 1s infinite 0.4s' }}></span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            {messages.length <= 2 && (
                <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '8px',
                    padding: '12px 16px',
                    borderTop: '1px solid rgba(255, 255, 255, 0.08)',
                }}>
                    {QUICK_ACTIONS.map((action) => (
                        <button
                            key={action.id}
                            onClick={() => handleQuickAction(action)}
                            style={{
                                padding: '6px 12px',
                                background: 'rgba(139, 92, 246, 0.15)',
                                border: '1px solid rgba(139, 92, 246, 0.3)',
                                borderRadius: '20px',
                                color: '#a78bfa',
                                fontSize: '12px',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                            }}
                        >
                            <action.icon size={12} />
                            {action.label}
                        </button>
                    ))}
                </div>
            )}

            {/* Input */}
            <div style={{
                display: 'flex',
                gap: '10px',
                padding: '16px',
                borderTop: '1px solid rgba(255, 255, 255, 0.08)',
                background: 'rgba(0, 0, 0, 0.2)',
                borderRadius: '0 0 16px 16px',
            }}>
                <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask Aria anything about social media..."
                    style={{
                        flex: 1,
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        borderRadius: '12px',
                        padding: '12px 14px',
                        color: 'white',
                        fontSize: '14px',
                        resize: 'none',
                        outline: 'none',
                        minHeight: '20px',
                        maxHeight: '100px',
                        fontFamily: 'inherit',
                    }}
                    rows={1}
                    disabled={isTyping}
                />
                <button
                    onClick={handleSend}
                    disabled={!input.trim() || isTyping}
                    style={{
                        width: '44px',
                        height: '44px',
                        background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                        border: 'none',
                        borderRadius: '12px',
                        color: 'white',
                        cursor: input.trim() && !isTyping ? 'pointer' : 'not-allowed',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        opacity: input.trim() && !isTyping ? 1 : 0.5,
                    }}
                >
                    <Send size={18} />
                </button>
            </div>
        </div>
    );
};

export default AriaAssistant;

