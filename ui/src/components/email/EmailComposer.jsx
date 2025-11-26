import React, { useState, useEffect } from 'react';
import {
    X, Minus, Maximize2, Send, Paperclip, Image, Link, Smile,
    Bold, Italic, Underline, List, ListOrdered, AlignLeft,
    ChevronDown, Sparkles, Clock, Trash2, Save, MoreHorizontal
} from 'lucide-react';

const EmailComposer = ({ 
    accounts = [], 
    selectedAccount, 
    replyTo,
    thread,
    onClose,
    onSend,
    onSaveDraft
}) => {
    const [isMinimized, setIsMinimized] = useState(false);
    const [isMaximized, setIsMaximized] = useState(false);
    const [isSending, setIsSending] = useState(false);
    
    // Form state
    const [fromAccount, setFromAccount] = useState(selectedAccount || accounts[0]?.id || '');
    const [to, setTo] = useState('');
    const [cc, setCc] = useState('');
    const [bcc, setBcc] = useState('');
    const [subject, setSubject] = useState('');
    const [body, setBody] = useState('');
    const [showCc, setShowCc] = useState(false);
    const [showBcc, setShowBcc] = useState(false);
    const [showAiSuggestions, setShowAiSuggestions] = useState(false);

    // Pre-fill for reply
    useEffect(() => {
        if (replyTo) {
            // Extract email from "Name <email>" format
            const fromMatch = replyTo.from?.match(/<(.+?)>/);
            const replyToEmail = fromMatch ? fromMatch[1] : replyTo.from;
            setTo(replyToEmail || '');
            
            // Set subject with Re: prefix
            const originalSubject = replyTo.subject || '';
            if (!originalSubject.toLowerCase().startsWith('re:')) {
                setSubject(`Re: ${originalSubject}`);
            } else {
                setSubject(originalSubject);
            }
            
            // Quote original message
            const lastMessage = thread?.messages?.[thread.messages.length - 1] || replyTo;
            const quotedBody = `\n\n--- Original Message ---\nFrom: ${lastMessage.from}\nDate: ${lastMessage.date}\nSubject: ${lastMessage.subject}\n\n${lastMessage.body || lastMessage.snippet || ''}`;
            setBody(quotedBody);
        }
    }, [replyTo, thread]);

    const handleSend = async () => {
        if (!to.trim()) {
            alert('Please enter a recipient');
            return;
        }
        
        setIsSending(true);
        try {
            const emailData = {
                to: to.split(',').map(e => e.trim()).filter(e => e),
                subject: subject,
                body: body,
                html: false,
            };
            
            if (cc.trim()) {
                emailData.cc = cc.split(',').map(e => e.trim()).filter(e => e);
            }
            if (bcc.trim()) {
                emailData.bcc = bcc.split(',').map(e => e.trim()).filter(e => e);
            }
            if (replyTo?.id) {
                emailData.reply_to_message_id = replyTo.id;
            }
            
            await onSend?.(emailData, fromAccount);
        } catch (error) {
            console.error('Failed to send:', error);
            alert('Failed to send email: ' + error.message);
        } finally {
            setIsSending(false);
        }
    };

    const handleSaveDraft = async () => {
        try {
            const draftData = {
                to: to.split(',').map(e => e.trim()).filter(e => e),
                subject: subject,
                body: body,
            };
            await onSaveDraft?.(draftData, fromAccount);
            alert('Draft saved!');
        } catch (error) {
            console.error('Failed to save draft:', error);
        }
    };

    const currentAccount = accounts.find(a => a.id === fromAccount);

    return (
        <div className={`email-composer ${isMinimized ? 'minimized' : ''} ${isMaximized ? 'maximized' : ''}`}>
            {/* Header */}
            <div className="email-composer-header">
                <span className="email-composer-title">
                    {replyTo ? 'Reply' : 'New Message'}
                </span>
                <div className="email-composer-controls">
                    <button onClick={() => setIsMinimized(!isMinimized)}>
                        <Minus size={16} />
                    </button>
                    <button onClick={() => setIsMaximized(!isMaximized)}>
                        <Maximize2 size={16} />
                    </button>
                    <button onClick={onClose}>
                        <X size={16} />
                    </button>
                </div>
            </div>

            {!isMinimized && (
                <>
                    {/* Form Fields */}
                    <div className="email-composer-fields">
                        {/* From Account Selector */}
                        <div className="email-field">
                            <label>From</label>
                            <div className="email-from-selector">
                                <select 
                                    value={fromAccount}
                                    onChange={(e) => setFromAccount(e.target.value)}
                                >
                                    {accounts.map(acc => (
                                        <option key={acc.id} value={acc.id}>
                                            {acc.email}
                                        </option>
                                    ))}
                                </select>
                                {currentAccount && (
                                    <div 
                                        className="email-from-indicator"
                                        style={{ background: currentAccount.color }}
                                    />
                                )}
                            </div>
                        </div>

                        {/* To */}
                        <div className="email-field">
                            <label>To</label>
                            <div className="email-field-input-wrapper">
                                <input
                                    type="text"
                                    value={to}
                                    onChange={(e) => setTo(e.target.value)}
                                    placeholder="Recipients (comma separated)"
                                />
                                <div className="email-field-actions">
                                    {!showCc && (
                                        <button onClick={() => setShowCc(true)}>Cc</button>
                                    )}
                                    {!showBcc && (
                                        <button onClick={() => setShowBcc(true)}>Bcc</button>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Cc */}
                        {showCc && (
                            <div className="email-field">
                                <label>Cc</label>
                                <input
                                    type="text"
                                    value={cc}
                                    onChange={(e) => setCc(e.target.value)}
                                    placeholder="Cc recipients"
                                />
                            </div>
                        )}

                        {/* Bcc */}
                        {showBcc && (
                            <div className="email-field">
                                <label>Bcc</label>
                                <input
                                    type="text"
                                    value={bcc}
                                    onChange={(e) => setBcc(e.target.value)}
                                    placeholder="Bcc recipients"
                                />
                            </div>
                        )}

                        {/* Subject */}
                        <div className="email-field">
                            <label>Subject</label>
                            <input
                                type="text"
                                value={subject}
                                onChange={(e) => setSubject(e.target.value)}
                                placeholder="Subject"
                            />
                        </div>
                    </div>

                    {/* Formatting Toolbar */}
                    <div className="email-composer-toolbar">
                        <div className="email-toolbar-group">
                            <button title="Bold"><Bold size={16} /></button>
                            <button title="Italic"><Italic size={16} /></button>
                            <button title="Underline"><Underline size={16} /></button>
                        </div>
                        <div className="email-toolbar-divider" />
                        <div className="email-toolbar-group">
                            <button title="Bullet List"><List size={16} /></button>
                            <button title="Numbered List"><ListOrdered size={16} /></button>
                        </div>
                        <div className="email-toolbar-divider" />
                        <div className="email-toolbar-group">
                            <button title="Attach File"><Paperclip size={16} /></button>
                            <button title="Insert Link"><Link size={16} /></button>
                            <button title="Insert Image"><Image size={16} /></button>
                            <button title="Insert Emoji"><Smile size={16} /></button>
                        </div>
                        <div className="email-toolbar-spacer" />
                        <button 
                            className={`email-ai-assist-btn ${showAiSuggestions ? 'active' : ''}`}
                            onClick={() => setShowAiSuggestions(!showAiSuggestions)}
                        >
                            <Sparkles size={16} />
                            AI Assist
                        </button>
                    </div>

                    {/* AI Suggestions Panel */}
                    {showAiSuggestions && (
                        <div className="email-ai-suggestions">
                            <div className="email-ai-suggestions-header">
                                <Sparkles size={14} />
                                <span>AI Writing Assistant</span>
                            </div>
                            <div className="email-ai-suggestions-actions">
                                <button onClick={() => {
                                    setBody(prev => prev + '\n\n[AI will help draft content here]');
                                    setShowAiSuggestions(false);
                                }}>
                                    <Sparkles size={12} />
                                    Draft Reply
                                </button>
                                <button>
                                    <Sparkles size={12} />
                                    Make Professional
                                </button>
                                <button>
                                    <Sparkles size={12} />
                                    Make Friendly
                                </button>
                                <button>
                                    <Sparkles size={12} />
                                    Shorten
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Body */}
                    <div className="email-composer-body">
                        <textarea
                            value={body}
                            onChange={(e) => setBody(e.target.value)}
                            placeholder="Compose your email..."
                        />
                    </div>

                    {/* Footer */}
                    <div className="email-composer-footer">
                        <div className="email-composer-footer-left">
                            <button 
                                className="email-send-btn"
                                onClick={handleSend}
                                disabled={isSending || !to.trim()}
                            >
                                {isSending ? (
                                    <>Sending...</>
                                ) : (
                                    <>
                                        <Send size={16} />
                                        Send
                                    </>
                                )}
                            </button>
                            <div className="email-send-options">
                                <button className="email-schedule-btn" title="Schedule Send">
                                    <Clock size={16} />
                                    <ChevronDown size={12} />
                                </button>
                            </div>
                        </div>
                        <div className="email-composer-footer-right">
                            <button 
                                className="email-draft-btn" 
                                onClick={handleSaveDraft}
                                title="Save Draft"
                            >
                                <Save size={16} />
                            </button>
                            <button 
                                className="email-discard-btn" 
                                onClick={onClose}
                                title="Discard"
                            >
                                <Trash2 size={16} />
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default EmailComposer;
