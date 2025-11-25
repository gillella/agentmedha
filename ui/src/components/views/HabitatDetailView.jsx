import React, { useState } from 'react';
import { Home, Lightbulb, Thermometer, Lock, Camera, Droplets, Zap, Shield } from 'lucide-react';
import DetailViewLayout from '../DetailViewLayout';

const HabitatDetailView = () => {
    const [lights, setLights] = useState({
        livingRoom: { on: true, brightness: 60 },
        bedroom: { on: false, brightness: 0 },
        kitchen: { on: true, brightness: 100 },
        office: { on: true, brightness: 80 },
    });

    const devices = [
        { id: 'thermostat', name: 'Thermostat', icon: Thermometer, status: '72°F', location: 'Living Room', online: true },
        { id: 'frontDoor', name: 'Front Door', icon: Lock, status: 'Locked', location: 'Entrance', online: true },
        { id: 'camera1', name: 'Front Camera', icon: Camera, status: 'Recording', location: 'Front Porch', online: true },
        { id: 'camera2', name: 'Back Camera', icon: Camera, status: 'Active', location: 'Backyard', online: true },
        { id: 'sprinkler', name: 'Sprinklers', icon: Droplets, status: 'Scheduled 6 AM', location: 'Garden', online: true },
    ];

    const energyData = {
        today: 12.4,
        yesterday: 14.2,
        monthAvg: 13.1,
        savings: 8,
    };

    return (
        <DetailViewLayout title="Habitat Control" icon={Home} currentDomain="habitat">
            <div className="habitat-detail">
                {/* Stats Overview */}
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.1)' }}>
                            <Shield size={24} className="text-green-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">Secure</span>
                            <span className="stat-label">All Systems</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.1)' }}>
                            <Lightbulb size={24} className="text-yellow-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">3/4</span>
                            <span className="stat-label">Lights On</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(59, 130, 246, 0.1)' }}>
                            <Thermometer size={24} className="text-blue-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">72°F</span>
                            <span className="stat-label">Temperature</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon" style={{ background: 'rgba(0, 217, 255, 0.1)' }}>
                            <Zap size={24} className="text-cyan-400" />
                        </div>
                        <div className="stat-info">
                            <span className="stat-value">{energyData.today} kWh</span>
                            <span className="stat-label">Energy Today</span>
                        </div>
                    </div>
                </div>

                {/* Lights Control */}
                <div className="control-section">
                    <h3 className="section-title">
                        <Lightbulb size={20} />
                        Lighting Control
                    </h3>
                    <div className="lights-grid">
                        {Object.entries(lights).map(([room, state]) => (
                            <div key={room} className={`light-card ${state.on ? 'on' : 'off'}`}>
                                <div className="light-header">
                                    <Lightbulb size={20} className={state.on ? 'text-yellow-400' : 'text-gray-500'} />
                                    <span className="light-name">{room.replace(/([A-Z])/g, ' $1').trim()}</span>
                                    <label className="toggle-switch">
                                        <input 
                                            type="checkbox" 
                                            checked={state.on}
                                            onChange={() => setLights(prev => ({
                                                ...prev,
                                                [room]: { ...prev[room], on: !prev[room].on }
                                            }))}
                                        />
                                        <span className="toggle-slider"></span>
                                    </label>
                                </div>
                                {state.on && (
                                    <div className="brightness-control">
                                        <input 
                                            type="range" 
                                            min="10" 
                                            max="100" 
                                            value={state.brightness}
                                            onChange={(e) => setLights(prev => ({
                                                ...prev,
                                                [room]: { ...prev[room], brightness: parseInt(e.target.value) }
                                            }))}
                                            className="brightness-slider"
                                        />
                                        <span className="brightness-value">{state.brightness}%</span>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Devices */}
                <div className="control-section">
                    <h3 className="section-title">
                        <Home size={20} />
                        Connected Devices
                    </h3>
                    <div className="devices-list">
                        {devices.map((device) => {
                            const DeviceIcon = device.icon;
                            return (
                                <div key={device.id} className="device-item">
                                    <DeviceIcon size={24} className="text-cyan-400" />
                                    <div className="device-info">
                                        <span className="device-name">{device.name}</span>
                                        <span className="device-location">{device.location}</span>
                                    </div>
                                    <div className="device-status">
                                        <span className="status-value">{device.status}</span>
                                        <span className={`status-dot ${device.online ? 'online' : 'offline'}`}></span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </DetailViewLayout>
    );
};

export default HabitatDetailView;


