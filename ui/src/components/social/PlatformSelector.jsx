import React from 'react';
import { Twitter, Linkedin, Instagram } from 'lucide-react';

const PlatformSelector = ({ activePlatform, setActivePlatform }) => {
    const platforms = [
        { id: 'twitter', label: 'Twitter', icon: Twitter, color: 'text-blue-400' },
        { id: 'linkedin', label: 'LinkedIn', icon: Linkedin, color: 'text-blue-600' },
        { id: 'instagram', label: 'Instagram', icon: Instagram, color: 'text-pink-500' }
    ];

    return (
        <div className="flex space-x-2 mb-4">
            {platforms.map((platform) => {
                const Icon = platform.icon;
                const isActive = activePlatform === platform.id;
                return (
                    <button
                        key={platform.id}
                        onClick={() => setActivePlatform(platform.id)}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${isActive
                                ? 'bg-white/10 text-white border border-white/20 shadow-lg'
                                : 'bg-transparent text-white/40 hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <Icon size={18} className={isActive ? platform.color : ''} />
                        <span className="font-medium">{platform.label}</span>
                    </button>
                );
            })}
        </div>
    );
};

export default PlatformSelector;
