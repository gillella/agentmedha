import React from 'react';
import DetailViewLayout from '../DetailViewLayout';
import ContentStudio from '../social/ContentStudio';
import { Share2 } from 'lucide-react';

const SocialDetailView = () => {
    return (
        <DetailViewLayout title="Social Media Manager" icon={Share2} currentDomain="social">
            <ContentStudio />
        </DetailViewLayout>
    );
};

export default SocialDetailView;


