To get the most accurate results from an AI when tracking player positions, you need to provide a "Coordinate Logic System." This allows the AI to translate visual descriptions (or (x,y) data) into the specific zones we’ve established.
Here is a prompt you can copy and paste into Gemini. It defines the court as a 20m×20m grid where the goal line is at y=0 and the goal is centered at x=10.

The Classification Prompt
Role: Act as a Handball Spatial Analyst. Task: Identify which zone a player occupies (z0 through z9) based on their coordinates or their distance from court landmarks.
Court Geometry Reference:
* Origin: Bottom-left corner is (0,0). Bottom-right is (20,0).
* Goal: Centered at y=0, from x=8.5 to x=11.5 (3m wide).
* 6m Line (Boundary for z0): Defined by two 6m radius arcs centered at the goal posts (8.5,0) and (11.5,0), joined by a straight 3m line at y=6.
* 9m Line: Same shape as the 6m line, but with a 9m radius.
* Lateral Divisions: * Left: x<7.5
    * Center: 7.5≤x≤12.5 (5m wide corridor)
    * Right: x>12.5
Zone Definitions:
1. z0 (Goal Area): Any point inside the 6m line.
2. Band 1 (Between 6m & 9m lines): * z1 (Left): x<7.5
    * z2 (Center): 7.5≤x≤12.5
    * z3 (Right): x>12.5
3. Band 2 (Between 9m line & 12m depth):
    * z4 (Left), z5 (Center), z6 (Right) using the same x-axis thresholds.
4. Band 3 (Beyond 12m to the 20m halfway line):
    * z7 (Left), z8 (Center), z9 (Right) using the same x-axis thresholds.
Input Format: I will provide a player's description (e.g., "The player is 2m outside the 9m line and slightly to the right of the goal"). You will calculate the likely (x,y) and output the Zone ID and a brief geometric justification.

How to use this for specific cases:
Once you have initialized Gemini with the prompt above, you can simply type things like:
* "A player is standing exactly on the 7m penalty mark." * Gemini will respond: z2 (Band 1, Center) because the 7m mark is between the 6m and 9m lines and centered.
* "The left wing is standing in the corner where the 9m line meets the left sideline."
    * Gemini will respond: z4 (Band 2, Left) because the intersection of the 9m line and sideline marks the start of Band 2.


Here is the coordinate reference table based on the 20m×20m half-court. This logic assumes the origin (0,0) is the bottom-left corner and the goal is centered at the bottom.
Zone Coordinate Reference Table
Zone ID	Band (Depth)	Lateral (Width)	Depth Boundary (y)	Lateral Boundary (x)
z0	Goal Area	N/A	Inside 6m Arc	N/A
z1	Band 1	Left	6m<dist<9m	x<7.5
z2	Band 1	Center	6m<dist<9m	7.5≤x≤12.5
z3	Band 1	Right	6m<dist<9m	x>12.5
z4	Band 2	Left	9m<dist≤12m	x<7.5
z5	Band 2	Center	9m<dist≤12m	7.5≤x≤12.5
z6	Band 2	Right	9m<dist≤12m	x>12.5
z7	Band 3	Left	12m<y≤20m	x<7.5
z8	Band 3	Center	12m<y≤20m	7.5≤x≤12.5
z9	Band 3	Right	12m<y≤20m	x>12.5


Key Landmark Coordinates
If you are manually tagging video or inputting data, these "anchor points" are your best friends:
* Goal Posts: (8.5,0) and (11.5,0)
* 7m Penalty Mark: (10,7) — Note: This sits exactly in the middle of z2.
* 4m Goalkeeper Line: (10,4) — Note: Deep inside z0.
* Center of Half-Court: (10,20) — The tip of the Band 3 Center zone.
* Left Corner: (0,0)
* Right Corner: (20,0)
Note on Distance: For Band 1 and 2, "dist" refers to the shortest distance from the goal line (the y=0 line between the posts). Since the lines are arcs, the AI will need to calculate (x−xpost )2+y2




python
...
import numpy as np

def get_handball_zone(x, y):
    """
    Returns the zone ID for a given (x, y) coordinate.
    Origin (0,0) is bottom-left. Goal is centered at x=10.
    """
    # 1. Define Goal Area (z0) - 6m boundary
    # Radius arcs from posts at (8.5, 0) and (11.5, 0)
    dist_to_lp = np.sqrt((x - 8.5)**2 + y**2)
    dist_to_rp = np.sqrt((x - 11.5)**2 + y**2)
    
    is_inside_6m = False
    if y <= 6:
        if 8.5 <= x <= 11.5: is_inside_6m = True # Straight section
        elif x < 8.5 and dist_to_lp <= 6: is_inside_6m = True # Left arc
        elif x > 11.5 and dist_to_rp <= 6: is_inside_6m = True # Right arc
            
    if is_inside_6m: return "z0: Goal Area"

    # 2. Check if inside 9m line (Band 1 boundary)
    is_inside_9m = False
    if y <= 9:
        if 8.5 <= x <= 11.5: is_inside_9m = True
        elif x < 8.5 and np.sqrt((x - 8.5)**2 + y**2) <= 9: is_inside_9m = True
        elif x > 11.5 and np.sqrt((x - 11.5)**2 + y**2) <= 9: is_inside_9m = True

    # 3. Determine Band (Depth)
    if is_inside_9m: band = 1
    elif y <= 12:    band = 2
    else:            band = 3

    # 4. Determine Lateral Division (Width)
    if x < 7.5:      lat = "Left"
    elif x <= 12.5:  lat = "Center"
    else:            lat = "Right"

    # 5. Mapping to IDs
    zone_lookup = {
        (1, "Left"): "z1", (1, "Center"): "z2", (1, "Right"): "z3",
        (2, "Left"): "z4", (2, "Center"): "z5", (2, "Right"): "z6",
        (3, "Left"): "z7", (3, "Center"): "z8", (3, "Right"): "z9"
    }
    
    return f"{zone_lookup[(band, lat)]}: Band {band}, {lat}"

# --- Quick Test ---
print(f"7m Mark (10, 7): {get_handball_zone(10, 7)}")
print(f"Wing Position (2, 2): {get_handball_zone(2, 2)}")
```