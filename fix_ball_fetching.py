#!/usr/bin/env python3
"""
Fix throw-in freeze and add ball fetching

PROBLEM (from screenshot):
  - RED BALL OUT OF BOUNDS
  - Ball is outside court (top right - orange icon)
  - Thrower goes directly to throw-in spot
  - Ball stays outside
  - FREEZE (no ball to throw)

SOLUTION:
  Add 2-phase throw-in:
    Phase 1: Fetch ball (go to ball location)
    Phase 2: Position (go to throw-in spot with ball)
    Phase 3: Throw (existing code)

USER REQUEST:
  "ゴール後やアウトオブバウンズの際、ボールを拾いに行ってから
   スローイン位置に行くようにしてください"
"""

def find_line(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=== BALL FETCHING FIX ===\n")

    # ===== FIX 1: Add phase to throwInState =====
    print("1. Adding phase system to throw-in...")

    idx = find_line(lines, 'throwInState = { team, x, y, reason, thrower:')
    if idx > 0:
        # Add phase: "fetching" initially
        lines[idx] = lines[idx].replace(
            'throwInState = { team, x, y, reason, thrower:',
            'throwInState = { team, x, y, reason, phase: "fetching", thrower:'
        )
        print("   ✓ Added phase system")

    # ===== FIX 2: Store ball position for fetching =====
    print("\n2. Storing ball position...")

    idx = find_line(lines, 'ball.vx = 0; ball.vy = 0; ball.vz = 0;')
    if idx > 0:
        # Before zeroing velocity, store ball position
        lines[idx] = '  throwInState.ballX = ball.x; throwInState.ballY = ball.y;\n' + lines[idx]
        print("   ✓ Storing ball position for fetching")

    # ===== FIX 3: Implement ball fetching logic =====
    print("\n3. Implementing ball fetching...")

    # Find thrower movement code
    idx = find_line(lines, 'if(throwInState && throwInState.thrower === p.id) {')
    if idx > 0:
        # Find the moveToward line
        for i in range(idx, idx + 10):
            if 'moveToward(p, throwInState.x, throwInState.y, p.spd * 0.06);' in lines[i]:
                # Replace with phase-based logic
                indent = '    '
                new_code = indent + '// フェーズ1: ボールを拾いに行く\n'
                new_code += indent + 'if(throwInState.phase === "fetching") {\n'
                new_code += indent + '  moveToward(p, throwInState.ballX, throwInState.ballY, p.spd * 0.08);\n'
                new_code += indent + '  // ボールを選手と一緒に移動\n'
                new_code += indent + '  ball.x = p.x; ball.y = p.y; ball.z = 45;\n'
                new_code += indent + '  // ボールに到達したらフェーズ2へ\n'
                new_code += indent + '  if(dist(p.x, p.y, throwInState.ballX, throwInState.ballY) < 30) {\n'
                new_code += indent + '    throwInState.phase = "positioning";\n'
                new_code += indent + '    addFloatingText(p.x, p.y - 40, "BALL FETCHED", [100, 255, 100]);\n'
                new_code += indent + '  }\n'
                new_code += indent + '  return;\n'
                new_code += indent + '}\n'
                new_code += indent + '// フェーズ2: スローイン位置へ移動\n'
                new_code += indent + 'if(throwInState.phase === "positioning") {\n'
                new_code += indent + '  moveToward(p, throwInState.x, throwInState.y, p.spd * 0.06);\n'
                new_code += indent + '  // ボールを選手と一緒に移動\n'
                new_code += indent + '  ball.x = p.x; ball.y = p.y; ball.z = 45;\n'
                new_code += indent + '  // スローイン位置に到達したらフェーズ3へ\n'
                new_code += indent + '  if(dist(p.x, p.y, throwInState.x, throwInState.y) < 20) {\n'
                new_code += indent + '    throwInState.phase = "ready";\n'
                new_code += indent + '  }\n'
                new_code += indent + '  return;\n'
                new_code += indent + '}\n'

                lines[i] = new_code
                print("   ✓ Added ball fetching and positioning phases")
                break

    # ===== FIX 4: Update ready phase condition =====
    print("\n4. Updating throw logic for ready phase...")

    idx = find_line(lines, 'if(dist(p.x, p.y, throwInState.x, throwInState.y) < 20) {')
    if idx > 0:
        # Change to check for ready phase
        lines[idx] = lines[idx].replace(
            'if(dist(p.x, p.y, throwInState.x, throwInState.y) < 20) {',
            'if(throwInState.phase === "ready") {'
        )
        print("   ✓ Updated throw condition to use phase")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("FIXES COMPLETE!")
    print("=" * 60)
    print("\nNew throw-in flow:")
    print("  Phase 1: Fetch ball (go to ball location)")
    print("  Phase 2: Position (go to throw-in spot)")
    print("  Phase 3: Ready (throw the ball)")
    print("\nExpected improvements:")
    print("  - No more freeze with ball outside")
    print("  - Realistic ball fetching")
    print("  - Smooth throw-in animation")

if __name__ == "__main__":
    main()
