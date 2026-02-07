# Physics Analysis Report: GI17scenes-Scene-011.mp4
Date: 2026-02-07T14:06:42.198197

**Configuration Verification:**
- **Target FPS:** 16.0
- **Spatial Resolution:** HIGH (1120 tokens/frame)
- **Cache Name:** cachedContents/51yi0lz0dgrepw3as2kjn03eoe7lqbh7zv66gnva
- **Total Tokens:** 9302

---


## [0_VERIFY]
Based on the provided video frames and timestamps:

1.  **Video Sampling Rate:** The timestamps increment by exactly 0.0625 seconds (0.000, 0.063, 0.125...), which confirms a sampling rate of **16 FPS**.
2.  **Spatial Resolution:** Confirmed high spatial resolution; court markings, player features, and jersey numbers are distinct.
3.  **Visibility:**
    *   **Jersey Numbers:** Clearly visible for most players facing the camera (e.g., White 14, White 30, Blue 11, Blue 10).
    *   **Ball:** Clearly visible and trackable against the blue court surface.
4.  **Visible Players:** Approximately **11 players** are actively visible on the court in the initial frames (1 Goalkeeper, ~5 Defenders in white, ~5 Attackers in blue).

Configuration verified. Ready to proceed with tracking.

## [1_TRACK_ASSIGNMENT]
PLAYER TRACKS at T=0:
- t1: Team white (Goalkeeper), Jersey null, Zone z0
- t2: Team white, Jersey 14, Zone z1
- t3: Team white, Jersey null, Zone z2
- t4: Team white, Jersey null, Zone z3
- t5: Team white, Jersey 30, Zone z4
- t6: Team white, Jersey null, Zone z9
- t7: Team blue, Jersey 18, Zone z9
- t8: Team blue, Jersey 11, Zone z3
- t9: Team blue, Jersey 10, Zone z6
- t10: Team blue, Jersey 22, Zone z10
- t11: Team blue, Jersey 23, Zone z8

## [2_BALL_STATE]
- [0.000s] Ball Holder: t2 | Zone: z9 | Status: Holding
- [0.313s] Ball Holder: t2 | Zone: z9 | Status: Holding
- [0.375s] Ball Holder: null | Zone: z9 | Status: In-Air
- [0.625s] Ball Holder: t3 | Zone: z10 | Status: Holding
- [1.125s] Ball Holder: t3 | Zone: z10 | Status: Holding
- [1.188s] Ball Holder: null | Zone: z10 | Status: In-Air
- [1.438s] Ball Holder: t2 | Zone: z9 | Status: Holding
- [1.875s] Ball Holder: t2 | Zone: z9 | Status: Holding
- [1.938s] Ball Holder: null | Zone: z9 | Status: In-Air
- [2.125s] Ball Holder: t4 | Zone: z8 | Status: Holding
- [2.313s] Ball Holder: t4 | Zone: z8 | Status: Holding
- [2.375s] Ball Holder: null | Zone: z8 | Status: In-Air
- [2.563s] Ball Holder: t5 | Zone: z7 | Status: Holding
- [3.250s] Ball Holder: t5 | Zone: z7 | Status: Holding
- [3.313s] Ball Holder: null | Zone: z7 | Status: In-Air
- [3.500s] Ball Holder: t6 | Zone: z2 | Status: Holding
- [4.063s] Ball Holder: t6 | Zone: z2 | Status: Holding
- [4.125s] Ball Holder: null | Zone: z2 | Status: In-Air
- [4.375s] Ball Holder: t5 | Zone: z2 | Status: Holding
- [4.750s] Ball Holder: t5 | Zone: z2 | Status: Holding
- [4.813s] Ball Holder: null | Zone: z1 | Status: In-Air
- [5.313s] Ball Holder: null | Zone: z0 | Status: Loose

## [3_POSITIONS]
FRAME at 00:00.000:
- t1: Zone z0, Jersey null, Team yellow (GK)
- t2: Zone z1, Jersey 14, Team white
- t3: Zone z2, Jersey null, Team white
- t4: Zone z3, Jersey null, Team white
- t5: Zone z4, Jersey 30, Team white
- t10: Zone z9, Jersey null, Team blue
- t11: Zone z10, Jersey 22, Team blue
- t9: Zone z8, Jersey 23, Team blue
- t8: Zone z7, Jersey null, Team blue
- t12: Zone z3, Jersey 18, Team blue

FRAME at 00:00.500:
- t1: Zone z0, Jersey null, Team yellow
- t2: Zone z1, Jersey 14, Team white
- t5: Zone z5, Jersey 30, Team white
- t10: Zone z9, Jersey null, Team blue
- t11: Zone z10, Jersey 22, Team blue (Holding ball)
- t9: Zone z8, Jersey 23, Team blue

FRAME at 00:01.000:
- t1: Zone z0, Jersey null, Team yellow
- t11: Zone z10, Jersey 22, Team blue (Holding ball)
- t5: Zone z5, Jersey 30, Team white
- t10: Zone z9, Jersey null, Team blue

FRAME at 00:01.500:
- t1: Zone z0, Jersey null, Team yellow
- t10: Zone z9, Jersey null, Team blue (Holding ball)
- t11: Zone z10, Jersey 22, Team blue
- t9: Zone z8, Jersey 23, Team blue
- t5: Zone z4, Jersey 30, Team white

FRAME at 00:02.000:
- t1: Zone z0, Jersey null, Team yellow
- t9: Zone z8, Jersey 23, Team blue (Holding ball)
- t10: Zone z9, Jersey null, Team blue
- t8: Zone z7, Jersey null, Team blue
- t4: Zone z3, Jersey null, Team white

FRAME at 00:02.500:
- t1: Zone z0, Jersey null, Team yellow
- t8: Zone z7, Jersey null, Team blue (Holding ball)
- t9: Zone z8, Jersey 23, Team blue
- t12: Zone z3, Jersey 18, Team blue
- t3: Zone z2, Jersey null, Team white

FRAME at 00:03.000:
- t1: Zone z0, Jersey null, Team yellow
- t8: Zone z7, Jersey null, Team blue (Holding ball)
- t12: Zone z2, Jersey 18, Team blue
- t3: Zone z2, Jersey null, Team white
- t2: Zone z1, Jersey 14, Team white

FRAME at 00:03.500:
- t1: Zone z0, Jersey null, Team yellow
- t12: Zone z2, Jersey 18, Team blue (Holding ball)
- t3: Zone z2, Jersey null, Team white
- t2: Zone z1, Jersey 14, Team white
- t8: Zone z7, Jersey null, Team blue

FRAME at 00:04.000:
- t1: Zone z0, Jersey null, Team yellow
- t12: Zone z2, Jersey 18, Team blue (Holding ball)
- t3: Zone z2, Jersey null, Team white
- t4: Zone z3, Jersey null, Team white

FRAME at 00:04.500:
- t1: Zone z0, Jersey null, Team yellow
- t12: Zone z2, Jersey 18, Team blue (Dribbling/Falling)
- t3: Zone z2, Jersey null, Team white
- t4: Zone z3, Jersey null, Team white

FRAME at 00:05.000:
- t1: Zone z0, Jersey null, Team yellow
- t12: Zone z2, Jersey 18, Team blue
- Ball: Zone z0 (In-Air)

FRAME at 00:05.500:
- t1: Zone z0, Jersey null, Team yellow
- Ball: Zone z0 (Loose/Rebound)

## [4_SANITY_CHECK]
Corrections made: Re-assigned ball possession from defending team (White) to attacking team (Blue). Corrected track IDs to follow the pass sequence: Right Back -> Center Back -> Left Back -> Left Wing. Adjusted zones to match court geometry.

## [5_JSON]
[
  {
    "timestamp": "0.000",
    "ball": {
      "holder_track_id": "t4",
      "zone": "z10",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t2", "zone": "z1", "jersey_number": "14", "team": "white"},
      {"track_id": "t3", "zone": "z5", "jersey_number": "30", "team": "white"},
      {"track_id": "t4", "zone": "z10", "jersey_number": "22", "team": "blue"},
      {"track_id": "t5", "zone": "z9", "jersey_number": "23", "team": "blue"},
      {"track_id": "t6", "zone": "z8", "jersey_number": "18", "team": "blue"},
      {"track_id": "t7", "zone": "z3", "jersey_number": "11", "team": "blue"}
    ]
  },
  {
    "timestamp": "0.500",
    "ball": {
      "holder_track_id": null,
      "zone": "z9",
      "state": "In-Air"
    },
    "players": [
      {"track_id": "t1", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t2", "zone": "z1", "jersey_number": "14", "team": "white"},
      {"track_id": "t3", "zone": "z5", "jersey_number": "30", "team": "white"},
      {"track_id": "t4", "zone": "z10", "jersey_number": "22", "team": "blue"},
      {"track_id": "t5", "zone": "z9", "jersey_number": "23", "team": "blue"},
      {"track_id": "t6", "zone": "z8", "jersey_number": "18", "team": "blue"},
      {"track_id": "t7", "zone": "z3", "jersey_number": "11", "team": "blue"}
    ]
  },
  {
    "timestamp": "1.000",
    "ball": {
      "holder_track_id": "t5",
      "zone": "z9",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t2", "zone": "z1", "jersey_number": "14", "team": "white"},
      {"track_id": "t3", "zone": "z5", "jersey_number": "30", "team": "white"},
      {"track_id": "t4", "zone": "z10", "jersey_number": "22", "team": "blue"},
      {"track_id": "t5", "zone": "z9", "jersey_number": "23", "team": "blue"},
      {"track_id": "t6", "zone": "z8", "jersey_number": "18", "team": "blue"},
      {"track_id": "t7", "zone": "z3", "jersey_number": "11", "team": "blue"}
    ]
  },
  {
    "timestamp": "1.500",
    "ball": {
      "holder_track_id": "t6",
      "zone": "z8",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t2", "zone": "z1", "jersey_number": "14", "team": "white"},
      {"track_id": "t3", "zone": "z4", "jersey_number": "30", "team": "white"},
      {"track_id": "t4", "zone": "z10", "jersey_number": "22", "team": "blue"},
      {"track_id": "t5", "zone": "z9", "jersey_number": "23", "team": "blue"},
      {"track_id": "t6", "zone": "z8", "jersey_number": "18", "team": "blue"},
      {"track_id": "t7", "zone": "z3", "jersey_number": "11", "team": "blue"}
    ]
  },
  {
    "timestamp": "2.000",
    "ball": {
      "holder_track_id": null,
      "zone": "z7",
      "state": "In-Air"
    },
    "players": [
      {"track_id": "t1", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t2", "zone": "z1", "jersey_number": "14", "team": "white"},
      {"track_id": "t3", "zone": "z4", "jersey_number": "30", "team": "white"},
      {"track_id": "t5", "zone": "z9", "jersey_number": "23", "team": "blue"},
      {"track_id": "t6", "zone": "z8", "jersey_number": "18", "team": "blue"},
      {"track_id": "t7", "zone": "z3", "jersey_number": "11", "team": "blue"}
    ]
  },
  {
    "timestamp": "2.500",
    "ball": {
      "holder_track_id": "t7",
      "zone": "z3",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t2", "zone": "z1", "jersey_number": "14", "team": "white"},
      {"track_id": "t3", "zone": "z3", "jersey_number": "30", "team": "white"},
      {"track_id": "t6", "zone": "z7", "jersey_number": "18", "team": "blue"},
      {"track_id": "t7", "zone": "z3", "jersey_number": "11", "team": "blue"}
    ]
  },
  {
    "timestamp": "3.000",
    "ball": {
      "holder_track_id": "t7",
      "zone": "z2",
      "state": "Dribbling"
    },
    "players": [
      {"track_id": "t1", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t2", "zone": "z1", "jersey_number": "14", "team": "white"},
      {"track_id": "t3", "zone": "z2", "jersey_number": "30", "team": "white"},
      {"track_id": "t6", "zone": "z7", "jersey_number": "18", "team": "blue"},
      {"track_id": "t7", "zone": "z2", "jersey_number": "11", "team": "blue"}
    ]
  },
  {
    "timestamp": "3.500",
    "ball": {
      "holder_track_id": "t7",
      "zone": "z2",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t2", "zone": "z1", "jersey_number": "14", "team": "white"},
      {"track_id": "t3", "zone": "z2", "jersey_number": "30", "team": "white"},
      {"track_id": "t7", "zone": "z2", "jersey_number": "11", "team": "blue"}
    ]
  },
  {
    "timestamp": "4.000",
    "ball": {
      "holder_track_id": null,
      "zone": "z1",
      "state": "In-Air"
    },
    "players": [
      {"track_id": "t1", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t2", "zone": "z1", "jersey_number": "14", "team": "white"},
      {"track_id": "t7", "zone": "z2", "jersey_number": "11", "team": "blue"}
    ]
  },
  {
    "timestamp": "4.500",
    "ball": {
      "holder_track_id": null,
      "zone": "z0",
      "state": "In-Air"
    },
    "players": [
      {"track_id": "t1", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t2", "zone": "z1", "jersey_number": "14", "team": "white"},
      {"track_id": "t7", "zone": "z2", "jersey_number": "11", "team": "blue"}
    ]
  },
  {
    "timestamp": "5.000",
    "ball": {
      "holder_track_id": null,
      "zone": "z0",
      "state": "Loose"
    },
    "players": [
      {"track_id": "t1", "zone": "z0", "jersey_number": null, "team": "yellow"},
      {"track_id": "t2", "zone": "z1", "jersey_number": "14", "team": "white"},
      {"track_id": "t7", "zone": "z2", "jersey_number": "11", "team": "blue"}
    ]
  }
]
