import React from 'react';
import DetailViewLayout from '../DetailViewLayout';
import TwitterDashboard from '../TwitterDashboard';
import { Twitter } from 'lucide-react';

const SocialDetailView = () => {
    return (
        <DetailViewLayout title="Social Media" icon={Twitter} currentDomain="social">
            <TwitterDashboard />
        </DetailViewLayout>
    );
};

export default SocialDetailView;


