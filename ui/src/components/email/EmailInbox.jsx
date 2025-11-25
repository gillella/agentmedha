import React, { useState } from 'react';
import {
    Star, Paperclip, Clock, MoreHorizontal, Archive, Trash2,
    CheckSquare, Square, ChevronDown, Sparkles, AlertTriangle,
    Tag, Reply, Forward
} from 'lucide-react';

// Mock emails data
const MOCK_EMAILS = [
    {
        id: 1,
        accountId: 'work',
        from: { name: 'Sarah Chen', email: 'sarah.chen@company.com', avatar: 'SC' },
        to: 'user.work@gmail.com',
        subject: 'Q4 Planning Meeting - Action Required',
        preview: 'Hi team, I wanted to follow up on our discussion from yesterday. The Q4 planning documents are ready for review and we need everyone\'s input by end of week...',
        body: 'Full email body here...',
        time: '10:32 AM',
        date: 'Today',
        isRead: false,
        isStarred: true,
        hasAttachment: true,
        labels: ['important'],
        priority: 'high',
        threadCount: 4
    },
    {
        id: 2,
        accountId: 'personal',
        from: { name: 'Netflix', email: 'info@netflix.com', avatar: 'N' },
        to: 'user.personal@gmail.com',
        subject: 'New releases this week you might enjoy',
        preview: 'Based on your viewing history, we think you\'ll love these new shows and movies that just dropped on Netflix this week...',
        body: 'Full email body here...',
        time: '9:15 AM',
        date: 'Today',
        isRead: true,
        isStarred: false,
        hasAttachment: false,
        labels: ['social'],
        priority: 'normal',
        threadCount: 1
    },
    {
        id: 3,
        accountId: 'business',
        from: { name: 'Michael Roberts', email: 'michael@clientco.com', avatar: 'MR' },
        to: 'user.business@gmail.com',
        subject: 'RE: Contract Renewal Discussion',
        preview: 'Thank you for sending over the proposal. Our legal team has reviewed the terms and we have a few questions regarding the payment schedule...',
        body: 'Full email body here...',
        time: '8:45 AM',
        date: 'Today',
        isRead: false,
        isStarred: false,
        hasAttachment: true,
        labels: ['finance'],
        priority: 'high',
        threadCount: 7
    },
    {
        id: 4,
        accountId: 'work',
        from: { name: 'GitHub', email: 'notifications@github.com', avatar: 'GH' },
        to: 'user.work@gmail.com',
        subject: '[agentMedha] Pull request merged: Feature/social-media-post-ui',
        preview: 'Your pull request has been merged into main. View the changes and deployment status...',
        body: 'Full email body here...',
        time: 'Yesterday',
        date: 'Nov 24',
        isRead: true,
        isStarred: false,
        hasAttachment: false,
        labels: [],
        priority: 'normal',
        threadCount: 3
    },
    {
        id: 5,
        accountId: 'personal',
        from: { name: 'American Airlines', email: 'aa@email.aa.com', avatar: 'AA' },
        to: 'user.personal@gmail.com',
        subject: 'Your Flight Confirmation - DFW to SFO',
        preview: 'Your flight is confirmed! Flight AA1234 departing Dec 15 at 8:30 AM. Check in online 24 hours before departure...',
        body: 'Full email body here...',
        time: 'Yesterday',
        date: 'Nov 24',
        isRead: false,
        isStarred: true,
        hasAttachment: true,
        labels: ['travel'],
        priority: 'normal',
        threadCount: 1
    },
    {
        id: 6,
        accountId: 'business',
        from: { name: 'QuickBooks', email: 'noreply@quickbooks.intuit.com', avatar: 'QB' },
        to: 'user.business@gmail.com',
        subject: 'Invoice #INV-2024-089 has been paid',
        preview: 'Great news! Your invoice to TechCorp Inc. for $4,500.00 has been paid. The funds will be deposited within 2-3 business days...',
        body: 'Full email body here...',
        time: '2 days ago',
        date: 'Nov 23',
        isRead: true,
        isStarred: false,
        hasAttachment: false,
        labels: ['finance'],
        priority: 'normal',
        threadCount: 1
    },
    {
        id: 7,
        accountId: 'work',
        from: { name: 'HR Department', email: 'hr@company.com', avatar: 'HR' },
        to: 'user.work@gmail.com',
        subject: 'Benefits Enrollment Deadline Reminder',
        preview: 'This is a friendly reminder that open enrollment for 2025 benefits closes on December 1st. Please log into the portal to make your selections...',
        body: 'Full email body here...',
        time: '2 days ago',
        date: 'Nov 23',
        isRead: false,
        isStarred: false,
        hasAttachment: false,
        labels: ['important'],
        priority: 'high',
        threadCount: 1
    },
    {
        id: 8,
        accountId: 'personal',
        from: { name: 'Spotify', email: 'digest@spotify.com', avatar: 'S' },
        to: 'user.personal@gmail.com',
        subject: 'Your 2024 Wrapped is here! 🎉',
        preview: 'The wait is over! Discover your top songs, artists, and podcasts from 2024. See how you compared to other listeners...',
        body: 'Full email body here...',
        time: '3 days ago',
        date: 'Nov 22',
        isRead: true,
        isStarred: false,
        hasAttachment: false,
        labels: ['social'],
        priority: 'normal',
        threadCount: 1
    },
];

const LABEL_COLORS = {
    important: '#ef4444',
    finance: '#f59e0b',
    travel: '#3b82f6',
    social: '#8b5cf6',
};

const EmailInbox = ({ selectedAccount, selectedFolder, searchQuery, accounts, onEmailSelect }) => {
    const [selectedEmails, setSelectedEmails] = useState(new Set());
    const [sortBy, setSortBy] = useState('date');
    const [hoveredEmail, setHoveredEmail] = useState(null);

    // Filter emails based on account and search
    const filteredEmails = MOCK_EMAILS.filter(email => {
        if (selectedAccount !== 'all' && email.accountId !== selectedAccount) {
            return false;
        }
        if (searchQuery) {
            const query = searchQuery.toLowerCase();
            return (
                email.subject.toLowerCase().includes(query) ||
                email.from.name.toLowerCase().includes(query) ||
                email.preview.toLowerCase().includes(query)
            );
        }
        return true;
    });

    const toggleEmailSelection = (emailId, e) => {
        e.stopPropagation();
        const newSelected = new Set(selectedEmails);
        if (newSelected.has(emailId)) {
            newSelected.delete(emailId);
        } else {
            newSelected.add(emailId);
        }
        setSelectedEmails(newSelected);
    };

    const toggleSelectAll = () => {
        if (selectedEmails.size === filteredEmails.length) {
            setSelectedEmails(new Set());
        } else {
            setSelectedEmails(new Set(filteredEmails.map(e => e.id)));
        }
    };

    const getAccountColor = (accountId) => {
        return accounts.find(a => a.id === accountId)?.color || '#6b7280';
    };

    const unreadCount = filteredEmails.filter(e => !e.isRead).length;

    return (
        <div className="email-inbox">
            {/* Inbox Header */}
            <div className="email-inbox-header">
                <div className="email-inbox-title">
                    <h2>
                        {selectedFolder.charAt(0).toUpperCase() + selectedFolder.slice(1)}
                        {selectedAccount !== 'all' && ` • ${accounts.find(a => a.id === selectedAccount)?.name}`}
                    </h2>
                    <span className="email-inbox-count">
                        {unreadCount} unread of {filteredEmails.length}
                    </span>
                </div>
                <div className="email-inbox-actions">
                    <button className="email-ai-summarize">
                        <Sparkles size={16} />
                        AI Summary
                    </button>
                    <div className="email-sort-dropdown">
                        <button className="email-sort-btn">
                            <span>Sort: {sortBy === 'date' ? 'Date' : 'Priority'}</span>
                            <ChevronDown size={14} />
                        </button>
                    </div>
                </div>
            </div>

            {/* Bulk Actions Bar */}
            {selectedEmails.size > 0 && (
                <div className="email-bulk-actions">
                    <span className="email-bulk-count">{selectedEmails.size} selected</span>
                    <div className="email-bulk-buttons">
                        <button className="email-bulk-btn">
                            <Archive size={16} />
                            Archive
                        </button>
                        <button className="email-bulk-btn">
                            <Tag size={16} />
                            Label
                        </button>
                        <button className="email-bulk-btn danger">
                            <Trash2 size={16} />
                            Delete
                        </button>
                    </div>
                </div>
            )}

            {/* Email List */}
            <div className="email-list-container">
                {/* List Header */}
                <div className="email-list-header">
                    <button 
                        className="email-checkbox-btn"
                        onClick={toggleSelectAll}
                    >
                        {selectedEmails.size === filteredEmails.length && filteredEmails.length > 0 ? (
                            <CheckSquare size={18} />
                        ) : (
                            <Square size={18} />
                        )}
                    </button>
                    <span className="email-list-header-label">Select all</span>
                </div>

                {/* Email Items */}
                <div className="email-list">
                    {filteredEmails.length === 0 ? (
                        <div className="email-empty-state">
                            <div className="email-empty-icon">📭</div>
                            <h3>No emails found</h3>
                            <p>Try adjusting your filters or search query</p>
                        </div>
                    ) : (
                        filteredEmails.map(email => (
                            <div
                                key={email.id}
                                className={`email-item ${!email.isRead ? 'unread' : ''} ${selectedEmails.has(email.id) ? 'selected' : ''}`}
                                onClick={() => onEmailSelect(email)}
                                onMouseEnter={() => setHoveredEmail(email.id)}
                                onMouseLeave={() => setHoveredEmail(null)}
                            >
                                {/* Account Indicator */}
                                <div 
                                    className="email-account-indicator"
                                    style={{ background: getAccountColor(email.accountId) }}
                                    title={accounts.find(a => a.id === email.accountId)?.email}
                                />

                                {/* Checkbox */}
                                <button 
                                    className="email-checkbox-btn"
                                    onClick={(e) => toggleEmailSelection(email.id, e)}
                                >
                                    {selectedEmails.has(email.id) ? (
                                        <CheckSquare size={18} />
                                    ) : (
                                        <Square size={18} />
                                    )}
                                </button>

                                {/* Star */}
                                <button 
                                    className={`email-star-btn ${email.isStarred ? 'starred' : ''}`}
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    <Star size={18} fill={email.isStarred ? 'currentColor' : 'none'} />
                                </button>

                                {/* Avatar */}
                                <div 
                                    className="email-avatar"
                                    style={{ 
                                        background: email.from.avatar === 'SC' ? '#ec4899' :
                                                   email.from.avatar === 'MR' ? '#8b5cf6' :
                                                   email.from.avatar === 'HR' ? '#06b6d4' :
                                                   '#6b7280'
                                    }}
                                >
                                    {email.from.avatar}
                                </div>

                                {/* Content */}
                                <div className="email-content-wrapper">
                                    <div className="email-content-top">
                                        <span className={`email-sender ${!email.isRead ? 'unread' : ''}`}>
                                            {email.from.name}
                                        </span>
                                        {email.priority === 'high' && (
                                            <span className="email-priority-badge">
                                                <AlertTriangle size={12} />
                                                Important
                                            </span>
                                        )}
                                        {email.labels.map(label => (
                                            <span 
                                                key={label}
                                                className="email-label-badge"
                                                style={{ background: `${LABEL_COLORS[label]}20`, color: LABEL_COLORS[label] }}
                                            >
                                                {label}
                                            </span>
                                        ))}
                                    </div>
                                    <div className="email-subject-line">
                                        <span className={`email-subject ${!email.isRead ? 'unread' : ''}`}>
                                            {email.subject}
                                        </span>
                                        {email.threadCount > 1 && (
                                            <span className="email-thread-count">{email.threadCount}</span>
                                        )}
                                    </div>
                                    <p className="email-preview-text">{email.preview}</p>
                                </div>

                                {/* Meta */}
                                <div className="email-meta">
                                    {hoveredEmail === email.id ? (
                                        <div className="email-hover-actions">
                                            <button className="email-action-btn" title="Archive">
                                                <Archive size={16} />
                                            </button>
                                            <button className="email-action-btn" title="Delete">
                                                <Trash2 size={16} />
                                            </button>
                                            <button className="email-action-btn" title="Reply">
                                                <Reply size={16} />
                                            </button>
                                        </div>
                                    ) : (
                                        <>
                                            {email.hasAttachment && (
                                                <Paperclip size={14} className="email-attachment-icon" />
                                            )}
                                            <span className="email-time">{email.time}</span>
                                        </>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default EmailInbox;

