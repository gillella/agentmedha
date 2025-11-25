import React from 'react';
import { Bot, Twitter, Search, MessageSquare, Zap } from 'lucide-react';

const AgentCard = ({
    agentId,
    name,
    type,
    status,
    lastActivity,
    currentTask,
    onViewDetails
}) => {
    // Map agent types to icons and colors
    const agentTypeConfig = {
        coordinator: { icon: Zap, color: '#8b5cf6', bgColor: 'rgba(139, 92, 246, 0.2)' },
        chat: { icon: MessageSquare, color: '#3b82f6', bgColor: 'rgba(59, 130, 246, 0.2)' },
        social: { icon: Twitter, color: '#06b6d4', bgColor: 'rgba(6, 182, 212, 0.2)' },
        research: { icon: Search, color: '#10b981', bgColor: 'rgba(16, 185, 129, 0.2)' },
        custom: { icon: Bot, color: '#f59e0b', bgColor: 'rgba(245, 158, 11, 0.2)' }
    };

    const config = agentTypeConfig[type] || agentTypeConfig.custom;
    const IconComponent = config.icon;

    // Format timestamp
    const formatTimestamp = (timestamp) => {
        if (!timestamp) return 'Never';
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        const diffDays = Math.floor(diffHours / 24);
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    };

    return (
        <div className="agent-card animate-scale-in" onClick={onViewDetails}>
            <div className="agent-card-header">
                <div className="agent-card-title">
                    <div
                        className="agent-icon"
                        style={{
                            backgroundColor: config.bgColor,
                            color: config.color
                        }}
                    >
                        <IconComponent size={20} />
                    </div>
                    <div>
                        <h3 className="text-white font-semibold text-base">{name}</h3>
                        <p className="text-xs text-gray-400 capitalize">{type}</p>
                    </div>
                </div>
                <div className={`status-badge ${status}`}>
                    <div className="status-indicator" />
                    {status}
                </div>
            </div>

            <div className="agent-card-body">
                <p className="agent-task-description">
                    {currentTask || 'No active task'}
                </p>
            </div>

            <div className="agent-card-footer">
                <span className="agent-timestamp">
                    {formatTimestamp(lastActivity)}
                </span>
                <button
                    className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
                    onClick={(e) => {
                        e.stopPropagation();
                        onViewDetails?.();
                    }}
                >
                    View Details →
                </button>
            </div>
        </div>
    );
};

export default AgentCard;
