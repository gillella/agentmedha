import React, { useState } from 'react';
import {
    Star, Paperclip, Clock, MoreHorizontal, Archive, Trash2,
    CheckSquare, Square, ChevronDown, Sparkles, AlertTriangle,
    Tag, Reply, Forward, Mail, RefreshCw, Loader2
} from 'lucide-react';

// Helper to format date
const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
        return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    } else if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return date.toLocaleDateString('en-US', { weekday: 'short' });
    } else {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
};

// Helper to extract sender name from "Name <email>" format
const parseSender = (from) => {
    if (!from) return { name: 'Unknown', email: '', avatar: '?' };
    
    const match = from.match(/^(.+?)\s*<(.+?)>$/);
    if (match) {
        const name = match[1].replace(/"/g, '').trim();
        const email = match[2];
        const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        return { name, email, avatar: initials };
    }
    
    // Just email
    const name = from.split('@')[0];
    const initials = name.substring(0, 2).toUpperCase();
    return { name: from, email: from, avatar: initials };
};

// Priority badge colors
const PRIORITY_COLORS = {
    high: '#ef4444',
    normal: '#6b7280',
    low: '#10b981',
};

const EmailInbox = ({ 
    emails = [], 
    isLoading = false,
    selectedAccount, 
    selectedFolder, 
    searchQuery,
    accounts = [],
    onEmailSelect,
    onArchive,
    onDelete,
    onStar,
    onRefresh
}) => {
    const [selectedEmails, setSelectedEmails] = useState(new Set());
    const [sortBy, setSortBy] = useState('date');
    const [hoveredEmail, setHoveredEmail] = useState(null);

    const handleSelectAll = () => {
        if (selectedEmails.size === emails.length) {
            setSelectedEmails(new Set());
        } else {
            setSelectedEmails(new Set(emails.map(e => e.id)));
        }
    };

    const handleSelectEmail = (emailId, e) => {
        e.stopPropagation();
        const newSelected = new Set(selectedEmails);
        if (newSelected.has(emailId)) {
            newSelected.delete(emailId);
        } else {
            newSelected.add(emailId);
        }
        setSelectedEmails(newSelected);
    };

    const handleStarClick = (email, e) => {
        e.stopPropagation();
        onStar?.(email);
    };

    const getAccountColor = (email) => {
        if (email.accountColor) return email.accountColor;
        const acc = accounts.find(a => a.id === email.accountId || a.email === email.accountEmail);
        return acc?.color || '#6b7280';
    };

    const unreadCount = emails.filter(e => e.is_unread).length;

    return (
        <div className="email-inbox">
            {/* Toolbar */}
            <div className="email-inbox-toolbar">
                <div className="email-toolbar-left">
                    <button 
                        className="email-checkbox-btn"
                        onClick={handleSelectAll}
                    >
                        {selectedEmails.size === emails.length && emails.length > 0 ? (
                            <CheckSquare size={18} />
                        ) : (
                            <Square size={18} />
                        )}
                    </button>
                    
                    {selectedEmails.size > 0 ? (
                        <div className="email-bulk-actions">
                            <span className="email-selected-count">{selectedEmails.size} selected</span>
                            <button className="email-action-btn" title="Archive">
                                <Archive size={16} />
                            </button>
                            <button className="email-action-btn" title="Delete">
                                <Trash2 size={16} />
                            </button>
                            <button className="email-action-btn" title="Mark as read">
                                <Mail size={16} />
                            </button>
                        </div>
                    ) : (
                        <div className="email-view-info">
                            <span className="email-count">
                                {emails.length} emails
                                {unreadCount > 0 && ` (${unreadCount} unread)`}
                            </span>
                        </div>
                    )}
                </div>

                <div className="email-toolbar-right">
                    <button 
                        className="email-sort-btn"
                        onClick={() => setSortBy(sortBy === 'date' ? 'sender' : 'date')}
                    >
                        <span>Sort by {sortBy}</span>
                        <ChevronDown size={14} />
                    </button>
                    <button 
                        className="email-refresh-btn" 
                        onClick={onRefresh}
                        disabled={isLoading}
                    >
                        <RefreshCw size={16} className={isLoading ? 'spinning' : ''} />
                    </button>
                </div>
            </div>

            {/* Email List */}
            <div className="email-list">
                {isLoading && emails.length === 0 ? (
                    <div className="email-loading">
                        <Loader2 size={32} className="spinning" />
                        <span>Loading emails...</span>
                    </div>
                ) : emails.length === 0 ? (
                    <div className="email-empty">
                        <Mail size={48} />
                        <h3>No emails found</h3>
                        <p>
                            {searchQuery 
                                ? `No emails matching "${searchQuery}"`
                                : 'This folder is empty'
                            }
                        </p>
                    </div>
                ) : (
                    emails.map(email => {
                        const sender = parseSender(email.from);
                        const isSelected = selectedEmails.has(email.id);
                        const isHovered = hoveredEmail === email.id;
                        const isStarred = email.labels?.includes('STARRED');
                        const hasAttachment = email.attachments?.length > 0;
                        const isUnread = email.is_unread;
                        
                        return (
                            <div
                                key={email.id}
                                className={`email-item ${isUnread ? 'unread' : ''} ${isSelected ? 'selected' : ''}`}
                                onClick={() => onEmailSelect?.(email)}
                                onMouseEnter={() => setHoveredEmail(email.id)}
                                onMouseLeave={() => setHoveredEmail(null)}
                            >
                                {/* Account indicator */}
                                <div 
                                    className="email-account-indicator"
                                    style={{ background: getAccountColor(email) }}
                                    title={email.accountEmail}
                                />

                                {/* Checkbox */}
                                <button 
                                    className="email-item-checkbox"
                                    onClick={(e) => handleSelectEmail(email.id, e)}
                                >
                                    {isSelected ? <CheckSquare size={18} /> : <Square size={18} />}
                                </button>

                                {/* Star */}
                                <button 
                                    className={`email-star-btn ${isStarred ? 'starred' : ''}`}
                                    onClick={(e) => handleStarClick(email, e)}
                                >
                                    <Star size={18} fill={isStarred ? 'currentColor' : 'none'} />
                                </button>

                                {/* Sender Avatar */}
                                <div className="email-sender-avatar">
                                    {sender.avatar}
                                </div>

                                {/* Email Content */}
                                <div className="email-item-content">
                                    <div className="email-item-header">
                                        <span className={`email-sender-name ${isUnread ? 'font-semibold' : ''}`}>
                                            {sender.name}
                                        </span>
                                        <span className="email-time">{formatDate(email.date)}</span>
                                    </div>
                                    <div className="email-item-subject">
                                        <span className={isUnread ? 'font-semibold' : ''}>
                                            {email.subject || '(no subject)'}
                                        </span>
                                    </div>
                                    <div className="email-item-preview">
                                        {email.snippet}
                                    </div>
                                </div>

                                {/* Indicators */}
                                <div className="email-item-indicators">
                                    {hasAttachment && (
                                        <Paperclip size={14} className="email-attachment-icon" />
                                    )}
                                    {email.labels?.filter(l => !['INBOX', 'UNREAD', 'STARRED', 'SENT', 'IMPORTANT'].includes(l)).map(label => (
                                        <span key={label} className="email-label-badge">
                                            {label}
                                        </span>
                                    )).slice(0, 2)}
                                </div>

                                {/* Hover Actions */}
                                {isHovered && (
                                    <div className="email-hover-actions">
                                        <button 
                                            className="email-hover-btn" 
                                            title="Archive"
                                            onClick={(e) => { e.stopPropagation(); onArchive?.(email); }}
                                        >
                                            <Archive size={16} />
                                        </button>
                                        <button 
                                            className="email-hover-btn" 
                                            title="Delete"
                                            onClick={(e) => { e.stopPropagation(); onDelete?.(email); }}
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                        <button className="email-hover-btn" title="More">
                                            <MoreHorizontal size={16} />
                                        </button>
                                    </div>
                                )}
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
};

export default EmailInbox;
