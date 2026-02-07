const videoPathInput = document.getElementById('videoPath');
const contextPathInput = document.getElementById('contextPath');
const startBtn = document.getElementById('startBtn');
const resultsSection = document.getElementById('resultsSection');
const statusSection = document.getElementById('statusSection');
const jobStatusText = document.getElementById('jobStatus');
const jobIdText = document.getElementById('jobId');
const progressBar = document.getElementById('progressBar');
const exportBtn = document.getElementById('exportBtn');
const resetBtn = document.getElementById('resetBtn');

let currentJobId = null;
let pollInterval = null;

startBtn.addEventListener('click', async () => {
    const videoPath = videoPathInput.value;
    const contextPath = contextPathInput.value;
    const startOffset = parseFloat(document.getElementById('startOffset').value) || 0;
    const maxFrames = parseInt(document.getElementById('maxFrames').value) || 6;

    if (!videoPath) return alert('Please provide a video path');

    startBtn.disabled = true;
    startBtn.innerText = 'Initializing...';
    resultsSection.innerHTML = '';
    statusSection.classList.remove('hidden');

    try {
        const res = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                video_path: videoPath,
                context_path: contextPath,
                start_offset: startOffset,
                num_frames: maxFrames,
                batch_size: maxFrames
            })
        });
        const data = await res.json();
        currentJobId = data.job_id;
        jobIdText.innerText = `Job ID: ${currentJobId}`;
        jobStatusText.innerText = 'QUEUED';
        startPolling();
    } catch (e) {
        alert('Error starting analysis: ' + e);
        startBtn.disabled = false;
        startBtn.innerText = 'Start Analysis';
    }
});

exportBtn.addEventListener('click', () => {
    window.location.href = '/download-results';
});

resetBtn.addEventListener('click', () => {
    currentJobId = null;
    if (pollInterval) clearInterval(pollInterval);
    resultsSection.innerHTML = '';
    statusSection.classList.add('hidden');
    startBtn.disabled = false;
    startBtn.innerText = 'Start Analysis';
});

function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`/jobs/${currentJobId}`);
            const data = await res.json();

            // Display descriptive status as is, fallback to uppercase for short ones
            if (data.status.length < 15) {
                jobStatusText.innerText = data.status.replace(/_/g, ' ').toUpperCase();
            } else {
                jobStatusText.innerText = data.status;
            }

            // Basic progress estimate based on status string
            if (data.status.includes('Analyzing batch')) {
                const parts = data.status.match(/batch (\d+) of (\d+)/i);
                if (parts) {
                    const current = parseInt(parts[1]);
                    const total = parseInt(parts[2]);
                    progressBar.style.width = `${(current / total) * 100}%`;
                }
            } else if (data.status === 'completed') {
                progressBar.style.width = '100%';
                clearInterval(pollInterval);
                startBtn.disabled = false;
                startBtn.innerText = 'Start Analysis';
            } else if (data.status.includes('error')) {
                clearInterval(pollInterval);
                startBtn.disabled = false;
                startBtn.innerText = 'Start Analysis';
                alert('Analysis failed: ' + data.status);
            }

            renderResults(data.results);
        } catch (e) {
            console.error('Polling error:', e);
        }
    }, 2000);
}

function renderResults(results) {
    if (!results || results.length === 0) return;

    // Only render if count changed or for existing ones update verification
    results.forEach(res => {
        let card = document.getElementById(`frame-${res.id}`);
        if (!card) {
            card = document.createElement('div');
            card.id = `frame-${res.id}`;
            card.className = 'frame-card card';
            resultsSection.appendChild(card);

            const inferred = res.inferred || {};

            card.innerHTML = `
                <div class="frame-media">
                    <img src="${res.frame_url}" loading="lazy">
                    <video src="${res.clip_url}" loop muted playsinline></video>
                </div>
                <div class="frame-info">
                    <h3>Frame ${res.id} <span class="timestamp">${res.timestamp.toFixed(2)}s</span></h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">Team</span>
                            <span class="stat-value">${inferred.team || 'N/A'}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Action</span>
                            <span class="stat-value">${inferred.action || 'N/A'}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Player</span>
                            <span class="stat-value">#${inferred.shirt_number || '-'}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Outcome</span>
                            <span class="stat-value">${inferred.shot_outcome || '-'}</span>
                        </div>
                    </div>
                </div>
                <div class="frame-actions">
                    <button class="verify-btn tick ${res.verification === 'tick' ? 'active' : ''}" onclick="verify(${res.id}, 'tick')">✓ Correct</button>
                    <button class="verify-btn cross ${res.verification === 'cross' ? 'active' : ''}" onclick="verify(${res.id}, 'cross')">✗ Incorrect</button>
                    <span class="saved-indicator hidden">Saved!</span>
                </div>
            `;

            const video = card.querySelector('video');
            card.querySelector('.frame-media').addEventListener('mouseenter', () => video.play());
            card.querySelector('.frame-media').addEventListener('mouseleave', () => {
                video.pause();
                video.currentTime = 0;
            });
        } else {
            // Update active state of buttons
            const tickBtn = card.querySelector('.verify-btn.tick');
            const crossBtn = card.querySelector('.verify-btn.cross');

            if (res.verification === 'tick') {
                tickBtn.classList.add('active');
                crossBtn.classList.remove('active');
            } else if (res.verification === 'cross') {
                tickBtn.classList.remove('active');
                crossBtn.classList.add('active');
            } else {
                tickBtn.classList.remove('active');
                crossBtn.classList.remove('active');
            }
        }
    });
}

window.verify = async (frameId, status) => {
    // Optimistic UI update
    const card = document.getElementById(`frame-${frameId}`);
    if (card) {
        const tickBtn = card.querySelector('.verify-btn.tick');
        const crossBtn = card.querySelector('.verify-btn.cross');
        if (status === 'tick') {
            tickBtn.classList.add('active');
            crossBtn.classList.remove('active');
        } else {
            tickBtn.classList.remove('active');
            crossBtn.classList.add('active');
        }
    }

    try {
        await fetch(`/jobs/${currentJobId}/verify?frame_id=${frameId}&status=${status}`, {
            method: 'POST'
        });

        // Show saved indicator
        const indicator = card.querySelector('.saved-indicator');
        indicator.classList.remove('hidden');
        setTimeout(() => indicator.classList.add('hidden'), 2000);

    } catch (e) {
        console.error('Verification error:', e);
        alert('Failed to save verification');
    }
};
