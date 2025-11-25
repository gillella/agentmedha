import React, { useState } from 'react';
import { Sparkles, Image as ImageIcon, RefreshCw, Send, Wand2, Hash, Type } from 'lucide-react';

const ContentStudio = ({
    topic, setTopic,
    content, setContent,
    image, setImage,
    isGenerating, setIsGenerating,
    onGenerateDraft, onGenerateImage, onPost,
    statusMessage, lastPostStatus
}) => {
    const [imagePrompt, setImagePrompt] = useState('');
    const [useAIImage, setUseAIImage] = useState(true);

    return (
        <div className="flex-1 flex flex-col h-full overflow-y-auto bg-[#1a1d24]">
            {/* Header */}
            <div className="px-8 pt-10 pb-8 border-b border-white/[0.08]">
                <h1 className="text-[26px] font-bold text-white tracking-tight">Content Studio</h1>
            </div>

            <div className="flex-1 px-8 py-8 flex flex-col gap-8">
                {/* Tweet Text Section */}
                <div className="flex flex-col gap-4">
                    <label className="text-[15px] font-medium text-white/90">Tweet Text</label>

                    <textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="Hello ironmarediately for NanoBananaAI"
                        className="nano-input h-40 resize-none"
                        style={{ fontFamily: 'inherit' }}
                    />

                    <button
                        onClick={onGenerateDraft}
                        disabled={isGenerating}
                        className="nano-button"
                    >
                        {isGenerating ? <RefreshCw size={18} className="animate-spin mx-auto" /> : 'Generate'}
                    </button>
                </div>

                {/* AI Image Prompt Section */}
                <div className="flex flex-col gap-4 pt-4">
                    <div className="flex items-center justify-between">
                        <label className="text-[15px] font-medium text-white/90">AI Image Prompt</label>
                        <div className="flex items-center gap-3">
                            <span className="text-[11px] text-white/50 font-semibold uppercase tracking-widest">AI</span>
                            <div
                                onClick={() => setUseAIImage(!useAIImage)}
                                className={`nano-toggle ${useAIImage ? 'active' : ''}`}
                            >
                                <div className="nano-toggle-thumb" />
                            </div>
                        </div>
                    </div>

                    <textarea
                        value={imagePrompt}
                        onChange={(e) => setImagePrompt(e.target.value)}
                        placeholder="Generate 1 image and art ormation with promp."
                        className="nano-input h-36 resize-none"
                        style={{ fontFamily: 'inherit' }}
                    />

                    <button
                        onClick={() => onGenerateImage(imagePrompt)}
                        disabled={isGenerating || !useAIImage}
                        className={`nano-button ${!useAIImage ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                        {isGenerating ? <RefreshCw size={18} className="animate-spin mx-auto" /> : 'Generate'}
                    </button>
                </div>

                {/* Status Message */}
                {statusMessage && (
                    <div className={`text-xs text-center mt-2 ${lastPostStatus === 'error' ? 'text-red-400' : 'text-green-400'}`}>
                        {statusMessage}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ContentStudio;
