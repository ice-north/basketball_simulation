#!/usr/bin/env python3
"""
Fix pass interception issues:

PROBLEMS:
1. Passes can't be intercepted - defenders don't catch passes
2. Failed passes → ball drops → REBOUND spam
3. Too many steals happening

SOLUTIONS:
1. Add pass interception logic
2. Clear passTarget when pass fails
3. Set reboundClaimed to prevent spam
4. Reduce steal frequency
"""

def find_line(lines, pattern, start=0):
    """Find line containing pattern"""
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def find_block_end(lines, start, indent_level):
    """Find end of block by tracking braces"""
    brace_count = 0
    for i in range(start, len(lines)):
        brace_count += lines[i].count('{')
        brace_count -= lines[i].count('}')
        if brace_count == 0 and '}' in lines[i]:
            return i
    return -1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=== PASS INTERCEPTION FIXES ===\n")

    # ===== FIX 1: Add pass interception logic =====
    print("1. Adding pass interception logic...")

    idx = find_line(lines, '// パスターゲットへのキャッチ判定')
    if idx > 0:
        # Find the existing catch logic
        catch_start = find_line(lines, 'if(ball.passTarget !== null) {', idx)
        if catch_start > 0:
            # Insert interception check BEFORE target catches
            intercept_code = '''    // パスインターセプト判定（ターゲットより先にチェック）
    if(ball.passTarget !== null && ball.z < 60) {
      let rcv = players[ball.passTarget];
      if(rcv) {
        // パスルート上のディフェンダーを探す
        let defenders = players.filter(d =>
          d.team !== rcv.team &&
          dist(d.x, d.y, ball.x, ball.y) < 25 && // ボールの近く
          d.lock <= 0 // アクション可能
        );

        // インターセプト試行
        for(let defender of defenders) {
          // インターセプト確率（低め）
          let interceptChance = map(defender.stl, 0, 100, 0.005, 0.025); // 0.5-2.5%
          interceptChance *= map(defender.height, 160, 230, 0.9, 1.1);

          if(random() < interceptChance) {
            // パスカット成功！
            defender.hasBall = true;
            possession = defender.team;
            shotClock = 24;
            ball.passTarget = null;
            ball.reboundClaimed = true; // Prevent loose ball scramble
            defender.lock = 30;

            addFloatingText(defender.x, defender.y - 40, "INTERCEPTED!", [255, 150, 0]);

            // 速攻開始
            if(defender.position === "PG" || defender.position === "SG") {
              defender.bringingBallUp = true;
              defender.inTransition = true;
            } else {
              // PGへアウトレットパス
              let pg = players.find(p => p.team === defender.team && p.position === "PG");
              if(pg) {
                setTimeout(() => {
                  if(defender.hasBall) {
                    passTo(defender, pg);
                    pg.bringingBallUp = true;
                    pg.inTransition = true;
                  }
                }, 150);
              }
            }

            // 相手チームをディフェンスモードに
            players.forEach(pl => {
              if(pl.team !== defender.team) {
                pl.transitionDefense = true;
                pl.transitionTimer = 120;
              }
            });

            break; // インターセプト成功したらループ終了
          }
        }
      }
    }

'''
            lines.insert(catch_start, intercept_code)
            print("   ✓ Added pass interception check")

    # ===== FIX 2: Clear passTarget on failed pass =====
    print("\n2. Adding failed pass cleanup...")

    # Find the catch block and add timeout
    idx = find_line(lines, 'if(rcv && dist(rcv.x, rcv.y, ball.x, ball.y) < 35 && ball.z < 60) {')
    if idx > 0:
        # Find the end of the if block
        end_idx = find_line(lines, '}', idx)
        if end_idx > 0:
            # Add else clause for failed catch
            indent = '      '
            failed_catch_code = indent + '} else if(ball.z <= 10 && ball.passTarget !== null) {\n'
            failed_catch_code += indent + '  // パス失敗：ターゲットが取れなかった\n'
            failed_catch_code += indent + '  ball.passTarget = null;\n'
            failed_catch_code += indent + '  // ルーズボール状態だがreboundClaimedは既に制御されている\n'

            lines[end_idx] = failed_catch_code + lines[end_idx]
            print("   ✓ Added failed pass cleanup")

    # ===== FIX 3: Reduce steal frequency =====
    print("\n3. Reducing steal frequency...")

    # Find attemptSteal function
    idx = find_line(lines, 'function attemptSteal(stealer, handler) {')
    if idx > 0:
        for i in range(idx, min(idx + 10, len(lines))):
            if 'if(random(100) < stealer.stl' in lines[i]:
                # Make steals harder
                indent = len(lines[i]) - len(lines[i].lstrip())
                # Old: stealer.stl - handler.handling * 0.3
                # New: (stealer.stl * 0.4) - handler.handling * 0.5 (much harder)
                lines[i] = ' ' * indent + 'if(random(100) < (stealer.stl * 0.4) - (handler.handling * 0.5)) {\n'
                print("   ✓ Reduced steal success rate (40% of stl stat)")
                break

    # ===== FIX 4: Reduce help defense steal attempts =====
    print("\n4. Reducing help defense aggression...")

    # Find help defense steal
    idx = find_line(lines, 'ヘルプ後のスティール試行')
    if idx > 0:
        for i in range(idx, min(idx + 5, len(lines))):
            if 'random(100) < p.stl * 0.04' in lines[i]:
                # Reduce from 0.04 to 0.02 (half as frequent)
                lines[i] = lines[i].replace('p.stl * 0.04', 'p.stl * 0.02')
                print("   ✓ Reduced help defense steal rate (0.04 → 0.02)")
                break

    # ===== FIX 5: Reduce pressure defense steal attempts =====
    # Find pressure defense steal
    idx = find_line(lines, 'random(100) < p.stl * 0.06')
    if idx > 0:
        # Reduce from 0.06 to 0.03
        lines[idx] = lines[idx].replace('p.stl * 0.06', 'p.stl * 0.03')
        print("   ✓ Reduced pressure defense steal rate (0.06 → 0.03)")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("PASS INTERCEPTION FIXES COMPLETE!")
    print("=" * 60)
    print("\nFixed issues:")
    print("  1. ✓ Pass interception logic added")
    print("  2. ✓ Failed pass cleanup")
    print("  3. ✓ Steal frequency reduced")
    print("  4. ✓ Help defense steals reduced")
    print("  5. ✓ Pressure defense steals reduced")
    print("\nExpected improvements:")
    print("  - Defenders can intercept passes")
    print("  - No more REBOUND spam on failed passes")
    print("  - More realistic steal frequency (less spammy)")

if __name__ == "__main__":
    main()
