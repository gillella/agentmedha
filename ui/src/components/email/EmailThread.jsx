import React, { useState } from 'react';
import {
    ArrowLeft, Star, Archive, Trash2, Reply, ReplyAll, Forward,
    MoreHorizontal, Paperclip, Download, ChevronDown, ChevronUp,
    Sparkles, Copy, ExternalLink, Clock, Tag, Printer
} from 'lucide-react';

// Helper to parse sender
const parseSender = (from) => {
    if (!from) return { name: 'Unknown', email: '', avatar: '?' };
    const match = from.match(/^(.+?)\s*<(.+?)>$/);
    if (match) {
        const name = match[1].replace(/"/g, '').trim();
        const email = match[2];
        const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        return { name, email, avatar: initials };
    }
    const name = from.split('@')[0];
    return { name: from, email: from, avatar: name.substring(0, 2).toUpperCase() };
};

// Format date for display
const formatDateTime = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
};

const EmailThread = ({ 
    email, 
    thread,
    onBack, 
    onReply,
    onArchive,
    onDelete,
    onStar
}) => {
    const [expandedMessages, setExpandedMessages] = useState(new Set([thread?.messages?.length - 1 || 0]));
    const [showAiPanel, setShowAiPanel] = useState(false);

    const messages = thread?.messages || [email];
    const isStarred = email?.labels?.includes('STARRED');

    const toggleMessage = (index) => {
        const newExpanded = new Set(expandedMessages);
        if (newExpanded.has(index)) {
            newExpanded.delete(index);
        } else {
            newExpanded.add(index);
        }
        setExpandedMessages(newExpanded);
    };

    const handleStarClick = () => {
        onStar?.();
    };

    // Clean up HTML content for display
    const renderEmailBody = (body) => {
        if (!body) return <p className="email-body-empty">No content</p>;
        
        // Check if it's HTML
        if (body.includes('<') && body.includes('>')) {
            return (
                <div 
                    className="email-body-html"
                    dangerouslySetInnerHTML={{ __html: body }}
                />
            );
        }
        
        // Plain text - preserve whitespace and line breaks
        return (
            <div className="email-body-text">
                {body.split('\n').map((line, i) => (
                    <React.Fragment key={i}>
                        {line}
                        <br />
                    </React.Fragment>
                ))}
            </div>
        );
    };

    return (
        <div className="email-thread">
            {/* Thread Header */}
            <div className="email-thread-header">
                <div className="email-thread-header-left">
                    <button className="email-back-btn" onClick={onBack}>
                        <ArrowLeft size={20} />
                    </button>
                    <h2 className="email-thread-subject">
                        {email?.subject || '(no subject)'}
                    </h2>
                </div>
                
                <div className="email-thread-actions">
                    <button 
                        className={`email-action-btn ${isStarred ? 'starred' : ''}`}
                        onClick={handleStarClick}
                        title={isStarred ? 'Unstar' : 'Star'}
                    >
                        <Star size={18} fill={isStarred ? 'currentColor' : 'none'} />
                    </button>
                    <button className="email-action-btn" onClick={onArchive} title="Archive">
                        <Archive size={18} />
                    </button>
                    <button className="email-action-btn" onClick={onDelete} title="Delete">
                        <Trash2 size={18} />
                    </button>
                    <button className="email-action-btn" title="Print">
                        <Printer size={18} />
                    </button>
                    <button className="email-action-btn" title="More">
                        <MoreHorizontal size={18} />
                    </button>
                </div>
            </div>

            {/* AI Analysis Panel Toggle */}
            <div className="email-ai-toggle">
                <button 
                    className={`email-ai-toggle-btn ${showAiPanel ? 'active' : ''}`}
                    onClick={() => setShowAiPanel(!showAiPanel)}
                >
                    <Sparkles size={16} />
                    <span>AI Analysis</span>
                    {showAiPanel ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </button>
            </div>

            {/* AI Analysis Panel */}
            {showAiPanel && (
                <div className="email-ai-panel">
                    <div className="email-ai-section">
                        <h4>Summary</h4>
                        <p>This email thread contains {messages.length} message(s) regarding "{email?.subject}".</p>
                    </div>
                    <div className="email-ai-section">
                        <h4>Key Points</h4>
                        <ul>
                            <li>Thread started: {formatDateTime(messages[0]?.date)}</li>
                            <li>Latest reply: {formatDateTime(messages[messages.length - 1]?.date)}</li>
                            <li>Participants: {[...new Set(messages.map(m => parseSender(m.from).name))].join(', ')}</li>
                        </ul>
                    </div>
                    <div className="email-ai-actions">
                        <button className="email-ai-action-btn">
                            <Sparkles size={14} />
                            Generate Reply
                        </button>
                        <button className="email-ai-action-btn">
                            <Copy size={14} />
                            Summarize
                        </button>
                    </div>
                </div>
            )}

            {/* Messages */}
            <div className="email-messages">
                {messages.map((msg, index) => {
                    const sender = parseSender(msg.from);
                    const isExpanded = expandedMessages.has(index);
                    const isLatest = index === messages.length - 1;

                    return (
                        <div 
                            key={msg.id || index} 
                            className={`email-message ${isExpanded ? 'expanded' : 'collapsed'}`}
                        >
                            {/* Message Header */}
                            <div 
                                className="email-message-header"
                                onClick={() => toggleMessage(index)}
                            >
                                <div className="email-message-avatar">
                                    {sender.avatar}
                                </div>
                                <div className="email-message-info">
                                    <div className="email-message-sender">
                                        <span className="email-sender-name">{sender.name}</span>
                                        <span className="email-sender-email">&lt;{sender.email}&gt;</span>
                                    </div>
                                    {!isExpanded && (
                                        <div className="email-message-preview">
                                            {msg.snippet || msg.body?.substring(0, 100)}...
                                        </div>
                                    )}
                                    {isExpanded && (
                                        <div className="email-message-meta">
                                            <span>to {msg.to || 'me'}</span>
                                        </div>
                                    )}
                                </div>
                                <div className="email-message-time">
                                    <Clock size={12} />
                                    <span>{formatDateTime(msg.date)}</span>
                                </div>
                                <button className="email-expand-btn">
                                    {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                </button>
                            </div>

                            {/* Message Body */}
                            {isExpanded && (
                                <div className="email-message-body">
                                    {renderEmailBody(msg.body)}

                                    {/* Attachments */}
                                    {msg.attachments?.length > 0 && (
                                        <div className="email-attachments">
                                            <div className="email-attachments-header">
                                                <Paperclip size={14} />
                                                <span>{msg.attachments.length} Attachment(s)</span>
                                            </div>
                                            <div className="email-attachments-list">
                                                {msg.attachments.map((att, i) => (
                                                    <div key={i} className="email-attachment-item">
                                                        <Paperclip size={14} />
                                                        <span>{att.filename}</span>
                                                        <span className="email-attachment-size">
                                                            {(att.size / 1024).toFixed(1)} KB
                                                        </span>
                                                        <button className="email-attachment-download">
                                                            <Download size={14} />
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Message Actions */}
                                    <div className="email-message-actions">
                                        <button className="email-reply-btn" onClick={onReply}>
                                            <Reply size={14} />
                                            Reply
                                        </button>
                                        <button className="email-reply-btn">
                                            <ReplyAll size={14} />
                                            Reply All
                                        </button>
                                        <button className="email-reply-btn">
                                            <Forward size={14} />
                                            Forward
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Quick Reply Box */}
            <div className="email-quick-reply">
                <div className="email-quick-reply-input">
                    <input 
                        type="text" 
                        placeholder="Click to reply..."
                        onClick={onReply}
                        readOnly
                    />
                </div>
                <div className="email-quick-reply-actions">
                    <button className="email-quick-reply-btn" onClick={onReply}>
                        <Reply size={16} />
                        Reply
                    </button>
                    <button className="email-quick-reply-btn">
                        <Forward size={16} />
                        Forward
                    </button>
                </div>
            </div>
        </div>
    );
};

export default EmailThread;
