import React, { useState } from 'react';
import { Heart, Dog, Droplets, UtensilsCrossed, Activity, Clock, Bell, Camera } from 'lucide-react';
import DetailViewLayout from '../DetailViewLayout';

const CareDetailView = () => {
    const [activeTab, setActiveTab] = useState('overview');

    const pets = [
        { 
            id: 1, 
            name: 'Luna', 
            type: 'Cat',
            lastFed: '10m ago',
            lastWater: '5m ago',
            weight: '4.2 kg',
            activity: 'Active',
            feederLevel: 80,
            waterLevel: 90,
        },
    ];

    const activityLog = [
        { time: '10:30 AM', event: 'Luna ate breakfast', type: 'feeding' },
        { time: '10:25 AM', event: 'Water fountain refilled automatically', type: 'water' },
        { time: '9:45 AM', event: 'Luna played with toy mouse', type: 'activity' },
        { time: '8:00 AM', event: 'Morning feeding scheduled', type: 'schedule' },
        { time: '7:30 AM', event: 'Luna woke up', type: 'activity' },
    ];

    const schedules = [
        { id: 1, time: '7:00 AM', action: 'Morning feeding', status: 'completed' },
        { id: 2, time: '12:00 PM', action: 'Midday snack', status: 'upcoming' },
        { id: 3, time: '6:00 PM', action: 'Evening feeding', status: 'upcoming' },
        { id: 4, time: '10:00 PM', action: 'Night snack', status: 'upcoming' },
    ];

    return (
        <DetailViewLayout title="Dependent Care" icon={Heart} currentDomain="care">
            <div className="care-detail">
                {/* Stats Overview */}
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(244, 114, 182, 0.1)' }}>
                            <Dog size={24} className="text-pink-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">Luna</span>
                            <span className="stat-label">Happy & Healthy</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.1)' }}>
                            <UtensilsCrossed size={24} className="text-green-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">80%</span>
                            <span className="stat-label">Feeder Level</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(59, 130, 246, 0.1)' }}>
                            <Droplets size={24} className="text-blue-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">90%</span>
                            <span className="stat-label">Water Level</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.1)' }}>
                            <Activity size={24} className="text-yellow-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">Active</span>
                            <span className="stat-label">Current Status</span>
                        </div>
                    </div>
                </div>

                {/* Tab Navigation */}
                <div className="detail-tabs">
                    <button 
                        className={`detail-tab ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                    >
                        Overview
                    </button>
                    <button 
                        className={`detail-tab ${activeTab === 'schedule' ? 'active' : ''}`}
                        onClick={() => setActiveTab('schedule')}
                    >
                        Feeding Schedule
                    </button>
                    <button 
                        className={`detail-tab ${activeTab === 'activity' ? 'active' : ''}`}
                        onClick={() => setActiveTab('activity')}
                    >
                        Activity Log
                    </button>
                </div>

                {/* Tab Content */}
                <div className="tab-content">
                    {activeTab === 'overview' && (
                        <div className="pet-overview">
                            {pets.map((pet) => (
                                <div key={pet.id} className="pet-card">
                                    <div className="pet-header">
                                        <div className="pet-avatar">🐱</div>
                                        <div className="pet-info">
                                            <h3>{pet.name}</h3>
                                            <span className="pet-type">{pet.type} • {pet.weight}</span>
                                        </div>
                                        <span className="pet-status active">
                                            <Activity size={14} /> {pet.activity}
                                        </span>
                                    </div>
                                    
                                    <div className="pet-stats">
                                        <div className="pet-stat">
                                            <UtensilsCrossed size={16} className="text-green-400" />
                                            <span>Last fed: {pet.lastFed}</span>
                                        </div>
                                        <div className="pet-stat">
                                            <Droplets size={16} className="text-blue-400" />
                                            <span>Last drink: {pet.lastWater}</span>
                                        </div>
                                    </div>

                                    <div className="level-bars">
                                        <div className="level-bar">
                                            <span className="level-label">Food</span>
                                            <div className="level-track">
                                                <div 
                                                    className="level-fill food" 
                                                    style={{ width: `${pet.feederLevel}%` }}
                                                ></div>
                                            </div>
                                            <span className="level-value">{pet.feederLevel}%</span>
                                        </div>
                                        <div className="level-bar">
                                            <span className="level-label">Water</span>
                                            <div className="level-track">
                                                <div 
                                                    className="level-fill water" 
                                                    style={{ width: `${pet.waterLevel}%` }}
                                                ></div>
                                            </div>
                                            <span className="level-value">{pet.waterLevel}%</span>
                                        </div>
                                    </div>

                                    <div className="pet-actions">
                                        <button className="btn-primary">
                                            <UtensilsCrossed size={16} /> Feed Now
                                        </button>
                                        <button className="btn-secondary">
                                            <Camera size={16} /> View Camera
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {activeTab === 'schedule' && (
                        <div className="schedule-list">
                            {schedules.map((item) => (
                                <div key={item.id} className={`schedule-item ${item.status}`}>
                                    <Clock size={16} />
                                    <span className="schedule-time">{item.time}</span>
                                    <span className="schedule-action">{item.action}</span>
                                    <span className={`schedule-status ${item.status}`}>
                                        {item.status === 'completed' ? '✓ Done' : 'Upcoming'}
                                    </span>
                                </div>
                            ))}
                            <button className="btn-secondary add-schedule">
                                + Add Feeding Time
                            </button>
                        </div>
                    )}

                    {activeTab === 'activity' && (
                        <div className="activity-log">
                            {activityLog.map((item, idx) => (
                                <div key={idx} className="activity-item">
                                    <span className="activity-time">{item.time}</span>
                                    <span className={`activity-dot ${item.type}`}></span>
                                    <span className="activity-event">{item.event}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </DetailViewLayout>
    );
};

export default CareDetailView;


