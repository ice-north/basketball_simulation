#!/usr/bin/env python3
"""
Fix two critical issues:

1. Players can't reach out-of-bounds ball (court constraints)
2. Centers don't play in the paint (positioning too far)

USER INSIGHTS:
  たぶんですが、アウトオブバウンズで停止する原因は、
  選手がコート外に出たボールを拾いに行けないからじゃないですか？
  あと両チームのCがゴール下でプレイしないのが気になります

PROBLEM 1: Court Constraints During Ball Fetch
-----------------------------------------------

Current code (line 1460-1461):
  p.x = constrain(p.x, 25, 975);
  p.y = constrain(p.y, 262.5, 550);

Issue:
  - Ball goes out of bounds at (995, 240)
  - Thrower tries to fetch: moveToward(p, 995, 240, ...)
  - BUT player position constrained to max x=975
  - Player can NEVER reach ball at x=995
  - Result: FREEZE (distance never < 30)

Court dimensions:
  - X: 12.5 ~ 987.5 (ball can go to ~1000)
  - Y: 250 ~ 562.5 (ball can go to ~240)
  - Player constraints: x=25-975, y=262.5-550
  - Gap: Ball can be 25 units outside player reach!

Solution:
  - Allow player to go slightly outside court during ball fetch
  - Expand constraints to: x=0-1000, y=240-575
  - Only during throwInState && phase === "fetching"

PROBLEM 2: Centers Too Far from Paint
--------------------------------------

Current center positioning (line 980):
  targetX = tg.x - side * 55;

  For PlayerTeam:
    - Goal: x=861.25
    - side = 1
    - targetX = 861.25 - 55 = 806.25
    - Distance from goal: 55 units! (TOO FAR)

  Paint area should be:
    - Within ~20-30 units of goal
    - Current: 55 units (almost at 3-point line!)

Solution:
  - Reduce low post distance: 55 → 30
  - High post distance: 100 → 70
  - Centers will actually play in the paint
"""

def find_line(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=" * 70)
    print("CRITICAL FIXES: Court Bounds & Center Positioning")
    print("=" * 70)
    print()

    # ===== FIX 1: Allow out-of-bounds movement during ball fetch =====
    print("1. Allowing players to fetch out-of-bounds ball...")

    idx = find_line(lines, 'function updatePlayerPosition(p) {')
    if idx > 0:
        # Find the constrain lines
        for i in range(idx, min(idx + 50, len(lines))):
            if 'p.x = constrain(p.x + cos(a)*actualSpeed, 25, 975);' in lines[i]:
                # Replace with conditional constraints
                indent = len(lines[i]) - len(lines[i].lstrip())

                new_code = ' ' * indent + '// OPUS FIX: Allow out-of-bounds during ball fetch\n'
                new_code += ' ' * indent + 'let minX = 25, maxX = 975, minY = 262.5, maxY = 550;\n'
                new_code += ' ' * indent + 'if(throwInState && throwInState.thrower === p.id && throwInState.phase === "fetching") {\n'
                new_code += ' ' * indent + '  // Expand bounds to reach out-of-bounds ball\n'
                new_code += ' ' * indent + '  minX = 0; maxX = 1000;\n'
                new_code += ' ' * indent + '  minY = 240; maxY = 575;\n'
                new_code += ' ' * indent + '}\n'
                new_code += ' ' * indent + 'p.x = constrain(p.x + cos(a)*actualSpeed, minX, maxX);\n'

                # Handle the Y constraint on next line
                if i + 1 < len(lines) and 'p.y = constrain(p.y + sin(a)*actualSpeed' in lines[i + 1]:
                    new_code += ' ' * indent + 'p.y = constrain(p.y + sin(a)*actualSpeed, minY, maxY);\n'
                    lines[i] = new_code
                    lines[i + 1] = ''  # Remove old Y line
                    print("   ✓ Players can now fetch out-of-bounds ball")
                    break

    # ===== FIX 2: Move centers closer to the paint =====
    print("\n2. Moving centers into the paint...")

    idx = find_line(lines, '} else { // C')
    if idx > 0:
        # Find low post position
        for i in range(idx, min(idx + 20, len(lines))):
            if 'targetX = tg.x - side * 55;' in lines[i]:
                # Move closer to goal
                old_line = lines[i]
                new_line = old_line.replace('side * 55', 'side * 30')
                new_line = new_line.replace('ローポスト（ペイント内）', 'ローポスト（真下）')
                lines[i] = new_line
                print(f"   ✓ Low post: 55 → 30 units from goal (line {i+1})")
                break

        # Find high post position
        for i in range(idx, min(idx + 20, len(lines))):
            if 'targetX = tg.x - side * 100;' in lines[i] and 'ハイポスト' in lines[i-1]:
                # Move closer
                old_line = lines[i]
                new_line = old_line.replace('side * 100', 'side * 70')
                lines[i] = new_line
                print(f"   ✓ High post: 100 → 70 units from goal (line {i+1})")
                break

    # ===== FIX 3: Adjust defense positioning for centers =====
    print("\n3. Adjusting defensive center positioning...")

    # Find defensive positioning section
    idx = find_line(lines, '} else { // C')
    # Find second occurrence (defensive section)
    if idx > 0:
        idx = find_line(lines, '} else { // C', idx + 1)
        if idx > 0:
            for i in range(idx, min(idx + 10, len(lines))):
                if 'idealX = p.team === "PlayerTeam" ? 800 : 200;' in lines[i]:
                    # Closer to goal on defense
                    old_line = lines[i]
                    new_line = old_line.replace('800 : 200', '850 : 150')
                    lines[i] = new_line
                    print(f"   ✓ Defensive center closer to goal (line {i+1})")
                    break

    # ===== FIX 4: Ensure ball follows player during fetch =====
    print("\n4. Ensuring ball position sync during fetch...")

    idx = find_line(lines, 'if(throwInState.phase === "fetching") {')
    if idx > 0:
        # Find where ball position is set
        for i in range(idx, min(idx + 10, len(lines))):
            if 'ball.x = p.x; ball.y = p.y; ball.z = 45;' in lines[i]:
                # This is correct, but let's add a comment
                indent = len(lines[i]) - len(lines[i].lstrip())
                lines[i] = ' ' * indent + '// Ball follows player (even out of bounds)\n' + lines[i]
                print("   ✓ Ball follows player during fetch")
                break

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 70)
    print("FIXES COMPLETE")
    print("=" * 70)
    print("\nFix 1: Out-of-Bounds Ball Fetch")
    print("  Before: Player max x=975, ball at x=995 → UNREACHABLE")
    print("  After:  Player can go to x=1000 during fetch → CAN REACH")
    print("\nFix 2: Center Positioning")
    print("  Before:")
    print("    - Low post: 55 units from goal (too far)")
    print("    - High post: 100 units from goal (3-point line)")
    print("  After:")
    print("    - Low post: 30 units from goal (IN THE PAINT)")
    print("    - High post: 70 units from goal (elbow area)")
    print("\nExpected improvements:")
    print("  ✓ No more freeze on out-of-bounds")
    print("  ✓ Centers play near the basket (realistic)")
    print("  ✓ Better rebounding positioning")
    print("  ✓ Post play opportunities")

if __name__ == "__main__":
    main()
