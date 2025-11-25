import React from 'react';
import { Send, Image as ImageIcon, Sparkles, Copy } from 'lucide-react';
import PlatformSelector from './PlatformSelector';

const ContentStudio = ({
    topic, setTopic,
    content, setContent,
    image, setImage,
    isGenerating, setIsGenerating,
    onGenerateDraft,
    onGenerateImage,
    onPost,
    statusMessage,
    lastPostStatus,
    activePlatform,
    setActivePlatform,
    onCopyToPlatform
}) => {

    const handleCopy = (targetPlatform) => {
        onCopyToPlatform(targetPlatform);
    };

    return (
        <div className="h-full flex flex-col bg-slate-900/50 backdrop-blur-sm p-6">
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-white mb-2">Content Studio</h2>
                <p className="text-white/40 text-sm">Create and schedule content for your social channels.</p>
            </div>

            {/* Platform Selector */}
            <PlatformSelector activePlatform={activePlatform} setActivePlatform={setActivePlatform} />

            {/* Input Area */}
            <div className="flex-1 flex flex-col space-y-4 overflow-y-auto pr-2">
                {/* Topic Input */}
                <div className="space-y-2">
                    <label className="text-xs font-semibold text-white/60 uppercase tracking-wider">Topic / Idea</label>
                    <div className="flex space-x-2">
                        <input
                            type="text"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            placeholder="What do you want to post about?"
                            className="flex-1 bg-slate-950/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-indigo-500 transition-colors"
                        />
                        <button
                            onClick={onGenerateDraft}
                            disabled={isGenerating || !topic.trim()}
                            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 rounded-lg flex items-center justify-center transition-colors"
                            title="Generate Draft"
                        >
                            <Sparkles size={20} />
                        </button>
                    </div>
                </div>

                {/* Content Editor */}
                <div className="flex-1 flex flex-col space-y-2 min-h-[200px]">
                    <div className="flex justify-between items-center">
                        <label className="text-xs font-semibold text-white/60 uppercase tracking-wider">Post Content ({activePlatform})</label>
                        <div className="flex space-x-2">
                            {['twitter', 'linkedin', 'instagram'].filter(p => p !== activePlatform).map(p => (
                                <button
                                    key={p}
                                    onClick={() => handleCopy(p)}
                                    className="text-xs text-white/40 hover:text-white flex items-center space-x-1 transition-colors"
                                    title={`Copy current content to ${p}`}
                                >
                                    <Copy size={12} />
                                    <span className="capitalize">To {p}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                    <textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder={`Write your ${activePlatform} post here...`}
                        className="flex-1 bg-slate-950/50 border border-white/10 rounded-lg p-4 text-white placeholder-white/20 focus:outline-none focus:border-indigo-500 transition-colors resize-none font-mono text-sm leading-relaxed"
                    />
                </div>

                {/* Image Generation */}
                <div className="space-y-2">
                    <div className="flex justify-between items-center">
                        <label className="text-xs font-semibold text-white/60 uppercase tracking-wider">Visuals</label>
                        <button
                            onClick={onGenerateImage}
                            disabled={isGenerating || !topic.trim()}
                            className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center space-x-1 transition-colors disabled:opacity-50"
                        >
                            <ImageIcon size={14} />
                            <span>Generate AI Image</span>
                        </button>
                    </div>

                    {image && (
                        <div className="relative group rounded-lg overflow-hidden border border-white/10 bg-slate-950/50 h-48 flex items-center justify-center">
                            <img src={image} alt="Generated" className="h-full w-full object-cover" />
                            <button
                                onClick={() => setImage(null)}
                                className="absolute top-2 right-2 bg-black/50 hover:bg-black/70 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Actions */}
            <div className="mt-6 pt-6 border-t border-white/10 flex justify-between items-center">
                <div className={`text-sm ${lastPostStatus === 'success' ? 'text-green-400' :
                        lastPostStatus === 'error' ? 'text-red-400' :
                            'text-white/40'
                    }`}>
                    {statusMessage}
                </div>
                <button
                    onClick={onPost}
                    disabled={isGenerating || !content.trim()}
                    className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-2.5 rounded-lg font-medium flex items-center space-x-2 shadow-lg shadow-indigo-500/20 transition-all transform active:scale-95"
                >
                    <Send size={18} />
                    <span>Post to {activePlatform.charAt(0).toUpperCase() + activePlatform.slice(1)}</span>
                </button>
            </div>
        </div>
    );
};

export default ContentStudio;
