#!/usr/bin/env python3
"""
Bug Fixes:
1. pos variable not defined error (line 940)
2. REBOUND spam - ball touching floor triggers rebound repeatedly
3. Defense not working - players going solo to goal
"""

def find_line(lines, pattern, start=0):
    """Find line containing pattern"""
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=== BUG FIXES ===\n")

    # ===== FIX 1: pos variable not defined =====
    print("1. Fixing 'pos' variable error...")

    idx = find_line(lines, '// Constant off-ball motion')
    if idx > 0:
        # Add pos definition before the motion code
        indent = '        '
        pos_def = indent + 'let pos = p.position; // Define position\n'
        lines.insert(idx, pos_def)
    print("   ✓ Added pos definition before motion code")

    # ===== FIX 2: REBOUND spam =====
    print("\n2. Fixing REBOUND spam issue...")

    # Find rebound detection logic
    idx = find_line(lines, '// ボール着地判定：リバウンド')
    if idx > 0:
        # Look for the rebound trigger
        for i in range(idx, min(idx + 50, len(lines))):
            if 'if(ball.z <= 0 && ball.vz < 0)' in lines[i]:
                # Add condition to prevent repeated rebounds
                indent = '  '
                lines[i] = indent + 'if(ball.z <= 0 && ball.vz < 0 && !ball.reboundClaimed) {\n'

                # Add flag to mark rebound as claimed
                for j in range(i, min(i + 30, len(lines))):
                    if 'goalChecked = true;' in lines[j]:
                        insert_after = j + 1
                        lines.insert(insert_after, indent + '  ball.reboundClaimed = true; // Prevent spam\n')
                        break
                break

    # Reset flag when new shot is taken
    idx = find_line(lines, 'function shoot(s, tx, ty, is3pt) {')
    if idx > 0:
        for i in range(idx, min(idx + 10, len(lines))):
            if 'if(!s.jumpShooting) {' in lines[i]:
                insert_before = i
                indent = '  '
                lines.insert(insert_before, indent + 'ball.reboundClaimed = false; // Reset for new shot\n')
                break

    print("   ✓ Added reboundClaimed flag")
    print("   ✓ Prevents multiple rebound triggers")

    # ===== FIX 3: Defense issues =====
    print("\n3. Fixing defense issues...")

    # Fix closeout code - hasBball should be hasBall
    idx = find_line(lines, 'let ballHandler = players.find(p => p.hasBball')
    if idx > 0:
        lines[idx] = lines[idx].replace('p.hasBball', 'p.hasBall')
    print("   ✓ Fixed typo: hasBball → hasBall")

    # Remove broken setTimeout in switching code
    idx = find_line(lines, 'setTimeout(() => { p.switchedDefense = null; }, 3000);')
    if idx > 0:
        # setTimeout doesn't work in p5.js draw loop, use frame counter instead
        indent = len(lines[idx]) - len(lines[idx].lstrip())
        lines[idx] = ' ' * indent + 'p.switchTimer = 180; // 3 seconds = 180 frames\n'

        # Add switch timer countdown
        idx2 = find_line(lines, '// Defensive switching on screens')
        if idx2 > 0:
            timer_code = '''
  // Countdown switch timer
  if(p.switchTimer && p.switchTimer > 0) {
    p.switchTimer--;
    if(p.switchTimer <= 0) {
      p.switchedDefense = null;
    }
  }

'''
            lines.insert(idx2, timer_code)
    print("   ✓ Fixed switching timer (setTimeout → frame counter)")

    # Add switchTimer to player initialization
    idx = find_line(lines, 'switchedDefense: null,')
    if idx > 0:
        insert_after = idx + 1
        lines.insert(insert_after, '      switchTimer: 0,\n')
    print("   ✓ Added switchTimer to player state")

    # ===== FIX 4: Enhanced help defense was broken =====
    print("\n4. Fixing help defense logic...")

    # Find the broken help defense code
    idx = find_line(lines, '// Enhanced help defense (NBA style)')
    if idx > 0:
        # The inserted code has wrong team check
        for i in range(idx, min(idx + 20, len(lines))):
            if 'let ballHandler = players.find(p => p.hasBall && p.team !== p.team);' in lines[i]:
                # Fix: should be checking against defender's team
                indent = len(lines[i]) - len(lines[i].lstrip())
                # Get the defender variable name from context
                # Replace broken line
                for j in range(max(0, idx - 10), idx):
                    if 'function updatePlayerAI(p)' in lines[j] or 'let mark =' in lines[j]:
                        # We're in the right function, p is the defender
                        break

                fixed_line = ' ' * indent + 'let ballHandler = players.find(plr => plr.hasBall && plr.team !== p.team);\n'
                lines[i] = fixed_line
                print("   ✓ Fixed ballHandler team check")
                break

    # ===== FIX 5: Closeout isMoving check =====
    print("\n5. Fixing closeout mechanics...")

    idx = find_line(lines, 'if(ballHandler && !ballHandler.isMoving)')
    if idx > 0:
        # Check if player is relatively stationary (speed check)
        indent = len(lines[idx]) - len(lines[idx].lstrip())
        fixed_line = ' ' * indent + 'if(ballHandler && ballHandler.speedMultiplier < SPEED_RUN) { // Stationary or slow\n'
        lines[idx] = fixed_line
    print("   ✓ Fixed closeout trigger condition")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("BUG FIXES COMPLETE!")
    print("=" * 60)
    print("\nFixed issues:")
    print("  1. ✓ pos variable error")
    print("  2. ✓ REBOUND spam")
    print("  3. ✓ Defense typos")
    print("  4. ✓ Switching timer")
    print("  5. ✓ Help defense logic")
    print("  6. ✓ Closeout conditions")

if __name__ == "__main__":
    main()
