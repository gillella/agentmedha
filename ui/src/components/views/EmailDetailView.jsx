import React, { useState } from 'react';
import { Mail, Star, Clock, AlertCircle, Archive, Trash2, Reply, Forward, CheckCircle2 } from 'lucide-react';
import DetailViewLayout from '../DetailViewLayout';

const EmailDetailView = () => {
    const [activeTab, setActiveTab] = useState('priority');

    const priorityEmails = [
        { id: 1, from: 'boss@company.com', subject: 'Q4 Planning Meeting - Action Required', preview: 'Please review the attached proposal before...', time: '10m ago', priority: 'urgent', unread: true },
        { id: 2, from: 'finance@company.com', subject: 'Monthly Budget Report', preview: 'Your department budget utilization for...', time: '1h ago', priority: 'high', unread: true },
        { id: 3, from: 'hr@company.com', subject: 'Benefits Enrollment Deadline', preview: 'Reminder: Open enrollment closes on...', time: '2h ago', priority: 'high', unread: false },
    ];

    const alerts = [
        { id: 1, type: 'financial', message: 'Large transaction detected: $2,450 at Electronics Store', time: '30m ago' },
        { id: 2, type: 'calendar', message: 'Meeting in 1 hour: Product Review', time: '1h ago' },
    ];

    const getPriorityColor = (priority) => {
        switch (priority) {
            case 'urgent': return 'bg-red-500/20 text-red-400 border-red-500/30';
            case 'high': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
            default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
        }
    };

    return (
        <DetailViewLayout title="Email & Alerts" icon={Mail} currentDomain="email">
            <div className="email-detail">
                {/* Stats Overview */}
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(239, 68, 68, 0.1)' }}>
                            <AlertCircle size={24} className="text-red-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">3</span>
                            <span className="stat-label">Urgent Emails</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(59, 130, 246, 0.1)' }}>
                            <Mail size={24} className="text-blue-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">12</span>
                            <span className="stat-label">Unread Total</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.1)' }}>
                            <Star size={24} className="text-yellow-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">5</span>
                            <span className="stat-label">Starred</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.1)' }}>
                            <CheckCircle2 size={24} className="text-green-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">24</span>
                            <span className="stat-label">Processed Today</span>
                        </div>
                    </div>
                </div>

                {/* Tab Navigation */}
                <div className="detail-tabs">
                    <button 
                        className={`detail-tab ${activeTab === 'priority' ? 'active' : ''}`}
                        onClick={() => setActiveTab('priority')}
                    >
                        Priority Inbox
                    </button>
                    <button 
                        className={`detail-tab ${activeTab === 'alerts' ? 'active' : ''}`}
                        onClick={() => setActiveTab('alerts')}
                    >
                        Alerts ({alerts.length})
                    </button>
                    <button 
                        className={`detail-tab ${activeTab === 'compose' ? 'active' : ''}`}
                        onClick={() => setActiveTab('compose')}
                    >
                        Compose
                    </button>
                </div>

                {/* Tab Content */}
                <div className="tab-content">
                    {activeTab === 'priority' && (
                        <div className="email-list">
                            {priorityEmails.map((email) => (
                                <div key={email.id} className={`email-item ${email.unread ? 'unread' : ''}`}>
                                    <div className="email-header">
                                        <span className="email-from">{email.from}</span>
                                        <span className={`priority-badge ${getPriorityColor(email.priority)}`}>
                                            {email.priority}
                                        </span>
                                        <span className="email-time">{email.time}</span>
                                    </div>
                                    <h4 className="email-subject">{email.subject}</h4>
                                    <p className="email-preview">{email.preview}</p>
                                    <div className="email-actions">
                                        <button className="action-btn"><Reply size={14} /> Reply</button>
                                        <button className="action-btn"><Forward size={14} /> Forward</button>
                                        <button className="action-btn"><Archive size={14} /> Archive</button>
                                        <button className="action-btn text-red-400"><Trash2 size={14} /></button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {activeTab === 'alerts' && (
                        <div className="alerts-list">
                            {alerts.map((alert) => (
                                <div key={alert.id} className="alert-item">
                                    <AlertCircle size={20} className="text-yellow-400" />
                                    <div className="alert-content">
                                        <p>{alert.message}</p>
                                        <span className="alert-time">{alert.time}</span>
                                    </div>
                                    <button className="btn-secondary">Dismiss</button>
                                </div>
                            ))}
                        </div>
                    )}

                    {activeTab === 'compose' && (
                        <div className="compose-email">
                            <input type="text" className="form-input" placeholder="To:" />
                            <input type="text" className="form-input" placeholder="Subject:" />
                            <textarea 
                                className="compose-input" 
                                placeholder="Write your email... or ask Medha to draft it for you"
                                rows={8}
                            />
                            <div className="compose-footer">
                                <button className="btn-secondary">Save Draft</button>
                                <button className="btn-primary">Send Email</button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </DetailViewLayout>
    );
};

export default EmailDetailView;


