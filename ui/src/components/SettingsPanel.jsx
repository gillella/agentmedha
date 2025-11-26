import React, { useState } from 'react';
import { Save, Layers, Puzzle } from 'lucide-react';

const SettingsPanel = () => {
    const [activeTab, setActiveTab] = useState('general');
    const [config, setConfig] = useState({
        model_name: 'gemini-1.5-pro',
        theme: 'dark',
        notifications: true
    });

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setConfig(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const saveConfig = async () => {
        try {
            alert("Configuration saved!");
        } catch (error) {
            console.error("Error saving config:", error);
        }
    };

    const tabs = [
        { id: 'general', label: 'General', icon: null },
        { id: 'llm-cortex', label: 'LLM Cortex', icon: Layers },
        { id: 'integrations', label: 'Integrations & MCP', icon: Puzzle }
    ];

    return (
        <div className="h-full overflow-y-auto" style={{ paddingBottom: '100px' }}>
            <div className="settings-container glass-panel">
                <div className="settings-header">
                    Settings
                </div>

                {/* Tabs */}
                <div className="flex gap-2 mb-6 border-b" style={{ borderColor: 'rgba(0, 217, 255, 0.2)' }}>
                    {tabs.map(tab => {
                        const Icon = tab.icon;
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`px-4 py-2 font-medium transition-all ${activeTab === tab.id
                                        ? 'border-b-2 text-white'
                                        : 'text-gray-400 hover:text-gray-300'
                                    }`}
                                style={{
                                    borderColor: activeTab === tab.id ? '#00d9ff' : 'transparent'
                                }}
                            >
                                <div className="flex items-center gap-2">
                                    {Icon && <Icon size={16} />}
                                    {tab.label}
                                </div>
                            </button>
                        );
                    })}
                </div>

                {/* General Tab */}
                {activeTab === 'general' && (
                    <div className="settings-section">
                        <h3 className="text-lg font-medium mb-4" style={{ color: '#00d9ff' }}>
                            General Settings
                        </h3>
                        <div className="form-group">
                            <label className="form-label">Primary LLM Model</label>
                            <select
                                name="model_name"
                                value={config.model_name}
                                onChange={handleChange}
                                className="form-select"
                            >
                                <option value="gemini-3-pro-preview">Gemini 3 Pro (Preview)</option>
                                <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                                <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                                <option value="gpt-4o">GPT-4o</option>
                                <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                                <option value="local-llama3">Local Llama 3 (Ollama)</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Theme</label>
                            <select
                                name="theme"
                                value={config.theme}
                                onChange={handleChange}
                                className="form-select"
                            >
                                <option value="dark">Dark (Teal)</option>
                                <option value="light">Light</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    name="notifications"
                                    checked={config.notifications}
                                    onChange={handleChange}
                                    className="w-4 h-4"
                                />
                                <span className="form-label mb-0">Enable Notifications</span>
                            </label>
                        </div>
                    </div>
                )}

                {/* LLM Cortex Tab */}
                {activeTab === 'llm-cortex' && (
                    <div className="settings-section">
                        <h3 className="text-lg font-medium mb-4" style={{ color: '#00d9ff' }}>
                            LLM Cortex Configuration
                        </h3>
                        <div className="form-group">
                            <label className="form-label">Google API Key</label>
                            <input
                                type="password"
                                name="google_api_key"
                                className="form-input"
                                placeholder="AIza..."
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">OpenAI API Key</label>
                            <input
                                type="password"
                                name="openai_api_key"
                                className="form-input"
                                placeholder="sk-..."
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Anthropic API Key</label>
                            <input
                                type="password"
                                name="anthropic_api_key"
                                className="form-input"
                                placeholder="sk-ant-..."
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Temperature</label>
                            <input
                                type="range"
                                min="0"
                                max="2"
                                step="0.1"
                                defaultValue="0.7"
                                className="w-full"
                            />
                            <span className="text-sm text-gray-400">0.7</span>
                        </div>
                    </div>
                )}

                {/* Integrations & MCP Tab */}
                {activeTab === 'integrations' && (
                    <div className="settings-section">
                        <h3 className="text-lg font-medium mb-4" style={{ color: '#00d9ff' }}>
                            Integrations & MCP Servers
                        </h3>
                        <div className="mb-4 p-4 rounded-lg" style={{
                            background: 'rgba(0, 217, 255, 0.1)',
                            border: '1px solid rgba(0, 217, 255, 0.3)'
                        }}>
                            <div className="flex items-center justify-between mb-2">
                                <span className="font-medium text-white">MCP Server Status</span>
                                <span className="text-sm px-2 py-1 rounded" style={{
                                    background: 'rgba(16, 185, 129, 0.2)',
                                    color: '#10b981'
                                }}>
                                    Connected
                                </span>
                            </div>
                            <div className="text-sm text-gray-400">
                                Latency: 45ms | Active Connections: 3
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Twitter API Key</label>
                            <input
                                type="password"
                                className="form-input"
                                placeholder="Enter Twitter API key..."
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">PETKIT API Key</label>
                            <input
                                type="password"
                                className="form-input"
                                placeholder="Enter PETKIT API key..."
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Smart Home Integration</label>
                            <select className="form-select">
                                <option>Home Assistant</option>
                                <option>Google Home</option>
                                <option>Apple HomeKit</option>
                            </select>
                        </div>
                    </div>
                )}

                <button className="save-btn flex items-center gap-2" onClick={saveConfig}>
                    <Save size={18} />
                    Save Changes
                </button>
            </div>
        </div>
    );
};

export default SettingsPanel;
