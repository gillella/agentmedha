import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, User } from 'lucide-react';
import AgentDashboard from './AgentDashboard';

const ChatInterface = () => {
    const [messages, setMessages] = useState([
        { role: 'agent', content: 'Hello! I am agentMedha, your AI coordinator. I manage multiple specialized agents to help you with various tasks. How can I assist you today?' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg.content })
            });

            const data = await response.json();

            setMessages(prev => [...prev, { role: 'agent', content: data.response }]);
        } catch (error) {
            console.error("Error sending message:", error);
            setMessages(prev => [...prev, { role: 'agent', content: "Sorry, I encountered an error connecting to the server." }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="flex flex-col h-full overflow-hidden">
            {/* Chat Section - Top Half */}
            <div className="flex flex-col" style={{ height: '45vh', minHeight: '300px' }}>
                <div className="px-6 py-4 border-b border-white/10">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <Bot size={24} className="text-purple-400" />
                        agentMedha Coordinator
                    </h2>
                    <p className="text-sm text-gray-400 mt-1">Your central AI coordination hub</p>
                </div>

                <div className="chat-container flex-1 overflow-y-auto">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`message ${msg.role}`}>
                            <div className="flex gap-3">
                                <div className="mt-1">
                                    {msg.role === 'agent' ? <Bot size={20} /> : <User size={20} />}
                                </div>
                                <div className="markdown-content">
                                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                                </div>
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div className="message agent">
                            <div className="flex gap-2 items-center">
                                <Bot size={20} />
                                <span className="animate-pulse">Thinking...</span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="input-area">
                    <input
                        type="text"
                        className="chat-input"
                        placeholder="Ask agentMedha to coordinate tasks across agents..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyPress}
                        disabled={isLoading}
                    />
                    <button className="send-btn" onClick={sendMessage} disabled={isLoading}>
                        <Send size={20} />
                    </button>
                </div>
            </div>

            {/* Agent Dashboard Section - Bottom Half */}
            <div className="flex-1 overflow-y-auto px-6 py-6 border-t border-white/10">
                <AgentDashboard />
            </div>
        </div>
    );
};

export default ChatInterface;
