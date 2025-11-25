import React, { useState, useRef, useEffect } from 'react';
import {
    X, Minimize2, Maximize2, Send, Paperclip, Image, Link2,
    Sparkles, ChevronDown, Bold, Italic, Underline, List,
    AlignLeft, Smile, Clock, Trash2, RefreshCw, Wand2,
    FileText, CheckCircle, AlertCircle
} from 'lucide-react';

const EmailComposer = ({ accounts, selectedAccount, replyTo, onClose }) => {
    const [isMinimized, setIsMinimized] = useState(false);
    const [isMaximized, setIsMaximized] = useState(false);
    const [fromAccount, setFromAccount] = useState(
        selectedAccount === 'all' ? accounts[0].id : selectedAccount
    );
    const [showFromDropdown, setShowFromDropdown] = useState(false);
    const [to, setTo] = useState(replyTo ? replyTo.from.email : '');
    const [cc, setCc] = useState('');
    const [bcc, setBcc] = useState('');
    const [showCcBcc, setShowCcBcc] = useState(false);
    const [subject, setSubject] = useState(replyTo ? `Re: ${replyTo.subject}` : '');
    const [body, setBody] = useState('');
    const [isSending, setIsSending] = useState(false);
    const [sendStatus, setSendStatus] = useState(null);
    const [isAiGenerating, setIsAiGenerating] = useState(false);
    const [showAiMenu, setShowAiMenu] = useState(false);
    const [attachments, setAttachments] = useState([]);
    
    const textareaRef = useRef(null);
    const fileInputRef = useRef(null);

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.focus();
        }
    }, []);

    const currentAccount = accounts.find(a => a.id === fromAccount);

    const handleSend = async () => {
        if (!to.trim() || !subject.trim()) {
            setSendStatus({ type: 'error', message: 'Please fill in recipient and subject' });
            return;
        }

        setIsSending(true);
        setSendStatus(null);

        try {
            // Simulate sending
            await new Promise(resolve => setTimeout(resolve, 2000));
            setSendStatus({ type: 'success', message: 'Email sent successfully!' });
            setTimeout(() => onClose(), 1500);
        } catch (error) {
            setSendStatus({ type: 'error', message: 'Failed to send email' });
        } finally {
            setIsSending(false);
        }
    };

    const handleAiAction = async (action) => {
        setShowAiMenu(false);
        setIsAiGenerating(true);

        try {
            // Simulate AI processing
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            switch (action) {
                case 'draft':
                    setBody(`Dear ${to.split('@')[0]},\n\nI hope this email finds you well. I wanted to reach out regarding ${subject || 'our recent discussion'}.\n\n[AI will elaborate based on context]\n\nBest regards,\n${currentAccount.name}`);
                    break;
                case 'improve':
                    setBody(body + '\n\n[AI improved version would appear here]');
                    break;
                case 'shorten':
                    setBody('Shortened version: ' + body.slice(0, 100) + '...');
                    break;
                case 'formal':
                    setBody(body.replace(/Hi|Hey/g, 'Dear').replace(/Thanks|Thx/g, 'Thank you'));
                    break;
                case 'friendly':
                    setBody('Hey there! ' + body);
                    break;
                default:
                    break;
            }
        } finally {
            setIsAiGenerating(false);
        }
    };

    const handleFileSelect = (e) => {
        const files = Array.from(e.target.files);
        setAttachments(prev => [...prev, ...files.map(f => ({
            id: Math.random(),
            name: f.name,
            size: f.size,
            type: f.type
        }))]);
    };

    const removeAttachment = (id) => {
        setAttachments(prev => prev.filter(a => a.id !== id));
    };

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    if (isMinimized) {
        return (
            <div className="email-composer-minimized" onClick={() => setIsMinimized(false)}>
                <div className="email-composer-minimized-content">
                    <span className="email-composer-minimized-title">
                        {subject || 'New Message'}
                    </span>
                    <button onClick={(e) => { e.stopPropagation(); onClose(); }}>
                        <X size={16} />
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className={`email-composer-overlay ${isMaximized ? 'maximized' : ''}`}>
            <div className={`email-composer ${isMaximized ? 'maximized' : ''}`}>
                {/* Header */}
                <div className="email-composer-header">
                    <span className="email-composer-title">
                        {replyTo ? 'Reply' : 'New Message'}
                    </span>
                    <div className="email-composer-header-actions">
                        <button 
                            onClick={() => setIsMinimized(true)}
                            className="email-composer-header-btn"
                        >
                            <Minimize2 size={16} />
                        </button>
                        <button 
                            onClick={() => setIsMaximized(!isMaximized)}
                            className="email-composer-header-btn"
                        >
                            <Maximize2 size={16} />
                        </button>
                        <button 
                            onClick={onClose}
                            className="email-composer-header-btn close"
                        >
                            <X size={16} />
                        </button>
                    </div>
                </div>

                {/* Form Fields */}
                <div className="email-composer-fields">
                    {/* From Field */}
                    <div className="email-composer-field">
                        <label>From</label>
                        <div className="email-composer-from">
                            <button 
                                className="email-from-selector"
                                onClick={() => setShowFromDropdown(!showFromDropdown)}
                            >
                                <div 
                                    className="email-from-avatar"
                                    style={{ background: currentAccount.color }}
                                >
                                    {currentAccount.name[0]}
                                </div>
                                <span>{currentAccount.email}</span>
                                <ChevronDown size={14} />
                            </button>
                            
                            {showFromDropdown && (
                                <div className="email-from-dropdown">
                                    {accounts.map(acc => (
                                        <button
                                            key={acc.id}
                                            className={`email-from-option ${fromAccount === acc.id ? 'active' : ''}`}
                                            onClick={() => {
                                                setFromAccount(acc.id);
                                                setShowFromDropdown(false);
                                            }}
                                        >
                                            <div 
                                                className="email-from-avatar"
                                                style={{ background: acc.color }}
                                            >
                                                {acc.name[0]}
                                            </div>
                                            <div className="email-from-info">
                                                <span className="email-from-name">{acc.name}</span>
                                                <span className="email-from-email">{acc.email}</span>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* To Field */}
                    <div className="email-composer-field">
                        <label>To</label>
                        <div className="email-composer-input-wrapper">
                            <input
                                type="text"
                                value={to}
                                onChange={(e) => setTo(e.target.value)}
                                placeholder="Recipients"
                                className="email-composer-input"
                            />
                            {!showCcBcc && (
                                <button 
                                    className="email-cc-toggle"
                                    onClick={() => setShowCcBcc(true)}
                                >
                                    Cc/Bcc
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Cc/Bcc Fields */}
                    {showCcBcc && (
                        <>
                            <div className="email-composer-field">
                                <label>Cc</label>
                                <input
                                    type="text"
                                    value={cc}
                                    onChange={(e) => setCc(e.target.value)}
                                    placeholder="Carbon copy"
                                    className="email-composer-input"
                                />
                            </div>
                            <div className="email-composer-field">
                                <label>Bcc</label>
                                <input
                                    type="text"
                                    value={bcc}
                                    onChange={(e) => setBcc(e.target.value)}
                                    placeholder="Blind carbon copy"
                                    className="email-composer-input"
                                />
                            </div>
                        </>
                    )}

                    {/* Subject Field */}
                    <div className="email-composer-field">
                        <label>Subject</label>
                        <input
                            type="text"
                            value={subject}
                            onChange={(e) => setSubject(e.target.value)}
                            placeholder="Subject"
                            className="email-composer-input"
                        />
                    </div>
                </div>

                {/* Formatting Toolbar */}
                <div className="email-composer-toolbar">
                    <div className="email-toolbar-group">
                        <button className="email-toolbar-btn" title="Bold">
                            <Bold size={16} />
                        </button>
                        <button className="email-toolbar-btn" title="Italic">
                            <Italic size={16} />
                        </button>
                        <button className="email-toolbar-btn" title="Underline">
                            <Underline size={16} />
                        </button>
                    </div>
                    <div className="email-toolbar-divider" />
                    <div className="email-toolbar-group">
                        <button className="email-toolbar-btn" title="Bullet list">
                            <List size={16} />
                        </button>
                        <button className="email-toolbar-btn" title="Align">
                            <AlignLeft size={16} />
                        </button>
                    </div>
                    <div className="email-toolbar-divider" />
                    <div className="email-toolbar-group">
                        <button 
                            className="email-toolbar-btn"
                            title="Insert link"
                        >
                            <Link2 size={16} />
                        </button>
                        <button 
                            className="email-toolbar-btn"
                            title="Insert emoji"
                        >
                            <Smile size={16} />
                        </button>
                    </div>
                    <div className="email-toolbar-spacer" />
                    
                    {/* AI Writing Assistant */}
                    <div className="email-ai-assistant">
                        <button 
                            className={`email-ai-trigger ${isAiGenerating ? 'generating' : ''}`}
                            onClick={() => setShowAiMenu(!showAiMenu)}
                            disabled={isAiGenerating}
                        >
                            {isAiGenerating ? (
                                <RefreshCw size={16} className="spin" />
                            ) : (
                                <Sparkles size={16} />
                            )}
                            <span>Medha AI</span>
                            <ChevronDown size={14} />
                        </button>
                        
                        {showAiMenu && (
                            <div className="email-ai-menu">
                                <button onClick={() => handleAiAction('draft')}>
                                    <Wand2 size={16} />
                                    <div>
                                        <span>Draft Email</span>
                                        <small>Generate a complete draft</small>
                                    </div>
                                </button>
                                <button onClick={() => handleAiAction('improve')}>
                                    <Sparkles size={16} />
                                    <div>
                                        <span>Improve Writing</span>
                                        <small>Enhance clarity and tone</small>
                                    </div>
                                </button>
                                <button onClick={() => handleAiAction('shorten')}>
                                    <FileText size={16} />
                                    <div>
                                        <span>Make Shorter</span>
                                        <small>Condense the message</small>
                                    </div>
                                </button>
                                <div className="email-ai-menu-divider" />
                                <button onClick={() => handleAiAction('formal')}>
                                    <span className="emoji">👔</span>
                                    <div>
                                        <span>More Formal</span>
                                        <small>Professional tone</small>
                                    </div>
                                </button>
                                <button onClick={() => handleAiAction('friendly')}>
                                    <span className="emoji">😊</span>
                                    <div>
                                        <span>More Friendly</span>
                                        <small>Casual and warm</small>
                                    </div>
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Body */}
                <div className="email-composer-body">
                    <textarea
                        ref={textareaRef}
                        value={body}
                        onChange={(e) => setBody(e.target.value)}
                        placeholder="Write your message... or let Medha AI help you draft it"
                        className="email-composer-textarea"
                    />
                </div>

                {/* Attachments */}
                {attachments.length > 0 && (
                    <div className="email-composer-attachments">
                        {attachments.map(file => (
                            <div key={file.id} className="email-attachment-item">
                                <Paperclip size={14} />
                                <span className="email-attachment-name">{file.name}</span>
                                <span className="email-attachment-size">{formatFileSize(file.size)}</span>
                                <button 
                                    className="email-attachment-remove"
                                    onClick={() => removeAttachment(file.id)}
                                >
                                    <X size={14} />
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Status Message */}
                {sendStatus && (
                    <div className={`email-composer-status ${sendStatus.type}`}>
                        {sendStatus.type === 'success' ? (
                            <CheckCircle size={16} />
                        ) : (
                            <AlertCircle size={16} />
                        )}
                        <span>{sendStatus.message}</span>
                    </div>
                )}

                {/* Footer */}
                <div className="email-composer-footer">
                    <div className="email-composer-footer-left">
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileSelect}
                            multiple
                            hidden
                        />
                        <button 
                            className="email-footer-btn"
                            onClick={() => fileInputRef.current?.click()}
                            title="Attach files"
                        >
                            <Paperclip size={18} />
                        </button>
                        <button className="email-footer-btn" title="Insert image">
                            <Image size={18} />
                        </button>
                        <button className="email-footer-btn" title="Schedule send">
                            <Clock size={18} />
                        </button>
                    </div>
                    <div className="email-composer-footer-right">
                        <button className="email-footer-btn" title="Discard draft">
                            <Trash2 size={18} />
                        </button>
                        <button 
                            className={`email-send-btn ${isSending ? 'sending' : ''}`}
                            onClick={handleSend}
                            disabled={isSending || !to.trim()}
                        >
                            {isSending ? (
                                <>
                                    <RefreshCw size={18} className="spin" />
                                    Sending...
                                </>
                            ) : (
                                <>
                                    <Send size={18} />
                                    Send
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EmailComposer;

