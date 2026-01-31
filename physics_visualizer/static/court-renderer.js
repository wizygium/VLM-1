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
            whiteTeam: '#E8E8E8',
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

        // Draw goal zone (z0) at bottom
        const goalHeight = this.courtHeight * 0.05;
        this.ctx.fillStyle = this.colors.goalZone;
        this.ctx.fillRect(
            this.courtMargin,
            this.courtMargin + this.courtHeight - goalHeight,
            this.courtWidth,
            goalHeight
        );

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
     * 
     * 10-Zone System:
     * z0: Goal area (inside 6m arc)
     * z1-z3: Band 1 (6m-9m) - Left/Center/Right
     * z4-z6: Band 2 (9m-12m) - Left/Center/Right  
     * z7-z9: Band 3 (12m-20m) - Left/Center/Right
     * 
     * Lateral divisions: Left (x<7.5), Center (7.5≤x≤12.5), Right (x>12.5)
     */
    drawZoneRegions() {
        const centerX = this.courtMargin + this.courtWidth / 2;
        const goalY = this.courtMargin + this.courtHeight;
        const metersToPixels = this.courtWidth / 20;
        const courtLeft = this.courtMargin;
        const courtRight = this.courtMargin + this.courtWidth;
        const courtTop = this.courtMargin;
        
        // Goal post positions (1.5m from center each side = 3m goal)
        const goalHalfWidth = 1.5 * metersToPixels;
        const leftPostX = centerX - goalHalfWidth;
        const rightPostX = centerX + goalHalfWidth;
        
        // Lateral boundaries (7.5m and 12.5m from left)
        const leftBoundary = courtLeft + 7.5 * metersToPixels;
        const rightBoundary = courtLeft + 12.5 * metersToPixels;
        
        // Depth boundaries
        const radius6m = 6 * metersToPixels;
        const radius9m = 9 * metersToPixels;
        const depth12m = goalY - 12 * metersToPixels;
        
        // Two alternating faint colors
        const colorA = 'rgba(200, 220, 240, 0.3)'; // Faint blue
        const colorB = 'rgba(240, 220, 200, 0.3)'; // Faint orange
        
        this.ctx.save();
        
        // === BAND 3 (z7, z8, z9) - 12m to 20m ===
        
        // z7 - Band 3 Left
        this.ctx.fillStyle = colorA;
        this.ctx.fillRect(courtLeft, courtTop, leftBoundary - courtLeft, depth12m - courtTop);
        
        // z8 - Band 3 Center
        this.ctx.fillStyle = colorB;
        this.ctx.fillRect(leftBoundary, courtTop, rightBoundary - leftBoundary, depth12m - courtTop);
        
        // z9 - Band 3 Right
        this.ctx.fillStyle = colorA;
        this.ctx.fillRect(rightBoundary, courtTop, courtRight - rightBoundary, depth12m - courtTop);
        
        // === BAND 2 (z4, z5, z6) - 9m to 12m ===
        
        // z4 - Band 2 Left
        this.ctx.fillStyle = colorB;
        this.ctx.fillRect(courtLeft, depth12m, leftBoundary - courtLeft, goalY - radius9m - depth12m);
        
        // z5 - Band 2 Center
        this.ctx.fillStyle = colorA;
        this.ctx.fillRect(leftBoundary, depth12m, rightBoundary - leftBoundary, goalY - radius9m - depth12m);
        
        // z6 - Band 2 Right
        this.ctx.fillStyle = colorB;
        this.ctx.fillRect(rightBoundary, depth12m, courtRight - rightBoundary, goalY - radius9m - depth12m);
        
        // === BAND 1 (z1, z2, z3) - 6m to 9m arc ===
        // Simplified rectangular approximation for visualization
        
        // z1 - Band 1 Left
        this.ctx.fillStyle = colorA;
        this.ctx.fillRect(courtLeft, goalY - radius9m, leftBoundary - courtLeft, radius9m - radius6m);
        
        // z2 - Band 1 Center
        this.ctx.fillStyle = colorB;
        this.ctx.fillRect(leftBoundary, goalY - radius9m, rightBoundary - leftBoundary, radius9m - radius6m);
        
        // z3 - Band 1 Right
        this.ctx.fillStyle = colorA;
        this.ctx.fillRect(rightBoundary, goalY - radius9m, courtRight - rightBoundary, radius9m - radius6m);
        
        // === z0 - Goal Area (inside 6m) ===
        this.ctx.fillStyle = 'rgba(255, 235, 205, 0.5)';
        this.ctx.beginPath();
        // Left arc
        this.ctx.arc(leftPostX, goalY, radius6m, Math.PI, Math.PI * 1.5, false);
        // Top straight line
        this.ctx.lineTo(rightPostX, goalY - radius6m);
        // Right arc
        this.ctx.arc(rightPostX, goalY, radius6m, Math.PI * 1.5, Math.PI * 2, false);
        this.ctx.lineTo(courtRight, goalY);
        this.ctx.lineTo(courtLeft, goalY);
        this.ctx.closePath();
        this.ctx.fill();
        
        this.ctx.restore();
    }
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
     * Draw zone labels (10-zone system)
     */
    drawZoneLabels() {
        this.ctx.fillStyle = this.colors.zoneLabel;
        this.ctx.font = '10px monospace';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';

        // Label all 10 zones (z0-z9)
        const zones = [
            'z0', 'z1', 'z2', 'z3', 'z4', 'z5',
            'z6', 'z7', 'z8', 'z9'
        ];

        zones.forEach(zone => {
            const coords = this.getZoneCoordinates(zone);
            if (coords) {
                // Draw small zone label
                this.ctx.globalAlpha = 0.5;
                this.ctx.fillText(zone, coords.x, coords.y);
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
     * Get zone coordinates for rendering
     * Maps 10-zone system to handball court positions
     * 
     * Court: 20m wide, 20m deep (attacking half shown)
     * z0: Goal Area (inside 6m arc)
     * z1-z3: Band 1 (6m-9m) - Left/Center/Right
     * z4-z6: Band 2 (9m-12m) - Left/Center/Right
     * z7-z9: Band 3 (12m-20m) - Left/Center/Right
     * 
     * Lateral: Left (x<7.5), Center (7.5≤x≤12.5), Right (x>12.5)
     */
    getZoneCoordinates(zone) {
        const goalY = this.courtMargin + this.courtHeight; // Bottom (goal line)
        const metersToPixels = this.courtWidth / 20; // pixels per meter
        const centerX = this.courtMargin + this.courtWidth / 2;
        const courtLeft = this.courtMargin;
        const courtRight = this.courtMargin + this.courtWidth;

        // Lateral column centers (in meters from left)
        const leftColCenter = 3.75 * metersToPixels;   // Center of x<7.5
        const centerColCenter = 10 * metersToPixels;   // Center of 7.5≤x≤12.5
        const rightColCenter = 16.25 * metersToPixels; // Center of x>12.5
        
        // Depth band centers (in meters from goal)
        const band1Center = 7.5 * metersToPixels;  // Center of 6m-9m
        const band2Center = 10.5 * metersToPixels; // Center of 9m-12m
        const band3Center = 16 * metersToPixels;   // Center of 12m-20m
        
        // Zone definitions - positioned at center of each zone region
        const zoneMap = {
            'z0': { x: centerX, y: goalY - 3 * metersToPixels }, // Goal Area center
            
            // Band 1 (6m-9m): z1-z3
            'z1': { x: courtLeft + leftColCenter, y: goalY - band1Center },
            'z2': { x: centerX, y: goalY - band1Center },
            'z3': { x: courtLeft + rightColCenter, y: goalY - band1Center },
            
            // Band 2 (9m-12m): z4-z6
            'z4': { x: courtLeft + leftColCenter, y: goalY - band2Center },
            'z5': { x: centerX, y: goalY - band2Center },
            'z6': { x: courtLeft + rightColCenter, y: goalY - band2Center },
            
            // Band 3 (12m-20m): z7-z9
            'z7': { x: courtLeft + leftColCenter, y: goalY - band3Center },
            'z8': { x: centerX, y: goalY - band3Center },
            'z9': { x: courtLeft + rightColCenter, y: goalY - band3Center }
        };

        return zoneMap[zone] || null;
    }

    /**
     * Draw players on the court
     */
    drawPlayers(players, ballHolderTrackId = null) {
        players.forEach(player => {
            const coords = this.getZoneCoordinates(player.zone);
            if (!coords) return;

            // Determine color based on team
            let fillColor = this.colors.unknownTeam;
            if (player.team === 'blue') {
                fillColor = this.colors.blueTeam;
            } else if (player.team === 'white') {
                fillColor = this.colors.whiteTeam;
            }

            // Highlight ball holder
            const isBallHolder = player.track_id === ballHolderTrackId;
            const radius = isBallHolder ? 20 : 15;

            // Draw player circle
            this.ctx.fillStyle = fillColor;
            this.ctx.beginPath();
            this.ctx.arc(coords.x, coords.y, radius, 0, Math.PI * 2);
            this.ctx.fill();

            // Border
            this.ctx.strokeStyle = isBallHolder ? this.colors.ballHolder : '#333';
            this.ctx.lineWidth = isBallHolder ? 3 : 2;
            this.ctx.stroke();

            // Jersey number
            this.ctx.fillStyle = player.team === 'white' ? '#333' : '#fff';
            this.ctx.font = 'bold 12px sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            const jersey = player.jersey_number || '?';
            this.ctx.fillText(jersey, coords.x, coords.y);

            // Track ID below
            this.ctx.fillStyle = '#333';
            this.ctx.font = '10px monospace';
            this.ctx.fillText(player.track_id, coords.x, coords.y + radius + 12);
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
