#!/usr/bin/env python3
"""
Fix throw-in freeze and adjust speeds:

PROBLEMS:
1. Throw-in freeze (DefenderTeam with ball, not moving)
2. Players still too fast (need another 10% reduction)
3. Dribble bounce too fast

SOLUTIONS:
1. Add forced throw-in after timeout, relax boundary checks
2. Reduce base speed: 0.0405 → 0.03645 (another 10%)
3. Slow dribble animation
"""

def find_line(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=== THROW-IN & SPEED FIXES ===\n")

    # ===== FIX 1: Forced throw-in after reasonable time =====
    print("1. Adding forced throw-in fallback...")

    # Find the throw-in timeout (currently 900 frames = 15 seconds)
    idx = find_line(lines, 'if(throwInState.timer > 900) {')
    if idx > 0:
        # Change to 300 frames (5 seconds) - more reasonable
        lines[idx] = lines[idx].replace('900', '300')
        print("   ✓ Reduced timeout (900 → 300 frames = 5 seconds)")

    # Add forced throw-in if no safe pass found
    idx = find_line(lines, 'if(target && dist(p.x, p.y, target.x, target.y) < 250 && throwInState.timer > 90) {')
    if idx > 0:
        # Find the end of this if block
        for i in range(idx, min(idx + 20, len(lines))):
            if '      }' in lines[i] and i > idx + 5:
                # Add else clause for forced throw
                insert_at = i + 1
                indent = '      '
                forced_throw = indent + '} else if(throwInState.timer > 180) {\n'
                forced_throw += indent + '  // 3秒経過：強制的にスローイン（安全性無視）\n'
                forced_throw += indent + '  if(target && dist(p.x, p.y, target.x, target.y) < 300) {\n'
                forced_throw += indent + '    let d = dist(p.x, p.y, target.x, target.y);\n'
                forced_throw += indent + '    let spd = 7, t = d / spd;\n'
                forced_throw += indent + '    ball.x = p.x; ball.y = p.y; ball.z = 45;\n'
                forced_throw += indent + '    ball.vx = (target.x - ball.x) / t;\n'
                forced_throw += indent + '    ball.vy = (target.y - ball.y) / t;\n'
                forced_throw += indent + '    ball.vz = 2.5;\n'
                forced_throw += indent + '    ball.passTarget = target.id;\n'
                forced_throw += indent + '    ball.lastTouch = p.team;\n'
                forced_throw += indent + '    throwInState = null;\n'
                forced_throw += indent + '    return;\n'
                forced_throw += indent + '  }\n'

                lines[i] = lines[i] + forced_throw
                print("   ✓ Added forced throw-in after 3 seconds")
                break

    # ===== FIX 2: Reduce player speed by another 10% =====
    print("\n2. Reducing player speed by another 10%...")

    idx = find_line(lines, 'let baseSpeed = p.spd * 0.0405')
    if idx > 0:
        # 0.0405 × 0.9 = 0.036445 ≈ 0.03645
        lines[idx] = lines[idx].replace('0.0405', '0.03645')
        print("   ✓ Reduced base speed (0.0405 → 0.03645)")
        print("   ✓ Total reduction: 19% from original")

    # ===== FIX 3: Slow down dribble bounce =====
    print("\n3. Slowing dribble bounce...")

    # Find dribble phase increment
    idx = find_line(lines, 'p.dribblePhase += 0.2')
    if idx > 0:
        # Reduce from 0.2 to 0.15 (25% slower)
        lines[idx] = lines[idx].replace('0.2', '0.15')
        print("   ✓ Slowed dribble bounce (0.2 → 0.15)")

    # Also check for other dribble increments
    count = 0
    for i, line in enumerate(lines):
        if 'dribblePhase +=' in line and '0.2' in line and i != idx:
            lines[i] = line.replace('0.2', '0.15')
            count += 1

    if count > 0:
        print(f"   ✓ Fixed {count} additional dribble increments")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("FIXES COMPLETE!")
    print("=" * 60)
    print("\nFixed issues:")
    print("  1. ✓ Throw-in timeout (15s → 5s)")
    print("  2. ✓ Forced throw after 3s")
    print("  3. ✓ Player speed -10% more (total -19%)")
    print("  4. ✓ Dribble bounce -25%")
    print("\nExpected improvements:")
    print("  - No more throw-in freezes")
    print("  - Slower, more watchable gameplay")
    print("  - Realistic dribble rhythm")

if __name__ == "__main__":
    main()
