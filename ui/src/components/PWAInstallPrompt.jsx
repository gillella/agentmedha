import React, { useState, useEffect } from 'react';
import { Download, X, Smartphone, Monitor } from 'lucide-react';

const PWAInstallPrompt = () => {
    const [deferredPrompt, setDeferredPrompt] = useState(null);
    const [showPrompt, setShowPrompt] = useState(false);
    const [isIOS, setIsIOS] = useState(false);
    const [isStandalone, setIsStandalone] = useState(false);

    useEffect(() => {
        // Check if already installed
        const standalone = window.matchMedia('(display-mode: standalone)').matches 
            || window.navigator.standalone 
            || document.referrer.includes('android-app://');
        setIsStandalone(standalone);

        // Check if iOS
        const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        setIsIOS(iOS);

        // Listen for install prompt
        const handleBeforeInstall = (e) => {
            e.preventDefault();
            setDeferredPrompt(e);
            // Show prompt after a delay (don't interrupt user immediately)
            setTimeout(() => {
                if (!localStorage.getItem('pwa-install-dismissed')) {
                    setShowPrompt(true);
                }
            }, 30000); // 30 seconds
        };

        window.addEventListener('beforeinstallprompt', handleBeforeInstall);

        // Listen for successful install
        window.addEventListener('appinstalled', () => {
            setShowPrompt(false);
            setDeferredPrompt(null);
            console.log('PWA installed successfully');
        });

        return () => {
            window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
        };
    }, []);

    const handleInstall = async () => {
        if (!deferredPrompt) return;

        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        
        if (outcome === 'accepted') {
            console.log('User accepted install prompt');
        } else {
            console.log('User dismissed install prompt');
        }
        
        setDeferredPrompt(null);
        setShowPrompt(false);
    };

    const handleDismiss = () => {
        setShowPrompt(false);
        localStorage.setItem('pwa-install-dismissed', 'true');
    };

    // Don't show if already installed or dismissed
    if (isStandalone || !showPrompt) return null;

    // iOS-specific instructions
    if (isIOS) {
        return (
            <div style={{
                position: 'fixed',
                bottom: '20px',
                left: '20px',
                right: '20px',
                zIndex: 9998,
                animation: 'slideUp 0.3s ease-out',
            }}>
                <div style={{
                    background: 'linear-gradient(135deg, rgba(15, 20, 30, 0.98), rgba(10, 15, 25, 0.98))',
                    border: '1px solid rgba(139, 92, 246, 0.3)',
                    borderRadius: '16px',
                    padding: '20px',
                    boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5)',
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div style={{ display: 'flex', gap: '12px' }}>
                            <div style={{
                                width: '44px',
                                height: '44px',
                                background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                                borderRadius: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'white',
                            }}>
                                <Smartphone size={22} />
                            </div>
                            <div>
                                <h3 style={{ margin: '0 0 4px', fontSize: '16px', fontWeight: '600', color: 'white' }}>
                                    Install agentMedha
                                </h3>
                                <p style={{ margin: 0, fontSize: '13px', color: '#94a3b8' }}>
                                    Tap <strong style={{ color: 'white' }}>Share</strong> then <strong style={{ color: 'white' }}>Add to Home Screen</strong>
                                </p>
                            </div>
                        </div>
                        <button onClick={handleDismiss} style={{
                            background: 'rgba(255, 255, 255, 0.1)',
                            border: 'none',
                            borderRadius: '8px',
                            width: '32px',
                            height: '32px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: '#94a3b8',
                            cursor: 'pointer',
                        }}>
                            <X size={16} />
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // Android/Desktop install prompt
    return (
        <div style={{
            position: 'fixed',
            bottom: '20px',
            left: '20px',
            right: '20px',
            zIndex: 9998,
            animation: 'slideUp 0.3s ease-out',
        }}>
            <div style={{
                background: 'linear-gradient(135deg, rgba(15, 20, 30, 0.98), rgba(10, 15, 25, 0.98))',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '16px',
                padding: '20px',
                boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5)',
                maxWidth: '400px',
                margin: '0 auto',
            }}>
                <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                    <div style={{
                        width: '52px',
                        height: '52px',
                        background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        flexShrink: 0,
                    }}>
                        <Monitor size={26} />
                    </div>
                    <div>
                        <h3 style={{ margin: '0 0 4px', fontSize: '16px', fontWeight: '600', color: 'white' }}>
                            Install agentMedha
                        </h3>
                        <p style={{ margin: 0, fontSize: '13px', color: '#94a3b8', lineHeight: '1.4' }}>
                            Install the app for a better experience with offline support and quick access.
                        </p>
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={handleDismiss} style={{
                        flex: 1,
                        padding: '10px 16px',
                        background: 'transparent',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        borderRadius: '8px',
                        color: '#94a3b8',
                        fontSize: '13px',
                        fontWeight: '600',
                        cursor: 'pointer',
                    }}>
                        Not now
                    </button>
                    <button onClick={handleInstall} style={{
                        flex: 1,
                        padding: '10px 16px',
                        background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                        border: 'none',
                        borderRadius: '8px',
                        color: 'white',
                        fontSize: '13px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '6px',
                    }}>
                        <Download size={14} />
                        Install
                    </button>
                </div>
            </div>

            <style>{`
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
            `}</style>
        </div>
    );
};

export default PWAInstallPrompt;

