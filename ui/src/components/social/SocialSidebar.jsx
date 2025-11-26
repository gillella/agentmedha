import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LayoutDashboard, PenTool, Calendar, BarChart2, Settings, User, ArrowLeft, Banana } from 'lucide-react';

const SocialSidebar = ({ activeTab, setActiveTab }) => {
    const navigate = useNavigate();

    const navItems = [
        { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { id: 'studio', icon: PenTool, label: 'Studio' },
        { id: 'schedule', icon: Calendar, label: 'Schedule' },
        { id: 'analytics', icon: BarChart2, label: 'Analytics' },
    ];

    return (
        <div className="w-64 flex flex-col py-6 border-r border-white/[0.12] bg-gradient-to-b from-[#1f2229] to-[#16181d] backdrop-blur-xl z-50">
            {/* Logo / Brand */}
            <button
                onClick={() => navigate('/')}
                className="mb-12 px-6 flex items-center gap-3 hover:opacity-80 transition-opacity"
                title="Back to Main Dashboard"
            >
                <div className="w-11 h-11 rounded-[14px] bg-gradient-to-br from-yellow-400 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/25">
                    <Banana className="text-white" size={24} />
                </div>
                <div className="flex flex-col">
                    <span className="text-white font-bold text-[17px] leading-tight">Nano</span>
                    <span className="text-white font-bold text-[17px] leading-tight">Banana</span>
                </div>
            </button>

            {/* Navigation */}
            <div className="flex-1 flex flex-col gap-1 w-full px-0">
                {navItems.map((item) => {
                    const isActive = activeTab === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={`
                                w-full flex items-center gap-4 px-6 py-[14px] group nano-sidebar-item
                                ${isActive ? 'active' : 'text-white/40 hover:text-white/70'}
                            `}
                        >
                            <item.icon size={20} className={`relative z-10 transition-colors duration-300 ${isActive ? 'text-yellow-400' : 'group-hover:text-white/70'}`} />
                            <span className="font-medium text-[15px] relative z-10">{item.label}</span>
                        </button>
                    );
                })}
            </div>

            {/* Bottom Actions */}
            <div className="flex flex-col gap-3 w-full px-3">
                <button className="w-full aspect-square rounded-xl flex items-center justify-center text-white/35 hover:text-white/60 hover:bg-white/5 transition-colors">
                    <Settings size={19} />
                </button>
                <button className="w-full aspect-square rounded-xl flex items-center justify-center bg-gradient-to-br from-gray-800/60 to-gray-900/60 border border-white/10 text-white/70 hover:border-white/20 transition-colors">
                    <User size={17} />
                </button>
            </div>
        </div>
    );
};

export default SocialSidebar;
