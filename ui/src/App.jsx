import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, Settings, Activity, Brain, Zap, Mail, Share2 } from 'lucide-react';
import DashboardView from './components/DashboardView';
import SettingsPanel from './components/SettingsPanel';
import SocialDetailView from './components/views/SocialDetailView';
import EmailDetailView from './components/views/EmailDetailView';
import HabitatDetailView from './components/views/HabitatDetailView';
import CareDetailView from './components/views/CareDetailView';
import FinanceDetailView from './components/views/FinanceDetailView';
import CommandBar from './components/CommandBar';
import { EmailManagerView } from './components/email';

// Keyboard navigation hook
const useKeyboardNav = () => {
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const handleKeyDown = (e) => {
            // Escape to go back to dashboard
            if (e.key === 'Escape' && location.pathname !== '/') {
                navigate('/');
            }
            // Number keys for quick navigation (when not typing)
            if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                switch (e.key) {
                    case '1': navigate('/social'); break;
                    case '2': navigate('/email'); break;
                    case '3': navigate('/habitat'); break;
                    case '4': navigate('/care'); break;
                    case '5': navigate('/finance'); break;
                    default: break;
                }
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [navigate, location]);
};

const AppContent = () => {
    useKeyboardNav();
    const location = useLocation();
    const isDetailView = location.pathname !== '/' && location.pathname !== '/settings';

    return (
        <div className="app-container">
            <aside className={`sidebar ${isDetailView ? 'compact' : ''}`}>
                {/* Logo */}
                <div className="sidebar-header">
                    <div className="logo-icon">
                        <Brain size={28} />
                    </div>
                    <h1 className="logo-text">agentMedha</h1>
                </div>

                {/* Main Navigation */}
                <nav className="sidebar-nav">
                    <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end>
                        <LayoutDashboard size={20} />
                        <span>Dashboard</span>
                    </NavLink>
                    <NavLink to="/social" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                        <Share2 size={20} />
                        <span>Social Media</span>
                    </NavLink>
                    <NavLink to="/email-manager" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                        <Mail size={20} />
                        <span>Email Hub</span>
                    </NavLink>
                    <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                        <Settings size={20} />
                        <span>Settings</span>
                    </NavLink>
                </nav>

                {/* Status Footer */}
                <div className="sidebar-footer">
                    <div className="status-indicator">
                        <Zap size={14} className="status-icon" />
                        <span className="status-text">
                            <span className="status-connected">Connected</span>
                            <span className="status-latency">45ms</span>
                        </span>
                    </div>
                    <div className="keyboard-hints">
                        <span className="hint">Press <kbd>1-5</kbd> to navigate</span>
                        <span className="hint"><kbd>Esc</kbd> to go home</span>
                    </div>
                </div>
            </aside>

            <main className="main-content">
                <Routes>
                    <Route path="/" element={<DashboardView />} />
                    <Route path="/settings" element={<SettingsPanel />} />
                    <Route path="/social" element={<SocialDetailView />} />
                    <Route path="/email" element={<EmailDetailView />} />
                    <Route path="/email-manager" element={<EmailManagerView />} />
                    <Route path="/habitat" element={<HabitatDetailView />} />
                    <Route path="/care" element={<CareDetailView />} />
                    <Route path="/finance" element={<FinanceDetailView />} />
                </Routes>
                <CommandBar />
            </main>
        </div>
    );
};

function App() {
    return (
        <Router>
            <AppContent />
        </Router>
    );
}

export default App;
