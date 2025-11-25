import React from 'react';
import { Mail, AlertCircle } from 'lucide-react';

const EmailPriorityWidget = () => {
    return (
        <div className="widget">
            <div className="widget-header">
                <div className="widget-icon">
                    <Mail size={20} />
                </div>
                <h3 className="widget-title">Email Priority</h3>
            </div>

            <div className="widget-content">
                <div className="widget-stat">
                    <span className="widget-stat-value">3</span>
                    <span>Urgent Emails from Work</span>
                </div>
                <div className="widget-stat">
                    <AlertCircle size={16} className="text-yellow-400" />
                    <span className="widget-stat-value">1</span>
                    <span>Financial Alert</span>
                </div>

                <button
                    className="mt-4 w-full px-4 py-2 rounded-lg text-sm font-medium transition-all"
                    style={{
                        background: 'rgba(0, 217, 255, 0.1)',
                        border: '1px solid rgba(0, 217, 255, 0.3)',
                        color: '#00d9ff'
                    }}
                    onMouseEnter={(e) => {
                        e.target.style.background = 'rgba(0, 217, 255, 0.2)';
                        e.target.style.borderColor = 'rgba(0, 217, 255, 0.5)';
                    }}
                    onMouseLeave={(e) => {
                        e.target.style.background = 'rgba(0, 217, 255, 0.1)';
                        e.target.style.borderColor = 'rgba(0, 217, 255, 0.3)';
                    }}
                >
                    Compose with Medha
                </button>
            </div>
        </div>
    );
};

export default EmailPriorityWidget;
