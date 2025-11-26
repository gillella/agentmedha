import React, { useState, useCallback } from 'react';
import {
    PenTool, Image, Video, Sparkles, Send, Clock, ChevronDown, Upload,
    Twitter, Linkedin, Youtube, Instagram, Facebook, Wand2, Hash,
    AtSign, Smile, Link, MapPin, BarChart2, Trash2, Edit3, Copy,
    Zap, MessageCircle, RefreshCw, Check, X, Play, Pause
} from 'lucide-react';
import MediaLab from './MediaLab';

// Platform configurations
const PLATFORMS = {
    twitter: { name: 'Twitter / X', icon: Twitter, color: '#1DA1F2', charLimit: 280 },
    linkedin: { name: 'LinkedIn', icon: Linkedin, color: '#0A66C2', charLimit: 3000 },
    youtube: { name: 'YouTube', icon: Youtube, color: '#FF0000', charLimit: null },
    instagram: { name: 'Instagram', icon: Instagram, color: '#E1306C', charLimit: 2200 },
    facebook: { name: 'Facebook', icon: Facebook, color: '#1877F2', charLimit: 63206 },
};

// AI Assist options
const AI_ASSIST_OPTIONS = [
    { id: 'improve', icon: Wand2, label: 'Improve Writing' },
    { id: 'hashtags', icon: Hash, label: 'Add Hashtags' },
    { id: 'shorten', icon: Edit3, label: 'Make Shorter' },
    { id: 'expand', icon: MessageCircle, label: 'Expand' },
    { id: 'formal', icon: Sparkles, label: 'Make Professional' },
    { id: 'casual', icon: Smile, label: 'Make Casual' },
];

const ContentStudio = ({ selectedPlatforms, accounts, onTogglePlatform, onShowAria }) => {
    // State
    const [content, setContent] = useState('');
    const [media, setMedia] = useState([]);
    const [showMediaLab, setShowMediaLab] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [previewPlatform, setPreviewPlatform] = useState('twitter');
    const [scheduleType, setScheduleType] = useState('now'); // now, schedule, best
    const [scheduleDate, setScheduleDate] = useState(null);

    // Character count
    const getCharLimit = () => {
        const limits = selectedPlatforms.map(p => PLATFORMS[p]?.charLimit).filter(Boolean);
        return limits.length > 0 ? Math.min(...limits) : null;
    };

    const charLimit = getCharLimit();
    const charCount = content.length;
    const charStatus = charLimit ? (charCount > charLimit ? 'danger' : charCount > charLimit * 0.9 ? 'warning' : '') : '';

    // AI Assist handler
    const handleAIAssist = async (action) => {
        setIsGenerating(true);
        // Simulate AI processing
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        switch (action) {
            case 'hashtags':
                setContent(prev => prev + '\n\n#AI #SocialMedia #ContentCreation #Digital');
                break;
            case 'improve':
                // Would call AI API
                break;
            default:
                break;
        }
        setIsGenerating(false);
    };

    // Handle media from MediaLab
    const handleMediaGenerated = (mediaItem) => {
        setMedia(prev => [...prev, mediaItem]);
        setShowMediaLab(false);
    };

    // Remove media
    const removeMedia = (index) => {
        setMedia(prev => prev.filter((_, i) => i !== index));
    };

    // Platform toggle button component
    const PlatformToggle = ({ platform }) => {
        const config = PLATFORMS[platform];
        if (!config) return null;
        const Icon = config.icon;
        const isActive = selectedPlatforms.includes(platform);
        
        return (
            <button
                className={`platform-toggle ${isActive ? 'active' : ''} ${platform}`}
                onClick={() => onTogglePlatform(platform)}
                title={config.name}
            >
                <Icon size={16} />
            </button>
        );
    };

    return (
        <div className="content-studio">
            {/* Main Composer */}
            <div className="studio-main">
                {/* Composer Card */}
                <div className="composer-card">
                    <div className="composer-header">
                        <div className="composer-title">
                            <PenTool size={18} />
                            <span>Create Post</span>
                        </div>
                        <div className="composer-platforms">
                            {Object.keys(PLATFORMS).map(platform => (
                                <PlatformToggle key={platform} platform={platform} />
                            ))}
                        </div>
                    </div>

                    <div className="composer-body">
                        {/* Text Area */}
                        <textarea
                            className="composer-textarea"
                            placeholder="What's on your mind? Let AI help you create engaging content..."
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                        />
                        
                        {/* Character Count */}
                        {charLimit && (
                            <div className={`char-count ${charStatus}`}>
                                {charCount} / {charLimit}
                            </div>
                        )}

                        {/* AI Assist Bar */}
                        <div className="ai-assist-bar">
                            {AI_ASSIST_OPTIONS.map(option => (
                                <button
                                    key={option.id}
                                    className="ai-assist-btn"
                                    onClick={() => handleAIAssist(option.id)}
                                    disabled={isGenerating}
                                >
                                    <option.icon size={14} />
                                    {option.label}
                                </button>
                            ))}
                        </div>

                        {/* Media Section */}
                        <div className="media-section">
                            <div className="media-header">
                                <span className="media-title">Media</span>
                            </div>
                            <div className="media-grid">
                                {/* Uploaded/Generated Media */}
                                {media.map((item, index) => (
                                    <div key={index} className="media-preview">
                                        {item.type === 'image' ? (
                                            <img src={item.url} alt="Media" />
                                        ) : (
                                            <video src={item.url} />
                                        )}
                                        <div className="media-preview-actions">
                                            <button 
                                                className="media-action-btn"
                                                onClick={() => removeMedia(index)}
                                            >
                                                <X size={14} />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                                
                                {/* Upload Zone */}
                                <div className="media-upload-zone">
                                    <Upload size={24} />
                                    <span>Upload</span>
                                </div>
                                
                                {/* AI Generate Zone */}
                                <div 
                                    className="ai-generate-zone"
                                    onClick={() => setShowMediaLab(true)}
                                >
                                    <Sparkles size={24} />
                                    <span>AI Generate</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="composer-footer">
                        <div className="composer-options">
                            <button className="composer-option">
                                <Clock size={14} />
                                <span>Schedule</span>
                                <ChevronDown size={12} />
                            </button>
                            <button className="composer-option">
                                <MapPin size={14} />
                                <span>Location</span>
                            </button>
                            <button className="composer-option">
                                <BarChart2 size={14} />
                                <span>Poll</span>
                            </button>
                        </div>
                        <div className="composer-actions">
                            <button className="draft-btn">
                                Save Draft
                            </button>
                            <button className="publish-btn" disabled={!content.trim()}>
                                <Send size={16} />
                                Publish Now
                            </button>
                        </div>
                    </div>
                </div>

                {/* Media Lab Modal */}
                {showMediaLab && (
                    <MediaLab 
                        onClose={() => setShowMediaLab(false)}
                        onGenerate={handleMediaGenerated}
                        contentContext={content}
                    />
                )}
            </div>

            {/* Sidebar - Preview & Tools */}
            <div className="studio-sidebar">
                {/* Preview Panel */}
                <div className="preview-panel">
                    <div className="preview-header">
                        {Object.entries(PLATFORMS)
                            .filter(([key]) => selectedPlatforms.includes(key))
                            .map(([key, platform]) => (
                                <button
                                    key={key}
                                    className={`preview-tab ${previewPlatform === key ? 'active' : ''}`}
                                    onClick={() => setPreviewPlatform(key)}
                                >
                                    {platform.name.split(' ')[0]}
                                </button>
                            ))
                        }
                    </div>
                    <div className="preview-content">
                        {previewPlatform === 'twitter' && (
                            <div className="twitter-preview">
                                <div className="twitter-post-header">
                                    <div className="twitter-avatar" />
                                    <div className="twitter-user-info">
                                        <span className="twitter-display-name">Your Name</span>
                                        <span className="twitter-handle"> @yourhandle · now</span>
                                    </div>
                                </div>
                                <div className="twitter-post-content">
                                    {content || 'Your post will appear here...'}
                                </div>
                                {media.length > 0 && (
                                    <div className="twitter-post-media">
                                        <img src={media[0].url} alt="Post media" />
                                    </div>
                                )}
                                <div className="twitter-post-actions">
                                    <span className="twitter-action">
                                        <MessageCircle size={16} /> 0
                                    </span>
                                    <span className="twitter-action">
                                        <RefreshCw size={16} /> 0
                                    </span>
                                    <span className="twitter-action">
                                        ❤️ 0
                                    </span>
                                    <span className="twitter-action">
                                        📊 0
                                    </span>
                                </div>
                            </div>
                        )}
                        {previewPlatform === 'linkedin' && (
                            <div className="linkedin-preview">
                                <div className="linkedin-post-header">
                                    <div className="linkedin-avatar" />
                                    <div className="linkedin-user-info">
                                        <h4>Your Name</h4>
                                        <p>Your headline • 1st</p>
                                    </div>
                                </div>
                                <div className="linkedin-post-content">
                                    {content || 'Your post will appear here...'}
                                </div>
                                {media.length > 0 && (
                                    <div className="linkedin-post-media">
                                        <img src={media[0].url} alt="Post media" />
                                    </div>
                                )}
                                <div className="linkedin-post-actions">
                                    <span className="linkedin-action">👍 Like</span>
                                    <span className="linkedin-action">💬 Comment</span>
                                    <span className="linkedin-action">🔄 Repost</span>
                                    <span className="linkedin-action">📤 Send</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Schedule Panel */}
                <div className="schedule-panel">
                    <div className="schedule-header">
                        <div className="schedule-title">
                            <Clock size={16} />
                            <span>Schedule</span>
                        </div>
                        <div className="best-time-badge">
                            <Zap size={12} />
                            Best: 9:00 AM
                        </div>
                    </div>
                    <div className="schedule-options">
                        <div 
                            className={`schedule-option ${scheduleType === 'now' ? 'active' : ''}`}
                            onClick={() => setScheduleType('now')}
                        >
                            <div className="schedule-option-label">Publish</div>
                            <div className="schedule-option-value">Now</div>
                        </div>
                        <div 
                            className={`schedule-option ${scheduleType === 'best' ? 'active' : ''}`}
                            onClick={() => setScheduleType('best')}
                        >
                            <div className="schedule-option-label">AI Optimized</div>
                            <div className="schedule-option-value">Best Time</div>
                        </div>
                        <div 
                            className={`schedule-option ${scheduleType === 'schedule' ? 'active' : ''}`}
                            onClick={() => setScheduleType('schedule')}
                            style={{ gridColumn: 'span 2' }}
                        >
                            <div className="schedule-option-label">Custom Schedule</div>
                            <div className="schedule-option-value">Pick Date & Time</div>
                        </div>
                    </div>
                </div>

                {/* AI Assistant Card */}
                <div className="ai-assistant-card">
                    <div className="ai-assistant-header">
                        <div className="ai-assistant-avatar">
                            <Sparkles size={22} />
                        </div>
                        <div className="ai-assistant-info">
                            <h3>Aria AI</h3>
                            <p>Your Social Media Assistant</p>
                        </div>
                    </div>
                    <div className="ai-suggestions">
                        <div className="ai-suggestion" onClick={onShowAria}>
                            <Wand2 size={16} />
                            <span>Generate post ideas for today</span>
                        </div>
                        <div className="ai-suggestion" onClick={onShowAria}>
                            <Hash size={16} />
                            <span>Find trending hashtags</span>
                        </div>
                        <div className="ai-suggestion" onClick={onShowAria}>
                            <BarChart2 size={16} />
                            <span>Analyze best posting times</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ContentStudio;
