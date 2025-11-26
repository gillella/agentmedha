import React, { useState } from 'react';
import SocialSidebar from './social/SocialSidebar';
import ContentStudio from './social/ContentStudio';
import PostPreview from './social/PostPreview';

const TwitterDashboard = () => {
    const [activeTab, setActiveTab] = useState('studio');

    // Studio State
    const [activePlatform, setActivePlatform] = useState('twitter');
    const [topic, setTopic] = useState('');
    const [content, setContent] = useState('');
    const [generatedImage, setGeneratedImage] = useState(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [statusMessage, setStatusMessage] = useState('');
    const [lastPostStatus, setLastPostStatus] = useState(null);

    // Store drafts for each platform to switch back and forth without losing work
    const [drafts, setDrafts] = useState({
        twitter: '',
        linkedin: '',
        instagram: ''
    });

    // Update content when switching platforms
    const handlePlatformChange = (newPlatform) => {
        // Save current content to draft
        setDrafts(prev => ({ ...prev, [activePlatform]: content }));
        // Load new platform content
        setContent(drafts[newPlatform] || '');
        setActivePlatform(newPlatform);
        setStatusMessage('');
    };

    const handleCopyToPlatform = (targetPlatform) => {
        setDrafts(prev => ({ ...prev, [targetPlatform]: content }));
        setStatusMessage(`Copied to ${targetPlatform}!`);
        setTimeout(() => setStatusMessage(''), 2000);
    };

    const handleGenerateDraft = async () => {
        if (!topic.trim()) return;
        setIsGenerating(true);
        setStatusMessage(`Maya is drafting for ${activePlatform}...`);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `Research and draft a ${activePlatform} post about: ${topic}`,
                    thread_id: "social_studio"
                })
            });
            const data = await response.json();
            if (response.ok) {
                setContent(data.response);
                setStatusMessage('Draft generated!');
            } else {
                setStatusMessage(`Error: ${data.detail}`);
            }
        } catch (error) {
            setStatusMessage(`Error: ${error.message}`);
        } finally {
            setIsGenerating(false);
        }
    };

    const handleGenerateImage = async () => {
        if (!topic.trim()) return;
        setIsGenerating(true);
        setStatusMessage('Maya is dreaming up visuals...');

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `Generate an image for a ${activePlatform} post about: ${topic}`,
                    thread_id: "social_studio"
                })
            });
            const data = await response.json();

            // Extract base64 image if present
            const imgMatch = data.response.match(/data:image\/[^;]+;base64,[^"'\s)]+/);
            if (imgMatch) {
                setGeneratedImage(imgMatch[0]);
                setStatusMessage('Visuals ready!');
            } else {
                setStatusMessage('Could not generate image.');
            }
        } catch (error) {
            setStatusMessage(`Error: ${error.message}`);
        } finally {
            setIsGenerating(false);
        }
    };

    const handlePost = async () => {
        if (!content.trim()) return;
        setIsGenerating(true);
        setStatusMessage(`Publishing to ${activePlatform}...`);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `Post this to ${activePlatform}: ${content}`,
                    thread_id: "social_dashboard"
                })
            });

            if (response.ok) {
                setLastPostStatus('success');
                setStatusMessage('Successfully published!');
                // Clear content for this platform
                setContent('');
                setDrafts(prev => ({ ...prev, [activePlatform]: '' }));
                setTopic('');
                setGeneratedImage(null);
            } else {
                setLastPostStatus('error');
                setStatusMessage('Failed to publish.');
            }
        } catch (error) {
            setLastPostStatus('error');
            setStatusMessage(`Network Error: ${error.message}`);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="flex h-full w-full bg-slate-950 overflow-hidden">
            {/* Left Sidebar */}
            <SocialSidebar activeTab={activeTab} setActiveTab={setActiveTab} />

            {/* Main Content Area */}
            <div className="flex-1 flex overflow-hidden">
                {activeTab === 'studio' ? (
                    <>
                        {/* Middle: Content Studio (Input) */}
                        <div className="w-1/2 border-r border-white/10">
                            <ContentStudio
                                topic={topic} setTopic={setTopic}
                                content={content} setContent={setContent}
                                image={generatedImage} setImage={setGeneratedImage}
                                isGenerating={isGenerating} setIsGenerating={setIsGenerating}
                                onGenerateDraft={handleGenerateDraft}
                                onGenerateImage={handleGenerateImage}
                                onPost={handlePost}
                                statusMessage={statusMessage}
                                lastPostStatus={lastPostStatus}
                                activePlatform={activePlatform}
                                setActivePlatform={handlePlatformChange}
                                onCopyToPlatform={handleCopyToPlatform}
                            />
                        </div>

                        {/* Right: Live Preview (Output) */}
                        <div className="w-1/2 bg-[url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop')] bg-cover bg-center">
                            <PostPreview content={content} image={generatedImage} platform={activePlatform} />
                        </div>
                    </>
                ) : (
                    <div className="flex-1 flex items-center justify-center text-white/40">
                        <div className="text-center">
                            <h2 className="text-xl font-bold mb-2">Coming Soon</h2>
                            <p>The {activeTab} module is under construction.</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TwitterDashboard;

