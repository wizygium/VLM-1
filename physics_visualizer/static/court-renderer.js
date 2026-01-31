/**
 * Handball Court Renderer
 *
 * Renders a handball court with 14-zone system and player positions
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

        // 14-zone system
        this.zoneCount = 14;

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
     * 6m zones (z1-z5): 5 evenly spaced around 6m D-line
     *   - z1, z5 (wings): extend from goal line to 8m, covering the wing corners
     *   - z2, z4: 45° arc sections from 6m to 8m
     *   - z3 (pivot): 3m wide center section (matches goal width)
     * 
     * 9m zones (z6-z10): 5 evenly spaced around 9m D-line, from 8m to 10m radius
     *   - z6, z10: extend from 8m to sideline (trimmed at court edge)
     *   - z8: 3m wide center section
     * 
     * Deep zones (z11-z13): Beyond 10m to court edge
     *   - z12: 3m wide center section
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
        
        // Radii for zone boundaries
        const radius6m = 6 * metersToPixels;   // 6m D-line
        const radius8m = 8 * metersToPixels;   // Outer edge of 6m zones / Inner edge of 9m zones
        const radius10m = 10 * metersToPixels; // Outer edge of 9m zones
        
        // Two alternating faint colors
        const colorA = 'rgba(200, 220, 240, 0.3)'; // Faint blue
        const colorB = 'rgba(240, 220, 200, 0.3)'; // Faint orange
        
        // Angles for dividing arcs into 2 zones each (45 degrees per zone)
        const angle45 = Math.PI / 4; // 45 degrees
        
        this.ctx.save();
        
        // === DEEP ZONES (z11, z12, z13) - beyond 10m radius ===
        
        // z11 - Deep left (from sideline to left edge of z12)
        this.ctx.fillStyle = colorA;
        this.ctx.beginPath();
        this.ctx.moveTo(courtLeft, courtTop);
        this.ctx.lineTo(courtLeft, goalY);
        // Follow 10m arc (clipped at sideline)
        const leftArcStartAngle10m = Math.PI + Math.acos(Math.min(1, (leftPostX - courtLeft) / radius10m));
        this.ctx.arc(leftPostX, goalY, radius10m, Math.PI, Math.min(leftArcStartAngle10m, Math.PI * 1.5), false);
        this.ctx.lineTo(leftPostX, courtTop);
        this.ctx.closePath();
        this.ctx.fill();
        
        // z12 - Deep center (3m wide, aligned with goal)
        this.ctx.fillStyle = colorB;
        this.ctx.beginPath();
        this.ctx.moveTo(leftPostX, courtTop);
        this.ctx.lineTo(leftPostX, goalY - radius10m);
        this.ctx.lineTo(rightPostX, goalY - radius10m);
        this.ctx.lineTo(rightPostX, courtTop);
        this.ctx.closePath();
        this.ctx.fill();
        
        // z13 - Deep right (from right edge of z12 to sideline)
        this.ctx.fillStyle = colorA;
        this.ctx.beginPath();
        this.ctx.moveTo(rightPostX, courtTop);
        this.ctx.lineTo(rightPostX, goalY - radius10m);
        this.ctx.arc(rightPostX, goalY, radius10m, Math.PI * 1.5, Math.PI * 2, false);
        this.ctx.lineTo(courtRight, goalY);
        this.ctx.lineTo(courtRight, courtTop);
        this.ctx.closePath();
        this.ctx.fill();
        
        // === 9m ZONES (z6-z10) - from 8m to 10m radius, clipped at sidelines ===
        
        // z6 - Far left back (from sideline, along left arc)
        this.ctx.fillStyle = colorB;
        this.ctx.beginPath();
        // Start at sideline intersection with 10m arc (or court edge)
        this.ctx.moveTo(courtLeft, goalY);
        // Outer arc (10m) - only draw if it reaches sideline
        if (leftPostX - courtLeft < radius10m) {
            const startAngle10m = Math.PI + Math.acos((leftPostX - courtLeft) / radius10m);
            this.ctx.arc(leftPostX, goalY, radius10m, Math.PI, Math.min(startAngle10m, Math.PI + angle45), false);
        }
        this.ctx.arc(leftPostX, goalY, radius10m, Math.PI, Math.PI + angle45, false);
        // Inner arc (8m) back
        this.ctx.arc(leftPostX, goalY, radius8m, Math.PI + angle45, Math.PI, true);
        this.ctx.lineTo(courtLeft, goalY);
        this.ctx.closePath();
        this.ctx.fill();
        
        // z7 - Left-center back (45° to 90° on left arc)
        this.ctx.fillStyle = colorA;
        this.ctx.beginPath();
        this.ctx.arc(leftPostX, goalY, radius10m, Math.PI + angle45, Math.PI * 1.5, false);
        this.ctx.arc(leftPostX, goalY, radius8m, Math.PI * 1.5, Math.PI + angle45, true);
        this.ctx.closePath();
        this.ctx.fill();
        
        // z8 - Center back (3m wide, the flat section between arcs at top)
        this.ctx.fillStyle = colorB;
        this.ctx.beginPath();
        this.ctx.moveTo(leftPostX, goalY - radius10m);
        this.ctx.lineTo(rightPostX, goalY - radius10m);
        this.ctx.lineTo(rightPostX, goalY - radius8m);
        this.ctx.lineTo(leftPostX, goalY - radius8m);
        this.ctx.closePath();
        this.ctx.fill();
        
        // z9 - Right-center back (90° to 45° on right arc)
        this.ctx.fillStyle = colorA;
        this.ctx.beginPath();
        this.ctx.arc(rightPostX, goalY, radius10m, Math.PI * 1.5, Math.PI * 2 - angle45, false);
        this.ctx.arc(rightPostX, goalY, radius8m, Math.PI * 2 - angle45, Math.PI * 1.5, true);
        this.ctx.closePath();
        this.ctx.fill();
        
        // z10 - Far right back (45° to sideline on right arc)
        this.ctx.fillStyle = colorB;
        this.ctx.beginPath();
        this.ctx.arc(rightPostX, goalY, radius10m, Math.PI * 2 - angle45, Math.PI * 2, false);
        this.ctx.lineTo(courtRight, goalY);
        this.ctx.arc(rightPostX, goalY, radius8m, Math.PI * 2, Math.PI * 2 - angle45, true);
        this.ctx.closePath();
        this.ctx.fill();
        
        // === 6m ZONES (z1-z5) - from goal line to 8m radius ===
        
        // z1 - Left wing (from goal line to 8m, covering wing corner area)
        // This zone extends from the goal line up to 8m arc, and from sideline to 45° line
        this.ctx.fillStyle = colorA;
        this.ctx.beginPath();
        this.ctx.moveTo(courtLeft, goalY);
        this.ctx.arc(leftPostX, goalY, radius8m, Math.PI, Math.PI + angle45, false);
        // Draw line down to 45° point on goal line
        const x45at0 = leftPostX - radius8m * Math.cos(angle45);
        this.ctx.lineTo(x45at0, goalY);
        this.ctx.closePath();
        this.ctx.fill();
        
        // z2 - Left-center (45° to 90° on left arc, from 6m to 8m)
        this.ctx.fillStyle = colorB;
        this.ctx.beginPath();
        this.ctx.arc(leftPostX, goalY, radius8m, Math.PI + angle45, Math.PI * 1.5, false);
        this.ctx.arc(leftPostX, goalY, radius6m, Math.PI * 1.5, Math.PI + angle45, true);
        this.ctx.closePath();
        this.ctx.fill();
        
        // z3 - Center pivot (3m wide, from 6m to 8m height)
        this.ctx.fillStyle = colorA;
        this.ctx.beginPath();
        this.ctx.moveTo(leftPostX, goalY - radius8m);
        this.ctx.lineTo(rightPostX, goalY - radius8m);
        this.ctx.lineTo(rightPostX, goalY - radius6m);
        this.ctx.lineTo(leftPostX, goalY - radius6m);
        this.ctx.closePath();
        this.ctx.fill();
        
        // z4 - Right-center (90° to 45° on right arc, from 6m to 8m)
        this.ctx.fillStyle = colorB;
        this.ctx.beginPath();
        this.ctx.arc(rightPostX, goalY, radius8m, Math.PI * 1.5, Math.PI * 2 - angle45, false);
        this.ctx.arc(rightPostX, goalY, radius6m, Math.PI * 2 - angle45, Math.PI * 1.5, true);
        this.ctx.closePath();
        this.ctx.fill();
        
        // z5 - Right wing (from goal line to 8m, covering wing corner area)
        this.ctx.fillStyle = colorA;
        this.ctx.beginPath();
        const x45atRight = rightPostX + radius8m * Math.cos(angle45);
        this.ctx.moveTo(x45atRight, goalY);
        this.ctx.arc(rightPostX, goalY, radius8m, Math.PI * 2 - angle45, Math.PI * 2, false);
        this.ctx.lineTo(courtRight, goalY);
        this.ctx.closePath();
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
     * Draw zone labels (sample zones)
     */
    drawZoneLabels() {
        this.ctx.fillStyle = this.colors.zoneLabel;
        this.ctx.font = '10px monospace';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';

        // Label all 14 zones
        const zones = [
            'z0', 'z1', 'z2', 'z3', 'z4', 'z5',
            'z6', 'z7', 'z8', 'z9', 'z10',
            'z11', 'z12', 'z13'
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
     * Maps 14-zone system to handball court positions
     * 
     * Court: 20m wide, 20m deep (attacking half shown)
     * z0: Goal (goalkeeper)
     * z1-z5: 6-8m (Wing & Close Attack)
     * z6-z10: 9m line (Backcourt)
     * z11-z13: Beyond 9m (Deep)
     */
    getZoneCoordinates(zone) {
        const goalY = this.courtMargin + this.courtHeight; // Bottom (goal line)
        const metersToPixels = this.courtWidth / 20; // pixels per meter
        const centerX = this.courtMargin + this.courtWidth / 2;
        const courtLeft = this.courtMargin;
        const courtRight = this.courtMargin + this.courtWidth;
        const courtWidth = this.courtWidth;

        // Goal posts are at ±1.5m from center
        const goalHalfWidth = 1.5 * metersToPixels;
        const leftPostX = centerX - goalHalfWidth;
        const rightPostX = centerX + goalHalfWidth;
        
        // Zone radii (center of each zone band)
        const radius7m = 7 * metersToPixels;   // Center of 6m zones (6-8m)
        const radius9m = 9 * metersToPixels;   // Center of 9m zones (8-10m)
        const radius14m = 14 * metersToPixels; // Center of deep zones (10m+)
        
        // Angles for zone positions
        // z1/z5/z6/z10: 22.5° (center of 0-45° wing sector)
        // z2/z4/z7/z9: 67.5° (center of 45-90° sector)
        // z3/z8/z12: center (between goal posts)
        
        const angle22 = 22.5 * Math.PI / 180;  // Wing zone center
        const angle67 = 67.5 * Math.PI / 180;  // Center-adjacent zone center
        
        // Zone definitions - positioned at center of each zone region
        const zoneMap = {
            'z0': { x: centerX, y: goalY - 10 }, // Goal
            
            // 6m zones (z1-z5) - wings extend to goal line, center at ~4m from goal
            'z1': { 
                x: leftPostX - radius7m * Math.cos(angle22) * 0.6, 
                y: goalY - radius7m * Math.sin(angle22) * 0.6
            },
            'z2': { 
                x: leftPostX - radius7m * Math.cos(angle67), 
                y: goalY - radius7m * Math.sin(angle67) 
            },
            'z3': { 
                x: centerX, 
                y: goalY - radius7m 
            },
            'z4': { 
                x: rightPostX + radius7m * Math.cos(angle67), 
                y: goalY - radius7m * Math.sin(angle67) 
            },
            'z5': { 
                x: rightPostX + radius7m * Math.cos(angle22) * 0.6, 
                y: goalY - radius7m * Math.sin(angle22) * 0.6
            },
            
            // 9m zones (z6-z10) - radially placed at center of each zone
            'z6': { 
                x: leftPostX - radius9m * Math.cos(angle22), 
                y: goalY - radius9m * Math.sin(angle22) 
            },
            'z7': { 
                x: leftPostX - radius9m * Math.cos(angle67), 
                y: goalY - radius9m * Math.sin(angle67) 
            },
            'z8': { 
                x: centerX, 
                y: goalY - radius9m 
            },
            'z9': { 
                x: rightPostX + radius9m * Math.cos(angle67), 
                y: goalY - radius9m * Math.sin(angle67) 
            },
            'z10': { 
                x: rightPostX + radius9m * Math.cos(angle22), 
                y: goalY - radius9m * Math.sin(angle22) 
            },
            
            // Deep zones (z11-z13) - beyond 10m
            'z11': { x: courtLeft + courtWidth * 0.25, y: goalY - radius14m },
            'z12': { x: centerX, y: goalY - radius14m },
            'z13': { x: courtRight - courtWidth * 0.25, y: goalY - radius14m }
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
