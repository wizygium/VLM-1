
import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    print(f"Checking health of {BASE_URL}...")
    try:
        resp = requests.get(BASE_URL)
        if resp.status_code == 200:
            print("✅ Server is UP")
        else:
            print(f"❌ Server returned {resp.status_code}")
            return
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # Trigger analysis (using a dummy video path if possible, or a real one if we know it)
    # The user has "GI17scenes-Scene-002.mp4" in ongoing conversations, or "video.mp4"
    # I'll use a path likely to exist or fail gracefully.
    # PRO TIP: The server creates a job even if video path is invalid initially, 
    # but let's try to point to something real if we can found one.
    # Handover mentioned: /Users/.../video.mp4
    
    # I'll use a nonexistent path to test the error handling safely, 
    # or better, search for a valid mp4 first. 
    video_path = "/Users/lukewildman/Projects/VLM-1/test_video.mp4" 

    print(f"Triggering analysis for {video_path}...")
    payload = {
        "video_path": video_path,
        "batch_size": 20,
        "fps": 1.5,
        "num_frames": 2 # Short run
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/analyze", json=payload)
        data = resp.json()
        job_id = data.get("job_id")
        print(f"✅ Job started: {job_id}")
    except Exception as e:
        print(f"❌ Failed to start job: {e}")
        return

    # Poll status
    for i in range(10):
        time.sleep(2)
        resp = requests.get(f"{BASE_URL}/jobs/{job_id}")
        if resp.status_code != 200:
             print(f"⚠️ Error polling job: {resp.status_code}")
             continue
             
        status = resp.json().get("status", "unknown")
        print(f"Status: {status}")
        
        if "Error" in status:
            print(f"❌ Job failed with error: {status}")
            break
        if status == "completed":
            print("✅ Job completed successfully!")
            break
            
if __name__ == "__main__":
    run_test()
