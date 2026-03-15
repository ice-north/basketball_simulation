#!/usr/bin/env python3
"""
Intense Rebound Battle System:
1. Increase upward bounce on missed shots
2. Players jump for rebounds
3. Height + Jump power calculations
4. Power-based box-out positioning battles
5. Multi-player rebound contests
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

    print("=== INTENSE REBOUND SYSTEM ===\n")

    # ===== 1. INCREASE BOUNCE ON MISSED SHOTS =====
    print("1. Enhancing miss physics - more upward bounces...")

    # Find the ball physics update section
    idx = find_line(lines, '// ボール物理更新')
    if idx < 0:
        idx = find_line(lines, 'function updateBall() {')

    if idx > 0:
        # Find rim collision section
        for i in range(idx, min(idx + 200, len(lines))):
            if 'if(dist(ball.x, ball.y, rx, ry) < ringSize' in lines[i]:
                # Find the bounce handling
                for j in range(i, min(i + 30, len(lines))):
                    if 'ball.vz = abs(ball.vz) * BOUNCE_FACTOR;' in lines[j]:
                        # Replace with enhanced bounce logic
                        lines[j] = '''        // リバウンド強化：上向きバウンス確率UP
        if(random() < 0.7) { // 70%の確率で上向きバウンス
          ball.vz = abs(ball.vz) * BOUNCE_FACTOR * 1.3; // より高く跳ねる
        } else {
          ball.vz = abs(ball.vz) * BOUNCE_FACTOR * 0.6; // たまに低いバウンス
        }
        // 横方向にも不規則にバウンド
        ball.vx += random(-2, 2);
        ball.vy += random(-2, 2);
'''
                        break
                break
    print("   ✓ 70% chance for high upward bounce")
    print("   ✓ Irregular horizontal bounce added")

    # ===== 2. ADD REBOUND JUMP STATE =====
    print("\n2. Adding rebound jump mechanics...")

    # Find player initialization
    idx = find_line(lines, 'function initPlayers() {')
    if idx > 0:
        for i in range(idx, min(idx + 50, len(lines))):
            if 'isJumping: false,' in lines[i]:
                # Add rebound-specific states
                insert_idx = i + 1
                lines.insert(insert_idx, '''      reboundJumping: false, // リバウンドジャンプ中
      reboundJumpTimer: 0,
      boxOutStrength: 0, // ボックスアウトの強さ
''')
                break
    print("   ✓ Rebound jumping state added")
    print("   ✓ Box-out strength tracking added")

    # ===== 3. ENHANCE BOX-OUT WITH POWER STRUGGLE =====
    print("\n3. Implementing power-based box-out battles...")

    # Find the box-out execution section
    idx = find_line(lines, '// ボックスアウト実行中（シュート後のリバウンド）')
    if idx > 0:
        # Replace the existing box-out logic
        for i in range(idx, min(idx + 30, len(lines))):
            if 'if(p.isBoxingOut && p.boxOutTarget !== null) {' in lines[i]:
                # Find the end of this if block
                block_end = i
                brace_count = 0
                for j in range(i, min(i + 50, len(lines))):
                    if '{' in lines[j]:
                        brace_count += lines[j].count('{')
                    if '}' in lines[j]:
                        brace_count -= lines[j].count('}')
                    if brace_count == 0:
                        block_end = j
                        break

                # Replace the entire block
                new_boxout = '''      // ボックスアウト実行中（シュート後のリバウンド）- パワー勝負
      if(p.isBoxingOut && p.boxOutTarget !== null) {
        let boxTarget = players[p.boxOutTarget];
        if(boxTarget && ball.z > 30) {
          p.speedMultiplier = SPEED_WALK;
          // 相手とゴールの間に入る
          let tg = p.team === "PlayerTeam" ? {x:finalGoal.ringX, y:finalGoal.ringY} : {x:1000-finalGoal.ringX, y:finalGoal.ringY};
          let ang = atan2(tg.y - boxTarget.y, tg.x - boxTarget.x);
          let boxX = boxTarget.x + cos(ang) * 25;
          let boxY = boxTarget.y + sin(ang) * 25;

          // パワー勝負：強い方が有利なポジションを取る
          let myPower = p.power + p.rebound * 0.5;
          let theirPower = boxTarget.power + boxTarget.rebound * 0.5;
          let powerDiff = (myPower - theirPower) / 100;

          // パワーが高い方が押し勝つ
          if(powerDiff > 0) {
            // 自分が強い：理想位置へ
            p.boxOutStrength = powerDiff * 15;
            moveToward(p, boxX, boxY, speed * 0.8);
            // 相手を押し出す
            let pushAngle = atan2(boxTarget.y - p.y, boxTarget.x - p.x);
            boxTarget.x += cos(pushAngle) * powerDiff * 2;
            boxTarget.y += sin(pushAngle) * powerDiff * 2;
          } else {
            // 相手が強い：押される
            p.boxOutStrength = 0;
            moveToward(p, boxX, boxY, speed * 0.5);
            let pushAngle = atan2(p.y - boxTarget.y, p.x - boxTarget.x);
            p.x += cos(pushAngle) * abs(powerDiff) * 1.5;
            p.y += sin(pushAngle) * abs(powerDiff) * 1.5;
          }

          return;
        } else if(ball.z < 20) {
          p.isBoxingOut = false;
          p.boxOutTarget = null;
        }
      }

'''
                # Replace lines
                for k in range(i, block_end + 1):
                    lines[i] = ''
                lines[i] = new_boxout
                for k in range(i + 1, block_end + 1):
                    if k < len(lines):
                        lines[k] = ''
                break
    print("   ✓ Power-based positioning battles")
    print("   ✓ Stronger players push opponents away")

    # ===== 4. ENHANCED REBOUND COMPETITION =====
    print("\n4. Creating intense multi-player rebound battles...")

    # Find the loose ball/rebound section
    idx = find_line(lines, '} else if(ball.z < 80 && !players.some(pl=>pl.hasBall)) {')
    if idx > 0:
        # Find the rebound chance calculation
        for i in range(idx, min(idx + 40, len(lines))):
            if 'if(dist(p.x,p.y,ball.x,ball.y) < 30 && ball.z < 40 && p.lock <= 0) {' in lines[i]:
                # Find the closing brace of this block
                block_end = i
                brace_count = 0
                for j in range(i, min(i + 30, len(lines))):
                    if '{' in lines[j]:
                        brace_count += lines[j].count('{')
                    if '}' in lines[j]:
                        brace_count -= lines[j].count('}')
                    if brace_count == 0:
                        block_end = j
                        break

                # Replace with enhanced rebound battle
                new_rebound = '''        if(dist(p.x,p.y,ball.x,ball.y) < 35 && ball.z < 60 && p.lock <= 0) {
          // リバウンドジャンプ開始
          if(!p.reboundJumping && ball.z > 25) {
            p.reboundJumping = true;
            p.reboundJumpTimer = 30;
            p.z = 0;
          }

          // ジャンプ中
          if(p.reboundJumping && p.reboundJumpTimer > 0) {
            p.reboundJumpTimer--;
            // ジャンプモーション（ジャンプ力に応じた高さ）
            let jumpHeight = map(p.jmp, 0, 100, 15, 35);
            p.z = sin((30 - p.reboundJumpTimer) / 30 * PI) * jumpHeight;
          }

          // ボールをキャッチできる位置にいるか
          let verticalReach = p.z + map(p.height, 160, 230, 0, 20);
          let ballHeight = ball.z;

          if(abs(verticalReach - ballHeight) < 25 && dist(p.x, p.y, ball.x, ball.y) < 30) {
            // リバウンド獲得判定：複数要素を考慮
            let reboundChance = map(p.rebound, 0, 100, 0.25, 0.75);

            // 身長ボーナス（高い選手ほど有利）
            reboundChance *= map(p.height, 160, 230, 0.7, 1.4);

            // ジャンプ力ボーナス（跳躍力が高いほど有利）
            reboundChance *= map(p.jmp, 0, 100, 0.8, 1.3);

            // パワーボーナス（場所取りの有利さ）
            reboundChance *= map(p.power, 0, 100, 0.85, 1.2);

            // ボックスアウト強度ボーナス
            reboundChance *= (1 + p.boxOutStrength * 0.05);

            // 近くの競合者がいると難易度UP
            let nearbyContestants = players.filter(pl =>
              pl.id !== p.id &&
              dist(pl.x, pl.y, ball.x, ball.y) < 35
            ).length;
            reboundChance *= map(nearbyContestants, 0, 4, 1.0, 0.4);

            if(random() < reboundChance) {
              p.hasBall = true;
              possession = p.team;
              shotClock = 24;
              p.reboundJumping = false;
              p.z = 0;
              addFloatingText(p.x, p.y - 40, "REBOUND!", [255, 200, 0]);

              // リバウンド後、他の選手のジャンプ停止
              players.forEach(pl => {
                if(pl.id !== p.id) {
                  pl.reboundJumping = false;
                  pl.reboundJumpTimer = 0;
                }
              });
            }
          }

          // ジャンプ終了
          if(p.reboundJumpTimer <= 0 && p.reboundJumping) {
            p.reboundJumping = false;
            p.z = 0;
          }
        }
'''
                # Replace
                for k in range(i, block_end + 1):
                    lines[i] = ''
                lines[i] = new_rebound
                for k in range(i + 1, block_end + 1):
                    if k < len(lines):
                        lines[k] = ''
                break
    print("   ✓ Multi-player jump contests")
    print("   ✓ Height + Jump + Power + Rebound skill")
    print("   ✓ Nearby contestants reduce success rate")
    print("   ✓ Jumping animation added")

    # ===== 5. ENSURE REBOUND POSITIONING IS CALLED =====
    print("\n5. Ensuring aggressive rebound positioning...")

    # Find positionForRebound function
    idx = find_line(lines, 'function positionForRebound(p) {')
    if idx > 0:
        # Make positioning more aggressive
        for i in range(idx, min(idx + 50, len(lines))):
            if 'let reboundX, reboundY;' in lines[i]:
                # Find the calculation section
                for j in range(i, min(i + 30, len(lines))):
                    if 'reboundX = predictedX +' in lines[j]:
                        # Make positioning tighter to the basket
                        lines[j] = lines[j].replace('random(-50, 50)', 'random(-35, 35)')
                    if 'reboundY = predictedY +' in lines[j]:
                        lines[j] = lines[j].replace('random(-50, 50)', 'random(-35, 35)')
    print("   ✓ Tighter positioning around basket")

    # Clean up empty lines
    lines = [line for line in lines if line.strip() or line == '\n']

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "="*50)
    print("INTENSE REBOUND SYSTEM IMPLEMENTED!")
    print("="*50)
    print("\nKey Features:")
    print("  • 70% high bounce probability")
    print("  • Power-based box-out battles")
    print("  • Height + Jump + Power calculations")
    print("  • Multi-player jumping contests")
    print("  • Realistic positioning battles")

if __name__ == "__main__":
    main()
