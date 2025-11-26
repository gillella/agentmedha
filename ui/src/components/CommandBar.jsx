import React, { useState } from 'react';
import { Mic, Image as ImageIcon } from 'lucide-react';

const CommandBar = () => {
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (input.trim() && !isLoading) {
            setIsLoading(true);
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: input }),
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                // For now, just alert the response to prove connectivity
                // In a real app, this would go into a chat history or overlay
                alert(`Agent says: ${data.response}`);

                setInput('');
            } catch (error) {
                console.error('Error sending command:', error);
                alert('Failed to send command. Check console for details.');
            } finally {
                setIsLoading(false);
            }
        }
    };

    return (
        <form onSubmit={handleSubmit} className="command-bar">
            <button type="button" className="command-icon-btn">
                <Mic size={20} />
            </button>
            <button type="button" className="command-icon-btn">
                <ImageIcon size={20} />
            </button>
            <input
                type="text"
                className="command-input"
                placeholder={isLoading ? "Thinking..." : "Ask Medha or type a command..."}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading}
            />
            <div className={`command-status-indicator ${isLoading ? 'loading' : ''}`} />
        </form>
    );
};

export default CommandBar;
