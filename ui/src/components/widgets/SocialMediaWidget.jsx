import React from 'react';
import { Twitter, Linkedin, Instagram, TrendingUp } from 'lucide-react';

const SocialMediaWidget = () => {
    return (
        <div className="widget">
            <div className="widget-header">
                <div className="widget-icon">
                    <Twitter size={20} />
                </div>
                <h3 className="widget-title">Social Media</h3>
                <div className="flex gap-2 ml-auto">
                    <Twitter size={16} className="text-blue-400" />
                    <Linkedin size={16} className="text-blue-500" />
                    <Instagram size={16} className="text-pink-500" />
                </div>
            </div>

            <div className="widget-content">
                <div className="widget-stat">
                    <span className="widget-stat-value">5</span>
                    <span>Unread Mentions</span>
                </div>
                <div className="widget-stat">
                    <span className="widget-stat-value">2</span>
                    <span>Scheduled Posts</span>
                </div>
                <div className="widget-stat">
                    <TrendingUp size={16} className="text-green-400" />
                    <span>Sentiment</span>
                </div>

                {/* Mini sentiment chart */}
                <div className="mt-4">
                    <svg width="100%" height="60" viewBox="0 0 200 60" preserveAspectRatio="none">
                        <defs>
                            <linearGradient id="sentimentGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stopColor="rgba(0, 217, 255, 0.3)" />
                                <stop offset="100%" stopColor="rgba(0, 217, 255, 0)" />
                            </linearGradient>
                        </defs>
                        <path
                            d="M 0,40 Q 50,30 100,35 T 200,25"
                            fill="none"
                            stroke="rgba(0, 217, 255, 0.8)"
                            strokeWidth="2"
                        />
                        <path
                            d="M 0,40 Q 50,30 100,35 T 200,25 L 200,60 L 0,60 Z"
                            fill="url(#sentimentGradient)"
                        />
                    </svg>
                </div>
            </div>
        </div>
    );
};

export default SocialMediaWidget;
