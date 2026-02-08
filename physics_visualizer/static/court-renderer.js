/**
 * Handball Court Renderer
 *
 * Renders a handball half-court with 14-zone system (z0-z13) and player positions.
 *
 * Zone System (goal at bottom, 20m × 20m half-court):
 *   z0:      Goal area (inside 6m D-line)
 *   z1-z5:   Close attack (6m-8m) - wing corners + center
 *   z6-z10:  Back court (8m-10m) - wing backs + center
 *   z11-z13: Deep court (10m+) - right/center/left
 *
 * Zone boundaries follow actual 6m and 8m D-line arc geometry.
 */

class HandballCourtRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this._lastFrameData = null;

        // Colors
        this.colors = {
            courtBg: '#f5f3e8',
            courtLines: '#2c3e50',
            goalZone: '#ffebcd',
            gridLines: '#d4d4d4',
            blueTeam: '#4A90E2',
            whiteTeam: '#666666',
            unknownTeam: '#95a5a6',
            ball: '#FFD700',
            ballHolder: '#FF6B6B',
            zoneLabel: '#7f8c8d'
        };

        // Size canvas to fit its container
        this.resize();

        // Watch for container resizes
        this._resizeObserver = new ResizeObserver(() => this.resize());
        this._resizeObserver.observe(canvas.parentElement);
    }

    /**
     * Resize canvas to fill its container (as a square)
     */
    resize() {
        const container = this.canvas.parentElement;
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;

        // Make court square, fitting within the container
        const size = Math.min(containerWidth, containerHeight);
        if (size <= 0) return;

        // Use device pixel ratio for crisp rendering on retina displays
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = size * dpr;
        this.canvas.height = size * dpr;
        this.canvas.style.width = size + 'px';
        this.canvas.style.height = size + 'px';

        this.ctx = this.canvas.getContext('2d');
        this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        this.width = size;
        this.height = size;

        // Court dimensions (proportional margins)
        this.courtMargin = Math.max(20, Math.round(size * 0.05));
        this.courtWidth = this.width - (this.courtMargin * 2);
        this.courtHeight = this.height - (this.courtMargin * 2);

        // Re-render current content
        if (this._lastFrameData) {
            this.renderFrame(this._lastFrameData);
        } else {
            this.drawCourt();
        }
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
    }

    /**
     * Convert meter coordinates to canvas pixels.
     * Origin: (0,0) = bottom-left of court, goal at y=0.
     */
    _m2px(mx, my) {
        const s = this.courtWidth / 20;
        return {
            x: this.courtMargin + mx * s,
            y: this.courtMargin + this.courtHeight - my * s
        };
    }

    /**
     * Generate points along the LEFT-post D-line arc (center 8.5, 0).
     * Returns array of {x, y} in meters from yFrom to yTo.
     */
    _arcL(r, yFrom, yTo, steps = 20) {
        const pts = [];
        for (let i = 0; i <= steps; i++) {
            const y = yFrom + (yTo - yFrom) * i / steps;
            const sq = r * r - y * y;
            if (sq < 0) continue;
            pts.push({ x: 8.5 - Math.sqrt(sq), y });
        }
        return pts;
    }

    /**
     * Generate points along the RIGHT-post D-line arc (center 11.5, 0).
     */
    _arcR(r, yFrom, yTo, steps = 20) {
        const pts = [];
        for (let i = 0; i <= steps; i++) {
            const y = yFrom + (yTo - yFrom) * i / steps;
            const sq = r * r - y * y;
            if (sq < 0) continue;
            pts.push({ x: 11.5 + Math.sqrt(sq), y });
        }
        return pts;
    }

    /**
     * Draw a filled polygon from meter-coordinate points.
     */
    _fillMeterPoly(points, fillColor, strokeColor = null) {
        if (!points || points.length < 3) return;
        const p0 = this._m2px(points[0].x, points[0].y);
        this.ctx.beginPath();
        this.ctx.moveTo(p0.x, p0.y);
        for (let i = 1; i < points.length; i++) {
            const p = this._m2px(points[i].x, points[i].y);
            this.ctx.lineTo(p.x, p.y);
        }
        this.ctx.closePath();
        this.ctx.fillStyle = fillColor;
        this.ctx.fill();
        if (strokeColor) {
            this.ctx.strokeStyle = strokeColor;
            this.ctx.lineWidth = 1;
            this.ctx.stroke();
        }
    }

    /**
     * Build the 14 zone polygons (z0-z13) using exact D-line arc geometry.
     *
     * Court: 20m wide × 20m deep. Goal posts at (8.5, 0) and (11.5, 0).
     * Key boundaries:
     *   6m D-line: arcs from each post (r=6) + 3m straight at y=6
     *   8m D-line: arcs from each post (r=8) + 3m straight at y=8
     *   Lateral splits: x=7, x=13 (center vs sides)
     *   Wing splits: x=3.5, x=16.5 (wing-back vs center-back)
     *   y=3: where 9m line meets sidelines (wing corner cutoff)
     *   y=10: back court / deep court boundary
     */
    _buildZonePolygons() {
        // Pre-compute intersection y-values
        const sq = (v) => v * v;
        const arc6L_x7_y  = Math.sqrt(36 - sq(8.5 - 7));    // 6m arc at x=7  ≈ 5.81
        const arc6R_x13_y = Math.sqrt(36 - sq(13 - 11.5));   // 6m arc at x=13 ≈ 5.81
        const arc8L_x7_y  = Math.sqrt(64 - sq(8.5 - 7));     // 8m arc at x=7  ≈ 7.86
        const arc8R_x13_y = Math.sqrt(64 - sq(13 - 11.5));   // 8m arc at x=13 ≈ 7.86
        const arc8L_x3_5_y = Math.sqrt(64 - sq(8.5 - 3.5));  // 8m arc at x=3.5 ≈ 6.24
        const arc8R_x16_5_y = Math.sqrt(64 - sq(16.5 - 11.5)); // 8m arc at x=16.5 ≈ 6.24

        const zones = [];

        // z0: Goal area (inside 6m D-line)
        zones[0] = [
            ...this._arcL(6, 0, 6, 30),
            { x: 11.5, y: 6 },
            ...this._arcR(6, 6, 0, 30)
        ];

        // z1: Right wing corner (display right, attacker's left wing)
        // Between 6m arc, sideline, goal line, and y=3
        zones[1] = [
            { x: 20, y: 0 },
            { x: 20, y: 3 },
            ...this._arcR(6, 3, 0, 15)   // (≈16.70, 3) → (17.5, 0)
        ];

        // z2: Right-center 6m-8m (display center-right)
        // Between 6m arc (inner), 8m arc (outer), x=13 (left), y=3 (bottom)
        zones[2] = [
            { x: 13, y: arc6R_x13_y },
            ...this._arcR(6, arc6R_x13_y, 3, 15),  // 6m arc: (13, 5.81) → (16.70, 3)
            ...this._arcR(8, 3, arc8R_x13_y, 15),   // 8m arc: (18.92, 3) → (13, 7.86)
        ];

        // z3: Center 6m-8m (between 6m and 8m D-lines, x=7 to x=13)
        zones[3] = [
            ...this._arcL(6, arc6L_x7_y, 6, 10),    // 6m left arc: (7, 5.81) → (8.5, 6)
            { x: 11.5, y: 6 },                        // 6m straight top
            ...this._arcR(6, 6, arc6R_x13_y, 10),    // 6m right arc: (11.5, 6) → (13, 5.81)
            { x: 13, y: arc8R_x13_y },                // up to 8m arc
            ...this._arcR(8, arc8R_x13_y, 8, 8),     // 8m right arc: (13, 7.86) → (11.5, 8)
            { x: 8.5, y: 8 },                          // 8m straight top
            ...this._arcL(8, 8, arc8L_x7_y, 8),      // 8m left arc: (8.5, 8) → (7, 7.86)
        ];

        // z4: Left-center 6m-8m (display center-left, mirror of z2)
        zones[4] = [
            ...this._arcL(6, 3, arc6L_x7_y, 15),    // 6m arc: (3.30, 3) → (7, 5.81)
            { x: 7, y: arc8L_x7_y },                  // up to 8m arc
            ...this._arcL(8, arc8L_x7_y, 3, 15),     // 8m arc: (7, 7.86) → (1.08, 3)
            { x: 8.5 - Math.sqrt(36 - 9), y: 3 },    // along y=3 to 6m arc start
        ];

        // z5: Left wing corner (display left, mirror of z1)
        zones[5] = [
            { x: 0, y: 0 },
            ...this._arcL(6, 0, 3, 15),   // (2.50, 0) → (≈3.30, 3)
            { x: 0, y: 3 }
        ];

        // z6: Far left back (display left, x=0 to 3.5, y=3 to 10)
        zones[6] = [
            { x: 0, y: 3 },
            { x: 0, y: 10 },
            { x: 3.5, y: 10 },
            { x: 3.5, y: arc8L_x3_5_y },
            ...this._arcL(8, arc8L_x3_5_y, 3, 12),  // 8m arc: (3.5, 6.24) → (1.08, 3)
        ];

        // z7: Left-center back (x=3.5 to 7, 8m arc to y=10)
        zones[7] = [
            { x: 3.5, y: arc8L_x3_5_y },
            { x: 3.5, y: 10 },
            { x: 7, y: 10 },
            { x: 7, y: arc8L_x7_y },
            ...this._arcL(8, arc8L_x7_y, arc8L_x3_5_y, 10),  // 8m arc: (7, 7.86) → (3.5, 6.24)
        ];

        // z8: Center back (x=7 to 13, 8m arc to y=10)
        zones[8] = [
            { x: 7, y: arc8L_x7_y },
            { x: 7, y: 10 },
            { x: 13, y: 10 },
            { x: 13, y: arc8R_x13_y },
            ...this._arcR(8, arc8R_x13_y, 8, 8),     // 8m right arc: (13, 7.86) → (11.5, 8)
            { x: 8.5, y: 8 },
            ...this._arcL(8, 8, arc8L_x7_y, 8),      // 8m left arc: (8.5, 8) → (7, 7.86)
        ];

        // z9: Right-center back (mirror of z7)
        zones[9] = [
            { x: 13, y: arc8R_x13_y },
            { x: 13, y: 10 },
            { x: 16.5, y: 10 },
            { x: 16.5, y: arc8R_x16_5_y },
            ...this._arcR(8, arc8R_x16_5_y, arc8R_x13_y, 10), // 8m arc: (16.5, 6.24) → (13, 7.86)
        ];

        // z10: Far right back (display right, mirror of z6)
        zones[10] = [
            { x: 20, y: 3 },
            ...this._arcR(8, 3, arc8R_x16_5_y, 12),  // 8m arc: (18.92, 3) → (16.5, 6.24)
            { x: 16.5, y: 10 },
            { x: 20, y: 10 },
        ];

        // z11: Deep right (x=13 to 20, y=10 to 20)
        zones[11] = [
            { x: 13, y: 10 }, { x: 13, y: 20 }, { x: 20, y: 20 }, { x: 20, y: 10 }
        ];

        // z12: Deep center (x=7 to 13, y=10 to 20)
        zones[12] = [
            { x: 7, y: 10 }, { x: 7, y: 20 }, { x: 13, y: 20 }, { x: 13, y: 10 }
        ];

        // z13: Deep left (x=0 to 7, y=10 to 20)
        zones[13] = [
            { x: 0, y: 10 }, { x: 0, y: 20 }, { x: 7, y: 20 }, { x: 7, y: 10 }
        ];

        return zones;
    }

    /**
     * Draw the 14 zone regions (z0-z13) with proper curved D-line boundaries.
     * Zone fills use subtle alternating colors for visual distinction.
     */
    drawZoneRegions() {
        const zoneFills = [
            'rgba(255, 235, 205, 0.50)',  // z0  goal (warm)
            'rgba(180, 210, 255, 0.25)',  // z1  right wing corner
            'rgba(255, 215, 185, 0.25)',  // z2  right-center 6-8m
            'rgba(210, 240, 210, 0.25)',  // z3  center 6-8m
            'rgba(255, 215, 185, 0.25)',  // z4  left-center 6-8m
            'rgba(180, 210, 255, 0.25)',  // z5  left wing corner
            'rgba(210, 195, 240, 0.22)',  // z6  far left back
            'rgba(240, 225, 200, 0.22)',  // z7  left-center back
            'rgba(200, 230, 200, 0.22)',  // z8  center back
            'rgba(240, 225, 200, 0.22)',  // z9  right-center back
            'rgba(210, 195, 240, 0.22)',  // z10 far right back
            'rgba(220, 220, 240, 0.18)',  // z11 deep right
            'rgba(240, 240, 220, 0.18)',  // z12 deep center
            'rgba(220, 220, 240, 0.18)',  // z13 deep left
        ];
        const zoneBorders = [
            'rgba(200, 170, 130, 0.35)',  // z0
            'rgba(130, 170, 220, 0.30)',  // z1
            'rgba(200, 160, 130, 0.30)',  // z2
            'rgba(150, 200, 150, 0.30)',  // z3
            'rgba(200, 160, 130, 0.30)',  // z4
            'rgba(130, 170, 220, 0.30)',  // z5
            'rgba(160, 140, 200, 0.25)',  // z6
            'rgba(200, 180, 150, 0.25)',  // z7
            'rgba(150, 190, 150, 0.25)',  // z8
            'rgba(200, 180, 150, 0.25)',  // z9
            'rgba(160, 140, 200, 0.25)',  // z10
            'rgba(170, 170, 200, 0.20)',  // z11
            'rgba(200, 200, 170, 0.20)',  // z12
            'rgba(170, 170, 200, 0.20)',  // z13
        ];

        const zonePolys = this._buildZonePolygons();
        zonePolys.forEach((poly, i) => {
            this._fillMeterPoly(poly, zoneFills[i], zoneBorders[i]);
        });
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
     * Draw zone labels (z0-z13) offset above zone centers
     * so player icons don't obscure them, with background pills for readability.
     */
    drawZoneLabels() {
        // Scale font size proportionally to court size
        const fontSize = Math.max(9, Math.round(this.courtWidth / 38));
        this.ctx.font = `bold ${fontSize}px monospace`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';

        // 14-Zone System (z0-z13)
        const zones = [
            'z0', 'z1', 'z2', 'z3', 'z4', 'z5',
            'z6', 'z7', 'z8', 'z9', 'z10',
            'z11', 'z12', 'z13'
        ];

        // Offset labels above zone center so player icons don't cover them
        const labelOffsetY = Math.max(14, Math.round(fontSize * 1.5));
        const pillPadX = 3;
        const pillPadY = 2;

        zones.forEach(id => {
            const coords = this.getZoneCoordinates(id);
            if (coords) {
                const labelX = coords.x;
                const labelY = coords.y - labelOffsetY;

                // Draw semi-transparent background pill for readability
                const textWidth = this.ctx.measureText(id).width;
                this.ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
                this.ctx.fillRect(
                    labelX - textWidth / 2 - pillPadX,
                    labelY - fontSize / 2 - pillPadY,
                    textWidth + pillPadX * 2,
                    fontSize + pillPadY * 2
                );

                // Draw label text
                this.ctx.fillStyle = this.colors.zoneLabel;
                this.ctx.globalAlpha = 0.85;
                this.ctx.fillText(id, labelX, labelY);
                this.ctx.globalAlpha = 1.0;
            }
        });
    }

    /**
     * Get zone coordinates (centroids) for player placement.
     * Uses meter-based zone centroids matching the 13-zone system:
     *
     *   Display layout (goal at bottom):
     *         [ z13 ]  [ z12 ]  [ z11 ]     Deep (y>10m)
     *     [z6] [z7]  [z8]  [z9] [z10]       Back (8m-10m)
     *     [z5]  [z4]  [z3]  [z2]  [z1]      Close (6m-8m)
     *              \___ z0 (Goal) ___/
     *
     *   z1 at display RIGHT (large x) = attacker's left wing
     *   z5 at display LEFT  (small x) = attacker's right wing
     */
    getZoneCoordinates(zone) {
        if (!zone) return null;
        const baseZone = zone.split('_')[0];

        // Zone centroids in meters (origin: bottom-left, y up, goal at y=0)
        const centroids = {
            'z0':  { x: 10,   y: 3 },     // Goal area
            'z1':  { x: 18.5, y: 1.5 },   // Right wing corner (display right)
            'z2':  { x: 15.5, y: 5.5 },   // Right-center 6-8m
            'z3':  { x: 10,   y: 7 },     // Center 6-8m
            'z4':  { x: 4.5,  y: 5.5 },   // Left-center 6-8m
            'z5':  { x: 1.5,  y: 1.5 },   // Left wing corner (display left)
            'z6':  { x: 1.5,  y: 6.5 },   // Far left back (display left)
            'z7':  { x: 5,    y: 9 },     // Left-center back
            'z8':  { x: 10,   y: 9 },     // Center back
            'z9':  { x: 15,   y: 9 },     // Right-center back
            'z10': { x: 18.5, y: 6.5 },   // Far right back (display right)
            'z11': { x: 16.5, y: 15 },    // Deep right (display right)
            'z12': { x: 10,   y: 15 },    // Deep center
            'z13': { x: 3.5,  y: 15 },    // Deep left (display left)
        };

        const c = centroids[zone] || centroids[baseZone];
        if (!c) return null;
        return this._m2px(c.x, c.y);
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
        this._lastFrameData = frameData;
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
