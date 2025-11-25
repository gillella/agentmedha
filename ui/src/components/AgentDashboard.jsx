import React, { useState, useEffect } from 'react';
import AgentCard from './AgentCard';
import { Activity, Filter, Search } from 'lucide-react';

const AgentDashboard = () => {
    const [agents, setAgents] = useState([
        {
            agentId: 'agent-1',
            name: 'Twitter Agent',
            type: 'social',
            status: 'active',
            lastActivity: new Date(Date.now() - 5 * 60000).toISOString(),
            currentTask: 'Monitoring social media mentions and scheduling posts'
        },
        {
            agentId: 'agent-2',
            name: 'Research Agent',
            type: 'research',
            status: 'idle',
            lastActivity: new Date(Date.now() - 30 * 60000).toISOString(),
            currentTask: null
        },
        {
            agentId: 'agent-3',
            name: 'Chat Assistant',
            type: 'chat',
            status: 'working',
            lastActivity: new Date(Date.now() - 1 * 60000).toISOString(),
            currentTask: 'Processing user query about API documentation'
        }
    ]);

    const [filterStatus, setFilterStatus] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');

    // Filter agents based on status and search
    const filteredAgents = agents.filter(agent => {
        const matchesStatus = filterStatus === 'all' || agent.status === filterStatus;
        const matchesSearch = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            agent.type.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesStatus && matchesSearch;
    });

    const handleViewDetails = (agentId) => {
        // TODO: Implement agent details modal or navigation
    };

    // Count agents by status
    const statusCounts = {
        all: agents.length,
        active: agents.filter(a => a.status === 'active').length,
        working: agents.filter(a => a.status === 'working').length,
        idle: agents.filter(a => a.status === 'idle').length,
        error: agents.filter(a => a.status === 'error').length
    };

    return (
        <div className="flex flex-col gap-6">
            {/* Dashboard Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white">Agent Coordination</h2>
                    <p className="text-sm text-gray-400 mt-1">
                        {agents.length} agent{agents.length !== 1 ? 's' : ''} • {statusCounts.active} active • {statusCounts.working} working
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    {/* Search */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                        <input
                            type="text"
                            placeholder="Search agents..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-10 pr-4 py-2 bg-black/20 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500/50"
                        />
                    </div>

                    {/* Status Filter */}
                    <div className="flex items-center gap-2 bg-black/20 border border-white/10 rounded-lg p-1">
                        <Filter size={16} className="text-gray-400 ml-2" />
                        <select
                            value={filterStatus}
                            onChange={(e) => setFilterStatus(e.target.value)}
                            className="bg-transparent text-white text-sm pr-8 py-1 focus:outline-none cursor-pointer"
                        >
                            <option value="all">All ({statusCounts.all})</option>
                            <option value="active">Active ({statusCounts.active})</option>
                            <option value="working">Working ({statusCounts.working})</option>
                            <option value="idle">Idle ({statusCounts.idle})</option>
                            <option value="error">Error ({statusCounts.error})</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Agent Grid */}
            <div className="agent-dashboard-grid">
                {filteredAgents.map(agent => (
                    <AgentCard
                        key={agent.agentId}
                        {...agent}
                        onViewDetails={() => handleViewDetails(agent.agentId)}
                    />
                ))}
            </div>

            {/* Empty State */}
            {filteredAgents.length === 0 && (
                <div className="text-center py-12">
                    <Activity size={48} className="text-gray-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-400 mb-2">No agents found</h3>
                    <p className="text-sm text-gray-500">
                        {searchQuery ? 'Try adjusting your search or filter' : 'No agents match the selected filter'}
                    </p>
                </div>
            )}

            {/* Activity Timeline Section */}
            <div className="glass-panel p-6 mt-4">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Activity size={20} className="text-purple-400" />
                    Recent Activity
                </h3>
                <div className="activity-timeline">
                    {/* Sample activity items */}
                    <div className="activity-item">
                        <div className="activity-icon" style={{ backgroundColor: 'rgba(6, 182, 212, 0.2)', color: '#06b6d4' }}>
                            <Activity size={16} />
                        </div>
                        <div className="activity-content">
                            <div className="activity-title">Twitter Agent posted a tweet</div>
                            <div className="activity-description">
                                Successfully posted: "Exploring the latest in AI agent coordination..."
                            </div>
                            <div className="activity-timestamp">5 minutes ago</div>
                        </div>
                    </div>

                    <div className="activity-item">
                        <div className="activity-icon" style={{ backgroundColor: 'rgba(59, 130, 246, 0.2)', color: '#3b82f6' }}>
                            <Activity size={16} />
                        </div>
                        <div className="activity-content">
                            <div className="activity-title">Chat Assistant completed task</div>
                            <div className="activity-description">
                                Responded to user query about API documentation
                            </div>
                            <div className="activity-timestamp">12 minutes ago</div>
                        </div>
                    </div>

                    <div className="activity-item">
                        <div className="activity-icon" style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#10b981' }}>
                            <Activity size={16} />
                        </div>
                        <div className="activity-content">
                            <div className="activity-title">Research Agent started</div>
                            <div className="activity-description">
                                Initialized and ready for research tasks
                            </div>
                            <div className="activity-timestamp">30 minutes ago</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AgentDashboard;
