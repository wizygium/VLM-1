/**
 * Handball Court Renderer
 *
 * Renders a handball court with 10-zone system (z0-z9) and player positions
 * 
 * Zone System:
 * z0: Goal Area (inside 6m arc)
 * z1-z3: Band 1 (6m-9m) - Left/Center/Right
 * z4-z6: Band 2 (9m-12m) - Left/Center/Right
 * z7-z9: Band 3 (12m-20m) - Left/Center/Right
 */

class HandballCourtRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Make court square for 20x20m half court
        const size = Math.min(canvas.width, canvas.height);
        this.width = size;
        this.height = size;

        // Update canvas size to be square
        canvas.width = size;
        canvas.height = size;

        // Court dimensions (scaled to canvas)
        this.courtMargin = 40;
        this.courtWidth = this.width - (this.courtMargin * 2);
        this.courtHeight = this.height - (this.courtMargin * 2);

        // 10-zone system (z0-z9)
        this.zoneCount = 10;

        // Colors
        this.colors = {
            courtBg: '#f5f3e8',
            courtLines: '#2c3e50',
            goalZone: '#ffebcd',
            gridLines: '#d4d4d4',
            blueTeam: '#4A90E2',
            whiteTeam: '#666666', // Fix 2: Dark Grey for better contrast vs courtBg
            unknownTeam: '#95a5a6',
            ball: '#FFD700',
            ballHolder: '#FF6B6B',
            zoneLabel: '#7f8c8d'
        };
    }

    /**
     * Draw the complete court
     */
    drawCourt() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.width, this.height);

        // Draw court background
        this.ctx.fillStyle = this.colors.courtBg;
        this.ctx.fillRect(
            this.courtMargin,
            this.courtMargin,
            this.courtWidth,
            this.courtHeight
        );

        // Draw zone regions with faint chessboard coloring
        this.drawZoneRegions();

        // Fix 3: Removed opaque "Goal Zone" rectangle that was hiding zone colors near the line
        // The D-zone (z0) is drawn later in drawZoneRegions and is sufficient.

        // Draw handball court lines (6m D, 9m D, sidelines)
        this.drawHandballCourtLines();

        // Draw court border
        this.ctx.strokeStyle = this.colors.courtLines;
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(
            this.courtMargin,
            this.courtMargin,
            this.courtWidth,
            this.courtHeight
        );

        // Draw labels
        this.drawZoneLabels();
        this.drawLegend();
    }

    /**
     * Draw faint chessboard coloring for zone regions
     * Extends to full width (corners) and depth (goal line)
     */
    /**
     * Draw circular zone regions (Painter's Algorithm with Clipping)
     * Layer 1: Band 3 (Deep) - Background
     * Layer 2: Band 2 (Outside 9m) - Drawn as Rects
     * Layer 3: Band 1 (Inside 9m) - Clipped to 9m Arc
     * Layer 4: Goal Area (Inside 6m) - Clipped to 6m Arc
     */
    drawZoneRegions() {
        const centerX = this.courtMargin + this.courtWidth / 2;
        const goalY = this.courtMargin + this.courtHeight;
        const metersToPixels = this.courtWidth / 20;

        const courtLeft = this.courtMargin;
        const courtRight = this.courtMargin + this.courtWidth;
        const courtTop = this.courtMargin;

        const radius6m = 6 * metersToPixels;
        const radius9m = 9 * metersToPixels;

        const goalHalfWidth = 1.5 * metersToPixels;
        const leftPostX = centerX - goalHalfWidth;
        const rightPostX = centerX + goalHalfWidth;

        // Colors
        const colorA = 'rgba(200, 220, 240, 0.3)';
        const colorB = 'rgba(240, 220, 200, 0.3)';
        const colorCorner = 'rgba(220, 200, 240, 0.3)';

        this.ctx.save();

        // 1. Deep Court (Band 3) + Band 2 base
        const y12m = goalY - 12 * metersToPixels;

        this.ctx.fillStyle = colorA;
        this.ctx.fillRect(courtLeft, courtTop, (centerX - courtLeft) / 2, y12m - courtTop);
        this.ctx.fillStyle = colorB;
        this.ctx.fillRect(courtLeft + (centerX - courtLeft) / 2, courtTop, centerX - (courtLeft + (centerX - courtLeft) / 2) + (centerX - courtLeft) / 2, y12m - courtTop);
        this.ctx.fillStyle = colorA;
        this.ctx.fillRect(courtLeft, courtTop, this.courtWidth, y12m - courtTop);

        // Band 2 Rects (9m-12m)
        this.ctx.fillStyle = colorB;
        this.ctx.fillRect(courtLeft, y12m, this.courtWidth, goalY - y12m);

        // 2. Band 1 (Inside 9m)
        this.ctx.save();
        this.ctx.beginPath();
        this.ctx.moveTo(leftPostX, goalY - radius9m);
        this.ctx.lineTo(rightPostX, goalY - radius9m);
        this.ctx.arc(rightPostX, goalY, radius9m, Math.PI * 1.5, Math.PI * 2, false);
        this.ctx.arc(rightPostX, goalY, radius9m, Math.PI * 1.5, Math.PI * 2, false);
        this.ctx.lineTo(leftPostX, goalY);
        this.ctx.arc(leftPostX, goalY, radius9m, Math.PI, Math.PI * 1.5, false);
        this.ctx.clip();

        // Draw Band 1 Zones inside Clip
        // Left Corner (z14)
        this.ctx.fillStyle = colorCorner;
        this.ctx.fillRect(courtLeft, goalY - 4 * metersToPixels, 3 * metersToPixels, 4 * metersToPixels);

        // Left Wing (z1)
        this.ctx.fillStyle = colorA;
        this.ctx.fillRect(courtLeft, goalY - 9 * metersToPixels, 5 * metersToPixels, 5 * metersToPixels);

        // Center (z2, z3, z4)
        this.ctx.fillStyle = colorB;
        this.ctx.fillRect(centerX - 5 * metersToPixels, goalY - 9 * metersToPixels, 10 * metersToPixels, 6 * metersToPixels);

        // Right Wing (z5)
        this.ctx.fillStyle = colorA;
        this.ctx.fillRect(courtRight - 5 * metersToPixels, goalY - 9 * metersToPixels, 5 * metersToPixels, 5 * metersToPixels);

        // Right Corner (z15)
        this.ctx.fillStyle = colorCorner;
        this.ctx.fillRect(courtRight - 3 * metersToPixels, goalY - 4 * metersToPixels, 3 * metersToPixels, 4 * metersToPixels);

        this.ctx.restore();

        // 3. Goal Area (Inside 6m)
        this.ctx.beginPath();
        this.ctx.moveTo(leftPostX, goalY - radius6m);
        this.ctx.lineTo(rightPostX, goalY - radius6m);
        this.ctx.arc(rightPostX, goalY, radius6m, Math.PI * 1.5, Math.PI * 2, false);
        this.ctx.lineTo(leftPostX, goalY);
        this.ctx.arc(leftPostX, goalY, radius6m, Math.PI, Math.PI * 1.5, false);
        this.ctx.closePath();

        this.ctx.fillStyle = 'rgba(255, 235, 205, 0.6)';
        this.ctx.fill();

        this.ctx.restore();
    }

    /**
     * Draw handball court lines (6m D-line, 9m D-line, halfway line)
     * Court: 20m wide x 20m deep (one half of full 40m court)
     * Goal: 3m wide
     */
    drawHandballCourtLines() {
        const centerX = this.courtMargin + this.courtWidth / 2;
        const goalY = this.courtMargin + this.courtHeight; // Bottom of court (goal line)

        // Court scale: 20m width and depth maps to canvas dimensions
        const metersToPixels = this.courtWidth / 20; // pixels per meter

        // Goal dimensions (3m wide)
        const goalWidthMeters = 3;
        const goalHalfWidth = (goalWidthMeters / 2) * metersToPixels; // 1.5m in pixels
        const leftPostX = centerX - goalHalfWidth;
        const rightPostX = centerX + goalHalfWidth;

        // Draw goal
        this.ctx.fillStyle = '#fff';
        this.ctx.fillRect(leftPostX, goalY - 8, goalHalfWidth * 2, 8);
        this.ctx.strokeStyle = '#000';
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(leftPostX, goalY - 8, goalHalfWidth * 2, 8);

        // === 6m D-line (solid) ===
        const radius6m = 6 * metersToPixels; // 6m radius in pixels
        const top6m = goalY - radius6m; // Where the straight line connects

        this.ctx.strokeStyle = this.colors.courtLines;
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([]);

        // Left arc (centered at left goal post)
        this.ctx.beginPath();
        this.ctx.arc(leftPostX, goalY, radius6m, Math.PI, Math.PI * 1.5, false);
        this.ctx.stroke();

        // Right arc (centered at right goal post)
        this.ctx.beginPath();
        this.ctx.arc(rightPostX, goalY, radius6m, Math.PI * 1.5, Math.PI * 2, false);
        this.ctx.stroke();

        // Connecting straight line (3m across the top)
        this.ctx.beginPath();
        this.ctx.moveTo(leftPostX, top6m);
        this.ctx.lineTo(rightPostX, top6m);
        this.ctx.stroke();

        // === 9m D-line (dashed) - trimmed at sidelines ===
        const radius9m = 9 * metersToPixels; // 9m radius in pixels
        const top9m = goalY - radius9m; // Where the straight line connects

        this.ctx.strokeStyle = this.colors.courtLines;
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([10, 10]);

        // Calculate where 9m arc intersects sideline
        const leftSidelineX = this.courtMargin;
        const rightSidelineX = this.courtMargin + this.courtWidth;

        // For left arc centered at leftPostX with radius9m
        // Distance from left post to left sideline (horizontal)
        const leftDx = leftPostX - leftSidelineX;

        // Left arc: starts at sideline intersection, goes up to vertical (3π/2)
        // The arc is centered at (leftPostX, goalY)
        // At x = leftSidelineX: leftPostX - radius9m*cos(θ) = leftSidelineX
        // So cos(θ) = leftDx/radius9m, and angle θ = π + acos(leftDx/radius9m)
        if (leftDx < radius9m) {
            const leftEndAngle = Math.PI + Math.acos(leftDx / radius9m);
            this.ctx.beginPath();
            this.ctx.arc(leftPostX, goalY, radius9m, leftEndAngle, Math.PI * 1.5, false);
            this.ctx.stroke();
        }

        // For right arc centered at rightPostX with radius9m
        // Distance from right post to right sideline
        const rightDx = rightSidelineX - rightPostX;

        // Right arc: starts at vertical (3π/2), goes to sideline intersection
        // At x = rightSidelineX: rightPostX + radius9m*cos(θ) = rightSidelineX
        // So cos(θ) = rightDx/radius9m, and angle θ = 2π - acos(rightDx/radius9m)
        if (rightDx < radius9m) {
            const rightEndAngle = Math.PI * 2 - Math.acos(rightDx / radius9m);
            this.ctx.beginPath();
            this.ctx.arc(rightPostX, goalY, radius9m, Math.PI * 1.5, rightEndAngle, false);
            this.ctx.stroke();
        }

        // Connecting dashed straight line (3m across the top) - only draw if within court
        if (top9m > this.courtMargin) {
            this.ctx.beginPath();
            this.ctx.moveTo(leftPostX, top9m);
            this.ctx.lineTo(rightPostX, top9m);
            this.ctx.stroke();
        }

        // Reset line dash
        this.ctx.setLineDash([]);

        // === Halfway line (20m from goal line) ===
        const halfwayY = goalY - (20 * metersToPixels);
        if (halfwayY >= this.courtMargin - 2) { // At top of court for 20x20 display
            this.ctx.strokeStyle = this.colors.courtLines;
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.moveTo(this.courtMargin, halfwayY);
            this.ctx.lineTo(this.courtMargin + this.courtWidth, halfwayY);
            this.ctx.stroke();
        }

        // === Sidelines ===
        this.ctx.strokeStyle = this.colors.courtLines;
        this.ctx.lineWidth = 2;

        // Left sideline
        this.ctx.beginPath();
        this.ctx.moveTo(this.courtMargin, this.courtMargin);
        this.ctx.lineTo(this.courtMargin, goalY);
        this.ctx.stroke();

        // Right sideline
        this.ctx.beginPath();
        this.ctx.moveTo(this.courtMargin + this.courtWidth, this.courtMargin);
        this.ctx.lineTo(this.courtMargin + this.courtWidth, goalY);
        this.ctx.stroke();
    }

    /**
     * Draw zone labels with descriptive names (z1_lw, etc.)
     */
    drawZoneLabels() {
        this.ctx.fillStyle = this.colors.zoneLabel;
        this.ctx.font = 'bold 10px monospace';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';

        // 16-Zone System Labels (Attacker's Perspective: Left is Left)
        const zones = [
            'z0:GA',
            'z14:LC', 'z1:LW', 'z2:LCP', 'z3:CB1', 'z4:RCP', 'z5:RW', 'z15:RC',
            'z6:LB', 'z7:LCB', 'z8:CB2', 'z9:RCB', 'z10:RB',
            'z11:DL', 'z12:DC', 'z13:DR'
        ];

        zones.forEach(zoneSpec => {
            const [id, label] = zoneSpec.split(':');
            const coords = this.getZoneCoordinates(id);
            if (coords) {
                this.ctx.globalAlpha = 0.6;
                this.ctx.fillText(zoneSpec, coords.x, coords.y);
                this.ctx.globalAlpha = 1.0;
            }
        });
    }

    /**
     * Draw legend
     */
    drawLegend() {
        const legendX = this.courtMargin + this.courtWidth + 10;
        const legendY = this.courtMargin;

        this.ctx.textAlign = 'left';
        this.ctx.font = '12px sans-serif';

        // Team colors
        this.ctx.fillStyle = this.colors.blueTeam;
        this.ctx.fillRect(legendX, legendY, 15, 15);
        this.ctx.fillStyle = '#000';
        this.ctx.fillText('Blue Team', legendX + 20, legendY + 12);

        this.ctx.fillStyle = this.colors.whiteTeam;
        this.ctx.strokeStyle = '#999';
        this.ctx.lineWidth = 1;
        this.ctx.fillRect(legendX, legendY + 25, 15, 15);
        this.ctx.strokeRect(legendX, legendY + 25, 15, 15);
        this.ctx.fillStyle = '#000';
        this.ctx.fillText('White Team', legendX + 20, legendY + 37);

        this.ctx.fillStyle = this.colors.ball;
        this.ctx.beginPath();
        this.ctx.arc(legendX + 7.5, legendY + 55, 7.5, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.fillStyle = '#000';
        this.ctx.fillText('Ball', legendX + 20, legendY + 60);
    }

    /**
     * Get zone coordinates including sub-zones
     * Handled SWAPPED orientation (Attacker Top-Down)
     */
    /**
     * Get zone coordinates including sub-zones
     * Standard Map Orientation: Canvas Left = Left Wing
     */
    getZoneCoordinates(zone) {
        if (!zone) return null;

        // Strip suffix if present to handle raw 'z1' vs 'z1_lw'
        const baseZone = zone.split('_')[0];

        const goalY = this.courtMargin + this.courtHeight;
        const metersToPixels = this.courtWidth / 20;
        const centerX = this.courtMargin + this.courtWidth / 2;
        const courtLeft = this.courtMargin;
        const courtRight = this.courtMargin + this.courtWidth;

        // X Positions (Canvas coordinates)
        const xLeft = courtLeft + 3.75 * metersToPixels;   // Canvas Left
        const xCenter = centerX;
        const xRight = courtLeft + 16.25 * metersToPixels; // Canvas Right

        // Y Positions
        const yBand1 = goalY - 4 * metersToPixels;  // Deep corner / Pivot
        const yBand2 = goalY - 10.5 * metersToPixels;
        const yBand3 = goalY - 16 * metersToPixels;
        const yGoal = goalY - 3 * metersToPixels;

        // Mapping: Standard Map View (Left is Left)

        // Coordinate definitions (meters relative to center/goal)
        // Canvas Center = (centerX, goalY)
        // xLeft = Margin, xRight = width-Margin

        // --- NEW MAPPING matching gemini_context_zones.md (16 Zones) ---

        // Band 1 (6-9m) & Corners
        // z14: Deep Left Corner (New)
        // z1: Left Wing
        // z2: Left Half
        // z3: Center
        // z4: Right Half
        // z5: Right Wing
        // z15: Deep Right Corner (New)

        const yCorner = goalY - 1 * metersToPixels; // Near goal line
        const yWings = goalY - 4 * metersToPixels;
        const yCenterBand1 = goalY - 7.5 * metersToPixels;

        const xWingL = this.courtMargin + (2 * metersToPixels);
        const xHalfL = centerX - (5 * metersToPixels);
        const xHalfR = centerX + (5 * metersToPixels);
        const xWingR = this.courtMargin + this.courtWidth - (2 * metersToPixels);

        const map = {
            // Goal (z0) - Move default z0 center to the goal line for GK,
            // but we will clamp defenders in drawPlayers.
            'z0': { x: centerX, y: goalY - 4 },

            // Corners (Deep Wings) - SWAPPED for Attacker Perspective
            'z14': { x: xWingR, y: yCorner }, // Attacker Left Corner -> Canvas Right
            'z15': { x: xWingL, y: yCorner }, // Attacker Right Corner -> Canvas Left

            // Band 1 (6-9m) - SWAPPED for Attacker Perspective
            'z1': { x: xWingR, y: yWings }, // Left Wing -> Canvas Right
            'z2': { x: xHalfR, y: yWings }, // Left Center -> Canvas Right
            'z3': { x: centerX, y: yCenterBand1 }, // Center -> Center
            'z4': { x: xHalfL, y: yWings }, // Right Center -> Canvas Left
            'z5': { x: xWingL, y: yWings }, // Right Wing -> Canvas Left

            // Band 2 (9-12m) - SWAPPED for Attacker Perspective
            'z6': { x: xWingR, y: goalY - 10 * metersToPixels }, // LB -> Canvas Right
            'z7': { x: xHalfR, y: goalY - 11 * metersToPixels }, // LCB -> Canvas Right
            'z8': { x: centerX, y: goalY - 12 * metersToPixels }, // CB -> Center
            'z9': { x: xHalfL, y: goalY - 11 * metersToPixels }, // RCB -> Canvas Left
            'z10': { x: xWingL, y: goalY - 10 * metersToPixels }, // RB -> Canvas Left

            // Deep Court (12m+) - SWAPPED for Attacker Perspective
            'z11': { x: xHalfR, y: goalY - 15 * metersToPixels }, // Deep Left -> Canvas Right
            'z12': { x: centerX, y: goalY - 16 * metersToPixels }, // Deep Center -> Center
            'z13': { x: xHalfL, y: goalY - 15 * metersToPixels }  // Deep Right -> Canvas Left
        };

        return map[zone] || map[baseZone] || null;
    }

    /**
     * Trigger a visual flash for a specific player
     */
    flashPlayer(trackId) {
        this.flashedTrackId = trackId;
        // Force re-render immediately (if the app loop isn't running fast enough, but it is 60Hz now)
        // Auto-clear after 500ms
        if (this.flashTimeout) clearTimeout(this.flashTimeout);
        this.flashTimeout = setTimeout(() => {
            this.flashedTrackId = null;
        }, 500);
    }

    /**
     * Draw players on the court
     * Attackers (Blue/White): Circle
     * Defenders (White/Red?): Triangle
     */
    drawPlayers(players, ballHolderTrackId = null) {
        players.forEach(player => {
            let zone = player.zone || 'z8'; // Default to CB area if unknown
            let coords = this.getZoneCoordinates(zone);
            if (!coords) return;

            // Determine if player is a defender
            const isDefender = player.team === 'white' || (player.role && player.role.startsWith('D'));

            // Boundary Constraint (Issue #25): Defenders cannot be inside z0 (6m area)
            // If inference puts them in z0, we clamp them to the 6m perimeter (z3 center-ish)
            if (isDefender && zone === 'z0') {
                const clampCoords = this.getZoneCoordinates('z3');
                coords = { ...clampCoords };
            }

            // Determining style...
            // User request: Defenders = Triangle, Attackers = Circle
            const isAttacker = !isDefender;

            let fillColor = this.colors.unknownTeam;
            if (player.team === 'blue') fillColor = this.colors.blueTeam;
            if (player.team === 'white') fillColor = this.colors.whiteTeam;

            // Highlight ball holder
            const isBallHolder = player.track_id === ballHolderTrackId;
            const isFlashed = player.track_id === this.flashedTrackId;

            const size = (isBallHolder || isFlashed) ? 22 : 16;

            // Draw Flash Glow
            if (isFlashed) {
                this.ctx.save();
                this.ctx.beginPath();
                this.ctx.arc(coords.x, coords.y, size + 10, 0, Math.PI * 2);
                this.ctx.fillStyle = 'rgba(255, 255, 0, 0.5)'; // Yellow Glow
                this.ctx.fill();
                this.ctx.restore();
            }

            this.ctx.fillStyle = fillColor;
            this.ctx.beginPath();

            if (isDefender) {
                // Draw Triangle
                // Center matches circle center at (coords.x, coords.y)
                // Point up
                this.ctx.moveTo(coords.x, coords.y - size);
                this.ctx.lineTo(coords.x + size, coords.y + size * 0.8);
                this.ctx.lineTo(coords.x - size, coords.y + size * 0.8);
                this.ctx.closePath();
            } else {
                // Draw Circle
                this.ctx.arc(coords.x, coords.y, size, 0, Math.PI * 2);
            }
            this.ctx.fill();

            // Draw Jersey Number inside the shape
            if (player.jersey_number) {
                this.ctx.fillStyle = player.team === 'white' ? '#333' : '#fff'; // Text color based on team
                this.ctx.font = 'bold 11px sans-serif';
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                // Adjust Y for triangle vs circle for better visual centering
                const textY = isDefender ? coords.y + 2 : coords.y;
                this.ctx.fillText(player.jersey_number, coords.x, textY);
            }

            // Border
            this.ctx.strokeStyle = isBallHolder ? this.colors.ballHolder : '#333';
            this.ctx.lineWidth = isBallHolder ? 3 : 2;
            this.ctx.stroke();



            // Track ID below
            this.ctx.fillStyle = '#333';
            this.ctx.font = '10px monospace';
            // Adjust text position for triangle
            const textY = isDefender ? coords.y + size + 16 : coords.y + size + 14;
            this.ctx.fillText(player.track_id, coords.x, textY);
        });
    }

    /**
     * Draw ball on the court
     */
    drawBall(ballZone, ballState) {
        const coords = this.getZoneCoordinates(ballZone);
        if (!coords) return;

        // Don't draw ball if it's being held (player circle shows it)
        if (ballState === 'Holding') return;

        // Draw ball
        this.ctx.fillStyle = this.colors.ball;
        this.ctx.beginPath();
        this.ctx.arc(coords.x, coords.y, 10, 0, Math.PI * 2);
        this.ctx.fill();

        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();

        // State label
        this.ctx.fillStyle = '#333';
        this.ctx.font = '10px sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(ballState, coords.x, coords.y + 20);
    }

    /**
     * Render a complete frame
     */
    renderFrame(frameData) {
        this.drawCourt();

        if (!frameData) return;

        // Draw players
        const ball = frameData.ball || {};
        const players = frameData.players || [];

        this.drawPlayers(players, ball.holder_track_id);

        // Draw ball if not held
        if (ball.zone && ball.state !== 'Holding') {
            this.drawBall(ball.zone, ball.state);
        }
    }
}

// Export for use in app.js
window.HandballCourtRenderer = HandballCourtRenderer;
