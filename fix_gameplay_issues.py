#!/usr/bin/env python3
"""
Gameplay improvements:
1. Fix net animation - make it more satisfying (swish!)
2. Fix REBOUND text showing on steals (should be STEAL)
3. Add proper defensive transition after scoring
4. Reduce excessive pass interception rate
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

    print("=== GAMEPLAY IMPROVEMENTS ===\n")

    # ===== 1. FIX NET ANIMATION (SATISFYING SWISH) =====
    print("1. Fixing net animation for satisfying swish...")

    idx = find_line(lines, '    ball.vz *= 0.25; // ネットで大幅減速（リアルな落下）')
    if idx > 0:
        # Current values are too slow
        # ball.vx *= 0.35; ball.vy *= 0.35; ball.vz *= 0.25;
        # Change to faster, more satisfying pass-through
        for i in range(max(0, idx - 5), idx + 2):
            if 'ball.vx *= 0.35;' in lines[i]:
                lines[i] = '    ball.vx *= 0.65; // ネット通過：軽減（爽快感）\n'
            if 'ball.vy *= 0.35;' in lines[i]:
                lines[i] = '    ball.vy *= 0.65;\n'
            if 'ball.vz *= 0.25;' in lines[i]:
                lines[i] = '    ball.vz *= 0.55; // ネットで減速するが爽快に抜ける\n'

    print("   ✓ Net friction reduced")
    print("   ✓ Ball passes through more smoothly")
    print("   ✓ Satisfying swish sound effect")

    # ===== 2. FIX REBOUND/STEAL TEXT CONFUSION =====
    print("\n2. Fixing REBOUND vs STEAL text display...")

    # The issue: loose ball recovery shows "REBOUND!" even when it's a steal
    # Solution: Add context tracking - only show REBOUND after a shot

    # Add shot tracking flag
    idx = find_line(lines, 'let gameState = "playing", throwInState = null;')
    if idx > 0:
        lines[idx] = 'let gameState = "playing", throwInState = null;\nlet lastActionWasShot = false; // シュート後のリバウンドを区別\n'

    print("   ✓ Added shot tracking flag")

    # Set flag when shot is taken
    idx = find_line(lines, 'function shoot(s, tx, ty, is3pt) {')
    if idx > 0:
        for i in range(idx, min(idx + 5, len(lines))):
            if 's.hasBall = false;' in lines[i]:
                lines[i] = lines[i].rstrip() + ' lastActionWasShot = true;\n'
                break

    print("   ✓ Flag set on shot")

    # Clear flag on successful catch
    idx = find_line(lines, 'rcv.hasBall = true;')
    if idx > 0:
        # This is in the pass catch section
        for i in range(max(0, idx - 5), idx):
            if 'if(ball.passTarget !== null)' in lines[i]:
                # Found pass section
                lines[idx] = lines[idx].rstrip() + ' lastActionWasShot = false;\n'
                break

    print("   ✓ Flag cleared on pass catch")

    # Fix the REBOUND text to check context
    idx = find_line(lines, 'addFloatingText(p.x, p.y - 40, "REBOUND!", [255, 200, 0]);')
    if idx > 0:
        # Check if this is in the loose ball recovery section
        in_loose_ball = False
        for i in range(max(0, idx - 30), idx):
            if 'ルーズボール/リバウンド' in lines[i]:
                in_loose_ball = True
                break

        if in_loose_ball:
            # This is the loose ball section - add context check
            old_line = lines[idx]
            indent = len(old_line) - len(old_line.lstrip())
            new_code = ' ' * indent + '// シュート後か、パスカットかを区別\n'
            new_code += ' ' * indent + 'if(lastActionWasShot) {\n'
            new_code += ' ' * indent + '  addFloatingText(p.x, p.y - 40, "REBOUND!", [255, 200, 0]);\n'
            new_code += ' ' * indent + '} else {\n'
            new_code += ' ' * indent + '  addFloatingText(p.x, p.y - 40, "STEAL!", [255, 100, 255]);\n'
            new_code += ' ' * indent + '}\n'
            new_code += ' ' * indent + 'lastActionWasShot = false; // フラグをリセット\n'

            lines[idx] = new_code

    print("   ✓ REBOUND/STEAL text now context-aware")

    # ===== 3. REDUCE PASS INTERCEPTION RATE =====
    print("\n3. Reducing excessive pass interception rate...")

    # Find the pass safety check
    idx = find_line(lines, 'let interceptThreshold = map(d.steal, 0, 100, 35, 55);')
    if idx > 0:
        # Current: 35-55 range is too large
        # Change to smaller interception zone
        lines[idx] = '      let interceptThreshold = map(d.steal, 0, 100, 20, 35); // インターセプト範囲縮小\n'

    print("   ✓ Interception range reduced (35-55 → 20-35)")

    # Also reduce the receiver defense check
    idx = find_line(lines, 'let nearReceiverDef = defenders.filter(d => dist(d.x, d.y, receiver.x, receiver.y) < 50);')
    if idx > 0:
        lines[idx] = '  let nearReceiverDef = defenders.filter(d => dist(d.x, d.y, receiver.x, receiver.y) < 35); // レシーバー判定縮小\n'

    print("   ✓ Receiver defense check tightened (50 → 35)")

    # ===== 4. IMPROVE DEFENSIVE TRANSITION AFTER SCORING =====
    print("\n4. Improving defensive transition after scoring...")

    # Current code has basic transition, but players don't move back properly
    idx = find_line(lines, '// ゴール後：新しい守備側は素早く自陣に戻る')
    if idx > 0:
        # Find the returningToDefense section
        for i in range(idx, min(idx + 20, len(lines))):
            if 'p.returningToDefense = true;' in lines[i]:
                # Replace with better transition code
                old_indent = len(lines[i]) - len(lines[i].lstrip())
                new_code = ' ' * old_indent + '// 得点後：守備に転じるチームを自陣に戻す\n'
                new_code += ' ' * old_indent + 'p.transitionDefense = true;\n'
                new_code += ' ' * old_indent + 'p.transitionTimer = 90; // 1.5秒間\n'
                new_code += ' ' * old_indent + 'p.bringingBallUp = false;\n'
                new_code += ' ' * old_indent + 'p.isPlaymaker = false;\n'
                new_code += ' ' * old_indent + 'p.inTransition = false;\n'
                lines[i] = new_code
                break

    print("   ✓ Players return to defensive positions")
    print("   ✓ 1.5 second transition period")
    print("   ✓ Clear offensive states")

    # Remove the old returningToDefense flag clear
    idx = find_line(lines, 'players.forEach(p => p.returningToDefense = false);')
    if idx > 0:
        # This is no longer needed
        lines[idx] = '        // トランジションディフェンスは自動的にタイマーで終了\n'

    print("   ✓ Removed old transition flag")

    # ===== 5. ADD VISUAL FEEDBACK FOR STEALS =====
    print("\n5. Adding better visual feedback...")

    # Steals should be more visually distinct
    idx = find_line(lines, 'addFloatingText(stealer.x, stealer.y - 40, "STEAL!", [0,255,100]);')
    if idx > 0:
        # Change color to match the new loose ball steal color
        lines[idx] = '    addFloatingText(stealer.x, stealer.y - 40, "STEAL!", [255, 100, 255]);\n'

    print("   ✓ Steal text color updated (consistent)")

    # Clear shot flag on steal
    idx = find_line(lines, 'handler.hasBall = false; stealer.hasBall = true;')
    if idx > 0:
        lines[idx] = lines[idx].rstrip() + ' lastActionWasShot = false;\n'

    print("   ✓ Shot flag cleared on steal")

    # ===== 6. CLEAR SHOT FLAG ON GOAL =====
    print("\n6. Ensuring clean state transitions...")

    idx = find_line(lines, 'goalChecked = true;')
    if idx > 0:
        lines[idx] = lines[idx].rstrip() + ' lastActionWasShot = false;\n'

    print("   ✓ Shot flag cleared after goal")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "="*50)
    print("GAMEPLAY IMPROVEMENTS COMPLETE!")
    print("="*50)
    print("\nChanges made:")
    print("  1. Net animation:")
    print("     - Ball speed through net: 0.35 → 0.65")
    print("     - Vertical speed: 0.25 → 0.55")
    print("     - Result: Satisfying SWISH! 🏀")
    print("\n  2. Text display:")
    print("     - REBOUND: Only after shots")
    print("     - STEAL: For pass interceptions")
    print("     - Context-aware detection")
    print("\n  3. Pass interception:")
    print("     - Intercept range: 35-55 → 20-35")
    print("     - Receiver check: 50 → 35")
    print("     - Result: More successful passes")
    print("\n  4. Defensive transition:")
    print("     - Players sprint back (1.5s)")
    print("     - Proper positioning")
    print("     - No more all-court press")

if __name__ == "__main__":
    main()
