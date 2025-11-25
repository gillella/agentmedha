import React from 'react';
import { DollarSign, TrendingUp } from 'lucide-react';

const FinancialOverviewWidget = () => {
    return (
        <div className="widget full-width">
            <div className="widget-header">
                <div className="widget-icon">
                    <DollarSign size={20} />
                </div>
                <h3 className="widget-title">Financial Overview</h3>
            </div>

            <div className="widget-content">
                <div className="flex gap-8 mb-4">
                    <div className="widget-stat">
                        <span>Monthly Spend vs. Budget</span>
                    </div>
                    <div className="widget-stat">
                        <span>Upcoming Bill:</span>
                        <span className="widget-stat-value">Electric ($120)</span>
                    </div>
                    <div className="widget-stat">
                        <TrendingUp size={16} className="text-green-400" />
                        <span>Investment Portfolio:</span>
                        <span className="widget-stat-value text-green-400">+1.2% today</span>
                    </div>
                </div>

                {/* Mini area chart for financial overview */}
                <div className="mt-4">
                    <svg width="100%" height="80" viewBox="0 0 400 80" preserveAspectRatio="none">
                        <defs>
                            <linearGradient id="financialGradient1" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stopColor="rgba(0, 217, 255, 0.3)" />
                                <stop offset="100%" stopColor="rgba(0, 217, 255, 0)" />
                            </linearGradient>
                            <linearGradient id="financialGradient2" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stopColor="rgba(0, 188, 212, 0.3)" />
                                <stop offset="100%" stopColor="rgba(0, 188, 212, 0)" />
                            </linearGradient>
                        </defs>

                        {/* Budget line */}
                        <path
                            d="M 0,50 Q 100,45 200,48 T 400,50"
                            fill="none"
                            stroke="rgba(0, 188, 212, 0.6)"
                            strokeWidth="2"
                            strokeDasharray="5,5"
                        />

                        {/* Spend line */}
                        <path
                            d="M 0,60 Q 100,40 200,45 T 400,35"
                            fill="none"
                            stroke="rgba(0, 217, 255, 0.8)"
                            strokeWidth="2"
                        />
                        <path
                            d="M 0,60 Q 100,40 200,45 T 400,35 L 400,80 L 0,80 Z"
                            fill="url(#financialGradient1)"
                        />
                    </svg>
                </div>
            </div>
        </div>
    );
};

export default FinancialOverviewWidget;
