import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    ArrowLeft, Mail, Inbox, Send, FileText, Trash2, Star, Archive,
    Search, Filter, RefreshCw, Plus, Settings, ChevronDown, Check,
    Sparkles, Clock, AlertCircle, MoreHorizontal, Tag
} from 'lucide-react';
import EmailInbox from './EmailInbox';
import EmailComposer from './EmailComposer';
import EmailThread from './EmailThread';

// Mock Gmail accounts configuration
const GMAIL_ACCOUNTS = [
    { id: 'personal', email: 'user.personal@gmail.com', name: 'Personal', color: '#3b82f6', unread: 12 },
    { id: 'work', email: 'user.work@gmail.com', name: 'Work', color: '#10b981', unread: 5 },
    { id: 'business', email: 'user.business@gmail.com', name: 'Business', color: '#f59e0b', unread: 3 },
];

const FOLDERS = [
    { id: 'inbox', name: 'Inbox', icon: Inbox, count: 20 },
    { id: 'starred', name: 'Starred', icon: Star, count: 8 },
    { id: 'sent', name: 'Sent', icon: Send, count: 0 },
    { id: 'drafts', name: 'Drafts', icon: FileText, count: 2 },
    { id: 'archive', name: 'Archive', icon: Archive, count: 0 },
    { id: 'trash', name: 'Trash', icon: Trash2, count: 0 },
];

const LABELS = [
    { id: 'important', name: 'Important', color: '#ef4444' },
    { id: 'finance', name: 'Finance', color: '#f59e0b' },
    { id: 'travel', name: 'Travel', color: '#3b82f6' },
    { id: 'social', name: 'Social', color: '#8b5cf6' },
];

const EmailManagerView = () => {
    const navigate = useNavigate();
    const [selectedAccount, setSelectedAccount] = useState('all');
    const [selectedFolder, setSelectedFolder] = useState('inbox');
    const [selectedEmail, setSelectedEmail] = useState(null);
    const [isComposerOpen, setIsComposerOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [showAccountDropdown, setShowAccountDropdown] = useState(false);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        // Simulate refresh
        await new Promise(resolve => setTimeout(resolve, 1500));
        setIsRefreshing(false);
    };

    const totalUnread = GMAIL_ACCOUNTS.reduce((sum, acc) => sum + acc.unread, 0);

    return (
        <div className="email-manager">
            {/* Top Navigation Bar */}
            <div className="email-topbar">
                <div className="email-topbar-left">
                    <button 
                        onClick={() => navigate('/')} 
                        className="email-back-btn"
                        title="Back to Dashboard"
                    >
                        <ArrowLeft size={20} />
                    </button>
                    <div className="email-brand">
                        <div className="email-brand-icon">
                            <Mail size={24} />
                        </div>
                        <div className="email-brand-text">
                            <h1>Email Hub</h1>
                            <span className="email-brand-subtitle">Powered by Medha AI</span>
                        </div>
                    </div>
                </div>

                <div className="email-search-container">
                    <Search size={18} className="email-search-icon" />
                    <input
                        type="text"
                        placeholder="Search emails across all accounts..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="email-search-input"
                    />
                    <button className="email-search-filter">
                        <Filter size={16} />
                    </button>
                </div>

                <div className="email-topbar-right">
                    <button 
                        onClick={handleRefresh}
                        className={`email-icon-btn ${isRefreshing ? 'refreshing' : ''}`}
                        title="Refresh"
                    >
                        <RefreshCw size={20} />
                    </button>
                    <button className="email-icon-btn" title="Settings">
                        <Settings size={20} />
                    </button>
                </div>
            </div>

            <div className="email-main-container">
                {/* Left Sidebar */}
                <aside className="email-sidebar">
                    {/* Compose Button */}
                    <button 
                        className="email-compose-btn"
                        onClick={() => setIsComposerOpen(true)}
                    >
                        <Plus size={20} />
                        <span>Compose</span>
                    </button>

                    {/* Account Selector */}
                    <div className="email-accounts-section">
                        <div 
                            className="email-account-selector"
                            onClick={() => setShowAccountDropdown(!showAccountDropdown)}
                        >
                            <div className="email-account-current">
                                {selectedAccount === 'all' ? (
                                    <>
                                        <div className="email-account-avatars">
                                            {GMAIL_ACCOUNTS.map(acc => (
                                                <div 
                                                    key={acc.id}
                                                    className="email-account-mini-avatar"
                                                    style={{ background: acc.color }}
                                                >
                                                    {acc.name[0]}
                                                </div>
                                            ))}
                                        </div>
                                        <span className="email-account-name">All Accounts</span>
                                        <span className="email-unread-badge">{totalUnread}</span>
                                    </>
                                ) : (
                                    (() => {
                                        const acc = GMAIL_ACCOUNTS.find(a => a.id === selectedAccount);
                                        return (
                                            <>
                                                <div 
                                                    className="email-account-avatar"
                                                    style={{ background: acc.color }}
                                                >
                                                    {acc.name[0]}
                                                </div>
                                                <span className="email-account-name">{acc.name}</span>
                                                {acc.unread > 0 && (
                                                    <span className="email-unread-badge">{acc.unread}</span>
                                                )}
                                            </>
                                        );
                                    })()
                                )}
                            </div>
                            <ChevronDown size={16} className={`email-dropdown-arrow ${showAccountDropdown ? 'open' : ''}`} />
                        </div>

                        {showAccountDropdown && (
                            <div className="email-account-dropdown">
                                <button
                                    className={`email-account-option ${selectedAccount === 'all' ? 'active' : ''}`}
                                    onClick={() => { setSelectedAccount('all'); setShowAccountDropdown(false); }}
                                >
                                    <div className="email-account-avatars">
                                        {GMAIL_ACCOUNTS.map(acc => (
                                            <div 
                                                key={acc.id}
                                                className="email-account-mini-avatar"
                                                style={{ background: acc.color }}
                                            >
                                                {acc.name[0]}
                                            </div>
                                        ))}
                                    </div>
                                    <span>All Accounts</span>
                                    <span className="email-unread-count">{totalUnread}</span>
                                    {selectedAccount === 'all' && <Check size={16} className="email-check-icon" />}
                                </button>
                                
                                <div className="email-dropdown-divider" />
                                
                                {GMAIL_ACCOUNTS.map(acc => (
                                    <button
                                        key={acc.id}
                                        className={`email-account-option ${selectedAccount === acc.id ? 'active' : ''}`}
                                        onClick={() => { setSelectedAccount(acc.id); setShowAccountDropdown(false); }}
                                    >
                                        <div 
                                            className="email-account-avatar"
                                            style={{ background: acc.color }}
                                        >
                                            {acc.name[0]}
                                        </div>
                                        <div className="email-account-details">
                                            <span className="email-account-label">{acc.name}</span>
                                            <span className="email-account-email">{acc.email}</span>
                                        </div>
                                        {acc.unread > 0 && (
                                            <span className="email-unread-count">{acc.unread}</span>
                                        )}
                                        {selectedAccount === acc.id && <Check size={16} className="email-check-icon" />}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Folders */}
                    <nav className="email-folders">
                        {FOLDERS.map(folder => {
                            const Icon = folder.icon;
                            return (
                                <button
                                    key={folder.id}
                                    className={`email-folder-item ${selectedFolder === folder.id ? 'active' : ''}`}
                                    onClick={() => setSelectedFolder(folder.id)}
                                >
                                    <Icon size={18} />
                                    <span>{folder.name}</span>
                                    {folder.count > 0 && (
                                        <span className="email-folder-count">{folder.count}</span>
                                    )}
                                </button>
                            );
                        })}
                    </nav>

                    {/* Labels */}
                    <div className="email-labels-section">
                        <div className="email-labels-header">
                            <span>Labels</span>
                            <button className="email-labels-add">
                                <Plus size={14} />
                            </button>
                        </div>
                        <div className="email-labels-list">
                            {LABELS.map(label => (
                                <button key={label.id} className="email-label-item">
                                    <div 
                                        className="email-label-dot"
                                        style={{ background: label.color }}
                                    />
                                    <span>{label.name}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* AI Assistant Card */}
                    <div className="email-ai-card">
                        <div className="email-ai-header">
                            <Sparkles size={18} />
                            <span>Medha AI</span>
                        </div>
                        <p className="email-ai-description">
                            Let AI help you manage, analyze, and respond to emails intelligently.
                        </p>
                        <div className="email-ai-actions">
                            <button className="email-ai-btn">
                                <Sparkles size={14} />
                                Summarize Unread
                            </button>
                            <button className="email-ai-btn">
                                <AlertCircle size={14} />
                                Find Important
                            </button>
                        </div>
                    </div>
                </aside>

                {/* Main Content Area */}
                <main className="email-content">
                    {selectedEmail ? (
                        <EmailThread 
                            email={selectedEmail} 
                            onBack={() => setSelectedEmail(null)}
                            onReply={() => setIsComposerOpen(true)}
                        />
                    ) : (
                        <EmailInbox 
                            selectedAccount={selectedAccount}
                            selectedFolder={selectedFolder}
                            searchQuery={searchQuery}
                            accounts={GMAIL_ACCOUNTS}
                            onEmailSelect={setSelectedEmail}
                        />
                    )}
                </main>
            </div>

            {/* Compose Modal */}
            {isComposerOpen && (
                <EmailComposer 
                    accounts={GMAIL_ACCOUNTS}
                    selectedAccount={selectedAccount}
                    replyTo={selectedEmail}
                    onClose={() => setIsComposerOpen(false)}
                />
            )}
        </div>
    );
};

export default EmailManagerView;

