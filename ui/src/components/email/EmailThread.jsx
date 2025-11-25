import React, { useState } from 'react';
import {
    ArrowLeft, Star, Reply, ReplyAll, Forward, MoreHorizontal,
    Archive, Trash2, Tag, Printer, ExternalLink, Paperclip,
    Download, ChevronDown, ChevronUp, Sparkles, RefreshCw,
    Clock, CheckCircle, Copy, MailOpen
} from 'lucide-react';

const EmailThread = ({ email, onBack, onReply }) => {
    const [isStarred, setIsStarred] = useState(email.isStarred);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [aiSummary, setAiSummary] = useState(null);
    const [expandedMessages, setExpandedMessages] = useState(new Set([email.id]));
    const [showMoreActions, setShowMoreActions] = useState(false);

    // Mock thread messages
    const threadMessages = [
        {
            id: email.id,
            from: email.from,
            to: email.to,
            subject: email.subject,
            body: `Hi team,

I wanted to follow up on our discussion from yesterday regarding the Q4 planning. The documents are ready for review and we need everyone's input by end of week.

Key points to address:
• Budget allocation for new initiatives
• Resource planning for the upcoming projects
• Timeline adjustments based on recent feedback

Please review the attached documents and share your thoughts in our next meeting.

Best regards,
${email.from.name}`,
            time: email.time,
            date: email.date,
            attachments: email.hasAttachment ? [
                { id: 1, name: 'Q4_Planning_2024.pdf', size: '2.4 MB', type: 'pdf' },
                { id: 2, name: 'Budget_Proposal.xlsx', size: '156 KB', type: 'excel' }
            ] : []
        },
        ...(email.threadCount > 1 ? [
            {
                id: email.id + '-1',
                from: { name: 'You', email: 'user@company.com', avatar: 'ME' },
                to: email.from.email,
                subject: `Re: ${email.subject}`,
                body: `Hi ${email.from.name.split(' ')[0]},

Thanks for sending this over. I'll review the documents today and prepare my feedback for the meeting.

Quick question - should we also include the risk assessment in our discussion?

Thanks,
User`,
                time: '11:45 AM',
                date: email.date,
                attachments: []
            },
            {
                id: email.id + '-2',
                from: email.from,
                to: 'user@company.com',
                subject: `Re: ${email.subject}`,
                body: `Great point! Yes, please include the risk assessment. I've attached the latest version for reference.

Looking forward to your input.

Best,
${email.from.name.split(' ')[0]}`,
                time: '2:30 PM',
                date: email.date,
                attachments: [
                    { id: 3, name: 'Risk_Assessment_Q4.pdf', size: '890 KB', type: 'pdf' }
                ]
            }
        ] : [])
    ];

    const handleAiAnalyze = async () => {
        setIsAnalyzing(true);
        // Simulate AI analysis
        await new Promise(resolve => setTimeout(resolve, 2000));
        setAiSummary({
            summary: "This email thread discusses Q4 planning at your company. The sender is requesting input on budget allocation, resource planning, and timeline adjustments. Action required by end of week.",
            keyPoints: [
                "Review Q4 planning documents",
                "Provide feedback by end of week",
                "Include risk assessment in discussion"
            ],
            sentiment: "Professional / Urgent",
            suggestedActions: [
                "Review attached documents",
                "Prepare talking points for meeting",
                "Schedule time block for review"
            ]
        });
        setIsAnalyzing(false);
    };

    const toggleMessageExpand = (msgId) => {
        const newExpanded = new Set(expandedMessages);
        if (newExpanded.has(msgId)) {
            newExpanded.delete(msgId);
        } else {
            newExpanded.add(msgId);
        }
        setExpandedMessages(newExpanded);
    };

    const getFileIcon = (type) => {
        switch (type) {
            case 'pdf': return '📄';
            case 'excel': return '📊';
            case 'doc': return '📝';
            case 'image': return '🖼️';
            default: return '📎';
        }
    };

    return (
        <div className="email-thread">
            {/* Thread Header */}
            <div className="email-thread-header">
                <div className="email-thread-header-left">
                    <button onClick={onBack} className="email-back-btn">
                        <ArrowLeft size={20} />
                    </button>
                    <div className="email-thread-title">
                        <h1>{email.subject}</h1>
                        <div className="email-thread-labels">
                            {email.labels.map(label => (
                                <span key={label} className={`email-label-badge ${label}`}>
                                    {label}
                                </span>
                            ))}
                            {email.priority === 'high' && (
                                <span className="email-priority-indicator">
                                    Important
                                </span>
                            )}
                        </div>
                    </div>
                </div>
                <div className="email-thread-header-actions">
                    <button 
                        className={`email-icon-btn ${isStarred ? 'starred' : ''}`}
                        onClick={() => setIsStarred(!isStarred)}
                        title="Star"
                    >
                        <Star size={20} fill={isStarred ? 'currentColor' : 'none'} />
                    </button>
                    <button className="email-icon-btn" title="Archive">
                        <Archive size={20} />
                    </button>
                    <button className="email-icon-btn" title="Delete">
                        <Trash2 size={20} />
                    </button>
                    <button className="email-icon-btn" title="Label">
                        <Tag size={20} />
                    </button>
                    <div className="email-more-menu">
                        <button 
                            className="email-icon-btn"
                            onClick={() => setShowMoreActions(!showMoreActions)}
                        >
                            <MoreHorizontal size={20} />
                        </button>
                        {showMoreActions && (
                            <div className="email-dropdown-menu">
                                <button><MailOpen size={16} /> Mark as unread</button>
                                <button><Printer size={16} /> Print</button>
                                <button><ExternalLink size={16} /> Open in new window</button>
                                <button><Copy size={16} /> Copy link</button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* AI Analysis Card */}
            <div className="email-ai-analysis-card">
                {aiSummary ? (
                    <div className="email-ai-summary">
                        <div className="email-ai-summary-header">
                            <Sparkles size={18} />
                            <span>AI Analysis</span>
                            <button 
                                className="email-ai-refresh"
                                onClick={handleAiAnalyze}
                                disabled={isAnalyzing}
                            >
                                <RefreshCw size={14} className={isAnalyzing ? 'spin' : ''} />
                            </button>
                        </div>
                        <p className="email-ai-summary-text">{aiSummary.summary}</p>
                        
                        <div className="email-ai-sections">
                            <div className="email-ai-section">
                                <h4>Key Points</h4>
                                <ul>
                                    {aiSummary.keyPoints.map((point, i) => (
                                        <li key={i}><CheckCircle size={14} /> {point}</li>
                                    ))}
                                </ul>
                            </div>
                            <div className="email-ai-section">
                                <h4>Suggested Actions</h4>
                                <ul>
                                    {aiSummary.suggestedActions.map((action, i) => (
                                        <li key={i}><Clock size={14} /> {action}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                        
                        <div className="email-ai-sentiment">
                            <span>Tone:</span> {aiSummary.sentiment}
                        </div>
                    </div>
                ) : (
                    <button 
                        className="email-ai-analyze-btn"
                        onClick={handleAiAnalyze}
                        disabled={isAnalyzing}
                    >
                        {isAnalyzing ? (
                            <>
                                <RefreshCw size={18} className="spin" />
                                Analyzing with Medha AI...
                            </>
                        ) : (
                            <>
                                <Sparkles size={18} />
                                Analyze with Medha AI
                            </>
                        )}
                    </button>
                )}
            </div>

            {/* Thread Messages */}
            <div className="email-thread-messages">
                {threadMessages.map((message, index) => {
                    const isExpanded = expandedMessages.has(message.id);
                    const isFromMe = message.from.avatar === 'ME';
                    
                    return (
                        <div 
                            key={message.id} 
                            className={`email-message ${isExpanded ? 'expanded' : ''} ${isFromMe ? 'from-me' : ''}`}
                        >
                            <div 
                                className="email-message-header"
                                onClick={() => toggleMessageExpand(message.id)}
                            >
                                <div 
                                    className="email-message-avatar"
                                    style={{ 
                                        background: isFromMe ? '#00d9ff' : 
                                            message.from.avatar === 'SC' ? '#ec4899' :
                                            message.from.avatar === 'MR' ? '#8b5cf6' : '#6b7280'
                                    }}
                                >
                                    {message.from.avatar}
                                </div>
                                <div className="email-message-info">
                                    <div className="email-message-sender">
                                        <span className="email-message-name">{message.from.name}</span>
                                        <span className="email-message-email">&lt;{message.from.email}&gt;</span>
                                    </div>
                                    <div className="email-message-to">
                                        to {isFromMe ? message.to : 'me'}
                                    </div>
                                </div>
                                <div className="email-message-meta">
                                    <span className="email-message-time">{message.date} at {message.time}</span>
                                    {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                </div>
                            </div>

                            {isExpanded && (
                                <div className="email-message-content">
                                    <div className="email-message-body">
                                        {message.body.split('\n').map((line, i) => (
                                            <React.Fragment key={i}>
                                                {line}
                                                <br />
                                            </React.Fragment>
                                        ))}
                                    </div>

                                    {/* Attachments */}
                                    {message.attachments.length > 0 && (
                                        <div className="email-message-attachments">
                                            <div className="email-attachments-header">
                                                <Paperclip size={16} />
                                                <span>{message.attachments.length} attachment{message.attachments.length > 1 ? 's' : ''}</span>
                                            </div>
                                            <div className="email-attachments-grid">
                                                {message.attachments.map(file => (
                                                    <div key={file.id} className="email-attachment-card">
                                                        <span className="email-attachment-icon">{getFileIcon(file.type)}</span>
                                                        <div className="email-attachment-info">
                                                            <span className="email-attachment-filename">{file.name}</span>
                                                            <span className="email-attachment-filesize">{file.size}</span>
                                                        </div>
                                                        <button className="email-attachment-download">
                                                            <Download size={16} />
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Message Actions */}
                                    <div className="email-message-actions">
                                        <button className="email-action-btn primary" onClick={onReply}>
                                            <Reply size={16} />
                                            Reply
                                        </button>
                                        <button className="email-action-btn">
                                            <ReplyAll size={16} />
                                            Reply All
                                        </button>
                                        <button className="email-action-btn">
                                            <Forward size={16} />
                                            Forward
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Quick Reply */}
            <div className="email-quick-reply">
                <div 
                    className="email-quick-reply-avatar"
                    style={{ background: '#00d9ff' }}
                >
                    ME
                </div>
                <div className="email-quick-reply-input" onClick={onReply}>
                    <span>Click to reply...</span>
                </div>
                <button className="email-quick-reply-btn" onClick={onReply}>
                    <Reply size={18} />
                </button>
            </div>
        </div>
    );
};

export default EmailThread;

