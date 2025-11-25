import React from 'react';
import { Home, Lightbulb, Camera, User } from 'lucide-react';

const HabitatStatusWidget = () => {
    return (
        <div className="widget">
            <div className="widget-header">
                <div className="widget-icon">
                    <Home size={20} />
                </div>
                <h3 className="widget-title">Habitat Status</h3>
                <div className="flex gap-2 ml-auto">
                    <Home size={16} className="text-teal-400" />
                    <Lightbulb size={16} className="text-teal-400" />
                    <User size={16} className="text-teal-400" />
                </div>
            </div>

            <div className="widget-content">
                <div className="widget-stat">
                    <span>All Systems</span>
                    <span className="widget-stat-value text-green-400">Normal</span>
                </div>
                <div className="widget-stat">
                    <Lightbulb size={16} className="text-yellow-400" />
                    <span>Living Room Lights:</span>
                    <span className="widget-stat-value">ON (60%)</span>
                </div>
                <div className="widget-stat">
                    <Camera size={16} className="text-blue-400" />
                    <span>Front Door Camera:</span>
                    <span className="widget-stat-value text-green-400">Active</span>
                </div>
            </div>
        </div>
    );
};

export default HabitatStatusWidget;
