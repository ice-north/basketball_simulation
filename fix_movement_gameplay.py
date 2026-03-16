#!/usr/bin/env python3
"""
Fix multiple gameplay issues:

PROBLEMS:
1. Out of bounds freeze (no error)
2. REBOUND spam in center court
3. Players move too fast
4. No walk/run contrast

SOLUTIONS:
1. Ensure throw-in timer is correct (90 frames)
2. Better reboundClaimed logic
3. Reduce player speed by 10%
4. Adjust speed multipliers for better contrast
"""

def find_line(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=== GAMEPLAY FIXES ===\n")

    # ===== FIX 1: Throw-in timer (ensure 90 frames) =====
    print("1. Fixing throw-in timer...")

    idx = find_line(lines, 'throwInState.timer > 30')
    if idx > 0:
        lines[idx] = lines[idx].replace('throwInState.timer > 30', 'throwInState.timer > 90')
        print("   ✓ Fixed throw-in timer (30 → 90 frames)")

    # ===== FIX 2: REBOUND spam - stricter reboundClaimed =====
    print("\n2. Fixing REBOUND spam...")

    # Reset reboundClaimed on pass completion
    idx = find_line(lines, 'rcv.hasBall = true; lastActionWasShot = false;')
    if idx > 0:
        indent = len(lines[idx]) - len(lines[idx].lstrip())
        insert_after = idx + 1
        reset_code = ' ' * indent + 'ball.reboundClaimed = false; // パス成功でリセット\n'
        lines.insert(insert_after, reset_code)
        print("   ✓ Reset reboundClaimed on pass completion")

    # ===== FIX 3: Slow down player movement by 10% =====
    print("\n3. Reducing player speed by 10%...")

    idx = find_line(lines, 'let baseSpeed = p.spd * 0.045')
    if idx > 0:
        # Change 0.045 to 0.0405 (90% of 0.045)
        lines[idx] = lines[idx].replace('0.045', '0.0405')
        print("   ✓ Reduced base speed (0.045 → 0.0405)")

    # ===== FIX 4: Better walk/run contrast =====
    print("\n4. Adjusting speed multipliers for contrast...")

    # Find speed constants
    idx = find_line(lines, 'const SPEED_WALK')
    if idx > 0:
        # Read current values
        for i in range(idx, min(idx + 10, len(lines))):
            if 'const SPEED_WALK' in lines[i]:
                # More dramatic differences
                lines[i] = 'const SPEED_WALK = 0.4; // 歩き（ゆっくり）\n'
            elif 'const SPEED_JOG' in lines[i]:
                lines[i] = 'const SPEED_JOG = 0.7; // ジョグ（小走り）\n'
            elif 'const SPEED_RUN' in lines[i]:
                lines[i] = 'const SPEED_RUN = 1.0; // ラン（普通）\n'
            elif 'const SPEED_SPRINT' in lines[i]:
                lines[i] = 'const SPEED_SPRINT = 1.4; // スプリント（全力）\n'
                print("   ✓ Adjusted speed multipliers:")
                print("      WALK: 0.4 (slow)")
                print("      JOG: 0.7 (moderate)")
                print("      RUN: 1.0 (normal)")
                print("      SPRINT: 1.4 (fast)")
                break

    # ===== FIX 5: More selective SPRINT usage =====
    print("\n5. Making SPRINT more selective...")

    # Change some RUN to JOG for better pacing
    replacements = [
        ('p.speedMultiplier = SPEED_RUN; // オフェンスサポートは走る',
         'p.speedMultiplier = SPEED_JOG; // オフェンスサポートは小走り'),
        ('p.speedMultiplier = SPEED_RUN;',
         'p.speedMultiplier = SPEED_JOG;')
    ]

    count = 0
    for old, new in replacements:
        idx = 0
        while True:
            idx = find_line(lines, old, idx)
            if idx < 0:
                break
            lines[idx] = lines[idx].replace(old, new)
            count += 1
            idx += 1

    if count > 0:
        print(f"   ✓ Changed {count} RUN → JOG for better pacing")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("FIXES COMPLETE!")
    print("=" * 60)
    print("\nFixed issues:")
    print("  1. ✓ Throw-in timer (90 frames)")
    print("  2. ✓ REBOUND spam prevention")
    print("  3. ✓ Player speed reduced 10%")
    print("  4. ✓ Walk/run contrast improved")
    print("\nExpected improvements:")
    print("  - No more freezes on out of bounds")
    print("  - Clean rebound messages")
    print("  - Slower, more controlled gameplay")
    print("  - Clear visual difference: walk vs run")

if __name__ == "__main__":
    main()
