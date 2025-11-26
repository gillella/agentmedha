import React, { useState } from 'react';
import {
    TrendingUp, TrendingDown, Users, Eye, Heart, MessageCircle,
    Share2, BarChart3, Twitter, Linkedin, Youtube, Instagram,
    ArrowUp, ArrowDown, Minus, Calendar, RefreshCw
} from 'lucide-react';

// Mock analytics data
const ANALYTICS_DATA = {
    overview: {
        followers: { value: 12453, change: 5.2 },
        impressions: { value: 89234, change: 12.8 },
        engagement: { value: 4.2, change: -0.3, isPercentage: true },
        reach: { value: 45678, change: 8.1 },
    },
    platforms: {
        twitter: {
            followers: 5234,
            impressions: 34567,
            engagement: 3.8,
            topPost: 'Excited to share our latest update!',
        },
        linkedin: {
            followers: 3421,
            impressions: 28456,
            engagement: 5.2,
            topPost: 'New insights on AI in business',
        },
        youtube: {
            subscribers: 2890,
            views: 18234,
            watchTime: 1234,
            topVideo: 'Getting Started Tutorial',
        },
        instagram: {
            followers: 908,
            impressions: 7977,
            engagement: 6.1,
            topPost: 'Behind the scenes',
        },
    },
    recentPosts: [
        { id: 1, platform: 'twitter', content: 'Great news!...', impressions: 1234, engagement: 4.5, date: '2 hours ago' },
        { id: 2, platform: 'linkedin', content: 'Excited to announce...', impressions: 2345, engagement: 6.2, date: '1 day ago' },
        { id: 3, platform: 'instagram', content: 'New product...', impressions: 890, engagement: 8.1, date: '2 days ago' },
    ],
};

const PLATFORM_COLORS = {
    twitter: '#1DA1F2',
    linkedin: '#0A66C2',
    youtube: '#FF0000',
    instagram: '#E1306C',
};

const PLATFORM_ICONS = {
    twitter: Twitter,
    linkedin: Linkedin,
    youtube: Youtube,
    instagram: Instagram,
};

const AnalyticsView = ({ accounts }) => {
    const [timeRange, setTimeRange] = useState('7d'); // 7d, 30d, 90d
    const [selectedPlatform, setSelectedPlatform] = useState('all');

    // Stat Card Component
    const StatCard = ({ icon: Icon, label, value, change, isPercentage, color }) => (
        <div style={{
            padding: '20px',
            background: 'var(--social-card-bg)',
            border: '1px solid var(--social-border)',
            borderRadius: '12px',
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '10px',
                    background: color ? `${color}20` : 'rgba(139, 92, 246, 0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: color || 'var(--social-accent)'
                }}>
                    <Icon size={20} />
                </div>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '12px',
                    color: change > 0 ? '#10b981' : change < 0 ? '#ef4444' : 'var(--social-text-muted)'
                }}>
                    {change > 0 ? <ArrowUp size={14} /> : change < 0 ? <ArrowDown size={14} /> : <Minus size={14} />}
                    {Math.abs(change)}%
                </div>
            </div>
            <div style={{ fontSize: '28px', fontWeight: '600', color: 'white', marginBottom: '4px' }}>
                {typeof value === 'number' ? value.toLocaleString() : value}
                {isPercentage && '%'}
            </div>
            <div style={{ fontSize: '13px', color: 'var(--social-text-secondary)' }}>
                {label}
            </div>
        </div>
    );

    return (
        <div>
            {/* Header */}
            <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '24px'
            }}>
                <div>
                    <h2 style={{ margin: 0, color: 'white', fontSize: '20px' }}>Analytics Overview</h2>
                    <p style={{ margin: '4px 0 0', color: 'var(--social-text-secondary)', fontSize: '13px' }}>
                        Track your social media performance
                    </p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                    {/* Time Range Selector */}
                    <div style={{ display: 'flex', gap: '4px' }}>
                        {[
                            { id: '7d', label: '7 Days' },
                            { id: '30d', label: '30 Days' },
                            { id: '90d', label: '90 Days' },
                        ].map(range => (
                            <button
                                key={range.id}
                                className={`preview-tab ${timeRange === range.id ? 'active' : ''}`}
                                onClick={() => setTimeRange(range.id)}
                            >
                                {range.label}
                            </button>
                        ))}
                    </div>
                    <button className="social-back-btn">
                        <RefreshCw size={14} />
                    </button>
                </div>
            </div>

            {/* Overview Stats */}
            <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(4, 1fr)', 
                gap: '16px',
                marginBottom: '24px'
            }}>
                <StatCard
                    icon={Users}
                    label="Total Followers"
                    value={ANALYTICS_DATA.overview.followers.value}
                    change={ANALYTICS_DATA.overview.followers.change}
                    color="#8b5cf6"
                />
                <StatCard
                    icon={Eye}
                    label="Impressions"
                    value={ANALYTICS_DATA.overview.impressions.value}
                    change={ANALYTICS_DATA.overview.impressions.change}
                    color="#3b82f6"
                />
                <StatCard
                    icon={Heart}
                    label="Engagement Rate"
                    value={ANALYTICS_DATA.overview.engagement.value}
                    change={ANALYTICS_DATA.overview.engagement.change}
                    isPercentage
                    color="#ef4444"
                />
                <StatCard
                    icon={Share2}
                    label="Reach"
                    value={ANALYTICS_DATA.overview.reach.value}
                    change={ANALYTICS_DATA.overview.reach.change}
                    color="#10b981"
                />
            </div>

            {/* Platform Breakdown */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
                {/* Platform Cards */}
                <div className="schedule-panel">
                    <div className="schedule-title" style={{ marginBottom: '16px' }}>
                        <BarChart3 size={16} />
                        <span>Platform Performance</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
                        {Object.entries(ANALYTICS_DATA.platforms).map(([platform, data]) => {
                            const Icon = PLATFORM_ICONS[platform];
                            const color = PLATFORM_COLORS[platform];
                            return (
                                <div
                                    key={platform}
                                    style={{
                                        padding: '16px',
                                        background: 'rgba(0, 0, 0, 0.2)',
                                        border: '1px solid var(--social-border)',
                                        borderRadius: '10px',
                                        cursor: 'pointer',
                                        transition: 'all 0.2s'
                                    }}
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                                        <div style={{
                                            width: '32px',
                                            height: '32px',
                                            borderRadius: '8px',
                                            background: `${color}20`,
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}>
                                            {Icon && <Icon size={16} style={{ color }} />}
                                        </div>
                                        <span style={{ 
                                            fontSize: '14px', 
                                            fontWeight: '600', 
                                            color: 'white',
                                            textTransform: 'capitalize'
                                        }}>
                                            {platform}
                                        </span>
                                    </div>
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
                                        <div>
                                            <div style={{ fontSize: '18px', fontWeight: '600', color: 'white' }}>
                                                {(data.followers || data.subscribers || 0).toLocaleString()}
                                            </div>
                                            <div style={{ fontSize: '11px', color: 'var(--social-text-muted)' }}>
                                                {platform === 'youtube' ? 'Subscribers' : 'Followers'}
                                            </div>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: '18px', fontWeight: '600', color: 'white' }}>
                                                {(data.impressions || data.views || 0).toLocaleString()}
                                            </div>
                                            <div style={{ fontSize: '11px', color: 'var(--social-text-muted)' }}>
                                                {platform === 'youtube' ? 'Views' : 'Impressions'}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Recent Posts Performance */}
                <div className="schedule-panel">
                    <div className="schedule-title" style={{ marginBottom: '16px' }}>
                        <TrendingUp size={16} />
                        <span>Recent Posts</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {ANALYTICS_DATA.recentPosts.map(post => {
                            const Icon = PLATFORM_ICONS[post.platform];
                            const color = PLATFORM_COLORS[post.platform];
                            return (
                                <div
                                    key={post.id}
                                    style={{
                                        padding: '14px',
                                        background: 'rgba(0, 0, 0, 0.2)',
                                        border: '1px solid var(--social-border)',
                                        borderRadius: '10px',
                                    }}
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                        {Icon && <Icon size={14} style={{ color }} />}
                                        <span style={{ fontSize: '12px', color: 'var(--social-text-muted)' }}>
                                            {post.date}
                                        </span>
                                    </div>
                                    <p style={{ 
                                        margin: '0 0 8px', 
                                        fontSize: '13px', 
                                        color: 'var(--social-text-primary)',
                                        lineHeight: '1.4'
                                    }}>
                                        {post.content}
                                    </p>
                                    <div style={{ display: 'flex', gap: '16px' }}>
                                        <span style={{ fontSize: '12px', color: 'var(--social-text-muted)' }}>
                                            <Eye size={12} style={{ marginRight: '4px' }} />
                                            {post.impressions.toLocaleString()}
                                        </span>
                                        <span style={{ fontSize: '12px', color: 'var(--social-text-muted)' }}>
                                            <Heart size={12} style={{ marginRight: '4px' }} />
                                            {post.engagement}%
                                        </span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsView;

