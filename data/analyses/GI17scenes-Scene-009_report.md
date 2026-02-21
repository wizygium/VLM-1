# Physics Analysis Report: GI17scenes-Scene-009.mp4
Date: 2026-02-14T09:39:07.067257

**Configuration Verification:**
- **Target FPS:** 16.0
- **Spatial Resolution:** HIGH (1120 tokens/frame)
- **Cache Name:** cachedContents/450rr0nyjit9wxasi6hec38tul7zhmfce2vnt0ao
- **Total Tokens:** 7023

---


## [0_VERIFY]
Based on the provided video frames, here is the configuration verification:

1.  **Video Sampling Rate (FPS):**
    The timestamps progress in intervals of 0.0625 seconds (0.000, 0.063, 0.125, etc.).
    Calculation: 1 / 0.0625 = **16 FPS**.

2.  **Spatial Resolution:**
    **Confirmed.** The image clarity is high, allowing for precise localization of players relative to court markings (6m/9m lines) and identification of small details.

3.  **Visibility of Jersey Numbers and Ball:**
    *   **Jersey Numbers:** Clearly visible for most players facing the camera (e.g., White #23, White #18, Blue #17, Blue #11).
    *   **Ball:** The ball is distinct and trackable throughout the sequence, with its state (holding vs. in-air) clearly observable.

4.  **Approximate Number of Visible Players:**
    In the standard wide view (e.g., at 00:01.000), there are **14 visible participants**:
    *   6 Attackers (White team)
    *   6 Defenders (Blue team)
    *   1 Goalkeeper (Black/Grey kit)
    *   1 Referee (Green shirt)

## [1_TRACK_ASSIGNMENT]
PLAYER TRACKS at T=0:
- t1: Team white, Jersey 23, Zone z9 (Ball Carrier)
- t2: Team white, Jersey 18, Zone z3 (Pivot)
- t3: Team blue, Jersey 11, Zone z2 (Defender)
- t4: Team blue, Jersey 18, Zone z3 (Defender)
- t5: Team blue, Jersey 17, Zone z4 (Defender)
- t6: Team blue, Jersey 8, Zone z1 (Defender)
- t7: Team white, Jersey 34, Zone z1 (Left Wing)
- t8: Team white, Jersey 25, Zone z7 (Right Back)
- t9: Team white, Jersey 73, Zone z5 (Right Wing)
- t10: Team blue, Jersey 22, Zone z5 (Defender)
- t11: Team blue, Jersey 4, Zone z3 (Defender)
- t12: Team black, Jersey 1, Zone z0 (Goalkeeper)
- t13: Team green, Jersey null, Zone z5 (Referee)
- t14: Team green, Jersey null, Zone z1 (Referee)
- t15: Team white, Jersey null, Zone z10 (Left Back)

## [2_BALL_STATE]
```json
{
  "timestamp": "00:00.000",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.063",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.125",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.188",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.250",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.313",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.375",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.438",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.500",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.563",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.625",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.688",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.750",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.813",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.875",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.938",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.000",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.063",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.125",
  "ball": {
    "holder_track_id": null,
    "zone": "z3",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.188",
  "ball": {
    "holder_track_id": null,
    "zone": "z3",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.250",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.313",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.375",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.438",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.500",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.563",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.625",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.688",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.750",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.813",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.875",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.938",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.000",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z3",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.063",
  "ball": {
    "holder_track_id": null,
    "zone": "z3",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.125",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.188",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.250",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.313",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.375",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.438",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.500",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.563",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.625",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.688",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.750",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.813",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.875",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.938",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.000",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.063",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.125",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.188",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.250",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.313",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.375",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.438",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.500",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.563",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.625",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.688",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.750",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.813",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.875",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.938",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:04.000",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:04.063",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:04.125",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:04.188",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:04.250",
  "ball": {
    "holder_track_id": null,
    "zone": "z0",
    "state": "Loose"
  },
  "players": [
    {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
    {"track_id": "t2", "zone": "z3", "jersey_number": "18", "team": "white"},
    {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
    {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
    {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
    {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
    {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
    {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
    {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
    {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
    {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
    {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"}
  ]
}
```

## [3_POSITIONS]
FRAME at 00:00.000:
- t1: Zone z9, Jersey 23, Team white
- t2: Zone z3, Jersey 18, Team white
- t3: Zone z3, Jersey 18, Team blue
- t4: Zone z2, Jersey 11, Team blue
- t5: Zone z4, Jersey 17, Team blue
- t6: Zone z1, Jersey 8, Team blue
- t7: Zone z5, Jersey 22, Team blue
- t8: Zone z7, Jersey 25, Team white
- t9: Zone z1, Jersey 34, Team white
- t10: Zone z5, Jersey 73, Team white
- t11: Zone z0, Jersey 1, Team black
- t12: Zone z5, Jersey null, Team green
- t13: Zone z3, Jersey 4, Team blue

FRAME at 00:00.500:
- t1: Zone z9, Jersey 23, Team white
- t2: Zone z3, Jersey 18, Team white
- t3: Zone z3, Jersey 18, Team blue
- t4: Zone z2, Jersey 11, Team blue
- t5: Zone z4, Jersey 17, Team blue
- t6: Zone z1, Jersey 8, Team blue
- t7: Zone z5, Jersey 22, Team blue
- t8: Zone z7, Jersey 25, Team white
- t9: Zone z1, Jersey 34, Team white
- t10: Zone z5, Jersey 73, Team white
- t11: Zone z0, Jersey 1, Team black
- t12: Zone z5, Jersey null, Team green
- t13: Zone z3, Jersey 4, Team blue

FRAME at 00:01.000:
- t1: Zone z3, Jersey 23, Team white
- t2: Zone z3, Jersey 18, Team white
- t3: Zone z3, Jersey 18, Team blue
- t4: Zone z2, Jersey 11, Team blue
- t5: Zone z4, Jersey 17, Team blue
- t6: Zone z1, Jersey 8, Team blue
- t7: Zone z5, Jersey 22, Team blue
- t8: Zone z7, Jersey 25, Team white
- t9: Zone z1, Jersey 34, Team white
- t10: Zone z5, Jersey 73, Team white
- t11: Zone z0, Jersey 1, Team black
- t12: Zone z5, Jersey null, Team green
- t13: Zone z3, Jersey 4, Team blue

FRAME at 00:01.500:
- t1: Zone z3, Jersey 23, Team white
- t2: Zone z3, Jersey 18, Team white
- t3: Zone z3, Jersey 18, Team blue
- t4: Zone z2, Jersey 11, Team blue
- t5: Zone z4, Jersey 17, Team blue
- t6: Zone z1, Jersey 8, Team blue
- t7: Zone z5, Jersey 22, Team blue
- t8: Zone z7, Jersey 25, Team white
- t9: Zone z1, Jersey 34, Team white
- t10: Zone z5, Jersey 73, Team white
- t11: Zone z0, Jersey 1, Team black
- t12: Zone z5, Jersey null, Team green
- t13: Zone z3, Jersey 4, Team blue

FRAME at 00:02.000:
- t1: Zone z3, Jersey 23, Team white
- t2: Zone z3, Jersey 18, Team white
- t3: Zone z3, Jersey 18, Team blue
- t4: Zone z2, Jersey 11, Team blue
- t5: Zone z4, Jersey 17, Team blue
- t6: Zone z1, Jersey 8, Team blue
- t7: Zone z5, Jersey 22, Team blue
- t8: Zone z7, Jersey 25, Team white
- t9: Zone z1, Jersey 34, Team white
- t10: Zone z5, Jersey 73, Team white
- t11: Zone z0, Jersey 1, Team black
- t12: Zone z5, Jersey null, Team green
- t13: Zone z3, Jersey 4, Team blue

FRAME at 00:02.500:
- t1: Zone z3, Jersey 23, Team white
- t2: Zone z3, Jersey 18, Team white
- t3: Zone z3, Jersey 18, Team blue
- t4: Zone z2, Jersey 11, Team blue
- t5: Zone z4, Jersey 17, Team blue
- t6: Zone z1, Jersey 8, Team blue
- t7: Zone z5, Jersey 22, Team blue
- t8: Zone z7, Jersey 25, Team white
- t9: Zone z1, Jersey 34, Team white
- t10: Zone z5, Jersey 73, Team white
- t11: Zone z0, Jersey 1, Team black
- t12: Zone z5, Jersey null, Team green
- t13: Zone z3, Jersey 4, Team blue

FRAME at 00:03.000:
- t1: Zone z3, Jersey 23, Team white
- t2: Zone z3, Jersey 18, Team white
- t3: Zone z3, Jersey 18, Team blue
- t4: Zone z2, Jersey 11, Team blue
- t5: Zone z4, Jersey 17, Team blue
- t6: Zone z1, Jersey 8, Team blue
- t7: Zone z5, Jersey 22, Team blue
- t8: Zone z7, Jersey 25, Team white
- t9: Zone z1, Jersey 34, Team white
- t10: Zone z5, Jersey 73, Team white
- t11: Zone z0, Jersey 1, Team black
- t12: Zone z5, Jersey null, Team green
- t13: Zone z3, Jersey 4, Team blue

FRAME at 00:03.500:
- t1: Zone z3, Jersey 23, Team white
- t2: Zone z3, Jersey 18, Team white
- t3: Zone z3, Jersey 18, Team blue
- t4: Zone z2, Jersey 11, Team blue
- t5: Zone z4, Jersey 17, Team blue
- t6: Zone z1, Jersey 8, Team blue
- t7: Zone z5, Jersey 22, Team blue
- t8: Zone z7, Jersey 25, Team white
- t9: Zone z1, Jersey 34, Team white
- t10: Zone z5, Jersey 73, Team white
- t11: Zone z0, Jersey 1, Team black
- t12: Zone z5, Jersey null, Team green
- t13: Zone z3, Jersey 4, Team blue

FRAME at 00:04.000:
- t1: Zone z3, Jersey 23, Team white
- t2: Zone z3, Jersey 18, Team white
- t3: Zone z3, Jersey 18, Team blue
- t4: Zone z2, Jersey 11, Team blue
- t5: Zone z4, Jersey 17, Team blue
- t6: Zone z1, Jersey 8, Team blue
- t7: Zone z5, Jersey 22, Team blue
- t8: Zone z7, Jersey 25, Team white
- t9: Zone z1, Jersey 34, Team white
- t10: Zone z5, Jersey 73, Team white
- t11: Zone z0, Jersey 1, Team black
- t12: Zone z5, Jersey null, Team green
- t13: Zone z3, Jersey 4, Team blue

## [4_SANITY_CHECK]
Corrections made:
1.  **Jersey Number Correction (t2 vs t15):** Player **t2** (White Pivot in z3) was incorrectly identified as #18. The player wearing White #18 is actually standing in the backcourt (z8/z12) and should be tracked separately (assigned **t15**). I will set t2's jersey to `null` as it is obscured, and ensure t15 is tracked as White #18.
2.  **Ball State Transition:** Confirmed the transition from t1 (Holding) -> In-Air (Pass) -> t2 (Holding) -> In-Air (Shot) -> Loose (Save/Rebound) is physically consistent with the visual evidence.
3.  **Zone Refinement:** Adjusted t1's zone progression from z9 to z3 to match his drive towards the goal line.

## [5_JSON]
[
  {
    "timestamp": "0.00",
    "ball": {
      "holder_track_id": "t1",
      "zone": "z9",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
      {"track_id": "t2", "zone": "z3", "jersey_number": null, "team": "white"},
      {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
      {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
      {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
      {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
      {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
      {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
      {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
      {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
      {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
      {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"},
      {"track_id": "t15", "zone": "z10", "jersey_number": "18", "team": "white"}
    ]
  },
  {
    "timestamp": "0.50",
    "ball": {
      "holder_track_id": "t1",
      "zone": "z9",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z9", "jersey_number": "23", "team": "white"},
      {"track_id": "t2", "zone": "z3", "jersey_number": null, "team": "white"},
      {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
      {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
      {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
      {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
      {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
      {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
      {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
      {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
      {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
      {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"},
      {"track_id": "t15", "zone": "z10", "jersey_number": "18", "team": "white"}
    ]
  },
  {
    "timestamp": "1.00",
    "ball": {
      "holder_track_id": "t1",
      "zone": "z3",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
      {"track_id": "t2", "zone": "z3", "jersey_number": null, "team": "white"},
      {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
      {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
      {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
      {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
      {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
      {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
      {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
      {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
      {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
      {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"},
      {"track_id": "t15", "zone": "z10", "jersey_number": "18", "team": "white"}
    ]
  },
  {
    "timestamp": "1.50",
    "ball": {
      "holder_track_id": "t2",
      "zone": "z3",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
      {"track_id": "t2", "zone": "z3", "jersey_number": null, "team": "white"},
      {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
      {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
      {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
      {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
      {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
      {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
      {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
      {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
      {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
      {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"},
      {"track_id": "t15", "zone": "z10", "jersey_number": "18", "team": "white"}
    ]
  },
  {
    "timestamp": "2.00",
    "ball": {
      "holder_track_id": "t2",
      "zone": "z3",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
      {"track_id": "t2", "zone": "z3", "jersey_number": null, "team": "white"},
      {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
      {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
      {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
      {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
      {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
      {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
      {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
      {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
      {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
      {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"},
      {"track_id": "t15", "zone": "z10", "jersey_number": "18", "team": "white"}
    ]
  },
  {
    "timestamp": "2.50",
    "ball": {
      "holder_track_id": null,
      "zone": "z0",
      "state": "Loose"
    },
    "players": [
      {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
      {"track_id": "t2", "zone": "z3", "jersey_number": null, "team": "white"},
      {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
      {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
      {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
      {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
      {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
      {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
      {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
      {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
      {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
      {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"},
      {"track_id": "t15", "zone": "z10", "jersey_number": "18", "team": "white"}
    ]
  },
  {
    "timestamp": "3.00",
    "ball": {
      "holder_track_id": null,
      "zone": "z0",
      "state": "Loose"
    },
    "players": [
      {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
      {"track_id": "t2", "zone": "z3", "jersey_number": null, "team": "white"},
      {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
      {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
      {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
      {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
      {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
      {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
      {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
      {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
      {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
      {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"},
      {"track_id": "t15", "zone": "z10", "jersey_number": "18", "team": "white"}
    ]
  },
  {
    "timestamp": "3.50",
    "ball": {
      "holder_track_id": null,
      "zone": "z0",
      "state": "Loose"
    },
    "players": [
      {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
      {"track_id": "t2", "zone": "z3", "jersey_number": null, "team": "white"},
      {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
      {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
      {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
      {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
      {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
      {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
      {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
      {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
      {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
      {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"},
      {"track_id": "t15", "zone": "z10", "jersey_number": "18", "team": "white"}
    ]
  },
  {
    "timestamp": "4.00",
    "ball": {
      "holder_track_id": null,
      "zone": "z0",
      "state": "Loose"
    },
    "players": [
      {"track_id": "t1", "zone": "z3", "jersey_number": "23", "team": "white"},
      {"track_id": "t2", "zone": "z3", "jersey_number": null, "team": "white"},
      {"track_id": "t3", "zone": "z3", "jersey_number": "18", "team": "blue"},
      {"track_id": "t4", "zone": "z2", "jersey_number": "11", "team": "blue"},
      {"track_id": "t5", "zone": "z4", "jersey_number": "17", "team": "blue"},
      {"track_id": "t6", "zone": "z1", "jersey_number": "8", "team": "blue"},
      {"track_id": "t7", "zone": "z5", "jersey_number": "22", "team": "blue"},
      {"track_id": "t8", "zone": "z7", "jersey_number": "25", "team": "white"},
      {"track_id": "t9", "zone": "z1", "jersey_number": "34", "team": "white"},
      {"track_id": "t10", "zone": "z5", "jersey_number": "73", "team": "white"},
      {"track_id": "t11", "zone": "z0", "jersey_number": "1", "team": "black"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "green"},
      {"track_id": "t13", "zone": "z3", "jersey_number": "4", "team": "blue"},
      {"track_id": "t15", "zone": "z10", "jersey_number": "18", "team": "white"}
    ]
  }
]
