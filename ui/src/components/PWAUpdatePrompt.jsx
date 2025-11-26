import React from 'react';
import { useRegisterSW } from 'virtual:pwa-register/react';
import { RefreshCw, X, Download } from 'lucide-react';

const PWAUpdatePrompt = () => {
    const {
        needRefresh: [needRefresh, setNeedRefresh],
        offlineReady: [offlineReady, setOfflineReady],
        updateServiceWorker,
    } = useRegisterSW({
        onRegistered(registration) {
            console.log('SW Registered:', registration);
            // Check for updates every hour
            if (registration) {
                setInterval(() => {
                    registration.update();
                }, 60 * 60 * 1000);
            }
        },
        onRegisterError(error) {
            console.error('SW registration error:', error);
        },
    });

    const close = () => {
        setOfflineReady(false);
        setNeedRefresh(false);
    };

    if (!needRefresh && !offlineReady) return null;

    return (
        <div style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            zIndex: 9999,
            animation: 'slideUp 0.3s ease-out',
        }}>
            <div style={{
                background: 'linear-gradient(135deg, rgba(15, 20, 30, 0.98), rgba(10, 15, 25, 0.98))',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '16px',
                padding: '20px',
                maxWidth: '360px',
                boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5), 0 0 30px rgba(139, 92, 246, 0.15)',
                backdropFilter: 'blur(10px)',
            }}>
                {/* Header */}
                <div style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'space-between',
                    marginBottom: '16px',
                }}>
                    <div style={{
                        width: '44px',
                        height: '44px',
                        background: offlineReady 
                            ? 'linear-gradient(135deg, #10b981, #059669)'
                            : 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                    }}>
                        {offlineReady ? <Download size={22} /> : <RefreshCw size={22} />}
                    </div>
                    <button
                        onClick={close}
                        style={{
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
                        }}
                    >
                        <X size={16} />
                    </button>
                </div>

                {/* Content */}
                <div style={{ marginBottom: '16px' }}>
                    <h3 style={{
                        margin: '0 0 8px',
                        fontSize: '16px',
                        fontWeight: '600',
                        color: 'white',
                    }}>
                        {offlineReady ? 'Ready to work offline!' : 'Update available'}
                    </h3>
                    <p style={{
                        margin: 0,
                        fontSize: '14px',
                        color: '#94a3b8',
                        lineHeight: '1.5',
                    }}>
                        {offlineReady
                            ? 'agentMedha has been installed and can now work offline.'
                            : 'A new version of agentMedha is available. Reload to update.'}
                    </p>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: '10px' }}>
                    {needRefresh && (
                        <>
                            <button
                                onClick={close}
                                style={{
                                    flex: 1,
                                    padding: '10px 16px',
                                    background: 'transparent',
                                    border: '1px solid rgba(255, 255, 255, 0.2)',
                                    borderRadius: '8px',
                                    color: '#94a3b8',
                                    fontSize: '13px',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                }}
                            >
                                Later
                            </button>
                            <button
                                onClick={() => updateServiceWorker(true)}
                                style={{
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
                                }}
                            >
                                <RefreshCw size={14} />
                                Update Now
                            </button>
                        </>
                    )}
                    {offlineReady && (
                        <button
                            onClick={close}
                            style={{
                                width: '100%',
                                padding: '10px 16px',
                                background: 'linear-gradient(135deg, #10b981, #059669)',
                                border: 'none',
                                borderRadius: '8px',
                                color: 'white',
                                fontSize: '13px',
                                fontWeight: '600',
                                cursor: 'pointer',
                            }}
                        >
                            Got it!
                        </button>
                    )}
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

export default PWAUpdatePrompt;

