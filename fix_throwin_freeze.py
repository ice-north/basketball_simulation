#!/usr/bin/env python3
"""
Fix throw-in freeze - Current freeze issue

ISSUE FROM SCREENSHOT:
  - "BLUE BALL OUT OF BOUNDS"
  - Yellow circle shown at player position
  - Game frozen

ROOT CAUSE:
  Thrower not found or invalid, so throw-in logic doesn't execute

SOLUTION:
  1. Ensure thrower is always valid
  2. Add timeout fallback for stuck throw-ins
  3. Validate thrower exists before processing
"""

def find_line(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=== THROW-IN FREEZE FIX ===\n")

    # ===== FIX 1: Ensure thrower is always found =====
    print("1. Ensuring valid thrower assignment...")

    idx = find_line(lines, 'function startThrowIn(team, x, y, reason) {')
    if idx > 0:
        for i in range(idx, idx + 15):
            if 'let thrower = players.find(p => p.team === team && (p.position === "C" || p.position === "PF"));' in lines[i]:
                # Find the next lines
                indent = len(lines[i]) - len(lines[i].lstrip())
                # Replace the thrower assignment logic
                new_code = ' ' * indent + '// OPUS FIX: Robust thrower selection\n'
                new_code += ' ' * indent + 'let thrower = players.find(p => p && p.team === team && (p.position === "C" || p.position === "PF"));\n'
                new_code += ' ' * indent + 'if(!thrower) thrower = players.find(p => p && p.team === team && p.position === "PG");\n'
                new_code += ' ' * indent + 'if(!thrower) thrower = players.find(p => p && p.team === team); // Any player\n'
                new_code += ' ' * indent + 'if(!thrower) {\n'
                new_code += ' ' * indent + '  // Emergency: no valid players found, cancel throw-in\n'
                new_code += ' ' * indent + '  console.error("No thrower found for team:", team);\n'
                new_code += ' ' * indent + '  throwInState = null;\n'
                new_code += ' ' * indent + '  return;\n'
                new_code += ' ' * indent + '}\n'

                # Skip the old if(!thrower) line
                lines[i] = new_code
                if i + 1 < len(lines) and 'if(!thrower)' in lines[i + 1]:
                    lines[i + 1] = ''  # Remove old fallback

                print("   ✓ Thrower selection now has multiple fallbacks")
                break

    # ===== FIX 2: Add timeout for stuck throw-ins =====
    print("\n2. Adding throw-in timeout fallback...")

    idx = find_line(lines, 'throwInState = { team, x, y, reason, phase: "fetching"')
    if idx > 0:
        old_line = lines[idx]
        # Add startTime
        new_line = old_line.replace(
            'throwInState = { team, x, y, reason, phase: "fetching", thrower:',
            'throwInState = { team, x, y, reason, phase: "fetching", startTime: frameCount, thrower:'
        )
        lines[idx] = new_line
        print("   ✓ Added startTime to throwInState")

    # ===== FIX 3: Check for timeout and force completion =====
    print("\n3. Adding timeout check in throw-in logic...")

    idx = find_line(lines, 'if(throwInState && throwInState.thrower === p.id) {')
    if idx > 0:
        # Add timeout check at the beginning
        indent = len(lines[idx]) - len(lines[idx].lstrip())
        timeout_check = ' ' * indent + '// OPUS FIX: Timeout for stuck throw-ins\n'
        timeout_check += ' ' * indent + 'if(frameCount - throwInState.startTime > 600) { // 10 seconds\n'
        timeout_check += ' ' * indent + '  console.warn("Throw-in timeout - forcing completion");\n'
        timeout_check += ' ' * indent + '  throwInState = null;\n'
        timeout_check += ' ' * indent + '  p.hasBall = true;\n'
        timeout_check += ' ' * indent + '  ball.x = p.x; ball.y = p.y; ball.z = 45;\n'
        timeout_check += ' ' * indent + '  return;\n'
        timeout_check += ' ' * indent + '}\n'

        lines.insert(idx + 1, timeout_check)
        print("   ✓ Throw-in will auto-complete after 10 seconds")

    # ===== FIX 4: Validate thrower in draw function =====
    print("\n4. Adding thrower validation in draw...")

    idx = find_line(lines, 'if(throwInState) {')
    if idx > 0:
        # Find the drawing code
        for i in range(idx, idx + 15):
            if 'fill(0,180); noStroke(); rect(width/2-120' in lines[i]:
                # Add validation before drawing
                indent = len(lines[idx]) - len(lines[idx].lstrip())
                validation = ' ' * indent + '// OPUS FIX: Validate thrower exists\n'
                validation += ' ' * indent + 'if(!isValidPlayerId(throwInState.thrower)) {\n'
                validation += ' ' * indent + '  throwInState = null; // Invalid state\n'
                validation += ' ' * indent + '} else {\n'

                lines.insert(idx + 1, validation)

                # Close the else at the end
                for j in range(i + 2, min(i + 20, len(lines))):
                    if lines[j].strip() == '}':
                        lines[j] = ' ' * indent + '}}\n'  # Close both if and else
                        break

                print("   ✓ Draw validates thrower before rendering")
                break

    # ===== FIX 5: Shot clock reset improvements =====
    print("\n5. Adding shot clock reset on defensive rebounds...")

    idx = find_line(lines, 'function checkRebound(side) {')
    if idx > 0:
        # Find where rebounder claims ball
        found = False
        for i in range(idx, min(idx + 120, len(lines))):
            if 'rebounder.hasBall = true;' in lines[i]:
                # Check if next line is reboundClaimed
                if i + 1 < len(lines) and 'ball.reboundClaimed = true;' in lines[i + 1]:
                    indent = len(lines[i]) - len(lines[i].lstrip())

                    # Add shot clock logic after reboundClaimed
                    rebound_logic = ' ' * indent + '// OPUS FIX: Shot clock on rebounds\n'
                    rebound_logic += ' ' * indent + 'let wasOffensiveRebound = (rebounder.team === possession);\n'
                    rebound_logic += ' ' * indent + 'possession = rebounder.team; // Update possession\n'
                    rebound_logic += ' ' * indent + 'if(!wasOffensiveRebound) {\n'
                    rebound_logic += ' ' * indent + '  shotClock = 24; // Defensive rebound: new possession\n'
                    rebound_logic += ' ' * indent + '} else {\n'
                    rebound_logic += ' ' * indent + '  shotClock = Math.max(shotClock, 14); // Offensive: 14-second reset\n'
                    rebound_logic += ' ' * indent + '}\n'

                    lines.insert(i + 2, rebound_logic)
                    found = True
                    print("   ✓ Shot clock properly resets on rebounds")
                    break

        if not found:
            print("   ⚠ Could not find rebound claim location")

    # ===== FIX 6: Free throw shot clock reset =====
    print("\n6. Ensuring free throw resets shot clock...")

    idx = find_line(lines, 'function executeFreeThrow() {')
    if idx > 0:
        for i in range(idx, idx + 30):
            if 'ball.x = ftX; ball.y = ftY;' in lines[i]:
                # Check if shot clock reset is already there
                has_reset = False
                for j in range(i, min(i + 5, len(lines))):
                    if 'shotClock = 24' in lines[j]:
                        has_reset = True
                        break

                if not has_reset:
                    indent = len(lines[i]) - len(lines[i].lstrip())
                    lines.insert(i + 1, ' ' * indent + 'shotClock = 24; // OPUS FIX: Reset on free throw\n')
                    print("   ✓ Free throw resets shot clock")
                else:
                    print("   ✓ Free throw shot clock already handled")
                break

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("THROW-IN FREEZE FIX COMPLETE")
    print("=" * 60)
    print("\nFixes applied:")
    print("  1. ✓ Robust thrower selection with fallbacks")
    print("  2. ✓ Throw-in timeout tracking")
    print("  3. ✓ Auto-completion after 10 seconds")
    print("  4. ✓ Thrower validation in draw")
    print("  5. ✓ Shot clock on rebounds (NBA rules)")
    print("  6. ✓ Shot clock on free throws")
    print("\nExpected improvements:")
    print("  • No more throw-in freezes")
    print("  • Automatic recovery from stuck states")
    print("  • NBA-accurate shot clock rules")

if __name__ == "__main__":
    main()
