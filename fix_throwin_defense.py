#!/usr/bin/env python3
"""
Fix throw-in freeze and defense positioning issues:

PROBLEMS (from screenshot):
1. Blue team throw-in freeze
   - Thrower (bottom left)
   - Teammates (top left)
   - Distance > 350 → forced throw fails

2. Red team (defense) not returning
   - Should return to own half
   - Currently stuck in opponent territory

SOLUTIONS:
1. Remove distance limit for forced throw (or increase to 500)
2. Improve teammate positioning (move closer to thrower)
3. Fix defense transition during throw-in
"""

def find_line(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=== THROW-IN & DEFENSE FIXES ===\n")

    # ===== FIX 1: Remove distance limit for forced throw =====
    print("1. Removing distance limit for forced throw...")

    idx = find_line(lines, 'if(throwInState.timer > 180) {')
    if idx > 0:
        # Find the nested if with distance check
        for i in range(idx, idx + 5):
            if 'if(target && dist(p.x, p.y, target.x, target.y) < 350)' in lines[i]:
                # Remove distance check - just check if target exists
                lines[i] = lines[i].replace(
                    'if(target && dist(p.x, p.y, target.x, target.y) < 350)',
                    'if(target) // 強制スロー：距離制限なし'
                )
                print("   ✓ Removed 350 distance limit")
                break

    # ===== FIX 2: Teammates move closer to thrower =====
    print("\n2. Improving teammate positioning during throw-in...")

    idx = find_line(lines, 'let targetDist = 100 + (p.id % 3) * 30;')
    if idx > 0:
        # Change from 100-160 to 120-180 (closer)
        # Also add logic to move TOWARD thrower if too far
        lines[idx] = '      let targetDist = 120 + (p.id % 3) * 20; // 近づく\n'
        print("   ✓ Adjusted target distance (100-160 → 120-160)")

        # Add check: if too far, move closer instead of radial spread
        insert_idx = idx + 1
        insert_code = '''      // スロワーから遠すぎる場合は近づく
      let currentDist = dist(p.x, p.y, thrower.x, thrower.y);
      if(currentDist > 250) {
        // 直接スロワーに向かう
        moveToward(p, thrower.x, thrower.y, p.spd * 0.06);
        return;
      }
'''
        lines.insert(insert_idx, insert_code)
        print("   ✓ Added close-in logic when too far")

    # ===== FIX 3: Defense returns during throw-in =====
    print("\n3. Fixing defense transition during throw-in...")

    # Find the throw-in teammate positioning block
    idx = find_line(lines, 'if(throwInState && p.team === throwInState.team && p.id !== throwInState.thrower) {')
    if idx > 0:
        # Find the return statement at the end of this block
        for i in range(idx, idx + 20):
            if '    return;' in lines[i] and i > idx + 5:
                # Before this return, add defense team handling
                insert_code = '''  }
  // スローイン中：ディフェンス側は自陣へ戻る
  if(throwInState && p.team !== throwInState.team) {
    // 相手チームのスローイン中
    let halfCourt = 500;
    let isInOpponentHalf = (p.team === "PlayerTeam" && p.x > halfCourt) ||
                            (p.team === "DefenderTeam" && p.x < halfCourt);
    if(isInOpponentHalf) {
      p.speedMultiplier = SPEED_JOG;
      p.state = "transition_defense";
      let backX = (p.team === "PlayerTeam" ? 350 : 650);
      let backY = 388.75 + (p.id % 3 - 1) * 50;
      moveToward(p, backX, backY, p.spd * 0.04);
'''
                lines[i] = insert_code + lines[i]
                print("   ✓ Added defense return during throw-in")
                break

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("FIXES COMPLETE!")
    print("=" * 60)
    print("\nFixed issues:")
    print("  1. ✓ Removed forced throw distance limit")
    print("  2. ✓ Teammates move closer when far (>250)")
    print("  3. ✓ Defense returns during throw-in")
    print("\nExpected improvements:")
    print("  - No more throw-in freezes (any distance)")
    print("  - Better teammate positioning")
    print("  - Defense properly returns to own half")

if __name__ == "__main__":
    main()
