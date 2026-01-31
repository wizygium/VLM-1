/**
 * Handball Physics Visualizer - Main Application
 */

// Global state
let physicsData = null;
let eventsData = null;
let currentFrameIndex = 0;
let courtRenderer = null;
let videoSyncEnabled = true;

// DOM Elements
const analysisSelect = document.getElementById('analysis-select');
const videoPlayer = document.getElementById('video-player');
const videoLoading = document.getElementById('video-loading');
const videoError = document.getElementById('video-error');
const playPauseBtn = document.getElementById('play-pause-btn');
const prevFrameBtn = document.getElementById('prev-frame-btn');
const nextFrameBtn = document.getElementById('next-frame-btn');
const playbackSpeed = document.getElementById('playback-speed');
const timelineScrubber = document.getElementById('timeline-scrubber');
const courtCanvas = document.getElementById('court-canvas');

// Info displays
const currentTimeDisplay = document.getElementById('current-time');
const currentFrameDisplay = document.getElementById('current-frame');
const ballInfoDisplay = document.getElementById('ball-info');
const eventsList = document.getElementById('events-list');
const playersList = document.getElementById('players-list');
const analysisInfo = document.getElementById('analysis-info');
const infoFrames = document.getElementById('info-frames');
const infoDuration = document.getElementById('info-duration');
const infoPlayers = document.getElementById('info-players');

// Timeline info
const timelineStart = document.getElementById('timeline-start');
const timelineCurrent = document.getElementById('timeline-current');
const timelineEnd = document.getElementById('timeline-end');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize court renderer
    courtRenderer = new HandballCourtRenderer(courtCanvas);
    courtRenderer.drawCourt();

    // Load available analyses
    await loadAnalyses();

    // Set up event listeners
    setupEventListeners();
});

/**
 * Load list of available analyses
 */
async function loadAnalyses() {
    try {
        const response = await fetch('/api/analyses');
        const data = await response.json();

        analysisSelect.innerHTML = '';

        if (data.analyses.length === 0) {
            analysisSelect.innerHTML = '<option value="">No analyses available</option>';
            return;
        }

        analysisSelect.innerHTML = '<option value="">Select an analysis...</option>';
        data.analyses.forEach(analysis => {
            const option = document.createElement('option');
            option.value = analysis.name;
            option.textContent = `${analysis.name} (${analysis.total_frames} frames, ${analysis.duration.toFixed(1)}s)`;
            analysisSelect.appendChild(option);
        });

    } catch (error) {
        console.error('Failed to load analyses:', error);
        analysisSelect.innerHTML = '<option value="">Error loading analyses</option>';
    }
}

/**
 * Load selected analysis
 */
async function loadAnalysis(analysisName) {
    if (!analysisName) return;

    try {
        // Show loading state
        videoLoading.style.display = 'flex';
        videoError.classList.add('hidden');

        // Fetch physics data
        const physicsResponse = await fetch(`/api/physics/${analysisName}`);
        physicsData = await physicsResponse.json();

        // Fetch events data (optional)
        try {
            const eventsResponse = await fetch(`/api/events/${analysisName}`);
            eventsData = await eventsResponse.json();
        } catch (e) {
            console.warn('No events data available');
            eventsData = null;
        }

        // Get video URL
        const videoUrlResponse = await fetch(`/api/video-url/${analysisName}`);
        const videoUrlData = await videoUrlResponse.json();

        // Load video
        videoPlayer.src = videoUrlData.url;
        videoPlayer.load();

        // Update UI
        updateAnalysisInfo();
        displayEvents();
        displayPlayers();

        // Enable controls
        playPauseBtn.disabled = false;
        prevFrameBtn.disabled = false;
        nextFrameBtn.disabled = false;
        timelineScrubber.disabled = false;

        // Set timeline range
        const frames = physicsData.frames || [];
        timelineScrubber.max = frames.length - 1;
        timelineScrubber.value = 0;

        // Display first frame
        currentFrameIndex = 0;
        renderCurrentFrame();

        videoLoading.style.display = 'none';

    } catch (error) {
        console.error('Failed to load analysis:', error);
        videoLoading.style.display = 'none';
        videoError.classList.remove('hidden');
        videoError.querySelector('p').textContent = `⚠️ ${error.message}`;
    }
}

/**
 * Update analysis info panel
 */
function updateAnalysisInfo() {
    if (!physicsData) return;

    const metadata = physicsData.metadata || {};
    const frames = physicsData.frames || [];

    // Calculate unique players
    const uniquePlayers = new Set();
    frames.forEach(frame => {
        (frame.players || []).forEach(player => {
            if (player.track_id) {
                uniquePlayers.add(player.track_id);
            }
        });
    });

    infoFrames.textContent = `${frames.length} frames`;
    infoDuration.textContent = `${(frames.length * 0.0625).toFixed(1)}s`;
    infoPlayers.textContent = `${uniquePlayers.size} players`;

    analysisInfo.classList.remove('hidden');

    // Update timeline labels
    timelineStart.textContent = '0.00s';
    if (frames.length > 0) {
        const lastFrame = frames[frames.length - 1];
        timelineEnd.textContent = `${parseFloat(lastFrame.timestamp || 0).toFixed(2)}s`;
    }
}

/**
 * Render current frame on court
 */
function renderCurrentFrame() {
    if (!physicsData || !courtRenderer) return;

    const frames = physicsData.frames || [];
    if (currentFrameIndex < 0 || currentFrameIndex >= frames.length) return;

    const frame = frames[currentFrameIndex];

    // Render court with frame data
    courtRenderer.renderFrame(frame);

    // Update info displays
    currentTimeDisplay.textContent = `${parseFloat(frame.timestamp || 0).toFixed(3)}s`;
    currentFrameDisplay.textContent = `${currentFrameIndex + 1} / ${frames.length}`;

    const ball = frame.ball || {};
    const holder = ball.holder_track_id ? `Held by ${ball.holder_track_id}` : 'Loose';
    ballInfoDisplay.textContent = `${ball.state || 'Unknown'} - ${holder} (${ball.zone || 'Unknown'})`;

    // Update timeline
    timelineScrubber.value = currentFrameIndex;
    timelineCurrent.textContent = `${parseFloat(frame.timestamp || 0).toFixed(2)}s`;

    // Sync video if enabled
    if (videoSyncEnabled && videoPlayer.paused) {
        const timestamp = parseFloat(frame.timestamp || 0);
        if (Math.abs(videoPlayer.currentTime - timestamp) > 0.1) {
            videoPlayer.currentTime = timestamp;
        }
    }
}

/**
 * Display events list
 */
function displayEvents() {
    if (!eventsData || !eventsData.events || eventsData.events.length === 0) {
        eventsList.innerHTML = '<p class="placeholder">No events detected</p>';
        return;
    }

    eventsList.innerHTML = '';

    eventsData.events.forEach((event, index) => {
        const card = document.createElement('div');
        card.className = `event-card ${event.type.toLowerCase()}`;
        card.onclick = () => seekToEvent(event);

        const type = document.createElement('div');
        type.className = 'event-type';
        type.textContent = `${event.type} @ ${parseFloat(event.time).toFixed(2)}s`;

        const details = document.createElement('div');
        details.className = 'event-details';

        if (event.type === 'PASS') {
            const from = event.from_jersey || '?';
            const to = event.to_jersey || '?';
            details.innerHTML = `
                #${from} → #${to}<br>
                ${event.from_zone} → ${event.to_zone}
            `;
        } else if (event.type === 'SHOT') {
            const shooter = event.shooter_jersey || '?';
            details.innerHTML = `
                Shooter: #${shooter}<br>
                From: ${event.from_zone}
            `;
        }

        card.appendChild(type);
        card.appendChild(details);
        eventsList.appendChild(card);
    });
}

/**
 * Display tracked players
 */
function displayPlayers() {
    if (!physicsData) return;

    // Collect all unique players
    const playersMap = new Map();

    (physicsData.frames || []).forEach(frame => {
        (frame.players || []).forEach(player => {
            if (!playersMap.has(player.track_id)) {
                playersMap.set(player.track_id, player);
            }
        });
    });

    if (playersMap.size === 0) {
        playersList.innerHTML = '<p class="placeholder">No players tracked</p>';
        return;
    }

    playersList.innerHTML = '';

    Array.from(playersMap.values()).forEach(player => {
        const card = document.createElement('div');
        card.className = `player-card ${player.team || 'unknown'}`;

        const trackId = document.createElement('div');
        trackId.className = 'player-track-id';
        trackId.textContent = player.track_id;

        const jersey = document.createElement('div');
        jersey.className = 'player-jersey';
        jersey.textContent = `#${player.jersey_number || '?'}`;

        const team = document.createElement('div');
        team.className = 'player-team';
        team.textContent = player.team || 'unknown';

        card.appendChild(trackId);
        card.appendChild(jersey);
        card.appendChild(team);

        playersList.appendChild(card);
    });
}

/**
 * Seek to event time
 */
function seekToEvent(event) {
    if (!physicsData) return;

    const eventTime = parseFloat(event.time);
    const frames = physicsData.frames || [];

    // Find closest frame
    let closestIndex = 0;
    let closestDiff = Infinity;

    frames.forEach((frame, index) => {
        const frameTime = parseFloat(frame.timestamp || 0);
        const diff = Math.abs(frameTime - eventTime);
        if (diff < closestDiff) {
            closestDiff = diff;
            closestIndex = index;
        }
    });

    currentFrameIndex = closestIndex;
    renderCurrentFrame();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Analysis selection
    analysisSelect.addEventListener('change', (e) => {
        loadAnalysis(e.target.value);
    });

    // Play/Pause
    playPauseBtn.addEventListener('click', () => {
        if (videoPlayer.paused) {
            videoPlayer.play();
            playPauseBtn.textContent = '⏸ Pause';
        } else {
            videoPlayer.pause();
            playPauseBtn.textContent = '▶️ Play';
        }
    });

    // Video state changes
    videoPlayer.addEventListener('play', () => {
        playPauseBtn.textContent = '⏸ Pause';
    });

    videoPlayer.addEventListener('pause', () => {
        playPauseBtn.textContent = '▶️ Play';
    });

    // Video time update - sync with physics frames
    videoPlayer.addEventListener('timeupdate', () => {
        if (!physicsData || !videoSyncEnabled) return;

        const currentTime = videoPlayer.currentTime;
        const frames = physicsData.frames || [];

        // Find closest frame
        let closestIndex = 0;
        let closestDiff = Infinity;

        frames.forEach((frame, index) => {
            const frameTime = parseFloat(frame.timestamp || 0);
            const diff = Math.abs(frameTime - currentTime);
            if (diff < closestDiff) {
                closestDiff = diff;
                closestIndex = index;
            }
        });

        if (closestIndex !== currentFrameIndex) {
            currentFrameIndex = closestIndex;
            renderCurrentFrame();
        }
    });

    // Playback speed
    playbackSpeed.addEventListener('change', (e) => {
        videoPlayer.playbackRate = parseFloat(e.target.value);
    });

    // Frame navigation
    prevFrameBtn.addEventListener('click', () => {
        if (currentFrameIndex > 0) {
            currentFrameIndex--;
            renderCurrentFrame();
        }
    });

    nextFrameBtn.addEventListener('click', () => {
        const frames = physicsData?.frames || [];
        if (currentFrameIndex < frames.length - 1) {
            currentFrameIndex++;
            renderCurrentFrame();
        }
    });

    // Timeline scrubber
    timelineScrubber.addEventListener('input', (e) => {
        currentFrameIndex = parseInt(e.target.value);
        renderCurrentFrame();
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'SELECT') return;

        switch (e.key) {
            case ' ':
                e.preventDefault();
                playPauseBtn.click();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                prevFrameBtn.click();
                break;
            case 'ArrowRight':
                e.preventDefault();
                nextFrameBtn.click();
                break;
        }
    });
}
