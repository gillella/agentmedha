import React, { useState, useEffect } from 'react';
import {
    AlertCircle, AlertTriangle, Clock, Mail, CheckCircle, TrendingUp,
    RefreshCw, Activity, Zap, Brain, Star, Inbox, Play, Pause,
    BarChart3, ArrowUp, ArrowDown, Minus, Sparkles, Eye, FileText
} from 'lucide-react';
import { mayaApi } from '../../services/mayaApi';

/**
 * Priority Badge Component
 */
const PriorityBadge = ({ priority }) => {
    const config = {
        urgent: { color: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)', icon: AlertCircle, label: 'Urgent' },
        high: { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)', icon: AlertTriangle, label: 'High' },
        normal: { color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.15)', icon: Mail, label: 'Normal' },
        low: { color: '#6b7280', bg: 'rgba(107, 114, 128, 0.15)', icon: Clock, label: 'Low' },
        newsletter: { color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.15)', icon: FileText, label: 'Newsletter' },
    };

    const { color, bg, icon: Icon, label } = config[priority] || config.normal;

    return (
        <span 
            className="priority-badge"
            style={{ 
                color, 
                backgroundColor: bg,
                padding: '2px 8px',
                borderRadius: '12px',
                fontSize: '11px',
                fontWeight: '600',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px'
            }}
        >
            <Icon size={12} />
            {label}
        </span>
    );
};

/**
 * Health Score Gauge
 */
const HealthGauge = ({ score }) => {
    const getColor = (s) => {
        if (s >= 80) return '#10b981';
        if (s >= 60) return '#f59e0b';
        if (s >= 40) return '#f97316';
        return '#ef4444';
    };

    const color = getColor(score);
    const circumference = 2 * Math.PI * 45;
    const strokeDashoffset = circumference - (score / 100) * circumference;

    return (
        <div className="health-gauge">
            <svg width="120" height="120" viewBox="0 0 120 120">
                {/* Background circle */}
                <circle
                    cx="60"
                    cy="60"
                    r="45"
                    fill="none"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="10"
                />
                {/* Progress circle */}
                <circle
                    cx="60"
                    cy="60"
                    r="45"
                    fill="none"
                    stroke={color}
                    strokeWidth="10"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                    transform="rotate(-90 60 60)"
                    style={{ transition: 'stroke-dashoffset 0.5s ease' }}
                />
                {/* Score text */}
                <text
                    x="60"
                    y="55"
                    textAnchor="middle"
                    fill="white"
                    fontSize="24"
                    fontWeight="bold"
                >
                    {Math.round(score)}
                </text>
                <text
                    x="60"
                    y="75"
                    textAnchor="middle"
                    fill="rgba(255,255,255,0.6)"
                    fontSize="12"
                >
                    Health
                </text>
            </svg>
        </div>
    );
};

/**
 * Stat Card Component
 */
const StatCard = ({ icon: Icon, label, value, trend, color = '#3b82f6' }) => (
    <div className="maya-stat-card">
        <div className="stat-icon" style={{ backgroundColor: `${color}20`, color }}>
            <Icon size={18} />
        </div>
        <div className="stat-content">
            <span className="stat-value">{value}</span>
            <span className="stat-label">{label}</span>
        </div>
        {trend !== undefined && (
            <div className={`stat-trend ${trend > 0 ? 'up' : trend < 0 ? 'down' : ''}`}>
                {trend > 0 ? <ArrowUp size={14} /> : trend < 0 ? <ArrowDown size={14} /> : <Minus size={14} />}
                {Math.abs(trend)}%
            </div>
        )}
    </div>
);

/**
 * Maya Dashboard Component
 * Shows email triage, inbox health, and AI insights
 */
const MayaDashboard = ({ onEmailSelect, accountId = 'primary' }) => {
    const [triageData, setTriageData] = useState(null);
    const [healthData, setHealthData] = useState(null);
    const [digestData, setDigestData] = useState(null);
    const [pipelineStatus, setPipelineStatus] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        loadDashboardData();
    }, [accountId]);

    const loadDashboardData = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const [triage, health, digest, pipeline] = await Promise.all([
                mayaApi.triageInbox({ accountId, maxResults: 30 }).catch(() => null),
                mayaApi.getInboxHealth().catch(() => null),
                mayaApi.getDailyDigest(accountId).catch(() => null),
                mayaApi.getPipelineStatus().catch(() => null),
            ]);

            setTriageData(triage);
            setHealthData(health);
            setDigestData(digest);
            setPipelineStatus(pipeline);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const togglePipeline = async () => {
        try {
            if (pipelineStatus?.status === 'running') {
                await mayaApi.stopPipeline();
            } else {
                await mayaApi.startPipeline({
                    check_interval_minutes: 15,
                    auto_draft_urgent: true,
                    notify_urgent: true,
                });
            }
            // Refresh status
            const status = await mayaApi.getPipelineStatus();
            setPipelineStatus(status);
        } catch (err) {
            console.error('Pipeline toggle error:', err);
        }
    };

    const getHealthScore = () => {
        if (!healthData?.accounts?.[accountId]) return 75;
        return healthData.accounts[accountId].health_score || 75;
    };

    const tabs = [
        { id: 'overview', label: 'Overview', icon: BarChart3 },
        { id: 'urgent', label: 'Urgent', icon: AlertCircle },
        { id: 'needs-reply', label: 'Needs Reply', icon: Mail },
        { id: 'digest', label: 'Digest', icon: FileText },
    ];

    if (isLoading) {
        return (
            <div className="maya-dashboard loading">
                <div className="maya-loading-spinner">
                    <Sparkles size={32} className="spinning" />
                    <p>Maya is analyzing your inbox...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="maya-dashboard">
            {/* Header */}
            <div className="maya-dashboard-header">
                <div className="header-left">
                    <div className="maya-brand">
                        <Sparkles size={24} />
                        <h2>Maya Insights</h2>
                    </div>
                    <span className="maya-tagline">Your AI Email Intelligence</span>
                </div>
                <div className="header-actions">
                    <button 
                        className={`pipeline-toggle ${pipelineStatus?.status === 'running' ? 'active' : ''}`}
                        onClick={togglePipeline}
                        title={pipelineStatus?.status === 'running' ? 'Stop Auto-Processing' : 'Start Auto-Processing'}
                    >
                        {pipelineStatus?.status === 'running' ? (
                            <>
                                <Pause size={14} />
                                <span>Auto-Processing</span>
                                <span className="pulse-dot"></span>
                            </>
                        ) : (
                            <>
                                <Play size={14} />
                                <span>Start Pipeline</span>
                            </>
                        )}
                    </button>
                    <button className="refresh-btn" onClick={loadDashboardData}>
                        <RefreshCw size={16} />
                    </button>
                </div>
            </div>

            {/* Stats Row */}
            <div className="maya-stats-row">
                <div className="health-section">
                    <HealthGauge score={getHealthScore()} />
                    <div className="health-label">Inbox Health</div>
                </div>
                <div className="stats-grid">
                    <StatCard 
                        icon={AlertCircle} 
                        label="Urgent" 
                        value={triageData?.urgent || 0} 
                        color="#ef4444"
                    />
                    <StatCard 
                        icon={AlertTriangle} 
                        label="High Priority" 
                        value={triageData?.high || 0} 
                        color="#f59e0b"
                    />
                    <StatCard 
                        icon={Mail} 
                        label="Needs Reply" 
                        value={triageData?.needs_response || 0} 
                        color="#3b82f6"
                    />
                    <StatCard 
                        icon={Inbox} 
                        label="Total Unread" 
                        value={triageData?.total || 0} 
                        color="#8b5cf6"
                    />
                </div>
            </div>

            {/* Tabs */}
            <div className="maya-tabs">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`maya-tab ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        <tab.icon size={14} />
                        {tab.label}
                        {tab.id === 'urgent' && triageData?.urgent > 0 && (
                            <span className="tab-badge urgent">{triageData.urgent}</span>
                        )}
                        {tab.id === 'needs-reply' && triageData?.needs_response > 0 && (
                            <span className="tab-badge">{triageData.needs_response}</span>
                        )}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="maya-tab-content">
                {activeTab === 'overview' && (
                    <div className="overview-content">
                        {digestData?.summary && (
                            <div className="digest-summary">
                                <h4><Brain size={16} /> AI Summary</h4>
                                <p>{digestData.summary}</p>
                            </div>
                        )}
                        
                        <div className="top-emails">
                            <h4><Zap size={16} /> Top Priority Emails</h4>
                            {triageData?.emails?.slice(0, 5).map((email, idx) => (
                                <div 
                                    key={email.id || idx} 
                                    className="triage-email-item"
                                    onClick={() => onEmailSelect?.(email)}
                                >
                                    <div className="email-priority">
                                        <PriorityBadge priority={email.priority} />
                                    </div>
                                    <div className="email-info">
                                        <span className="email-sender">{email.sender}</span>
                                        <span className="email-subject">{email.subject}</span>
                                        {email.summary && (
                                            <span className="email-summary">{email.summary}</span>
                                        )}
                                    </div>
                                    <div className="email-actions">
                                        {email.requires_response && (
                                            <span className="needs-reply-badge">
                                                <Mail size={12} /> Reply needed
                                            </span>
                                        )}
                                        {email.has_deadline && (
                                            <span className="deadline-badge">
                                                <Clock size={12} /> {email.deadline}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'urgent' && (
                    <div className="urgent-content">
                        <h4><AlertCircle size={16} /> Urgent Emails</h4>
                        {triageData?.emails
                            ?.filter(e => e.priority === 'urgent')
                            .map((email, idx) => (
                                <div 
                                    key={email.id || idx} 
                                    className="triage-email-item urgent"
                                    onClick={() => onEmailSelect?.(email)}
                                >
                                    <div className="email-info">
                                        <span className="email-sender">{email.sender}</span>
                                        <span className="email-subject">{email.subject}</span>
                                        {email.summary && (
                                            <span className="email-summary">{email.summary}</span>
                                        )}
                                    </div>
                                    <div className="email-meta">
                                        <span className="email-date">{email.date}</span>
                                        {email.suggested_actions?.length > 0 && (
                                            <div className="suggested-actions">
                                                <strong>Suggested:</strong>
                                                <ul>
                                                    {email.suggested_actions.map((action, i) => (
                                                        <li key={i}>{action}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )) || <p className="no-emails">No urgent emails! 🎉</p>}
                    </div>
                )}

                {activeTab === 'needs-reply' && (
                    <div className="needs-reply-content">
                        <h4><Mail size={16} /> Awaiting Your Response</h4>
                        {triageData?.emails
                            ?.filter(e => e.requires_response)
                            .map((email, idx) => (
                                <div 
                                    key={email.id || idx} 
                                    className="triage-email-item"
                                    onClick={() => onEmailSelect?.(email)}
                                >
                                    <PriorityBadge priority={email.priority} />
                                    <div className="email-info">
                                        <span className="email-sender">{email.sender}</span>
                                        <span className="email-subject">{email.subject}</span>
                                    </div>
                                    {email.suggested_response && (
                                        <div className="suggested-response">
                                            <Eye size={12} /> Preview response
                                        </div>
                                    )}
                                </div>
                            )) || <p className="no-emails">All caught up! ✅</p>}
                    </div>
                )}

                {activeTab === 'digest' && (
                    <div className="digest-content">
                        <h4><FileText size={16} /> Daily Digest</h4>
                        {digestData ? (
                            <>
                                <div className="digest-stats">
                                    <div className="digest-stat">
                                        <span className="label">Total Unread</span>
                                        <span className="value">{digestData.total_unread}</span>
                                    </div>
                                    <div className="digest-stat urgent">
                                        <span className="label">Urgent</span>
                                        <span className="value">{digestData.urgent_count}</span>
                                    </div>
                                    <div className="digest-stat">
                                        <span className="label">High Priority</span>
                                        <span className="value">{digestData.high_priority_count}</span>
                                    </div>
                                    <div className="digest-stat">
                                        <span className="label">Newsletters</span>
                                        <span className="value">{digestData.newsletter_count}</span>
                                    </div>
                                </div>
                                <div className="digest-summary-full">
                                    <h5>Summary</h5>
                                    <p>{digestData.summary}</p>
                                </div>
                            </>
                        ) : (
                            <p className="no-digest">Digest not available yet.</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default MayaDashboard;

