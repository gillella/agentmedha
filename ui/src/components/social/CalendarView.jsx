import React, { useState } from 'react';
import {
    ChevronLeft, ChevronRight, Plus, Clock, Twitter, Linkedin,
    Youtube, Instagram, MoreHorizontal, Edit2, Trash2, Eye
} from 'lucide-react';

// Platform icons mapping
const PLATFORM_ICONS = {
    twitter: Twitter,
    linkedin: Linkedin,
    youtube: Youtube,
    instagram: Instagram,
};

// Mock scheduled posts
const MOCK_SCHEDULED = [
    {
        id: '1',
        content: 'Excited to share our latest product update! 🚀',
        platforms: ['twitter', 'linkedin'],
        scheduledFor: new Date(2025, 10, 27, 9, 0),
        media: null,
    },
    {
        id: '2',
        content: 'New video tutorial coming soon! Stay tuned 🎬',
        platforms: ['youtube'],
        scheduledFor: new Date(2025, 10, 28, 14, 0),
        media: null,
    },
    {
        id: '3',
        content: 'Behind the scenes of our creative process ✨',
        platforms: ['instagram'],
        scheduledFor: new Date(2025, 10, 29, 11, 0),
        media: null,
    },
];

const CalendarView = ({ scheduled = MOCK_SCHEDULED }) => {
    const [currentDate, setCurrentDate] = useState(new Date());
    const [selectedDate, setSelectedDate] = useState(null);
    const [viewMode, setViewMode] = useState('month'); // month, week, day

    // Calendar helpers
    const daysInMonth = new Date(
        currentDate.getFullYear(),
        currentDate.getMonth() + 1,
        0
    ).getDate();

    const firstDayOfMonth = new Date(
        currentDate.getFullYear(),
        currentDate.getMonth(),
        1
    ).getDay();

    const monthNames = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];

    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    // Navigate months
    const prevMonth = () => {
        setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
    };

    const nextMonth = () => {
        setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
    };

    // Check if date has posts
    const getPostsForDate = (day) => {
        return scheduled.filter(post => {
            const postDate = new Date(post.scheduledFor);
            return postDate.getDate() === day &&
                   postDate.getMonth() === currentDate.getMonth() &&
                   postDate.getFullYear() === currentDate.getFullYear();
        });
    };

    // Check if today
    const isToday = (day) => {
        const today = new Date();
        return day === today.getDate() &&
               currentDate.getMonth() === today.getMonth() &&
               currentDate.getFullYear() === today.getFullYear();
    };

    // Generate calendar days
    const renderCalendarDays = () => {
        const days = [];
        
        // Previous month days
        for (let i = 0; i < firstDayOfMonth; i++) {
            const prevMonthDays = new Date(
                currentDate.getFullYear(),
                currentDate.getMonth(),
                0
            ).getDate();
            days.push(
                <div key={`prev-${i}`} className="calendar-day other-month">
                    <span className="calendar-day-number">
                        {prevMonthDays - firstDayOfMonth + i + 1}
                    </span>
                </div>
            );
        }

        // Current month days
        for (let day = 1; day <= daysInMonth; day++) {
            const posts = getPostsForDate(day);
            const hasPost = posts.length > 0;
            
            days.push(
                <div
                    key={day}
                    className={`calendar-day ${isToday(day) ? 'today' : ''} ${hasPost ? 'has-posts' : ''}`}
                    onClick={() => setSelectedDate(day)}
                >
                    <span className="calendar-day-number">{day}</span>
                    {hasPost && (
                        <div style={{ 
                            display: 'flex', 
                            gap: '2px', 
                            marginTop: '4px',
                            flexWrap: 'wrap'
                        }}>
                            {posts.slice(0, 3).map((post, idx) => (
                                <div
                                    key={idx}
                                    style={{
                                        width: '6px',
                                        height: '6px',
                                        borderRadius: '50%',
                                        background: 'var(--social-accent)'
                                    }}
                                />
                            ))}
                        </div>
                    )}
                </div>
            );
        }

        // Next month days
        const remainingDays = 42 - days.length;
        for (let i = 1; i <= remainingDays; i++) {
            days.push(
                <div key={`next-${i}`} className="calendar-day other-month">
                    <span className="calendar-day-number">{i}</span>
                </div>
            );
        }

        return days;
    };

    // Render upcoming posts
    const upcomingPosts = scheduled
        .filter(post => new Date(post.scheduledFor) > new Date())
        .sort((a, b) => new Date(a.scheduledFor) - new Date(b.scheduledFor))
        .slice(0, 5);

    return (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '24px' }}>
            {/* Calendar */}
            <div className="calendar-view">
                <div className="calendar-header">
                    <div className="calendar-nav">
                        <button className="calendar-nav-btn" onClick={prevMonth}>
                            <ChevronLeft size={16} />
                        </button>
                        <h2 className="calendar-month">
                            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
                        </h2>
                        <button className="calendar-nav-btn" onClick={nextMonth}>
                            <ChevronRight size={16} />
                        </button>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        {['month', 'week', 'day'].map(mode => (
                            <button
                                key={mode}
                                className={`preview-tab ${viewMode === mode ? 'active' : ''}`}
                                onClick={() => setViewMode(mode)}
                                style={{ textTransform: 'capitalize' }}
                            >
                                {mode}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="calendar-grid">
                    {dayNames.map(day => (
                        <div key={day} className="calendar-day-header">{day}</div>
                    ))}
                    {renderCalendarDays()}
                </div>
            </div>

            {/* Upcoming Posts Sidebar */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="schedule-panel">
                    <div className="schedule-header">
                        <div className="schedule-title">
                            <Clock size={16} />
                            <span>Upcoming Posts</span>
                        </div>
                        <button className="ai-assist-btn" style={{ padding: '6px 12px' }}>
                            <Plus size={14} />
                            New
                        </button>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
                        {upcomingPosts.length === 0 ? (
                            <p style={{ 
                                color: 'var(--social-text-muted)', 
                                textAlign: 'center',
                                padding: '20px'
                            }}>
                                No scheduled posts
                            </p>
                        ) : (
                            upcomingPosts.map(post => (
                                <div
                                    key={post.id}
                                    style={{
                                        padding: '14px',
                                        background: 'rgba(0, 0, 0, 0.2)',
                                        border: '1px solid var(--social-border)',
                                        borderRadius: '10px',
                                    }}
                                >
                                    <div style={{ 
                                        display: 'flex', 
                                        justifyContent: 'space-between',
                                        alignItems: 'flex-start',
                                        marginBottom: '8px'
                                    }}>
                                        <div style={{ display: 'flex', gap: '6px' }}>
                                            {post.platforms.map(platform => {
                                                const Icon = PLATFORM_ICONS[platform];
                                                return Icon ? (
                                                    <Icon 
                                                        key={platform} 
                                                        size={14} 
                                                        style={{ 
                                                            color: platform === 'twitter' ? '#1DA1F2' :
                                                                   platform === 'linkedin' ? '#0A66C2' :
                                                                   platform === 'youtube' ? '#FF0000' :
                                                                   '#E1306C'
                                                        }}
                                                    />
                                                ) : null;
                                            })}
                                        </div>
                                        <button style={{
                                            background: 'none',
                                            border: 'none',
                                            color: 'var(--social-text-muted)',
                                            cursor: 'pointer'
                                        }}>
                                            <MoreHorizontal size={14} />
                                        </button>
                                    </div>
                                    <p style={{ 
                                        color: 'var(--social-text-primary)',
                                        fontSize: '13px',
                                        marginBottom: '8px',
                                        lineHeight: '1.4'
                                    }}>
                                        {post.content.slice(0, 80)}...
                                    </p>
                                    <div style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '6px',
                                        color: 'var(--social-text-muted)',
                                        fontSize: '12px'
                                    }}>
                                        <Clock size={12} />
                                        {new Date(post.scheduledFor).toLocaleDateString('en-US', {
                                            month: 'short',
                                            day: 'numeric',
                                            hour: 'numeric',
                                            minute: '2-digit'
                                        })}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Quick Stats */}
                <div className="schedule-panel">
                    <div className="schedule-title" style={{ marginBottom: '16px' }}>
                        <span>This Week</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                        <div style={{ textAlign: 'center', padding: '16px', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '10px' }}>
                            <div style={{ fontSize: '24px', fontWeight: '600', color: 'white' }}>
                                {scheduled.length}
                            </div>
                            <div style={{ fontSize: '12px', color: 'var(--social-text-secondary)' }}>
                                Scheduled
                            </div>
                        </div>
                        <div style={{ textAlign: 'center', padding: '16px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '10px' }}>
                            <div style={{ fontSize: '24px', fontWeight: '600', color: 'white' }}>
                                12
                            </div>
                            <div style={{ fontSize: '12px', color: 'var(--social-text-secondary)' }}>
                                Published
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CalendarView;

