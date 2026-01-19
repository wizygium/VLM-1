
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import numpy as np
import click
from pathlib import Path

# --- Configuration & Geometry ---
COURT_WIDTH = 20  # meters (width)
COURT_DEPTH = 15  # meters (attacking half depth)
GOAL_WIDTH_M = 3.0

# Approximate Centroids for Zones (Origin: Center of Goal Line)
# NOTE: Attacker POV (looking down at goal). Left is Positive X, Right is Negative X.
ZONE_COORDS = {
    0:  (0.0, 0.5),    # Goal (Goalie)
    
    # 6m-8m Zones (Left to Right from attacker POV)
    1:  (8.0, 7.0),    # Zone 1 (Far Left Wing) -> Positive X
    2:  (5.0, 7.5),    # Zone 2 (Left Center)
    3:  (0.0, 7.0),    # Zone 3 (Center Pivot)
    4:  (-5.0, 7.5),   # Zone 4 (Right Center)
    5:  (-8.0, 7.0),   # Zone 5 (Far Right Wing) -> Negative X
    
    # 8m-10m Zones (Back Court)
    6:  (8.0, 11.0),   # Zone 6 (Deep Left Back)
    7:  (5.0, 12.0),   # Zone 7 (Left Back)
    8:  (0.0, 12.0),   # Zone 8 (Center Back)
    9:  (-5.0, 12.0),  # Zone 9 (Right Back)
    10: (-8.0, 11.0),  # Zone 10 (Deep Right Back)
    
    # Deep Court
    11: (5.0, 16.0),   # Zone 11 (Deep Left)
    12: (0.0, 16.0),   # Zone 12 (Deep Center)
    13: (-5.0, 16.0),  # Zone 13 (Deep Right)
}

ROLE_COLORS = {
    "Attackers": "blue",
    "Defenders": "red",
    "Ball": "yellow"
}

def draw_court(ax):
    """Draws key handball court lines with correct geometry (quarter arcs + lines)."""
    # Court styling
    ax.set_xlim(-11, 11) # Slightly wider to see wings
    ax.set_ylim(-1, 20)
    ax.set_aspect('equal')
    ax.axis('off') 
    
    # Background
    court_bg = patches.Rectangle((-11, -1), 22, 21, linewidth=0, facecolor='#e6ceaa', zorder=0)
    ax.add_patch(court_bg)

    # Goal Dimensions
    post_offset = 1.5  # 3m wide goal -> posts at +/- 1.5m

    # --- 6m Line ---
    # Left Arc (Center: -1.5, 0, Radius: 6, Angle: 90-180) -- Actually on Plot Left (Neg X)
    # Wait, "Left" for attacker (Pos X) is Plot Right. Confusing terms. Use Plot coords.
    # Plot Right Arc (Pos X): Center (+1.5, 0)
    arc6_right = patches.Arc((post_offset, 0), 12, 12, theta1=0, theta2=90, edgecolor='white', linewidth=2, zorder=1)
    ax.add_patch(arc6_right)
    
    # Plot Left Arc (Neg X): Center (-1.5, 0)
    arc6_left = patches.Arc((-post_offset, 0), 12, 12, theta1=90, theta2=180, edgecolor='white', linewidth=2, zorder=1)
    ax.add_patch(arc6_left)
    
    # Straight Line
    ax.plot([-post_offset, post_offset], [6, 6], color='white', linewidth=2, zorder=1)

    # --- 9m Line (Dashed) ---
    arc9_right = patches.Arc((post_offset, 0), 18, 18, theta1=0, theta2=90, edgecolor='white', linewidth=2, linestyle='--', zorder=1)
    ax.add_patch(arc9_right)
    
    arc9_left = patches.Arc((-post_offset, 0), 18, 18, theta1=90, theta2=180, edgecolor='white', linewidth=2, linestyle='--', zorder=1)
    ax.add_patch(arc9_left)
    
    # Straight Line
    ax.plot([-post_offset, post_offset], [9, 9], color='white', linewidth=2, linestyle='--', zorder=1)
    
    # Goal
    goal = patches.Rectangle((-1.5, -0.5), 3, 1, linewidth=2, edgecolor='black', facecolor='white', hatch='///', zorder=1)
    ax.add_patch(goal)

    # --- Zone Overlay (Faint Sketch) ---
    for z_id, (zx, zy) in ZONE_COORDS.items():
        if z_id == 0: continue
        ax.text(zx, zy, str(z_id), ha='center', va='center', fontsize=20, color='black', alpha=0.08, fontweight='bold', zorder=0.5)
        # Optional: Draw small circle at centroid
        # ax.plot(zx, zy, '+', color='black', alpha=0.05)

    # Sector Separators (Faint)
    # Central channel (+/- 1.5m)
    ax.plot([-1.5, -1.5], [6, 18], color='black', alpha=0.05, linestyle=':', zorder=0.5)
    ax.plot([1.5, 1.5], [6, 18], color='black', alpha=0.05, linestyle=':', zorder=0.5)


@click.command()
@click.argument("input_json", type=click.Path(exists=True))
@click.option("--output", "-o", default="analysis_viz.mp4", help="Output MP4 filename")
def visualize(input_json, output):
    """Visualize JSON analysis output."""
    
    with open(input_json, 'r') as f:
        data = json.load(f)

    # Find the main array
    frames = []
    if isinstance(data, list):
        frames = data
    elif "analysis" in data:
        frames = data["analysis"]
    else:
        for k, v in data.items():
            if isinstance(v, list): 
                frames = v
                break
    
    frames = [f for f in frames if "frame" in f]
    
    if not frames:
        print("No frames found to animate.")
        return

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 12))
    
    def init():
        ax.clear()
        draw_court(ax)
        return []

    def update(frame_idx):
        ax.clear() 
        draw_court(ax)
        
        frame_data = frames[frame_idx]["frame"]
        time_str = frame_data.get("time", "0.00")
        event = frame_data.get("event", {})
        possession = frame_data.get("possession", {})
        game_state = frame_data.get("game_state", "Unknown")
        
        # 1. Draw Defenders (Red Circles)
        df = frame_data.get("defensive_formation", {}).get("defenders", {})
        for role, zone in df.items():
            if zone is not None:
                x, y = ZONE_COORDS.get(zone, (0,0))
                # Add jitter based on role to prevent overlap
                offset_x = (hash(role) % 10 - 5) / 15.0 
                ax.plot(x + offset_x, y, 'o', color='#e74c3c', markersize=18, mec='white', mew=1.5, zorder=5)
                ax.text(x + offset_x, y, role, color='white', ha='center', va='center', fontsize=8, fontweight='bold', zorder=6)

        # 2. Draw Attackers (Blue Triangles)
        at = frame_data.get("attackers", {})
        for role, zone in at.items():
            if zone is not None:
                x, y = ZONE_COORDS.get(zone, (0,0))
                # Add jitter
                offset_x = (hash(role) % 10 - 5) / 15.0 
                ax.plot(x + offset_x, y, '^', color='#3498db', markersize=18, mec='white', mew=1.5, zorder=5)
                ax.text(x + offset_x, y, role, color='white', ha='center', va='center', fontsize=7, fontweight='bold', zorder=6)

        # 3. Draw Ball & Events
        event_type = event.get("type", "NONE")
        desc = event.get("description", "")
        
        ball_x, ball_y = 0,0
        
        if event_type == "PASS":
            fz = event.get("from_zone")
            tz = event.get("to_zone")
            x1, y1 = ZONE_COORDS.get(fz, (0,0))
            x2, y2 = ZONE_COORDS.get(tz, (0,0))
            
            # PASS Arrow (Dashed, Orange)
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="->", color='#f39c12', lw=3, ls='-'), zorder=4)
            ball_x, ball_y = (x1+x2)/2, (y1+y2)/2
            
        elif event_type == "MOVEMENT":
            oz = event.get("origin_zone")
            dz = event.get("destination_zone")
            with_ball = event.get("with_ball", True) # Default to true if missing
            
            x1, y1 = ZONE_COORDS.get(oz, (0,0))
            x2, y2 = ZONE_COORDS.get(dz, (0,0))
            
            if with_ball:
                # Solid Line
                ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                            arrowprops=dict(arrowstyle="->", color='#2980b9', lw=3, ls='-'), zorder=4)
                ball_x, ball_y = x2, y2
            else:
                # Dotted Line (Off-ball cut)
                ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                            arrowprops=dict(arrowstyle="->", color='#95a5a6', lw=2, ls=':'), zorder=3)
                # Ball does NOT move with player


        elif event_type == "SHOT":
             fz = event.get("from_zone")
             x1, y1 = ZONE_COORDS.get(fz, (0,0))
             x2, y2 = ZONE_COORDS.get(0, (0,0)) # Goal
             
             # SHOT Arrow (Red, Thick)
             ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="->", color='#c0392b', lw=3), zorder=4)
             ball_x, ball_y = (x1+3*x2)/4, (y1+3*y2)/4 # Near goal
             
        elif "zone" in possession:
             z = possession["zone"]
             ball_x, ball_y = ZONE_COORDS.get(z, (0,0))
             # Offset slightly to "hold" ball
             ball_x += 0.5
             ball_y -= 0.5

        if ball_x != 0 or ball_y != 0:
             ax.plot(ball_x, ball_y, 'o', color='#f1c40f', markeredgecolor='black', markersize=10, zorder=7)

        # 4. Info Box
        info_text = f"Time: {time_str}\nState: {game_state}\nEvent: {event_type}\n{desc}"
        # Title box
        ax.text(0, 19, info_text, ha='center', va='top', fontsize=11, 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', alpha=0.95, edgecolor='#7f8c8d'), zorder=10)
        
        # Legend (Manual)
        ax.text(-9, -0.5, "▲ Attackers (Blue)", fontsize=8, color='#2980b9', fontweight='bold')
        ax.text(5, -0.5, "● Defenders (Red)", fontsize=8, color='#c0392b', fontweight='bold')

        return []

    # Animation
    # Set interval to 2000ms (2 seconds) per keyframe to give time to read
    print(f"Generating animation ({len(frames)} frames)...")
    ani = animation.FuncAnimation(fig, update, frames=len(frames), init_func=init, blit=False, interval=2000)
    
    try:
        ani.save(output, writer='ffmpeg', fps=0.5) # 0.5 fps = 2 seconds per frame
        print(f"✅ Saved visualization to {output}")
    except Exception as e:
        print(f"❌ Error saving video: {e}")
        print("Try installing ffmpeg: `brew install ffmpeg`")

if __name__ == '__main__':
    visualize()
