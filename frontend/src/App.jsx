import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Database, Battery, Wifi, ShieldCheck, AlertTriangle } from 'lucide-react'
import './App.css'

// Configuration
const API_URL = "http://localhost:8000"

function App() {
    const [status, setStatus] = useState({
        mode: "EXPLORE",
        status: "SYSTEM INITIALIZING",
        confidence: 0,
        landmark_count: 0,
        best_match: -1
    })

    const [history, setHistory] = useState([])

    useEffect(() => {
        // Polling interval for system status
        const interval = setInterval(async () => {
            try {
                const res = await fetch(`${API_URL}/status`)
                const data = await res.json()
                setStatus(data)

                // Sync local timeline state with backend
                if (data.mode === "EXPLORE" && data.landmark_count > history.length) {
                    setHistory(prev => [...prev, { time: new Date().toLocaleTimeString(), id: data.landmark_count - 1 }])
                }
            } catch (e) {
                console.error("Link Failure", e)
            }
        }, 500)
        return () => clearInterval(interval)
    }, [history.length])

    const toggleMode = async () => {
        const newMode = status.mode === "EXPLORE" ? "RETURN" : "EXPLORE"
        try {
            await fetch(`${API_URL}/set_mode/${newMode}`, { method: 'POST' })
        } catch (e) {
            console.error("Mode switch failed", e)
        }
    }

    return (
        <div className="app-container">

            <div className="bg-grid"></div>
            <div className="bg-scanlines"></div>

            {/* HUD Header */}
            <header className="hud-header">
                <div className="logo-section">
                    <ShieldCheck className="icon-shield pulse" />
                    <h1 className="title">TRAIL<span>SENSE</span></h1>
                </div>
                <div className="system-info">
                    <div className="info-item">
                        <Wifi className="icon-sm" />
                        <span>ONLINE</span>
                    </div>
                    <div className="info-item">
                        <Battery className="icon-sm color-amber" />
                        <span>87%</span>
                    </div>
                    <div className="version-badge">SYS.V.1.0.4</div>
                </div>
            </header>

            <main className="main-grid">

                {/* Left Control Panel */}
                <aside className="sidebar left-sidebar">

                    <div className="panel status-panel">
                        <div className="panel-glow"></div>
                        <div className="panel-content">
                            <h2>System Status</h2>
                            <div className={`status-value ${status.mode === 'RETURN' ? (status.confidence > 70 ? 'color-green' : 'color-red') : 'color-blue'}`}>
                                {status.status}
                            </div>
                            <div className="mode-label">MODE: <span>{status.mode}</span></div>
                        </div>
                        <div className="corner c-tl"></div>
                        <div className="corner c-br"></div>
                    </div>

                    <div className="panel timeline-panel">
                        <h2><Database className="icon-xs" /> Landmark Log</h2>
                        <div className="timeline-list">
                            <AnimatePresence>
                                {history.slice().reverse().map((item, idx) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        className="timeline-item"
                                    >
                                        <span className="time">{item.time}</span>
                                        <span className="id">LM_ID_{item.id}</span>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                            {history.length === 0 && <div className="empty-state">No landmarks captured yet.</div>}
                        </div>
                    </div>
                </aside>

                {/* Primary Viewport */}
                <section className="center-feed">
                    <div className="video-frame">
                        <div className="crosshair">
                            <div className="circle">
                                <div className="dot"></div>
                            </div>
                            <div className="line horizontal"></div>
                            <div className="line vertical"></div>
                        </div>

                        <img src={`${API_URL}/video_feed`} alt="Live Feed" className="video-stream" />

                        <div className="hud-corner top-left"></div>
                        <div className="hud-corner top-right"></div>
                        <div className="hud-corner bottom-left"></div>
                        <div className="hud-corner bottom-right"></div>
                    </div>

                    <div className="controls">
                        <button
                            onClick={toggleMode}
                            className={`action-btn ${status.mode === "EXPLORE" ? "btn-primary" : "btn-secondary"}`}
                        >
                            {status.mode === "EXPLORE" ? "INITIATE RETURN" : "RESUME EXPLORATION"}
                        </button>
                    </div>
                </section>

                {/* Right Telemetry Panel */}
                <aside className="sidebar right-sidebar">
                    <div className="panel confidence-panel">
                        <h2>Match Confidence</h2>
                        <div className="gauge-container">
                            <svg className="gauge-svg" viewBox="0 0 128 128">
                                <circle cx="64" cy="64" r="60" className="gauge-bg" />
                                <circle
                                    cx="64" cy="64" r="60"
                                    className="gauge-progress"
                                    strokeDasharray={377}
                                    strokeDashoffset={377 - (377 * status.confidence) / 100}
                                    stroke={status.confidence > 70 ? "#00ff00" : status.confidence > 30 ? "#ffbf00" : "#ff0000"}
                                />
                            </svg>
                            <div className="gauge-value">{Math.round(status.confidence)}%</div>
                        </div>
                        <div className="signal-bar-container">
                            <div className="signal-label">
                                <span>SIGNAL</span>
                                <span>{status.confidence > 70 ? "STRONG" : "WEAK"}</span>
                            </div>
                            <div className="signal-track">
                                <div className="signal-fill" style={{ width: `${status.confidence}%`, backgroundColor: status.confidence > 70 ? '#00ff00' : '#ff0000' }}></div>
                            </div>
                        </div>
                    </div>

                    <div className="panel telemetry-panel">
                        <h2>Telemetry</h2>
                        <div className="telemetry-list">
                            <div className="t-row"><span className="label">FPS</span><span className="val color-green">60.0</span></div>
                            <div className="t-row"><span className="label">LATENCY</span><span className="val color-green">14ms</span></div>
                            <div className="t-row"><span className="label">FEATURES</span><span className="val color-amber">492</span></div>
                            <div className="t-row"><span className="label">GPS</span><span className="val color-red">OFFLINE</span></div>
                        </div>
                        <div className="viz-bars">
                            {[40, 60, 30, 80, 50, 90, 20, 40, 60].map((h, i) => (
                                <div key={i} className="viz-bar" style={{ height: `${h}%`, animationDelay: `${i * 0.1}s` }}></div>
                            ))}
                        </div>
                    </div>
                </aside>

            </main>

            <footer className="hud-footer">
                <div>TRAILSENSE OS // BUILD 2026.02.15</div>
                <div>SECURE CONNECTION ESTABLISHED</div>
            </footer>
        </div>
    )
}

export default App
