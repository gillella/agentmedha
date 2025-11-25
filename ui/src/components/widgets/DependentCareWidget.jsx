import React from 'react';
import { Heart } from 'lucide-react';

const DependentCareWidget = () => {
    return (
        <div className="widget">
            <div className="widget-header">
                <div className="widget-icon">
                    <Heart size={20} />
                </div>
                <h3 className="widget-title">Dependent Care (PETKIT)</h3>
            </div>

            <div className="widget-content">
                <div className="widget-stat">
                    <span>Feeder:</span>
                    <span className="widget-stat-value text-green-400">80% Full</span>
                </div>
                <div className="widget-stat">
                    <span>Water Fountain:</span>
                    <span className="widget-stat-value text-blue-400">Clean</span>
                </div>
                <div className="widget-stat">
                    <span>Last Activity:</span>
                    <span className="widget-stat-value">Eating 10m ago</span>
                </div>
            </div>
        </div>
    );
};

export default DependentCareWidget;
