import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Twitter, Mail, Home, Heart, DollarSign } from 'lucide-react';

const domains = [
    { id: 'social', label: 'Social', icon: Twitter, path: '/social', color: '#00d9ff' },
    { id: 'email', label: 'Email', icon: Mail, path: '/email', color: '#3b82f6' },
    { id: 'habitat', label: 'Habitat', icon: Home, path: '/habitat', color: '#10b981' },
    { id: 'care', label: 'Care', icon: Heart, path: '/care', color: '#f472b6' },
    { id: 'finance', label: 'Finance', icon: DollarSign, path: '/finance', color: '#f59e0b' },
];

const DetailViewLayout = ({ title, icon: Icon, children, currentDomain }) => {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <div className="detail-view">
            {/* Header with back button and title */}
            <div className="detail-header">
                <button 
                    onClick={() => navigate('/')} 
                    className="back-button"
                    title="Back to Dashboard (Esc)"
                >
                    <ArrowLeft size={20} />
                    <span>Dashboard</span>
                </button>
                
                <div className="detail-title">
                    {Icon && <Icon size={24} />}
                    <h1>{title}</h1>
                </div>
            </div>

            {/* Quick-jump navigation pills */}
            <div className="quick-nav">
                {domains.map((domain) => {
                    const DomainIcon = domain.icon;
                    const isActive = currentDomain === domain.id;
                    return (
                        <button
                            key={domain.id}
                            onClick={() => navigate(domain.path)}
                            className={`quick-nav-pill ${isActive ? 'active' : ''}`}
                            style={isActive ? { 
                                borderColor: domain.color,
                                color: domain.color,
                                background: `${domain.color}15`
                            } : {}}
                        >
                            <DomainIcon size={16} />
                            <span>{domain.label}</span>
                        </button>
                    );
                })}
            </div>

            {/* Main content area */}
            <div className="detail-content">
                {children}
            </div>
        </div>
    );
};

export default DetailViewLayout;


