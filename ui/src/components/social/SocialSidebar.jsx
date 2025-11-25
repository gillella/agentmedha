import React from 'react';
import { LayoutDashboard, PenTool, Calendar, BarChart2, Settings, User } from 'lucide-react';

const SocialSidebar = ({ activeTab, setActiveTab }) => {
    const navItems = [
        { id: 'dashboard', icon: LayoutDashboard, label: 'Overview' },
        { id: 'studio', icon: PenTool, label: 'Studio' },
        { id: 'schedule', icon: Calendar, label: 'Schedule' },
        { id: 'analytics', icon: BarChart2, label: 'Analytics' },
    ];

    return (
        <div className="w-20 flex flex-col items-center py-6 border-r border-white/10 bg-black/20 backdrop-blur-xl">
            {/* Logo / Brand */}
            <div className="mb-8 w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-violet-600 flex items-center justify-center shadow-lg shadow-pink-500/20">
                <span className="text-white font-bold text-lg">M</span>
            </div>

            {/* Navigation */}
            <div className="flex-1 flex flex-col gap-4 w-full px-3">
                {navItems.map((item) => {
                    const isActive = activeTab === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={`
                                w-full aspect-square rounded-xl flex flex-col items-center justify-center gap-1 transition-all duration-300 group relative
                                ${isActive
                                    ? 'bg-white/10 text-white shadow-inner'
                                    : 'text-white/40 hover:text-white hover:bg-white/5'
                                }
                            `}
                            title={item.label}
                        >
                            <item.icon size={20} className={`transition-transform duration-300 ${isActive ? 'scale-110' : 'group-hover:scale-110'}`} />
                            {isActive && (
                                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-pink-500 to-violet-500 rounded-r-full" />
                            )}
                        </button>
                    );
                })}
            </div>

            {/* Bottom Actions */}
            <div className="flex flex-col gap-4 w-full px-3">
                <button className="w-full aspect-square rounded-xl flex items-center justify-center text-white/40 hover:text-white hover:bg-white/5 transition-colors">
                    <Settings size={20} />
                </button>
                <button className="w-full aspect-square rounded-xl flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900 border border-white/10 text-white/80 hover:border-white/30 transition-colors">
                    <User size={18} />
                </button>
            </div>
        </div>
    );
};

export default SocialSidebar;
