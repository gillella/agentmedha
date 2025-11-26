import React, { useState } from 'react';
import SocialSidebar from './SocialSidebar';
import ContentStudio from './ContentStudio';
import TwitterDashboard from '../TwitterDashboard';

const SocialLayout = () => {
    const [activeTab, setActiveTab] = useState('studio');

    const renderContent = () => {
        switch (activeTab) {
            case 'dashboard':
                return <TwitterDashboard />;
            case 'studio':
                return <ContentStudio />;
            case 'schedule':
                return <div className="p-8 text-white">Schedule View (Coming Soon)</div>;
            case 'analytics':
                return <div className="p-8 text-white">Analytics View (Coming Soon)</div>;
            default:
                return <ContentStudio />;
        }
    };

    return (
        <div className="flex h-full w-full bg-[#0f1115]">
            <SocialSidebar activeTab={activeTab} setActiveTab={setActiveTab} />
            <div className="flex-1 overflow-hidden">
                {renderContent()}
            </div>
        </div>
    );
};

export default SocialLayout;
