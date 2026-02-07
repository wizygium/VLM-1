import json
import math
import sys
from pathlib import Path
from typing import List, Dict, Any

# --- Configuration ---
MAX_SPEED_MPS = 12.0  # Meters per second (World Record Sprint is ~10-11 m/s, accounting for burst)
MAX_PASS_SPEED_MPS = 25.0 # Ball speed can be higher

# Zone Centroids (Meters) - 10-zone system (z0-z9)
# Origin (0,0) is bottom-left corner. Goal is centered at x=10, y=0.
# Court is 20m wide x 20m deep.
ZONE_COORDS = {
    "z0":  (10, 3),   # Goal Area (inside 6m arc)
    "z1":  (4, 7.5),  # Band 1, Left (6m-9m, x<7.5)
    "z2":  (10, 7.5), # Band 1, Center (6m-9m, 7.5≤x≤12.5)
    "z3":  (16, 7.5), # Band 1, Right (6m-9m, x>12.5)
    "z4":  (4, 10.5), # Band 2, Left (9m-12m, x<7.5)
    "z5":  (10, 10.5),# Band 2, Center (9m-12m, 7.5≤x≤12.5)
    "z6":  (16, 10.5),# Band 2, Right (9m-12m, x>12.5)
    "z7":  (4, 16),   # Band 3, Left (12m-20m, x<7.5)
    "z8":  (10, 16),  # Band 3, Center (12m-20m, 7.5≤x≤12.5)
    "z9":  (16, 16),  # Band 3, Right (12m-20m, x>12.5)
}

VALID_ROLES = {
    "LW", "LB", "CB", "RB", "RW", "PV", "PV2", "GK", "GOAL",
    "DL1", "DL2", "DL3", "DR3", "DR2", "DR1", "ADV", # New Defensive Roles
    "D1", "D2", "D3", "D4", "D5", "D6" # Legacy support (optional, can remove)
}

def parse_time(time_str: str) -> float:
    """Parses '1.50 seconds' or '00:01.700' to float seconds."""
    try:
        if "seconds" in time_str:
            return float(time_str.replace(" seconds", "").strip())
        if ":" in time_str:
            parts = time_str.split(":")
            minutes = float(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        return float(time_str)
    except:
        return 0.0

def get_dist(z1_id: str, z2_id: str) -> float:
    if z1_id not in ZONE_COORDS or z2_id not in ZONE_COORDS:
        return 0.0
    x1, y1 = ZONE_COORDS[z1_id]
    x2, y2 = ZONE_COORDS[z2_id]
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def validate_json(file_path: Path):
    print(f"\n🔍 Validating: {file_path.name}")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Handle 'analysis' wrapper
        if isinstance(data, dict) and 'analysis' in data:
            data = data['analysis']
            
    except Exception as e:
        print(f"  ❌ JSON Load Error: {e}")
        return

    frames = [item['frame'] for item in data if 'frame' in item]
    if not frames:
        print("  ⚠️ No frames found found in JSON.")
        return

    errors = []
    warnings = []
    
    # State tracking
    prev_time = -1.0
    prev_role_zone: Dict[str, int] = {} # Map role -> last known zone
    ball_holder = None

    for i, frame in enumerate(frames):
        t = parse_time(frame.get('time', "0.0"))
        event = frame.get('event', {})
        possession = frame.get('possession', {})
        
        # 1. Check Monotonic Time
        if t <= prev_time and i > 0:
            errors.append(f"Timestamp regression or duplicate at {t}s (Frame {i})")
        
        dt = t - prev_time if prev_time >= 0 else 0.5 # Default first step
        if dt == 0: dt = 0.01 # Avoid div/0
        
        # 2. Check Roles
        actors = []
        if 'from_role' in event: actors.append(event['from_role'])
        if 'to_role' in event: actors.append(event['to_role'])
        if 'player_role' in possession: actors.append(possession['player_role'])
        
        for actor in set(actors):
            if actor and actor not in VALID_ROLES and "Left" not in actor: # Allow descriptive fallback if strictly needed
                errors.append(f"Invalid Role '{actor}' at {t}s")

        # 3. Velocity Check (Teleportation)
        # Verify valid movement for 'from_role' if they acted previously
        active_role = event.get('from_role') or possession.get('player_role')
        current_zone = event.get('from_zone') or possession.get('zone')
        
        if active_role and current_zone and active_role in prev_role_zone:
            last_zone = prev_role_zone[active_role]
            dist = get_dist(last_zone, current_zone)
            speed = dist / dt
            
            if speed > MAX_SPEED_MPS:
                warnings.append(f"Implausible Speed for {active_role}: {speed:.1f} m/s (Zone {last_zone}->{current_zone} in {dt:.2f}s) at {t}s")

        # Update State
        if active_role and current_zone:
            prev_role_zone[active_role] = current_zone
        
        # 4. Continuity Check
        # If PASS, receiver should have ball next
        if event.get('type') == 'PASS':
            receiver = event.get('to_role')
            # Look ahead logic is hard in single pass, but we can update 'ball_holder'
            ball_holder = receiver

        prev_time = t

    # Report
    if not errors and not warnings:
        print("  ✅ Validation Passed")
    else:
        for e in errors:
            print(f"  ❌ {e}")
        for w in warnings:
            print(f"  ⚠️ {w}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to JSON file or directory")
    args = parser.parse_args()
    
    path = Path(args.path)
    if path.is_file():
        validate_json(path)
    elif path.is_dir():
        for p in path.glob("*_analysis.json"):
            validate_json(p)
