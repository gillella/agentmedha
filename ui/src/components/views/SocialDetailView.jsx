import React, { useState } from 'react';
import DetailViewLayout from '../DetailViewLayout';
import ContentStudio from '../social/ContentStudio';
import { Share2 } from 'lucide-react';

// Default accounts for standalone view
const DEFAULT_ACCOUNTS = [
    { id: '1', platform: 'twitter', name: 'Twitter Account', handle: '@user', connected: true },
];

const SocialDetailView = () => {
    const [selectedPlatforms, setSelectedPlatforms] = useState(['twitter']);
    const [showAria, setShowAria] = useState(false);

    const togglePlatform = (platform) => {
        setSelectedPlatforms(prev => 
            prev.includes(platform) 
                ? prev.filter(p => p !== platform)
                : [...prev, platform]
        );
    };

    return (
        <DetailViewLayout title="Social Media Manager" icon={Share2} currentDomain="social">
            <ContentStudio 
                selectedPlatforms={selectedPlatforms}
                accounts={DEFAULT_ACCOUNTS}
                onTogglePlatform={togglePlatform}
                onShowAria={() => setShowAria(true)}
            />
        </DetailViewLayout>
    );
};

export default SocialDetailView;


