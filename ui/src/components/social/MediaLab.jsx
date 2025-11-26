import React, { useState } from 'react';
import {
    X, Sparkles, Image, Video, Wand2, RefreshCw, Check,
    Download, Maximize2, Loader, Palette, Layers, Camera
} from 'lucide-react';

// AI Models configuration
const AI_MODELS = {
    image: [
        { id: 'nano-banana', name: 'Nano Banana', type: 'Image', description: 'Fast, creative images' },
        { id: 'midjourney', name: 'Midjourney', type: 'Image', description: 'Artistic, high quality' },
        { id: 'dalle3', name: 'DALL-E 3', type: 'Image', description: 'Precise, detailed' },
        { id: 'stable-diffusion', name: 'Stable Diffusion', type: 'Image', description: 'Versatile, open source' },
    ],
    video: [
        { id: 'veo3', name: 'Veo 3', type: 'Video', description: 'Google DeepMind video' },
        { id: 'runway', name: 'Runway Gen-3', type: 'Video', description: 'Professional video AI' },
        { id: 'pika', name: 'Pika Labs', type: 'Video', description: 'Creative animations' },
    ]
};

// Style presets
const STYLE_PRESETS = [
    { id: 'realistic', label: 'Realistic', icon: Camera },
    { id: 'artistic', label: 'Artistic', icon: Palette },
    { id: 'minimalist', label: 'Minimalist', icon: Layers },
    { id: 'vibrant', label: 'Vibrant', icon: Sparkles },
];

const MediaLab = ({ onClose, onGenerate, contentContext }) => {
    const [mediaType, setMediaType] = useState('image'); // image or video
    const [selectedModel, setSelectedModel] = useState('nano-banana');
    const [prompt, setPrompt] = useState('');
    const [selectedStyle, setSelectedStyle] = useState('realistic');
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedMedia, setGeneratedMedia] = useState([]);
    const [selectedMedia, setSelectedMedia] = useState(null);

    // Generate media with AI
    const handleGenerate = async () => {
        if (!prompt.trim()) return;
        
        setIsGenerating(true);
        setGeneratedMedia([]);
        
        try {
            // Call backend API to generate image
            const response = await fetch('/api/generate-image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: prompt,
                    model: selectedModel,
                    style: selectedStyle
                })
            });
            
            const result = await response.json();
            
            if (result.success && result.image_data) {
                // Single generated image from Nano Banana
                const generatedImage = {
                    id: Date.now().toString(),
                    url: result.image_data,
                    type: 'image'
                };
                setGeneratedMedia([generatedImage]);
            } else if (result.detail) {
                // Error from backend
                console.error('Image generation failed:', result.detail);
                alert('Failed to generate image: ' + result.detail);
            } else {
                console.error('Image generation failed:', result.error || result);
                alert('Failed to generate image: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error generating image:', error);
            alert('Failed to generate image. Please try again.');
        } finally {
            setIsGenerating(false);
        }
    };

    // Use selected media
    const handleUseMedia = () => {
        if (selectedMedia) {
            onGenerate(selectedMedia);
        }
    };

    // Auto-generate prompt from content context
    const autoPrompt = () => {
        if (contentContext) {
            setPrompt(`Create a visually appealing image for a social media post about: ${contentContext.slice(0, 100)}...`);
        }
    };

    const models = mediaType === 'image' ? AI_MODELS.image : AI_MODELS.video;

    return (
        <div className="media-lab-overlay" onClick={onClose}>
            <div className="media-lab" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="media-lab-header">
                    <div className="media-lab-title">
                        <Sparkles size={20} />
                        <span>AI Media Lab</span>
                    </div>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                        <span className="media-lab-badge">Powered by AI</span>
                        <button 
                            className="media-action-btn" 
                            onClick={onClose}
                            style={{ background: 'rgba(255,255,255,0.1)' }}
                        >
                            <X size={16} />
                        </button>
                    </div>
                </div>

                {/* Body */}
                <div className="media-lab-body">
                    {/* Media Type Toggle */}
                    <div className="ai-model-selector">
                        <button
                            className={`ai-model-btn ${mediaType === 'image' ? 'active' : ''}`}
                            onClick={() => setMediaType('image')}
                        >
                            <div className="ai-model-name">
                                <Image size={16} style={{ marginRight: '8px' }} />
                                Image
                            </div>
                            <div className="ai-model-type">AI Generated</div>
                        </button>
                        <button
                            className={`ai-model-btn ${mediaType === 'video' ? 'active' : ''}`}
                            onClick={() => setMediaType('video')}
                        >
                            <div className="ai-model-name">
                                <Video size={16} style={{ marginRight: '8px' }} />
                                Video
                            </div>
                            <div className="ai-model-type">AI Generated</div>
                        </button>
                    </div>

                    {/* Model Selection */}
                    <div style={{ marginBottom: '16px' }}>
                        <label style={{ 
                            display: 'block', 
                            fontSize: '12px', 
                            color: 'var(--social-text-secondary)',
                            marginBottom: '8px'
                        }}>
                            AI Model
                        </label>
                        <div className="ai-model-selector">
                            {models.map(model => (
                                <button
                                    key={model.id}
                                    className={`ai-model-btn ${selectedModel === model.id ? 'active' : ''}`}
                                    onClick={() => setSelectedModel(model.id)}
                                    style={{ flex: 1 }}
                                >
                                    <div className="ai-model-name">{model.name}</div>
                                    <div className="ai-model-type">{model.description}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Style Presets */}
                    <div style={{ marginBottom: '16px' }}>
                        <label style={{ 
                            display: 'block', 
                            fontSize: '12px', 
                            color: 'var(--social-text-secondary)',
                            marginBottom: '8px'
                        }}>
                            Style
                        </label>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            {STYLE_PRESETS.map(style => (
                                <button
                                    key={style.id}
                                    className={`ai-model-btn ${selectedStyle === style.id ? 'active' : ''}`}
                                    onClick={() => setSelectedStyle(style.id)}
                                    style={{ flex: 1, padding: '10px' }}
                                >
                                    <style.icon size={16} style={{ marginBottom: '4px' }} />
                                    <div className="ai-model-type">{style.label}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Prompt Input */}
                    <div style={{ position: 'relative' }}>
                        <textarea
                            className="prompt-input"
                            placeholder="Describe the image or video you want to create..."
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                        />
                        {contentContext && (
                            <button
                                onClick={autoPrompt}
                                style={{
                                    position: 'absolute',
                                    right: '12px',
                                    top: '12px',
                                    padding: '6px 12px',
                                    background: 'rgba(139, 92, 246, 0.2)',
                                    border: '1px solid rgba(139, 92, 246, 0.3)',
                                    borderRadius: '6px',
                                    color: '#a78bfa',
                                    fontSize: '11px',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '4px'
                                }}
                            >
                                <Wand2 size={12} />
                                Auto from post
                            </button>
                        )}
                    </div>

                    {/* Generate Button */}
                    <button 
                        className="generate-btn"
                        onClick={handleGenerate}
                        disabled={isGenerating || !prompt.trim()}
                    >
                        {isGenerating ? (
                            <>
                                <Loader size={18} className="spinning" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <Sparkles size={18} />
                                Generate {mediaType === 'image' ? 'Images' : 'Video'}
                            </>
                        )}
                    </button>

                    {/* Generated Content */}
                    {generatedMedia.length > 0 && (
                        <div className="generated-content">
                            <div style={{ 
                                display: 'flex', 
                                justifyContent: 'space-between', 
                                alignItems: 'center',
                                marginBottom: '12px'
                            }}>
                                <span style={{ color: 'var(--social-text-secondary)', fontSize: '13px' }}>
                                    Generated Results
                                </span>
                                <button 
                                    onClick={handleGenerate}
                                    style={{
                                        background: 'none',
                                        border: 'none',
                                        color: 'var(--social-accent)',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '4px',
                                        fontSize: '12px'
                                    }}
                                >
                                    <RefreshCw size={14} />
                                    Regenerate
                                </button>
                            </div>
                            <div className="generated-grid">
                                {generatedMedia.map((item) => (
                                    <div 
                                        key={item.id}
                                        className={`generated-item ${selectedMedia?.id === item.id ? 'selected' : ''}`}
                                        onClick={() => setSelectedMedia(item)}
                                    >
                                        <img src={item.url} alt="Generated" />
                                        <div className="generated-item-overlay">
                                            {selectedMedia?.id === item.id ? (
                                                <button className="use-btn" onClick={handleUseMedia}>
                                                    <Check size={14} style={{ marginRight: '4px' }} />
                                                    Use This
                                                </button>
                                            ) : (
                                                <button className="use-btn">Select</button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Loading State */}
                    {isGenerating && (
                        <div className="generated-content generating" style={{ 
                            height: '200px', 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center',
                            borderRadius: '12px',
                            marginTop: '20px'
                        }}>
                            <div style={{ textAlign: 'center', color: 'var(--social-text-secondary)' }}>
                                <Loader size={32} className="spinning" style={{ marginBottom: '12px' }} />
                                <p>Creating your {mediaType}...</p>
                                <p style={{ fontSize: '12px', opacity: 0.7 }}>This may take a moment</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

// Add overlay styles
const overlayStyles = `
.media-lab-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(4px);
}

.media-lab-overlay .media-lab {
    width: 600px;
    max-height: 80vh;
    overflow-y: auto;
    animation: slideUp 0.3s ease;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.spinning {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
`;

// Inject styles
if (typeof document !== 'undefined') {
    const styleSheet = document.createElement('style');
    styleSheet.textContent = overlayStyles;
    document.head.appendChild(styleSheet);
}

export default MediaLab;

