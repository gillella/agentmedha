import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    ArrowLeft, Mail, Inbox, Send, FileText, Trash2, Star, Archive,
    Search, Filter, RefreshCw, Plus, Settings, ChevronDown, Check,
    Sparkles, Clock, AlertCircle, MoreHorizontal, Tag, Wifi, WifiOff
} from 'lucide-react';
import EmailInbox from './EmailInbox';
import EmailComposer from './EmailComposer';
import EmailThread from './EmailThread';
import { gmailApi } from '../../services/gmailApi';

// Account colors for visual distinction
const ACCOUNT_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'];

const FOLDERS = [
    { id: 'inbox', name: 'Inbox', icon: Inbox, query: 'in:inbox' },
    { id: 'starred', name: 'Starred', icon: Star, query: 'is:starred' },
    { id: 'sent', name: 'Sent', icon: Send, query: 'in:sent' },
    { id: 'drafts', name: 'Drafts', icon: FileText, query: 'in:drafts' },
    { id: 'archive', name: 'All Mail', icon: Archive, query: '' },
    { id: 'trash', name: 'Trash', icon: Trash2, query: 'in:trash' },
];

const EmailManagerView = () => {
    const navigate = useNavigate();
    
    // State
    const [accounts, setAccounts] = useState([]);
    const [selectedAccount, setSelectedAccount] = useState('all');
    const [selectedFolder, setSelectedFolder] = useState('inbox');
    const [emails, setEmails] = useState([]);
    const [selectedEmail, setSelectedEmail] = useState(null);
    const [emailThread, setEmailThread] = useState(null);
    const [isComposerOpen, setIsComposerOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [showAccountDropdown, setShowAccountDropdown] = useState(false);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState(null);
    const [labels, setLabels] = useState([]);

    // Load accounts on mount
    useEffect(() => {
        loadAccounts();
    }, []);

    // Load emails when account or folder changes
    useEffect(() => {
        if (accounts.length > 0) {
            loadEmails();
        }
    }, [selectedAccount, selectedFolder, accounts]);

    const loadAccounts = async () => {
        try {
            setIsLoading(true);
            const health = await gmailApi.healthCheck();
            setIsConnected(health.gmail_connected);
            
            if (health.gmail_connected) {
                const data = await gmailApi.listAccounts();
                const accountsWithColors = (data.accounts || []).map((acc, idx) => ({
                    ...acc,
                    color: ACCOUNT_COLORS[idx % ACCOUNT_COLORS.length],
                    name: acc.email.split('@')[0],
                    unread: 0, // Will be updated when loading emails
                }));
                setAccounts(accountsWithColors);
                
                // Load labels from first account
                if (accountsWithColors.length > 0) {
                    try {
                        const labelsData = await gmailApi.listLabels(accountsWithColors[0].id);
                        setLabels(labelsData.labels?.filter(l => l.type === 'user') || []);
                    } catch (e) {
                        console.warn('Could not load labels:', e);
                    }
                }
            }
            setError(null);
        } catch (err) {
            console.error('Failed to load accounts:', err);
            setError('Failed to connect to Gmail server');
            setIsConnected(false);
        } finally {
            setIsLoading(false);
        }
    };

    const loadEmails = async () => {
        try {
            setIsLoading(true);
            const folder = FOLDERS.find(f => f.id === selectedFolder);
            const query = folder?.query || '';
            const combinedQuery = searchQuery ? `${query} ${searchQuery}`.trim() : query;
            
            let allEmails = [];
            
            if (selectedAccount === 'all') {
                // Load from all accounts
                const results = await Promise.all(
                    accounts.map(async (acc) => {
                        try {
                            const data = await gmailApi.listMessages({
                                accountId: acc.id,
                                query: combinedQuery || 'in:inbox',
                                maxResults: 20,
                            });
                            return (data.messages || []).map(email => ({
                                ...email,
                                accountId: acc.id,
                                accountEmail: acc.email,
                                accountColor: acc.color,
                            }));
                        } catch (e) {
                            console.warn(`Failed to load from ${acc.email}:`, e);
                            return [];
                        }
                    })
                );
                allEmails = results.flat();
                // Sort by date (newest first)
                allEmails.sort((a, b) => new Date(b.date) - new Date(a.date));
            } else {
                // Load from selected account
                const acc = accounts.find(a => a.id === selectedAccount);
                if (acc) {
                    const data = await gmailApi.listMessages({
                        accountId: acc.id,
                        query: combinedQuery || 'in:inbox',
                        maxResults: 50,
                    });
                    allEmails = (data.messages || []).map(email => ({
                        ...email,
                        accountId: acc.id,
                        accountEmail: acc.email,
                        accountColor: acc.color,
                    }));
                }
            }
            
            setEmails(allEmails);
            setError(null);
        } catch (err) {
            console.error('Failed to load emails:', err);
            setError('Failed to load emails');
        } finally {
            setIsLoading(false);
        }
    };

    const handleRefresh = async () => {
        setIsRefreshing(true);
        await loadEmails();
        setIsRefreshing(false);
    };

    const handleSearch = useCallback((e) => {
        e.preventDefault();
        loadEmails();
    }, [searchQuery, selectedAccount, selectedFolder]);

    const handleEmailSelect = async (email) => {
        setSelectedEmail(email);
        
        // Load full thread
        try {
            const thread = await gmailApi.getThread(email.thread_id, email.accountId);
            setEmailThread(thread);
            
            // Mark as read
            if (email.is_unread) {
                await gmailApi.markAsRead(email.id, email.accountId);
                // Update local state
                setEmails(prev => prev.map(e => 
                    e.id === email.id ? { ...e, is_unread: false } : e
                ));
            }
        } catch (err) {
            console.error('Failed to load thread:', err);
        }
    };

    const handleArchive = async (email) => {
        try {
            await gmailApi.archiveMessage(email.id, email.accountId);
            setEmails(prev => prev.filter(e => e.id !== email.id));
            if (selectedEmail?.id === email.id) {
                setSelectedEmail(null);
                setEmailThread(null);
            }
        } catch (err) {
            console.error('Failed to archive:', err);
        }
    };

    const handleDelete = async (email) => {
        try {
            await gmailApi.trashMessage(email.id, email.accountId);
            setEmails(prev => prev.filter(e => e.id !== email.id));
            if (selectedEmail?.id === email.id) {
                setSelectedEmail(null);
                setEmailThread(null);
            }
        } catch (err) {
            console.error('Failed to delete:', err);
        }
    };

    const handleStar = async (email) => {
        try {
            const isStarred = email.labels?.includes('STARRED');
            if (isStarred) {
                await gmailApi.unstarMessage(email.id, email.accountId);
            } else {
                await gmailApi.starMessage(email.id, email.accountId);
            }
            // Update local state
            setEmails(prev => prev.map(e => 
                e.id === email.id 
                    ? { ...e, labels: isStarred 
                        ? e.labels.filter(l => l !== 'STARRED')
                        : [...(e.labels || []), 'STARRED']
                    } 
                    : e
            ));
        } catch (err) {
            console.error('Failed to star:', err);
        }
    };

    const totalUnread = emails.filter(e => e.is_unread).length;

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
                            <span className="email-brand-subtitle">
                                {isConnected ? (
                                    <><Wifi size={12} style={{ color: '#10b981' }} /> Connected</>
                                ) : (
                                    <><WifiOff size={12} style={{ color: '#ef4444' }} /> Disconnected</>
                                )}
                            </span>
                        </div>
                    </div>
                </div>

                <form className="email-search-container" onSubmit={handleSearch}>
                    <Search size={18} className="email-search-icon" />
                    <input
                        type="text"
                        placeholder="Search emails across all accounts..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="email-search-input"
                    />
                    <button type="submit" className="email-search-filter">
                        <Filter size={16} />
                    </button>
                </form>

                <div className="email-topbar-right">
                    <button 
                        onClick={handleRefresh}
                        className={`email-icon-btn ${isRefreshing ? 'refreshing' : ''}`}
                        title="Refresh"
                        disabled={isRefreshing}
                    >
                        <RefreshCw size={20} />
                    </button>
                    <button className="email-icon-btn" title="Settings">
                        <Settings size={20} />
                    </button>
                </div>
            </div>

            {error && (
                <div className="email-error-banner">
                    <AlertCircle size={16} />
                    <span>{error}</span>
                    <button onClick={loadAccounts}>Retry</button>
                </div>
            )}

            <div className="email-main-container">
                {/* Left Sidebar */}
                <aside className="email-sidebar">
                    {/* Compose Button */}
                    <button 
                        className="email-compose-btn"
                        onClick={() => setIsComposerOpen(true)}
                        disabled={accounts.length === 0}
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
                                            {accounts.map(acc => (
                                                <div 
                                                    key={acc.id}
                                                    className="email-account-mini-avatar"
                                                    style={{ background: acc.color }}
                                                >
                                                    {acc.name[0]?.toUpperCase()}
                                                </div>
                                            ))}
                                        </div>
                                        <span className="email-account-name">All Accounts</span>
                                        {totalUnread > 0 && (
                                            <span className="email-unread-badge">{totalUnread}</span>
                                        )}
                                    </>
                                ) : (
                                    (() => {
                                        const acc = accounts.find(a => a.id === selectedAccount);
                                        if (!acc) return null;
                                        return (
                                            <>
                                                <div 
                                                    className="email-account-avatar"
                                                    style={{ background: acc.color }}
                                                >
                                                    {acc.name[0]?.toUpperCase()}
                                                </div>
                                                <span className="email-account-name">{acc.name}</span>
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
                                        {accounts.map(acc => (
                                            <div 
                                                key={acc.id}
                                                className="email-account-mini-avatar"
                                                style={{ background: acc.color }}
                                            >
                                                {acc.name[0]?.toUpperCase()}
                                            </div>
                                        ))}
                                    </div>
                                    <span>All Accounts</span>
                                    {selectedAccount === 'all' && <Check size={16} className="email-check-icon" />}
                                </button>
                                
                                <div className="email-dropdown-divider" />
                                
                                {accounts.map(acc => (
                                    <button
                                        key={acc.id}
                                        className={`email-account-option ${selectedAccount === acc.id ? 'active' : ''}`}
                                        onClick={() => { setSelectedAccount(acc.id); setShowAccountDropdown(false); }}
                                    >
                                        <div 
                                            className="email-account-avatar"
                                            style={{ background: acc.color }}
                                        >
                                            {acc.name[0]?.toUpperCase()}
                                        </div>
                                        <div className="email-account-details">
                                            <span className="email-account-label">{acc.name}</span>
                                            <span className="email-account-email">{acc.email}</span>
                                        </div>
                                        <span className="email-account-count">
                                            {acc.messages_total?.toLocaleString()}
                                        </span>
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
                                </button>
                            );
                        })}
                    </nav>

                    {/* Labels */}
                    {labels.length > 0 && (
                        <div className="email-labels-section">
                            <div className="email-labels-header">
                                <span>Labels</span>
                                <button className="email-labels-add">
                                    <Plus size={14} />
                                </button>
                            </div>
                            <div className="email-labels-list">
                                {labels.slice(0, 5).map(label => (
                                    <button key={label.id} className="email-label-item">
                                        <div 
                                            className="email-label-dot"
                                            style={{ background: '#8b5cf6' }}
                                        />
                                        <span>{label.name}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

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
                            <button className="email-ai-btn" onClick={() => setSearchQuery('is:unread')}>
                                <Sparkles size={14} />
                                Show Unread
                            </button>
                            <button className="email-ai-btn" onClick={() => setSearchQuery('is:important')}>
                                <AlertCircle size={14} />
                                Find Important
                            </button>
                        </div>
                    </div>
                </aside>

                {/* Main Content Area */}
                <main className="email-content">
                    {selectedEmail && emailThread ? (
                        <EmailThread 
                            email={selectedEmail}
                            thread={emailThread}
                            onBack={() => { setSelectedEmail(null); setEmailThread(null); }}
                            onReply={() => setIsComposerOpen(true)}
                            onArchive={() => handleArchive(selectedEmail)}
                            onDelete={() => handleDelete(selectedEmail)}
                            onStar={() => handleStar(selectedEmail)}
                        />
                    ) : (
                        <EmailInbox 
                            emails={emails}
                            isLoading={isLoading}
                            selectedAccount={selectedAccount}
                            selectedFolder={selectedFolder}
                            searchQuery={searchQuery}
                            accounts={accounts}
                            onEmailSelect={handleEmailSelect}
                            onArchive={handleArchive}
                            onDelete={handleDelete}
                            onStar={handleStar}
                            onRefresh={handleRefresh}
                        />
                    )}
                </main>
            </div>

            {/* Compose Modal */}
            {isComposerOpen && (
                <EmailComposer 
                    accounts={accounts}
                    selectedAccount={selectedAccount === 'all' ? accounts[0]?.id : selectedAccount}
                    replyTo={selectedEmail}
                    thread={emailThread}
                    onClose={() => setIsComposerOpen(false)}
                    onSend={async (emailData, accountId) => {
                        await gmailApi.sendEmail(emailData, accountId);
                        setIsComposerOpen(false);
                        handleRefresh();
                    }}
                    onSaveDraft={async (draftData, accountId) => {
                        await gmailApi.createDraft(draftData, accountId);
                    }}
                />
            )}
        </div>
    );
};

export default EmailManagerView;
