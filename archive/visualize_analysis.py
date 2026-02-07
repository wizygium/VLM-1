
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import numpy as np
import click
from pathlib import Path
import cv2  # Requires opencv-python

# --- Configuration & Geometry ---
COURT_WIDTH = 20  # meters (width)
COURT_DEPTH = 15  # meters (attacking half depth)
GOAL_WIDTH_M = 3.0

# Approximate Centroids for Zones (Origin: Center of Goal Line)
# NOTE: Attacker POV (looking down at goal). Left is Positive X, Right is Negative X.
# Approximate Centroids for Zones (Origin: Center of Goal Line)
# NOTE: Attacker POV (looking down at goal). Left is Positive X, Right is Negative X.
ZONE_COORDS = {
    "z0":  (0.0, 0.5),    # Goal (Goalie)
    "z1":  (8.0, 7.0),    # Zone 1 (Far Left Wing)
    "z2":  (5.0, 7.5),    # Zone 2 (Left Center)
    "z3":  (0.0, 7.0),    # Zone 3 (Center Pivot)
    "z4":  (-5.0, 7.5),   # Zone 4 (Right Center)
    "z5":  (-8.0, 7.0),   # Zone 5 (Far Right Wing)
    "z6":  (8.0, 11.0),   # Zone 6 (Deep Left Back)
    "z7":  (5.0, 12.0),   # Zone 7 (Left Back)
    "z8":  (0.0, 12.0),   # Zone 8 (Center Back)
    "z9":  (-5.0, 12.0),  # Zone 9 (Right Back)
    "z10": (-8.0, 11.0),  # Zone 10 (Deep Right Back)
    "z11": (5.0, 16.0),   # Zone 11 (Deep Left)
    "z12": (0.0, 16.0),   # Zone 12 (Deep Center)
    "z13": (-5.0, 16.0),  # Zone 13 (Deep Right)
}

def draw_court(ax):
    """Draws key handball court lines with correct geometry (quarter arcs + lines)."""
    # Court styling
    ax.set_xlim(-11, 11)
    ax.set_ylim(-1, 20)
    ax.set_aspect('equal')
    ax.axis('off') 
    
    # Background
    court_bg = patches.Rectangle((-11, -1), 22, 21, linewidth=0, facecolor='#e6ceaa', zorder=0)
    ax.add_patch(court_bg)

    # Goal Dimensions
    post_offset = 1.5

    # --- 6m Line ---
    arc6_right = patches.Arc((post_offset, 0), 12, 12, theta1=0, theta2=90, edgecolor='white', linewidth=2, zorder=1)
    ax.add_patch(arc6_right)
    arc6_left = patches.Arc((-post_offset, 0), 12, 12, theta1=90, theta2=180, edgecolor='white', linewidth=2, zorder=1)
    ax.add_patch(arc6_left)
    ax.plot([-post_offset, post_offset], [6, 6], color='white', linewidth=2, zorder=1)

    # --- 9m Line (Dashed) ---
    arc9_right = patches.Arc((post_offset, 0), 18, 18, theta1=0, theta2=90, edgecolor='white', linewidth=2, linestyle='--', zorder=1)
    ax.add_patch(arc9_right)
    arc9_left = patches.Arc((-post_offset, 0), 18, 18, theta1=90, theta2=180, edgecolor='white', linewidth=2, linestyle='--', zorder=1)
    ax.add_patch(arc9_left)
    ax.plot([-post_offset, post_offset], [9, 9], color='white', linewidth=2, linestyle='--', zorder=1)
    
    # Goal
    goal = patches.Rectangle((-1.5, -0.5), 3, 1, linewidth=2, edgecolor='black', facecolor='white', hatch='///', zorder=1)
    ax.add_patch(goal)

    # --- Zone Overlay ---
    for z_id, (zx, zy) in ZONE_COORDS.items():
        if z_id == "z0": continue
        ax.text(zx, zy, z_id, ha='center', va='center', fontsize=16, color='black', alpha=0.15, fontweight='bold', zorder=0.5)

@click.command()
@click.argument("input_json", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output MP4 filename (default: auto-generated)")
@click.option("--video-dir", "-v", default="videos/", help="Directory containing source videos")
def visualize(input_json, output, video_dir):
    """Visualize JSON analysis output side-by-side with original video."""
    
    input_path = Path(input_json)
    if output is None:
        output = input_path.stem + "_viz_comparison.mp4"

    print(f"Loading analysis from: {input_path}")
    with open(input_path, 'r') as f:
        data = json.load(f)

    # Parse JSON structure
    frames = []
    video_filename = None
    
    if isinstance(data, dict):
        video_filename = data.get("video_file")
        if "analysis" in data:
            frames = data["analysis"]
        elif "frames" in data:
            frames = data["frames"]
    elif isinstance(data, list):
        # Infer video filename from first item if possible or external knowledge
        frames = data

    frames = [f for f in frames if "frame" in f]
    
    if not frames:
        print("❌ No frames found to animate.")
        return

    # Load Video
    cap = None
    if video_filename:
        vid_path = Path(video_dir) / video_filename
        if not vid_path.exists():
            # Try current dir
            vid_path = Path(video_filename)
        
        if vid_path.exists():
            print(f"🎬 Found source video: {vid_path}")
            cap = cv2.VideoCapture(str(vid_path))
        else:
            print(f"⚠️ Warning: Source video '{video_filename}' not found in '{video_dir}'. Comparison will be blank.")

    # Create figure with 2 subplots
    fig, (ax_video, ax_schematic) = plt.subplots(1, 2, figsize=(20, 10))
    plt.subplots_adjust(wspace=0.1, left=0.02, right=0.98, bottom=0.02, top=0.95)

    def init():
        ax_video.axis('off')
        ax_schematic.clear()
        draw_court(ax_schematic)
        return []

    def update(frame_idx):
        # --- Right Panel: Schematic ---
        ax_schematic.clear() 
        draw_court(ax_schematic)
        
        frame_data = frames[frame_idx]["frame"]
        time_str = frame_data.get("time", "0.00")
        event = frame_data.get("event", {})
        possession = frame_data.get("possession", {})
        game_state = frame_data.get("game_state", "Unknown")
        
        # Parse Time
        try:
            if "seconds" in time_str:
                time_val = float(time_str.replace("seconds", "").strip())
            elif ":" in time_str:
                parts = time_str.split(":")
                time_val = float(parts[0]) * 60 + float(parts[1])
            else:
                time_val = float(time_str)
        except:
            time_val = 0.0

        # --- Left Panel: Video Frame ---
        ax_video.clear()
        ax_video.axis('off')
        ax_video.set_title(f"Original Video @ {time_val:.2f}s", fontsize=14, color='white', backgroundcolor='black')
        
        if cap and cap.isOpened():
            # Seek to timestamp
            ms = time_val * 1000
            cap.set(cv2.CAP_PROP_POS_MSEC, ms)
            ret, viz_frame = cap.read()
            if ret:
                viz_frame = cv2.cvtColor(viz_frame, cv2.COLOR_BGR2RGB)
                ax_video.imshow(viz_frame)
            else:
                ax_video.text(0.5, 0.5, "Frame Seek Failed", ha='center', va='center', color='red')
        else:
             ax_video.text(0.5, 0.5, "Video Not Available", ha='center', va='center')


        # --- Schematic Logic ---
        # 1. Draw Defenders (Red Circles)
        df = frame_data.get("defensive_formation", {}).get("defenders", {})
        for role, zone in df.items():
            if zone is not None:
                # zone is now "z10", "z5" etc.
                if zone not in ZONE_COORDS: continue
                x, y = ZONE_COORDS.get(zone, (0,0))

                offset_x = (hash(role) % 10 - 5) / 15.0 
                ax_schematic.plot(x + offset_x, y, 'o', color='#e74c3c', markersize=20, mec='white', mew=2, zorder=5)
                ax_schematic.text(x + offset_x, y, role, color='white', ha='center', va='center', fontsize=9, fontweight='bold', zorder=6)

        # 2. Draw Attackers (Blue Triangles)
        at = frame_data.get("attackers", {})
        for role, zone in at.items():
            if zone is not None and zone in ZONE_COORDS:
                x, y = ZONE_COORDS.get(zone, (0,0))
                offset_x = (hash(role) % 10 - 5) / 15.0 
                ax_schematic.plot(x + offset_x, y, '^', color='#3498db', markersize=20, mec='white', mew=2, zorder=5)
                ax_schematic.text(x + offset_x, y, role, color='white', ha='center', va='center', fontsize=8, fontweight='bold', zorder=6)

        # 3. Draw Ball & Events
        event_type = event.get("type", "NONE")
        ball_x, ball_y = 0,0
        
        if event_type == "PASS" and "from_zone" in event and "to_zone" in event:
            fz = event["from_zone"]
            tz = event["to_zone"]
            if fz in ZONE_COORDS and tz in ZONE_COORDS:
                x1, y1 = ZONE_COORDS.get(fz, (0,0))
                x2, y2 = ZONE_COORDS.get(tz, (0,0))
                ax_schematic.annotate("", xy=(x2, y2), xytext=(x1, y1),
                            arrowprops=dict(arrowstyle="->", color='#f39c12', lw=4, ls='-'), zorder=4)
                ball_x, ball_y = (x1+x2)/2, (y1+y2)/2
            
        elif event_type == "MOVEMENT":
             pass 
             
        elif "zone" in possession:
             z = possession["zone"]
             if z in ZONE_COORDS:
                ball_x, ball_y = ZONE_COORDS.get(z, (0,0))
                ball_x += 0.5
                ball_y -= 0.5

        if ball_x != 0 or ball_y != 0:
             ax_schematic.plot(ball_x, ball_y, 'o', color='#f1c40f', markeredgecolor='black', markersize=12, zorder=7)


        # 4. Info Box Overlay
        info_text = f"Time: {time_str}\n{event_type}\n{event.get('description', '')}"
        ax_schematic.text(0, 19, info_text, ha='center', va='top', fontsize=12, 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', alpha=0.9, edgecolor='#7f8c8d'), zorder=10)

        return []

    # Animation
    print(f"Generating side-by-side animation ({len(frames)} frames)...")
    ani = animation.FuncAnimation(fig, update, frames=len(frames), init_func=init, blit=False, interval=1500)
    
    try:
        ani.save(output, writer='ffmpeg', fps=1) 
        print(f"✅ Saved visualization to {output}")
    except Exception as e:
        print(f"❌ Error saving video: {e}")

    if cap:
        cap.release()

if __name__ == '__main__':
    visualize()
