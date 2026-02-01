import json
import sys
import argparse
from pathlib import Path

def convert(input_path, output_path, s3_prefix=None):
    with open(input_path) as f:
        raw_data = json.load(f)
    
    metadata = {}
    frames = []
    
    # Process raw items
    raw_frames = []
    for item in raw_data:
        if "video" in item:
            metadata["video"] = item["video"]
        elif "frame" in item:
            raw_frames.append(item["frame"])
            
    # Estimate total frames/duration if not present
    metadata["total_frames"] = len(raw_frames)
    metadata["duration_seconds"] = len(raw_frames) * 1.0 # Default 1fps if not specified

    video_path = metadata.get("video", "")
    
    # Handle S3 Prefix injection
    if s3_prefix and video_path and not video_path.startswith("s3://"):
        s3_prefix = s3_prefix.rstrip("/")
        video_name = Path(video_path).name
        video_path = f"{s3_prefix}/{video_name}"
        metadata["video"] = video_path

    # Synthesize Physics Data
    processed_frames = []
    for i, raw_frame in enumerate(raw_frames):
        # Base frame info
        new_frame = {
            "time": raw_frame.get("time"),
            "timestamp": i * 1.0, # approximate
            "game_state": raw_frame.get("game_state", "Attacking"),
            "original_event": raw_frame.get("event") # Keep original event for ref
        }
        
        # 1. Synthesize Players
        players = []
        
        # Jersey Map (Role -> Number)
        jersey_map = {
            "LW": "11", "LB": "3", "CB": "9", "RB": "10", "RW": "14", "PV": "7",
            "GK": "1"
        }
        
        # Attacker (Possession)
        poss = raw_frame.get("possession", {})
        attacker_role = poss.get("player_role")
        attacker_zone = poss.get("zone")
        attacker_action = poss.get("action")
        
        if attacker_role:
            players.append({
                "track_id": attacker_role,
                "role": attacker_role,
                "team": "blue", # Map ARG/Attacker to blue
                "zone": f"z{attacker_zone}" if attacker_zone is not None else "z0",
                "jersey_number": jersey_map.get(attacker_role, "99")
            })
            
        # Defenders
        def_formation = raw_frame.get("defensive_formation", {})
        defenders = def_formation.get("defenders", {})
        for d_role, d_zone in defenders.items():
            players.append({
                "track_id": d_role,
                "role": d_role,
                "team": "white", # Map Defenders to white
                "zone": f"z{d_zone}" if d_zone is not None else "z6",
                "jersey_number": d_role.replace("D", "")
            })
            
        new_frame["players"] = players
        
        # 2. Synthesize Ball
        # If action is Pass/Shot, state is In-Air. Else Holding/Dribbling.
        ball_state = "Holding"
        if attacker_action in ["Pass", "Shot"]:
            ball_state = "In-Air"
        elif attacker_action == "Dribble":
            ball_state = "Dribbling"
        
        # Determine Ball Zone
        # If Shot, ball goes to z0 (Goal)
        ball_zone = f"z{attacker_zone}" if attacker_zone is not None else "z0"
        if attacker_action == "Shot":
            ball_zone = "z0" # Force ball to goal zone for Shot detection
            
        new_frame["ball"] = {
            "zone": ball_zone,
            "state": ball_state,
            "holder_track_id": attacker_role if ball_state == "Holding" else None 
        }
        
        # For event detector compatibility:
        # Pass detection needs: prev_holder != curr_holder AND prev_ball.state == "In-Air"
        # If I strictly follow logic:
        # Frame N: Player A passes. Action="Pass", State="In-Air".
        # Frame N+1: Player B receives. Action="Hold"?
        # If detector checks PREV state == In-Air, then Frame N is perfect.
        # But we need to ensure holder_track_id logic works.
        # If state is "In-Air", usually holder is None.
        # But detector checks: prev_holder = prev.ball.holder_track_id
        # If In-Air, holder is None. So prev_holder is None.
        # Then curr_holder (Frame N+1) is Player B. None != Player B. True.
        # AND prev.state ("In-Air") == "In-Air". True.
        # So "Pass" detected!
        
        # BUT wait: `physics_to_events.py` line 34: `prev_holder = prev_ball.get("holder_track_id")`
        # If I set holder_track_id to None when In-Air, then prev_holder is None.
        # Does that make sense? A pass comes FROM someone.
        # If `prev_holder` is None, we don't know who passed it!
        # The detector says: `events.append(..., from_track_id=prev_holder, ...)`
        # If prev_holder is None, then `from_track_id` is None.
        # We want `from_track_id` to be the Passer.
        # So when state is "In-Air" (Passing), the ball should probably still be associated with the Passer 
        # OR the logic in `physics_to_events` expects the state *before* the pass to have the holder?
        
        # `physics_to_events` loop:
        # prev = frame[i-1], curr = frame[i]
        # if prev.holder != curr.holder AND prev.state == "In-Air"
        
        # Case A:
        # Frame 0: Holder=A, State=Holding.
        # Frame 1: Holder=A, State=In-Air (Just released).
        # Frame 2: Holder=B, State=Holding (Received).
        
        # At i=1 (Prev=0, Curr=1): 
        # Prev.Holder(A) == Curr.Holder(A). No event.
        # At i=2 (Prev=1, Curr=2):
        # Prev.Holder(A) != Curr.Holder(B). 
        # Prev.State(In-Air) == In-Air. 
        # Event detected! PASS A->B.
        
        # So: In the frame where Action="Pass", I should KEEP the holder ID but set state to In-Air?
        # OR set holder to None?
        # If I set holder to A in Frame 1 (In-Air), then Prev(1).Holder=A.
        # Curr(2).Holder=B. A != B. Detected.
        # This seems correct.
        
        # So I will set holder_track_id to attacker_role even if In-Air,
        # implies "Last Holder" or "Current Propeller".
        
        new_frame["ball"]["holder_track_id"] = attacker_role
        
        processed_frames.append(new_frame)

    output_data = {
        "metadata": metadata,
        "video": video_path, 
        "frames": processed_frames
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    print(f"Converted {len(processed_frames)} frames to {output_path}")
    print(f"Video Path: {video_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Gemini Raw JSON to Physics Schema")
    parser.add_argument("input", help="Input JSON file")
    parser.add_argument("output", help="Output JSON file")
    parser.add_argument("--s3-prefix", help="S3 Prefix to prepend to video filename (e.g. s3://my-bucket/videos)")
    
    args = parser.parse_args()
    
    convert(args.input, args.output, args.s3_prefix)
