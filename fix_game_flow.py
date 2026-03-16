#!/usr/bin/env python3
"""
Fix game flow issues:

PROBLEMS:
1. Defense doesn't return to their zone after opponent scores
2. Ball falls too slowly through net after made shot
3. Throw-in starts too quickly (players not positioned)

SOLUTIONS:
1. Set returningToDefense for scoring team
2. Reduce net slowdown (0.55 → 0.85 for vz)
3. Increase throw-in delay (30 frames → 90 frames)
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

    print("=== GAME FLOW FIXES ===\n")

    # ===== FIX 1: Defense returns after scoring =====
    print("1. Fixing defense return after scoring...")

    idx = find_line(lines, '// ゴール後：新しい守備側は素早く自陣に戻る')
    if idx > 0:
        # Find the forEach block
        for i in range(idx, min(idx + 30, len(lines))):
            if 'setTimeout(() => {' in lines[i]:
                # Insert code before setTimeout to make scoring team return too
                indent = '      '
                insert_code = '''
      // 得点したチームも自陣へ戻る（両チームが位置につく）
      players.forEach(p => {
        if(p.team !== newTeam) {
          // 得点したチーム：自陣のオフェンス位置へ
          p.returningToDefense = true;
          p.transitionTimer = 90; // 守備側と同じ時間
          p.bringingBallUp = false;
          p.isPlaymaker = false;
          p.inTransition = false;
        }
      });

'''
                lines.insert(i, insert_code)
                print("   ✓ Added returningToDefense for scoring team")
                break

    # ===== FIX 2: Faster ball drop through net =====
    print("\n2. Speeding up ball through net...")

    idx = find_line(lines, 'ball.vz *= 0.55; // ネットで減速するが爽快に抜ける')
    if idx > 0:
        # Change from 0.55 (45% slowdown) to 0.85 (15% slowdown)
        lines[idx] = '    ball.vz *= 0.85; // ネット通過：軽い減速のみ（爽快感）\n'
        print("   ✓ Reduced net slowdown (0.55 → 0.85)")
        print("   ✓ Ball now falls faster through net")

    # Also reduce horizontal slowdown for more natural fall
    idx2 = find_line(lines, 'ball.vx *= 0.65; // ネット通過：軽減（爽快感）')
    if idx2 > 0:
        lines[idx2] = '    ball.vx *= 0.75; // ネット通過：軽減（爽快感）\n'
        idx3 = idx2 + 1
        if 'ball.vy *= 0.65;' in lines[idx3]:
            lines[idx3] = '    ball.vy *= 0.75;\n'
        print("   ✓ Adjusted horizontal slowdown (0.65 → 0.75)")

    # ===== FIX 3: Longer throw-in delay =====
    print("\n3. Adding positioning time before throw-in...")

    # Find the throw-in timer check
    idx = find_line(lines, 'throwInState.timer > 30')
    if idx > 0:
        # Change from 30 frames (0.5s) to 90 frames (1.5s)
        lines[idx] = lines[idx].replace('throwInState.timer > 30', 'throwInState.timer > 90')
        print("   ✓ Increased throw-in delay (30 → 90 frames)")
        print("   ✓ Players now have 1.5 seconds to position")

    # ===== FIX 4: Add visual indicator for throw-in preparation =====
    print("\n4. Improving throw-in preparation...")

    # Find updatePlayerAI function and throw-in handling
    idx = find_line(lines, 'if(throwInState.timer > 300)')
    if idx > 0:
        # Add comment about the timeout
        for i in range(idx - 5, idx):
            if 'throwInState.timer++;' in lines[i]:
                insert_after = i + 1
                comment = '      // Timer: 0-90 = positioning, 90-300 = can throw, 300+ = timeout\n'
                lines.insert(insert_after, comment)
                print("   ✓ Added timer explanation comment")
                break

    # ===== FIX 5: Ensure defense positioning completes =====
    print("\n5. Ensuring defense completes positioning...")

    # Find returningToDefense logic
    idx = find_line(lines, 'if(p.returningToDefense) {')
    if idx > 0:
        # Check if there's proper termination
        found_termination = False
        for i in range(idx, min(idx + 50, len(lines))):
            if 'p.returningToDefense = false' in lines[i]:
                found_termination = True
                break

        if not found_termination:
            # Need to add termination logic
            # Find the end of returningToDefense block
            for i in range(idx, min(idx + 40, len(lines))):
                if 'moveToward(p,' in lines[i] and 'returningToDefense' in ''.join(lines[idx:i+1]):
                    # Add distance check after moveToward
                    insert_after = i + 1
                    indent = '    '
                    termination_code = '''
    // 位置についたら完了
    if(dist(p.x, p.y, idealX, idealY) < 20) {
      p.returningToDefense = false;
    }
'''
                    # Check if this code doesn't already exist
                    if 'p.returningToDefense = false' not in ''.join(lines[idx:i+10]):
                        lines.insert(insert_after, termination_code)
                        print("   ✓ Added positioning completion check")
                    break

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("GAME FLOW FIXES COMPLETE!")
    print("=" * 60)
    print("\nFixed issues:")
    print("  1. ✓ Defense returns after opponent scores")
    print("  2. ✓ Ball falls faster through net (0.55 → 0.85)")
    print("  3. ✓ Throw-in delay increased (0.5s → 1.5s)")
    print("  4. ✓ Timer clarification added")
    print("  5. ✓ Positioning completion check")
    print("\nExpected improvements:")
    print("  - Both teams return to positions after score")
    print("  - Quick, satisfying net swish")
    print("  - Proper spacing before throw-in")
    print("  - More realistic game flow")

if __name__ == "__main__":
    main()
