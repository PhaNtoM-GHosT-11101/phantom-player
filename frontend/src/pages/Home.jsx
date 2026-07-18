import React from 'react';

export default function Home() {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div className="topbar"></div>
            <div className="content-area">
                <h1 className="section-title">Welcome back to Phantom</h1>
                <p style={{ color: 'var(--text-muted)' }}>Search for music using the sidebar or login to view your playlists.</p>
            </div>
        </div>
    );
}
