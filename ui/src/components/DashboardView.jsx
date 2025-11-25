import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Twitter, Mail, Home, Heart, DollarSign, TrendingUp, Linkedin, Instagram, Lightbulb, Camera, ArrowRight } from 'lucide-react';

const DashboardCard = ({ title, icon: Icon, color, path, children, stats }) => {
    const navigate = useNavigate();

    return (
        <div 
            className="dashboard-card"
            onClick={() => navigate(path)}
            style={{ '--card-color': color }}
        >
            <div className="card-header">
                <div className="card-icon" style={{ background: `${color}15`, color }}>
                    <Icon size={22} />
                </div>
                <h3 className="card-title">{title}</h3>
                <ArrowRight size={18} className="card-arrow" />
            </div>
            
            <div className="card-content">
                {children}
            </div>

            {stats && (
                <div className="card-stats">
                    {stats.map((stat, idx) => (
                        <div key={idx} className="card-stat">
                            <span className="stat-value">{stat.value}</span>
                            <span className="stat-label">{stat.label}</span>
                        </div>
                    ))}
                </div>
            )}

            <div className="card-footer">
                <span className="card-hint">Click to open</span>
            </div>
        </div>
    );
};

const DashboardView = () => {
    return (
        <div className="dashboard-view">
            <div className="dashboard-header">
                <h1>Welcome back</h1>
                <p>Your personal AI agents are ready to assist</p>
            </div>

            <div className="dashboard-cards">
                {/* Social Media Card */}
                <DashboardCard
                    title="Social Media"
                    icon={Twitter}
                    color="#00d9ff"
                    path="/social"
                    stats={[
                        { value: '5', label: 'Mentions' },
                        { value: '2', label: 'Scheduled' },
                        { value: '+12%', label: 'Engagement' },
                    ]}
                >
                    <div className="card-platforms">
                        <Twitter size={16} className="text-blue-400" />
                        <Linkedin size={16} className="text-blue-500" />
                        <Instagram size={16} className="text-pink-500" />
                    </div>
                    <div className="mini-chart">
                        <svg width="100%" height="40" viewBox="0 0 200 40" preserveAspectRatio="none">
                            <defs>
                                <linearGradient id="socialGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                    <stop offset="0%" stopColor="rgba(0, 217, 255, 0.3)" />
                                    <stop offset="100%" stopColor="rgba(0, 217, 255, 0)" />
                                </linearGradient>
                            </defs>
                            <path d="M 0,30 Q 50,20 100,25 T 200,15" fill="none" stroke="rgba(0, 217, 255, 0.8)" strokeWidth="2" />
                            <path d="M 0,30 Q 50,20 100,25 T 200,15 L 200,40 L 0,40 Z" fill="url(#socialGradient)" />
                        </svg>
                    </div>
                </DashboardCard>

                {/* Email Card */}
                <DashboardCard
                    title="Email Priority"
                    icon={Mail}
                    color="#3b82f6"
                    path="/email"
                    stats={[
                        { value: '3', label: 'Urgent' },
                        { value: '12', label: 'Unread' },
                        { value: '24', label: 'Processed' },
                    ]}
                >
                    <div className="priority-list">
                        <div className="priority-item urgent">
                            <span className="priority-dot"></span>
                            <span>3 Urgent from Work</span>
                        </div>
                        <div className="priority-item alert">
                            <span className="priority-dot"></span>
                            <span>1 Financial Alert</span>
                        </div>
                    </div>
                </DashboardCard>

                {/* Habitat Card */}
                <DashboardCard
                    title="Habitat Status"
                    icon={Home}
                    color="#10b981"
                    path="/habitat"
                    stats={[
                        { value: '72°F', label: 'Temp' },
                        { value: '3/4', label: 'Lights' },
                        { value: 'Secure', label: 'Status' },
                    ]}
                >
                    <div className="habitat-quick">
                        <div className="habitat-item">
                            <Lightbulb size={14} className="text-yellow-400" />
                            <span>Living Room: ON (60%)</span>
                        </div>
                        <div className="habitat-item">
                            <Camera size={14} className="text-cyan-400" />
                            <span>Front Camera: Active</span>
                        </div>
                    </div>
                </DashboardCard>

                {/* Dependent Care Card */}
                <DashboardCard
                    title="Dependent Care"
                    icon={Heart}
                    color="#f472b6"
                    path="/care"
                    stats={[
                        { value: '80%', label: 'Food' },
                        { value: '90%', label: 'Water' },
                        { value: 'Active', label: 'Status' },
                    ]}
                >
                    <div className="care-status">
                        <div className="pet-quick">
                            <span className="pet-emoji">🐱</span>
                            <div className="pet-info">
                                <span className="pet-name">Luna</span>
                                <span className="pet-activity">Last fed 10m ago</span>
                            </div>
                        </div>
                    </div>
                </DashboardCard>

                {/* Finance Card */}
                <DashboardCard
                    title="Financial Overview"
                    icon={DollarSign}
                    color="#f59e0b"
                    path="/finance"
                    stats={[
                        { value: '$77.9k', label: 'Balance' },
                        { value: '+$1.6k', label: 'Month' },
                        { value: '71%', label: 'Budget' },
                    ]}
                >
                    <div className="finance-quick">
                        <div className="finance-item">
                            <TrendingUp size={14} className="text-green-400" />
                            <span>Portfolio: +1.2% today</span>
                        </div>
                        <div className="finance-item warning">
                            <span>Upcoming: Electric $120</span>
                        </div>
                    </div>
                </DashboardCard>
            </div>
        </div>
    );
};

export default DashboardView;
