import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    ArrowLeft, Share2, Home, PenTool, Calendar, BarChart3, Settings,
    Image, Video, Sparkles, Send, Clock, ChevronDown, Plus, RefreshCw,
    Twitter, Linkedin, Youtube, Instagram, Facebook, MessageCircle,
    Heart, Repeat2, Eye, TrendingUp, Zap, Wand2, FileText, Hash,
    Users, Bell, Search, MoreHorizontal, Check, X, Upload, Play
} from 'lucide-react';
import ContentStudio from './ContentStudio';
import MediaLab from './MediaLab';
import CalendarView from './CalendarView';
import AnalyticsView from './AnalyticsView';
import AriaAssistant from './AriaAssistant';
import './SocialManager.css';

// Platform configurations
const PLATFORMS = {
    twitter: { name: 'Twitter / X', icon: Twitter, color: '#1DA1F2', charLimit: 280 },
    linkedin: { name: 'LinkedIn', icon: Linkedin, color: '#0A66C2', charLimit: 3000 },
    youtube: { name: 'YouTube', icon: Youtube, color: '#FF0000', charLimit: null },
    instagram: { name: 'Instagram', icon: Instagram, color: '#E1306C', charLimit: 2200 },
    facebook: { name: 'Facebook', icon: Facebook, color: '#1877F2', charLimit: 63206 },
};

// Mock connected accounts
const CONNECTED_ACCOUNTS = [
    { id: '1', platform: 'twitter', name: 'Aravind Gillella', handle: '@aravindg', avatar: null, connected: true },
    { id: '2', platform: 'linkedin', name: 'Aravind Gillella', handle: 'aravind-gillella', avatar: null, connected: true },
    { id: '3', platform: 'youtube', name: 'Aravind Tech', handle: '@aravindtech', avatar: null, connected: true },
    { id: '4', platform: 'instagram', name: 'aravind.gillella', handle: '@aravind.gillella', avatar: null, connected: false },
];

const SocialManagerView = () => {
    const navigate = useNavigate();
    
    // State
    const [activeView, setActiveView] = useState('studio'); // studio, calendar, analytics, settings
    const [selectedPlatforms, setSelectedPlatforms] = useState(['twitter']);
    const [accounts, setAccounts] = useState(CONNECTED_ACCOUNTS);
    const [showAria, setShowAria] = useState(false);
    const [drafts, setDrafts] = useState([]);
    const [scheduled, setScheduled] = useState([]);

    // Navigation items
    const navItems = [
        { id: 'studio', icon: PenTool, label: 'Content Studio', badge: null },
        { id: 'calendar', icon: Calendar, label: 'Calendar', badge: scheduled.length || null },
        { id: 'analytics', icon: BarChart3, label: 'Analytics', badge: null },
        { id: 'drafts', icon: FileText, label: 'Drafts', badge: drafts.length || null },
        { id: 'settings', icon: Settings, label: 'Settings', badge: null },
    ];

    // Platform icon component
    const PlatformIcon = ({ platform, size = 16 }) => {
        const config = PLATFORMS[platform];
        if (!config) return null;
        const Icon = config.icon;
        return <Icon size={size} style={{ color: config.color }} />;
    };

    // Toggle platform selection
    const togglePlatform = (platform) => {
        setSelectedPlatforms(prev => 
            prev.includes(platform) 
                ? prev.filter(p => p !== platform)
                : [...prev, platform]
        );
    };

    // Render main content based on active view
    const renderContent = () => {
        switch (activeView) {
            case 'studio':
                return (
                    <ContentStudio 
                        selectedPlatforms={selectedPlatforms}
                        accounts={accounts}
                        onTogglePlatform={togglePlatform}
                        onShowAria={() => setShowAria(true)}
                    />
                );
            case 'calendar':
                return <CalendarView scheduled={scheduled} />;
            case 'analytics':
                return <AnalyticsView accounts={accounts} />;
            case 'drafts':
                return (
                    <div className="drafts-view">
                        <h2>Drafts</h2>
                        {drafts.length === 0 ? (
                            <p>No drafts yet. Start creating content in the studio!</p>
                        ) : (
                            drafts.map(draft => (
                                <div key={draft.id} className="draft-card">
                                    {draft.content}
                                </div>
                            ))
                        )}
                    </div>
                );
            default:
                return <ContentStudio selectedPlatforms={selectedPlatforms} accounts={accounts} />;
        }
    };

    return (
        <div className="social-manager">
            {/* Top Bar */}
            <header className="social-topbar">
                <div className="social-topbar-left">
                    <button className="social-back-btn" onClick={() => navigate('/')}>
                        <ArrowLeft size={16} />
                        <span>Back</span>
                    </button>
                    <div className="social-title">
                        <div className="social-title-icon">
                            <Share2 size={20} />
                        </div>
                        <div>
                            <h1>Social Hub</h1>
                        </div>
                        <span className="social-title-badge">AI-Powered</span>
                    </div>
                </div>

                {/* Platform Quick Tabs */}
                <div className="platform-tabs">
                    {Object.entries(PLATFORMS).map(([key, platform]) => {
                        const Icon = platform.icon;
                        const isActive = selectedPlatforms.includes(key);
                        return (
                            <button
                                key={key}
                                className={`platform-tab ${key} ${isActive ? 'active' : ''}`}
                                onClick={() => togglePlatform(key)}
                                title={platform.name}
                            >
                                <Icon size={16} />
                                <span>{platform.name.split(' ')[0]}</span>
                            </button>
                        );
                    })}
                </div>

                {/* Action buttons */}
                <div style={{ display: 'flex', gap: '10px' }}>
                    <button 
                        className="social-back-btn"
                        onClick={() => setShowAria(!showAria)}
                        style={{ background: showAria ? 'rgba(139, 92, 246, 0.2)' : undefined }}
                    >
                        <Sparkles size={16} />
                        <span>Aria AI</span>
                    </button>
                    <button className="social-back-btn">
                        <RefreshCw size={16} />
                    </button>
                    <button className="social-back-btn">
                        <Settings size={16} />
                    </button>
                </div>
            </header>

            {/* Main Body */}
            <div className="social-body">
                {/* Sidebar */}
                <aside className="social-sidebar">
                    {/* Navigation */}
                    <nav className="social-nav">
                        <div className="social-nav-section">
                            <div className="social-nav-title">Menu</div>
                            {navItems.map(item => (
                                <button
                                    key={item.id}
                                    className={`social-nav-item ${activeView === item.id ? 'active' : ''}`}
                                    onClick={() => setActiveView(item.id)}
                                >
                                    <item.icon size={18} />
                                    <span>{item.label}</span>
                                    {item.badge && (
                                        <span className="nav-badge">{item.badge}</span>
                                    )}
                                </button>
                            ))}
                        </div>

                        <div className="social-nav-section">
                            <div className="social-nav-title">Quick Actions</div>
                            <button className="social-nav-item" onClick={() => setActiveView('studio')}>
                                <Plus size={18} />
                                <span>New Post</span>
                            </button>
                            <button className="social-nav-item">
                                <Video size={18} />
                                <span>New Video</span>
                            </button>
                            <button className="social-nav-item">
                                <Image size={18} />
                                <span>AI Image</span>
                            </button>
                        </div>
                    </nav>

                    {/* Connected Accounts */}
                    <div className="account-cards">
                        <div className="social-nav-title" style={{ marginBottom: '12px' }}>
                            Connected Accounts
                        </div>
                        {accounts.map(account => (
                            <div 
                                key={account.id} 
                                className={`account-card ${selectedPlatforms.includes(account.platform) ? 'active' : ''}`}
                                onClick={() => togglePlatform(account.platform)}
                            >
                                <div className="account-avatar">
                                    {account.avatar ? (
                                        <img src={account.avatar} alt={account.name} />
                                    ) : (
                                        account.name.charAt(0)
                                    )}
                                    <div className="account-platform-icon">
                                        <PlatformIcon platform={account.platform} size={10} />
                                    </div>
                                </div>
                                <div className="account-info">
                                    <div className="account-name">{account.name}</div>
                                    <div className="account-handle">{account.handle}</div>
                                </div>
                                <div className={`account-status ${account.connected ? '' : 'disconnected'}`} />
                            </div>
                        ))}
                        <button className="social-nav-item" style={{ marginTop: '8px' }}>
                            <Plus size={18} />
                            <span>Add Account</span>
                        </button>
                    </div>
                </aside>

                {/* Content Area */}
                <main className="social-content">
                    {renderContent()}
                </main>

                {/* Aria AI Assistant */}
                {showAria && (
                    <AriaAssistant 
                        isOpen={showAria}
                        onClose={() => setShowAria(false)}
                        selectedPlatforms={selectedPlatforms}
                    />
                )}
            </div>
        </div>
    );
};

export default SocialManagerView;

