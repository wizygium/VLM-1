#!/usr/bin/env python3
"""
Verification script for physics-only analyzer implementation.

Tests that all components are properly integrated and ready to use,
without requiring an actual video file.
"""

import json
from pathlib import Path
from validate_physics_output import PhysicsValidator, ZoneGraph


def test_zone_graph():
    """Test zone adjacency graph."""
    print("\n🧪 Testing Zone Adjacency Graph...")

    tests = [
        # (zone1, zone2, should_be_adjacent)
        ("z3_4", "z3_4", True, "Same zone"),
        ("z3_4", "z3_5", True, "Adjacent lateral"),
        ("z3_4", "z4_4", True, "Adjacent depth"),
        ("z3_4", "z4_5", True, "Diagonal"),
        ("z3_4", "z5_6", False, "Too far"),
        ("z1_1", "z0", True, "Near goal to goal"),
        ("z0", "z1_4", True, "Goal to near goal"),
        ("z0", "z3_4", False, "Goal to far zone"),
    ]

    passed = 0
    failed = 0

    for zone1, zone2, expected, desc in tests:
        result = ZoneGraph.is_adjacent(zone1, zone2)
        if result == expected:
            print(f"  ✓ {desc}: {zone1} → {zone2} = {result}")
            passed += 1
        else:
            print(f"  ✗ {desc}: {zone1} → {zone2} = {result} (expected {expected})")
            failed += 1

    print(f"\n  Results: {passed} passed, {failed} failed")
    return failed == 0


def test_validator_with_mock_data():
    """Test validator with mock physics data."""
    print("\n🧪 Testing Physics Validator...")

    # Valid mock data
    valid_data = [
        {
            "timestamp": "0.0000",
            "ball": {
                "holder_track_id": "t1",
                "zone": "z3_4",
                "state": "Holding",
            },
            "players": [
                {
                    "track_id": "t1",
                    "zone": "z3_4",
                    "jersey_number": "25",
                    "team": "white",
                },
                {
                    "track_id": "t2",
                    "zone": "z3_5",
                    "jersey_number": None,
                    "team": "white",
                },
            ],
        },
        {
            "timestamp": "0.0625",
            "ball": {
                "holder_track_id": "t1",
                "zone": "z3_4",
                "state": "Holding",
            },
            "players": [
                {
                    "track_id": "t1",
                    "zone": "z3_4",
                    "jersey_number": "25",
                    "team": "white",
                },
                {
                    "track_id": "t2",
                    "zone": "z3_6",  # Adjacent move from z3_5
                    "jersey_number": "12",  # Jersey now visible
                    "team": "white",
                },
            ],
        },
    ]

    validator = PhysicsValidator()
    errors = validator.validate_all(valid_data, fps=16.0)

    if not errors:
        print("  ✓ Valid data passed validation")
    else:
        print(f"  ✗ Valid data failed validation with {len(errors)} errors:")
        for error in errors[:5]:
            print(f"    - {error}")
        return False

    # Test adjacency violation detection
    invalid_data = [
        {
            "timestamp": "0.0000",
            "ball": {"holder_track_id": "t1", "zone": "z3_4", "state": "Holding"},
            "players": [{"track_id": "t1", "zone": "z3_4", "jersey_number": "25", "team": "white"}],
        },
        {
            "timestamp": "0.0625",
            "ball": {"holder_track_id": "t1", "zone": "z5_6", "state": "Holding"},
            "players": [
                {
                    "track_id": "t1",
                    "zone": "z5_6",  # Violation: z3_4 → z5_6 not adjacent
                    "jersey_number": "25",
                    "team": "white",
                }
            ],
        },
    ]

    errors = validator.validate_all(invalid_data, fps=16.0)
    if errors:
        adjacency_error_found = any("violated adjacency" in e for e in errors)
        if adjacency_error_found:
            print("  ✓ Adjacency violation correctly detected")
        else:
            print(f"  ✗ Expected adjacency violation error, got: {errors}")
            return False
    else:
        print("  ✗ Failed to detect adjacency violation")
        return False

    print("\n  Results: All validation tests passed")
    return True


def test_event_detection():
    """Test event detection logic."""
    print("\n🧪 Testing Event Detection...")

    try:
        from physics_to_events import detect_events

        # Mock physics frames with a PASS event
        frames = [
            {
                "timestamp": "0.0000",
                "ball": {"holder_track_id": "t1", "zone": "z3_4", "state": "Holding"},
                "players": [
                    {"track_id": "t1", "zone": "z3_4", "jersey_number": "25", "team": "white"},
                    {"track_id": "t2", "zone": "z2_5", "jersey_number": "12", "team": "white"},
                ],
            },
            {
                "timestamp": "0.0625",
                "ball": {"holder_track_id": "t1", "zone": "z3_4", "state": "In-Air"},
                "players": [
                    {"track_id": "t1", "zone": "z3_4", "jersey_number": "25", "team": "white"},
                    {"track_id": "t2", "zone": "z2_5", "jersey_number": "12", "team": "white"},
                ],
            },
            {
                "timestamp": "0.1250",
                "ball": {"holder_track_id": "t2", "zone": "z2_5", "state": "Holding"},
                "players": [
                    {"track_id": "t1", "zone": "z3_4", "jersey_number": "25", "team": "white"},
                    {"track_id": "t2", "zone": "z2_5", "jersey_number": "12", "team": "white"},
                ],
            },
        ]

        events = detect_events(frames)

        # Should detect 1 PASS event (holder changed from t1 to t2 + ball was in-air)
        pass_events = [e for e in events if e["type"] == "PASS"]

        if len(pass_events) == 1:
            print(f"  ✓ Detected {len(pass_events)} PASS event")
            event = pass_events[0]
            print(f"    - From: {event['from_track_id']} (jersey {event.get('from_jersey')})")
            print(f"    - To: {event['to_track_id']} (jersey {event.get('to_jersey')})")
            print(f"    - Zones: {event['from_zone']} → {event['to_zone']}")
        else:
            print(f"  ✗ Expected 1 PASS event, got {len(pass_events)}")
            return False

        # Test SHOT detection
        frames_with_shot = [
            {
                "timestamp": "0.0000",
                "ball": {"holder_track_id": "t1", "zone": "z1_4", "state": "Holding"},
                "players": [
                    {"track_id": "t1", "zone": "z1_4", "jersey_number": "25", "team": "white"}
                ],
            },
            {
                "timestamp": "0.0625",
                "ball": {"holder_track_id": None, "zone": "z0", "state": "In-Air"},
                "players": [
                    {"track_id": "t1", "zone": "z1_4", "jersey_number": "25", "team": "white"}
                ],
            },
        ]

        events = detect_events(frames_with_shot)
        shot_events = [e for e in events if e["type"] == "SHOT"]

        if len(shot_events) == 1:
            print(f"  ✓ Detected {len(shot_events)} SHOT event")
            event = shot_events[0]
            print(f"    - Shooter: {event['shooter_track_id']} (jersey {event.get('shooter_jersey')})")
            print(f"    - From zone: {event['from_zone']}")
        else:
            print(f"  ✗ Expected 1 SHOT event, got {len(shot_events)}")
            return False

        print("\n  Results: All event detection tests passed")
        return True

    except Exception as e:
        print(f"  ✗ Event detection test failed: {e}")
        return False


def test_file_structure():
    """Verify all required files exist."""
    print("\n🧪 Testing File Structure...")

    required_files = [
        "physics_prompt.md",
        "gemini_physics_analyzer.py",
        "validate_physics_output.py",
        "physics_to_events.py",
        "README_PHYSICS_ANALYZER.md",
    ]

    all_exist = True
    for filename in required_files:
        path = Path(filename)
        if path.exists():
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} (missing)")
            all_exist = False

    return all_exist


def test_49_zone_generation():
    """Test that all 49 zones are valid."""
    print("\n🧪 Testing 49-Zone System...")

    validator = PhysicsValidator()
    zones = validator.valid_zones

    # Should have exactly 49 zones
    if len(zones) != 49:
        print(f"  ✗ Expected 49 zones, got {len(zones)}")
        return False

    print(f"  ✓ Generated {len(zones)} zones")

    # Verify z0 exists
    if "z0" not in zones:
        print("  ✗ Missing z0 (goal)")
        return False

    # Verify depth/lateral ranges
    depth_count = {d: 0 for d in range(1, 7)}
    lateral_count = {w: 0 for w in range(1, 9)}

    for zone in zones:
        if zone == "z0":
            continue
        parsed = ZoneGraph.parse_zone(zone)
        if parsed:
            depth, lateral = parsed
            if depth in depth_count:
                depth_count[depth] += 1
            if lateral in lateral_count:
                lateral_count[lateral] += 1

    # Each depth should have 8 zones
    all_correct = True
    for depth, count in depth_count.items():
        if count != 8:
            print(f"  ✗ Depth {depth} has {count} zones (expected 8)")
            all_correct = False

    # Each lateral should have 6 zones
    for lateral, count in lateral_count.items():
        if count != 6:
            print(f"  ✗ Lateral {lateral} has {count} zones (expected 6)")
            all_correct = False

    if all_correct:
        print("  ✓ Zone distribution correct (6 depths × 8 lateral + z0)")

    return all_correct


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Physics-Only Analyzer Verification")
    print("=" * 60)

    tests = [
        ("File Structure", test_file_structure),
        ("49-Zone System", test_49_zone_generation),
        ("Zone Adjacency", test_zone_graph),
        ("Physics Validator", test_validator_with_mock_data),
        ("Event Detection", test_event_detection),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n  ✗ Test crashed: {e}")
            import traceback

            traceback.print_exc()
            results[name] = False

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All verification tests passed!")
        print("\nThe physics analyzer is ready to use. To test with a video:")
        print("  python gemini_physics_analyzer.py video.mp4 -o results_physics/ -v")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
