/**
 * Handball Physics Visualizer - Main Application
 */

// Global state
let physicsData = null;
let eventsData = null;
let currentFrameIndex = 0;
let courtRenderer = null;
let videoSyncEnabled = true;
let zoneTestMode = false;

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
const zoneTestBtn = document.getElementById('zone-test-btn');
const clearTestBtn = document.getElementById('clear-test-btn');
const zoneLegend = document.getElementById('zone-legend');
const testSelect = document.getElementById('test-select');

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
    
    // Load test files into test dropdown
    await loadTestFiles();

    // Set up event listeners
    setupEventListeners();
});

/**
 * Load list of available analyses
 */
async function loadAnalyses() {
    console.log('loadAnalyses: Starting...');
    
    // Add visual debug element 
    const debugDiv = document.createElement('div');
    debugDiv.id = 'debug-output';
    debugDiv.style.cssText = 'position:fixed;top:10px;right:10px;background:#333;color:#0f0;padding:10px;font-family:monospace;font-size:12px;max-width:400px;z-index:9999;';
    document.body.appendChild(debugDiv);
    
    function debug(msg) {
        console.log(msg);
        debugDiv.innerHTML += msg + '<br>';
    }
    
    if (!analysisSelect) {
        debug('ERROR: analysisSelect is null!');
        return;
    }
    debug('analysisSelect found: ' + analysisSelect.id);
    
    try {
        debug('Fetching /api/analyses...');
        const response = await fetch('/api/analyses');
        debug('Response status: ' + response.status);
        const data = await response.json();
        debug('Data received: ' + JSON.stringify(data).substring(0, 200));
        debug('Analyses count: ' + (data.analyses ? data.analyses.length : 0));

        analysisSelect.innerHTML = '';

        if (!data.analyses || data.analyses.length === 0) {
            analysisSelect.innerHTML = '<option value="">No analyses available</option>';
            debug('No analyses found');
            return;
        }

        analysisSelect.innerHTML = '<option value="">Select an analysis...</option>';
        let addedCount = 0;
        data.analyses.forEach(analysis => {
            debug('Processing: ' + analysis.name);
            // Skip TEST files in main dropdown
            if (analysis.name.startsWith('TEST-')) {
                debug('Skipping TEST file: ' + analysis.name);
                return;
            }
            
            const option = document.createElement('option');
            option.value = analysis.name;
            option.textContent = `${analysis.name} (${analysis.total_frames} frames, ${analysis.duration.toFixed(1)}s)`;
            analysisSelect.appendChild(option);
            addedCount++;
        });
        debug('Added ' + addedCount + ' options to dropdown');

    } catch (error) {
        debug('ERROR: ' + error.message);
        console.error('loadAnalyses: Failed:', error);
        analysisSelect.innerHTML = '<option value="">Error loading analyses</option>';
    }
}

/**
 * Load test files into test dropdown
 */
async function loadTestFiles() {
    if (!testSelect) return;
    
    try {
        const response = await fetch('/api/analyses');
        const data = await response.json();

        testSelect.innerHTML = '<option value="">Load Test File...</option>';
        
        data.analyses.forEach(analysis => {
            // Only include TEST files
            if (!analysis.name.startsWith('TEST-')) return;
            
            const option = document.createElement('option');
            option.value = analysis.name;
            // Clean up the name for display
            const displayName = analysis.name.replace('TEST-', '').replace(/_/g, ' ');
            option.textContent = displayName;
            testSelect.appendChild(option);
        });

    } catch (error) {
        console.error('Failed to load test files:', error);
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
            case 't':
            case 'T':
                e.preventDefault();
                toggleZoneTest();
                break;
        }
    });

    // Zone test button
    if (zoneTestBtn) {
        zoneTestBtn.addEventListener('click', toggleZoneTest);
    }
    if (clearTestBtn) {
        clearTestBtn.addEventListener('click', clearZoneTest);
    }
    
    // Test file selector
    if (testSelect) {
        testSelect.addEventListener('change', async (e) => {
            const testName = e.target.value;
            if (!testName) return;
            
            await loadTestAnalysis(testName);
        });
    }
}

/**
 * Load a test analysis (no video, just physics data on court)
 */
async function loadTestAnalysis(testName) {
    try {
        const response = await fetch(`/api/physics/${testName}`);
        if (!response.ok) {
            throw new Error('Test file not found');
        }
        const testData = await response.json();
        
        // Store as current physics data
        physicsData = testData;
        currentFrameIndex = 0;
        
        // Enable frame navigation
        const frames = testData.frames || [];
        if (frames.length > 0) {
            prevFrameBtn.disabled = false;
            nextFrameBtn.disabled = false;
            timelineScrubber.disabled = false;
            timelineScrubber.max = frames.length - 1;
            timelineScrubber.value = 0;
        }
        
        // Render first frame
        renderCurrentFrame();
        
        // Show zone legend
        if (zoneLegend) zoneLegend.classList.remove('hidden');
        
        // Update display
        const metadata = testData.metadata || {};
        currentTimeDisplay.textContent = `TEST: ${testName}`;
        infoFrames.textContent = `${frames.length} frames`;
        infoDuration.textContent = metadata.test_description || 'Test file';
        analysisInfo.classList.remove('hidden');
        
    } catch (error) {
        console.error('Failed to load test analysis:', error);
        alert(`Failed to load test file: ${error.message}`);
    }
}

/**
 * Toggle zone test mode - loads TEST-10zone-all analysis
 */
async function toggleZoneTest() {
    if (zoneTestMode) {
        clearZoneTest();
        return;
    }
    
    zoneTestMode = true;
    zoneTestBtn.classList.add('hidden');
    clearTestBtn.classList.remove('hidden');
    if (zoneLegend) zoneLegend.classList.remove('hidden');
    
    // Load the test analysis via API
    try {
        const response = await fetch('/api/physics/TEST-10zone-all');
        if (!response.ok) {
            throw new Error('Test file not found');
        }
        const testData = await response.json();
        
        if (testData.frames && testData.frames.length > 0) {
            courtRenderer.renderFrame(testData.frames[0]);
            
            // Update info displays
            currentTimeDisplay.textContent = 'TEST MODE';
            currentFrameDisplay.textContent = 'Zone Test (z0-z9)';
            
            const ball = testData.frames[0].ball || {};
            ballInfoDisplay.textContent = `${ball.state} - ${ball.holder_track_id} (${ball.zone})`;
        }
    } catch (error) {
        console.error('Failed to load test data:', error);
        // Fallback: render inline test data
        showZoneTestFallback();
    }
}

/**
 * Fallback: show zone test with inline data if API fails
 */
function showZoneTestFallback() {
    if (!courtRenderer) return;

    // Create test frame with a player in each zone
    const testFrame = {
        timestamp: "TEST",
        ball: {
            holder_track_id: "t5",
            zone: "z5",
            state: "Holding"
        },
        players: [
            { track_id: "GK", zone: "z0", jersey_number: "1", team: "white" },
            { track_id: "t1", zone: "z1", jersey_number: "LW", team: "blue" },
            { track_id: "t2", zone: "z2", jersey_number: "PV", team: "blue" },
            { track_id: "t3", zone: "z3", jersey_number: "RW", team: "blue" },
            { track_id: "t4", zone: "z4", jersey_number: "LB", team: "white" },
            { track_id: "t5", zone: "z5", jersey_number: "CB", team: "white" },
            { track_id: "t6", zone: "z6", jersey_number: "RB", team: "white" },
            { track_id: "t7", zone: "z7", jersey_number: "7", team: "blue" },
            { track_id: "t8", zone: "z8", jersey_number: "8", team: "blue" },
            { track_id: "t9", zone: "z9", jersey_number: "9", team: "blue" }
        ]
    };

    courtRenderer.renderFrame(testFrame);

    // Update info displays
    currentTimeDisplay.textContent = 'TEST MODE';
    currentFrameDisplay.textContent = 'Zone Test (Fallback)';
    ballInfoDisplay.textContent = 'Holding - t5 (z5 - Band 2 Center)';
}

/**
 * Clear zone test and restore normal display
 */
function clearZoneTest() {
    zoneTestMode = false;
    zoneTestBtn.classList.remove('hidden');
    clearTestBtn.classList.add('hidden');
    if (zoneLegend) zoneLegend.classList.add('hidden');

    // Restore current frame or draw empty court
    if (physicsData && physicsData.frames && physicsData.frames.length > 0) {
        renderCurrentFrame();
    } else {
        courtRenderer.drawCourt();
        currentTimeDisplay.textContent = '0.000s';
        currentFrameDisplay.textContent = '0 / 0';
        ballInfoDisplay.textContent = '-';
    }
}
