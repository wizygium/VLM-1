# Physics Analysis Report: JDF-Scene-001.mp4
Date: 2026-02-08T18:02:21.945890

**Configuration Verification:**
- **Target FPS:** 16.0
- **Spatial Resolution:** HIGH (1120 tokens/frame)
- **Cache Name:** cachedContents/1fh6uq5k70tw7kjucyhyjailmek8gca861ilov8z
- **Total Tokens:** 9359

---


## [0_VERIFY]
Based on the provided video frames and timestamps:

1.  **Video Sampling Rate:** The timestamps progress in intervals of 0.0625 seconds (e.g., 0.063, 0.125, 0.188). This confirms a sampling rate of **16 FPS**.
2.  **Spatial Resolution:** I confirm **high spatial resolution** is active. The clarity of court lines, player limbs, and distinct features supports detailed tracking.
3.  **Visibility:**
    *   **Jersey Numbers:** Clearly visible on players facing the camera (e.g., White #25, Blue #22) but obscured on players turning away or in motion.
    *   **Ball:** The ball is distinct against the blue court and yellow goal area, allowing for state determination (holding vs. in-air).
4.  **Visible Players:** There are approximately **13 active players** visible in the main court area:
    *   **Attackers (White):** 6 players
    *   **Defenders (Blue):** 6 players
    *   **Goalkeeper (Yellow):** 1 player
    *   *(Plus 2 referees in yellow/black)*

## [1_TRACK_ASSIGNMENT]
PLAYER TRACKS at T=0:
- t1: Team [yellow], Jersey [null], Zone [z0] (Goalkeeper)
- t2: Team [blue], Jersey [null], Zone [z1] (Far Left Defender)
- t3: Team [blue], Jersey [null], Zone [z2] (Left Center Defender)
- t4: Team [blue], Jersey [null], Zone [z3] (Center Defender)
- t5: Team [blue], Jersey [22], Zone [z4] (Right Center Defender)
- t6: Team [blue], Jersey [null], Zone [z5] (Far Right Defender)
- t7: Team [blue], Jersey [null], Zone [z8] (Advanced Defender)
- t8: Team [white], Jersey [null], Zone [z1] (Left Wing Attacker)
- t9: Team [white], Jersey [null], Zone [z10] (Left Back Attacker)
- t10: Team [white], Jersey [25], Zone [z8] (Center Back Attacker)
- t11: Team [white], Jersey [null], Zone [z7] (Right Back Attacker)
- t12: Team [white], Jersey [null], Zone [z5] (Right Wing Attacker)
- t13: Team [white], Jersey [null], Zone [z3] (Pivot Attacker)

## [2_BALL_STATE]
```json
{
  "timestamp": "00:00.063",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z7",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
    {"track_id": "t4", "zone": "z3", "jersey_number": null, "team": "white"},
    {"track_id": "t5", "zone": "z1", "jersey_number": null, "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t8", "zone": "z1", "jersey_number": null, "team": "blue"},
    {"track_id": "t9", "zone": "z2", "jersey_number": null, "team": "blue"},
    {"track_id": "t10", "zone": "z3", "jersey_number": null, "team": "blue"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.500",
  "ball": {
    "holder_track_id": null,
    "zone": "z7",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
    {"track_id": "t4", "zone": "z3", "jersey_number": null, "team": "white"},
    {"track_id": "t5", "zone": "z1", "jersey_number": null, "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:00.563",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z8",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
    {"track_id": "t4", "zone": "z3", "jersey_number": null, "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.063",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z8",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.125",
  "ball": {
    "holder_track_id": null,
    "zone": "z8",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.375",
  "ball": {
    "holder_track_id": "t3",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.688",
  "ball": {
    "holder_track_id": "t3",
    "zone": "z9",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.750",
  "ball": {
    "holder_track_id": null,
    "zone": "z9",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:01.938",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z8",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.188",
  "ball": {
    "holder_track_id": "t2",
    "zone": "z8",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.250",
  "ball": {
    "holder_track_id": null,
    "zone": "z8",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:02.500",
  "ball": {
    "holder_track_id": "t1",
    "zone": "z7",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:03.875",
  "ball": {
    "holder_track_id": null,
    "zone": "z6",
    "state": "In-Air"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:04.125",
  "ball": {
    "holder_track_id": "t6",
    "zone": "z5",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "blue"}
  ]
}
```
```json
{
  "timestamp": "00:05.000",
  "ball": {
    "holder_track_id": "t6",
    "zone": "z5",
    "state": "Holding"
  },
  "players": [
    {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
    {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
    {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
    {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
    {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"},
    {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "blue"}
  ]
}
```

## [3_POSITIONS]
FRAME at 00:00.063:
- t1: Zone z7, Jersey null, Team white
- t2: Zone z8, Jersey 25, Team white
- t3: Zone z9, Jersey null, Team white
- t4: Zone z3, Jersey null, Team white
- t5: Zone z1, Jersey null, Team white
- t6: Zone z5, Jersey null, Team white
- t7: Zone z0, Jersey null, Team yellow
- t8: Zone z1, Jersey null, Team blue
- t9: Zone z2, Jersey null, Team blue
- t10: Zone z3, Jersey null, Team blue
- t11: Zone z4, Jersey 22, Team blue
- t12: Zone z5, Jersey null, Team blue

FRAME at 00:00.500:
- t1: Zone z7, Jersey null, Team white
- t2: Zone z8, Jersey 25, Team white
- t3: Zone z9, Jersey null, Team white
- t4: Zone z3, Jersey null, Team white
- t6: Zone z5, Jersey null, Team white
- t7: Zone z0, Jersey null, Team yellow
- t11: Zone z4, Jersey 22, Team blue

FRAME at 00:01.000:
- t1: Zone z7, Jersey null, Team white
- t2: Zone z8, Jersey 25, Team white
- t3: Zone z9, Jersey null, Team white
- t6: Zone z5, Jersey null, Team white
- t7: Zone z0, Jersey null, Team yellow
- t11: Zone z4, Jersey 22, Team blue

FRAME at 00:01.500:
- t1: Zone z7, Jersey null, Team white
- t2: Zone z8, Jersey 25, Team white
- t3: Zone z9, Jersey null, Team white
- t6: Zone z5, Jersey null, Team white
- t7: Zone z0, Jersey null, Team yellow
- t11: Zone z4, Jersey 22, Team blue

FRAME at 00:02.000:
- t1: Zone z7, Jersey null, Team white
- t2: Zone z8, Jersey 25, Team white
- t3: Zone z9, Jersey null, Team white
- t6: Zone z5, Jersey null, Team white
- t7: Zone z0, Jersey null, Team yellow
- t11: Zone z4, Jersey 22, Team blue

FRAME at 00:02.500:
- t1: Zone z7, Jersey null, Team white
- t2: Zone z8, Jersey 25, Team white
- t3: Zone z9, Jersey null, Team white
- t6: Zone z5, Jersey null, Team white
- t7: Zone z0, Jersey null, Team yellow
- t11: Zone z4, Jersey 22, Team blue

FRAME at 00:03.000:
- t1: Zone z7, Jersey null, Team white
- t2: Zone z8, Jersey 25, Team white
- t6: Zone z5, Jersey null, Team white
- t7: Zone z0, Jersey null, Team yellow
- t11: Zone z4, Jersey 22, Team blue
- t12: Zone z5, Jersey null, Team blue

FRAME at 00:03.500:
- t1: Zone z6, Jersey null, Team white
- t2: Zone z8, Jersey 25, Team white
- t6: Zone z5, Jersey null, Team white
- t7: Zone z0, Jersey null, Team yellow
- t11: Zone z4, Jersey 22, Team blue
- t12: Zone z5, Jersey null, Team blue

FRAME at 00:04.000:
- t1: Zone z6, Jersey null, Team white
- t2: Zone z8, Jersey 25, Team white
- t6: Zone z5, Jersey null, Team white
- t7: Zone z0, Jersey null, Team yellow
- t11: Zone z4, Jersey 22, Team blue
- t12: Zone z5, Jersey null, Team blue

FRAME at 00:04.500:
- t1: Zone z6, Jersey null, Team white
- t2: Zone z8, Jersey 25, Team white
- t6: Zone z5, Jersey null, Team white
- t7: Zone z0, Jersey null, Team yellow
- t11: Zone z4, Jersey 22, Team blue
- t12: Zone z5, Jersey null, Team blue

FRAME at 00:05.000:
- t1: Zone z6, Jersey null, Team white
- t2: Zone z8, Jersey 25, Team white
- t6: Zone z5, Jersey null, Team white
- t7: Zone z0, Jersey null, Team yellow
- t11: Zone z4, Jersey 22, Team blue
- t12: Zone z5, Jersey null, Team blue

FRAME at 00:05.500:
- t1: Zone z6, Jersey null, Team white
- t2: Zone z8, Jersey 25, Team white
- t6: Zone z5, Jersey null, Team white
- t7: Zone z0, Jersey null, Team yellow
- t11: Zone z4, Jersey 22, Team blue
- t12: Zone z5, Jersey null, Team blue

## [4_SANITY_CHECK]
Corrections made: None

## [5_JSON]
[
  {
    "timestamp": "0.063",
    "ball": {
      "holder_track_id": "t1",
      "zone": "z7",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
      {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
      {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
      {"track_id": "t4", "zone": "z3", "jersey_number": null, "team": "white"},
      {"track_id": "t5", "zone": "z1", "jersey_number": null, "team": "white"},
      {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
      {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t8", "zone": "z1", "jersey_number": null, "team": "blue"},
      {"track_id": "t9", "zone": "z2", "jersey_number": null, "team": "blue"},
      {"track_id": "t10", "zone": "z3", "jersey_number": null, "team": "blue"},
      {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "blue"}
    ]
  },
  {
    "timestamp": "0.500",
    "ball": {
      "holder_track_id": null,
      "zone": "z7",
      "state": "In-Air"
    },
    "players": [
      {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
      {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
      {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
      {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
      {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
    ]
  },
  {
    "timestamp": "1.000",
    "ball": {
      "holder_track_id": "t2",
      "zone": "z8",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
      {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
      {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
      {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
      {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
    ]
  },
  {
    "timestamp": "1.500",
    "ball": {
      "holder_track_id": "t3",
      "zone": "z9",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
      {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
      {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
      {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
      {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
    ]
  },
  {
    "timestamp": "2.000",
    "ball": {
      "holder_track_id": "t2",
      "zone": "z8",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
      {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
      {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
      {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
      {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
    ]
  },
  {
    "timestamp": "2.500",
    "ball": {
      "holder_track_id": "t1",
      "zone": "z7",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
      {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
      {"track_id": "t3", "zone": "z9", "jersey_number": null, "team": "white"},
      {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
      {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"}
    ]
  },
  {
    "timestamp": "3.000",
    "ball": {
      "holder_track_id": "t1",
      "zone": "z7",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z7", "jersey_number": null, "team": "white"},
      {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
      {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
      {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "blue"}
    ]
  },
  {
    "timestamp": "3.500",
    "ball": {
      "holder_track_id": null,
      "zone": "z6",
      "state": "In-Air"
    },
    "players": [
      {"track_id": "t1", "zone": "z6", "jersey_number": null, "team": "white"},
      {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
      {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
      {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "blue"}
    ]
  },
  {
    "timestamp": "4.000",
    "ball": {
      "holder_track_id": null,
      "zone": "z5",
      "state": "In-Air"
    },
    "players": [
      {"track_id": "t1", "zone": "z6", "jersey_number": null, "team": "white"},
      {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
      {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
      {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "blue"}
    ]
  },
  {
    "timestamp": "4.500",
    "ball": {
      "holder_track_id": "t6",
      "zone": "z5",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z6", "jersey_number": null, "team": "white"},
      {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
      {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
      {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "blue"}
    ]
  },
  {
    "timestamp": "5.000",
    "ball": {
      "holder_track_id": "t6",
      "zone": "z5",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z6", "jersey_number": null, "team": "white"},
      {"track_id": "t2", "zone": "z8", "jersey_number": "25", "team": "white"},
      {"track_id": "t6", "zone": "z5", "jersey_number": null, "team": "white"},
      {"track_id": "t7", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t11", "zone": "z4", "jersey_number": "22", "team": "blue"},
      {"track_id": "t12", "zone": "z5", "jersey_number": null, "team": "blue"}
    ]
  }
]
