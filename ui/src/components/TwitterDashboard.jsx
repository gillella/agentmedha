import React, { useState } from 'react';
import { Twitter, Send, Activity, CheckCircle, AlertCircle, Hash, Image as ImageIcon, PenTool, Sparkles, RefreshCw } from 'lucide-react';

const TwitterDashboard = () => {
    const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'studio'
    const [tweetContent, setTweetContent] = useState('');
    const [isPosting, setIsPosting] = useState(false);
    const [lastPostStatus, setLastPostStatus] = useState(null); // 'success' | 'error' | null
    const [statusMessage, setStatusMessage] = useState('');

    // Studio State
    const [topic, setTopic] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedImage, setGeneratedImage] = useState(null);
    const [studioStatus, setStudioStatus] = useState('');

    const maxChars = 280;
    const charCount = tweetContent.length;
    const isOverLimit = charCount > maxChars;

    const handlePost = async () => {
        if (!tweetContent.trim() || isOverLimit) return;

        setIsPosting(true);
        setLastPostStatus(null);
        setStatusMessage('');

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `Post this to Twitter: ${tweetContent}`,
                    thread_id: "social_dashboard"
                })
            });

            const data = await response.json();

            if (response.ok) {
                setLastPostStatus('success');
                setStatusMessage('Tweet posted successfully!');
                setTweetContent('');
            } else {
                setLastPostStatus('error');
                setStatusMessage(`Error: ${data.detail || 'Failed to post'}`);
            }
        } catch (error) {
            setLastPostStatus('error');
            setStatusMessage(`Network Error: ${error.message}`);
        } finally {
            setIsPosting(false);
        }
    };

    const handleGenerate = async () => {
        if (!topic.trim()) return;
        setIsGenerating(true);
        setStudioStatus('Researching and Drafting...');
        setGeneratedImage(null);

        try {
            // 1. Generate Draft
            const draftResponse = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `Research and draft a tweet about: ${topic}`,
                    thread_id: "social_studio"
                })
            });
            const draftData = await draftResponse.json();
            setTweetContent(draftData.response);

            // 2. Generate Image
            setStudioStatus('Generating Image (Nano Banana Pro)...');
            const imgResponse = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `Generate an image for a tweet about: ${topic}`,
                    thread_id: "social_studio"
                })
            });
            const imgData = await imgResponse.json();

            // Extract base64 image if present in response text (it might be embedded or just text description if failed)
            // The worker returns the data URI directly as the tool output, which the agent repeats.
            // We need to parse it out.
            const imgMatch = imgData.response.match(/data:image\/[^;]+;base64,[^"'\s)]+/);
            if (imgMatch) {
                setGeneratedImage(imgMatch[0]);
            }

            setStudioStatus('Generation Complete');
            setActiveTab('dashboard'); // Switch to composer to review
        } catch (error) {
            setStudioStatus(`Error: ${error.message}`);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="h-full flex flex-col gap-6 p-6 overflow-y-auto">
            {/* Header / Status Card */}
            <div className="glass-panel p-6 flex items-center justify-between bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-white/10">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-blue-500/20 rounded-xl text-blue-400">
                        <Twitter size={32} />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white">Social Command Center</h1>
                        <p className="text-white/60">Manage your X (Twitter) presence</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => setActiveTab('dashboard')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'dashboard' ? 'bg-blue-600 text-white' : 'bg-white/5 text-white/60 hover:bg-white/10'}`}
                    >
                        Dashboard
                    </button>
                    <button
                        onClick={() => setActiveTab('studio')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${activeTab === 'studio' ? 'bg-purple-600 text-white' : 'bg-white/5 text-white/60 hover:bg-white/10'}`}
                    >
                        <Sparkles size={16} /> Content Studio
                    </button>
                </div>
            </div>

            {activeTab === 'studio' ? (
                <div className="glass-panel p-8 max-w-2xl mx-auto w-full space-y-6">
                    <div className="text-center space-y-2">
                        <h2 className="text-2xl font-bold text-white">AI Content Studio</h2>
                        <p className="text-white/60">Research, Draft, and Create with Nano Banana Pro</p>
                    </div>

                    <div className="space-y-4">
                        <label className="block text-sm font-medium text-white/80">Topic or Idea</label>
                        <textarea
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            placeholder="e.g., The future of AI agents in daily life..."
                            className="w-full h-32 bg-black/20 border border-white/10 rounded-xl p-4 text-white placeholder-white/20 focus:outline-none focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/50 transition-all resize-none"
                        />
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={isGenerating || !topic.trim()}
                        className={`
                            w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-3 transition-all
                            ${isGenerating || !topic.trim()
                                ? 'bg-white/5 text-white/20 cursor-not-allowed'
                                : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white shadow-lg shadow-purple-600/20'
                            }
                        `}
                    >
                        {isGenerating ? (
                            <>
                                <RefreshCw className="animate-spin" />
                                {studioStatus}
                            </>
                        ) : (
                            <>
                                <Sparkles /> Generate Content
                            </>
                        )}
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Composer Column */}
                    <div className="lg:col-span-2 flex flex-col gap-6">
                        <div className="glass-panel p-6 space-y-4">
                            <div className="flex items-center justify-between mb-2">
                                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                                    <Send size={20} className="text-blue-400" />
                                    Compose Tweet
                                </h2>
                                <span className={`text-sm font-mono ${isOverLimit ? 'text-red-400' : 'text-white/40'}`}>
                                    {charCount} / {maxChars}
                                </span>
                            </div>

                            <div className="relative group">
                                <textarea
                                    value={tweetContent}
                                    onChange={(e) => setTweetContent(e.target.value)}
                                    placeholder="What's happening in the AI world?"
                                    className="w-full h-48 bg-black/20 border border-white/10 rounded-xl p-4 text-white placeholder-white/20 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all resize-none"
                                />
                                <div className="absolute bottom-4 right-4 flex gap-2">
                                    <button className="p-2 hover:bg-white/10 rounded-lg text-white/40 hover:text-blue-400 transition-colors">
                                        <ImageIcon size={20} />
                                    </button>
                                    <button className="p-2 hover:bg-white/10 rounded-lg text-white/40 hover:text-blue-400 transition-colors">
                                        <Hash size={20} />
                                    </button>
                                </div>
                            </div>

                            {generatedImage && (
                                <div className="relative rounded-xl overflow-hidden border border-white/10 bg-black/20">
                                    <img src={generatedImage} alt="Generated" className="w-full h-64 object-cover" />
                                    <div className="absolute top-2 right-2 bg-black/60 px-2 py-1 rounded text-xs text-white">
                                        Nano Banana Pro
                                    </div>
                                </div>
                            )}

                            <div className="flex items-center justify-between pt-2">
                                <div className="flex items-center gap-2">
                                    {lastPostStatus === 'success' && (
                                        <span className="text-green-400 text-sm flex items-center gap-1 animate-fade-in">
                                            <CheckCircle size={16} /> {statusMessage}
                                        </span>
                                    )}
                                    {lastPostStatus === 'error' && (
                                        <span className="text-red-400 text-sm flex items-center gap-1 animate-fade-in">
                                            <AlertCircle size={16} /> {statusMessage}
                                        </span>
                                    )}
                                </div>
                                <button
                                    onClick={handlePost}
                                    disabled={isPosting || !tweetContent.trim() || isOverLimit}
                                    className={`
                                        px-6 py-2.5 rounded-xl font-medium flex items-center gap-2 transition-all
                                        ${isPosting || !tweetContent.trim() || isOverLimit
                                            ? 'bg-white/5 text-white/20 cursor-not-allowed'
                                            : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20 hover:shadow-blue-500/30 hover:-translate-y-0.5'
                                        }
                                    `}
                                >
                                    {isPosting ? (
                                        <>
                                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                            Posting...
                                        </>
                                    ) : (
                                        <>
                                            Post Tweet <Send size={18} />
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Activity Feed Column */}
                    <div className="lg:col-span-1">
                        <div className="glass-panel p-6 h-full">
                            <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                                <Activity size={20} className="text-purple-400" />
                                Recent Activity
                            </h2>

                            <div className="space-y-4">
                                {/* Mock Activity Items */}
                                {[1, 2, 3].map((i) => (
                                    <div key={i} className="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                                        <div className="flex items-start gap-3">
                                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white">
                                                AG
                                            </div>
                                            <div>
                                                <p className="text-white/80 text-sm leading-relaxed">
                                                    Just deployed a new update to the neural core. Optimization levels at 99%. 🚀 #AI #Tech
                                                </p>
                                                <span className="text-white/30 text-xs mt-2 block">
                                                    {i * 15} mins ago
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TwitterDashboard;
