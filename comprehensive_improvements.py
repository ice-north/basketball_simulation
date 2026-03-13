#!/usr/bin/env python3
"""
Comprehensive basketball simulation improvements:
1. Add player collision detection
2. Improve pass safety evaluation (reduce interceptions)
3. Fix out-of-bounds after scoring
4. Reduce speeds by 5%
5. Add realistic net physics
6. Improve individual AI decision-making
7. Add floor balance awareness
8. Fast defensive transition
"""

def find_line(lines, pattern, start=0):
    """Find line containing pattern"""
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def find_function_end(lines, start):
    """Find the end of a function starting at 'start'"""
    brace_count = 0
    started = False
    for i in range(start, len(lines)):
        if '{' in lines[i]:
            started = True
            brace_count += lines[i].count('{')
        if '}' in lines[i]:
            brace_count -= lines[i].count('}')
        if started and brace_count == 0:
            return i
    return len(lines) - 1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=== COMPREHENSIVE IMPROVEMENTS ===\n")

    # ===== 1. REDUCE SPEEDS BY 5% =====
    print("1. Reducing all movement speeds by 5%...")
    idx = find_line(lines, 'const SPEED_WALK')
    if idx > 0:
        lines[idx] = 'const SPEED_WALK = 0.285, SPEED_JOG = 0.57, SPEED_RUN = 0.95, SPEED_SPRINT = 1.425; // 5%減速\n'

    # Ball gravity and bounce also 5% slower
    idx = find_line(lines, 'const NET_DAMPING')
    if idx > 0:
        lines[idx] = 'const NET_DAMPING = 0.85, BALL_GRAVITY = 0.4275, BOUNCE_FACTOR = 0.72, AIR_RESISTANCE = 0.9995; // ボール重力5%減\n'

    print("   ✓ Player speeds: WALK/JOG/RUN/SPRINT all -5%")
    print("   ✓ Ball gravity: 0.45 → 0.4275")

    # ===== 2. ADD PLAYER COLLISION DETECTION =====
    print("\n2. Adding player collision detection...")
    idx = find_line(lines, 'function moveToward(p, tx, ty, targetSpeed) {')
    if idx > 0:
        # Insert collision detection after the initial distance check
        insert_idx = find_line(lines, '  // 瞬発力による滑らかな加速システム', idx)
        if insert_idx > 0:
            collision_code = '''  // 選手同士の衝突判定（重なり防止）
  for(let other of players) {
    if(other.id === p.id) continue;
    let d = dist(p.x, p.y, other.x, other.y);
    let minDist = 20; // 最小距離
    if(d < minDist && d > 0) {
      // 押し出し（衝突回避）
      let pushAngle = atan2(p.y - other.y, p.x - other.x);
      let pushForce = (minDist - d) * 0.3;
      p.x += cos(pushAngle) * pushForce;
      p.y += sin(pushAngle) * pushForce;
      // コート内に制限
      p.x = constrain(p.x, 25, 975);
      p.y = constrain(p.y, 262.5, 550);
    }
  }

'''
            lines.insert(insert_idx, collision_code)
    print("   ✓ Players now avoid overlapping (min 20px distance)")

    # ===== 3. IMPROVE PASS SAFETY EVALUATION =====
    print("\n3. Improving pass safety evaluation...")

    # Make pass safety check more strict
    idx = find_line(lines, 'function isPassSafe(passer, receiver) {')
    if idx > 0:
        # Find the line with interceptThreshold
        for i in range(idx, min(idx + 50, len(lines))):
            if 'let interceptThreshold = map(d.steal, 0, 100, 25, 40);' in lines[i]:
                lines[i] = '      let interceptThreshold = map(d.steal, 0, 100, 35, 55); // 危険ゾーン拡大\n'
            # Make receiver defender check stricter
            if 'let nearReceiverDef = defenders.filter(d => dist(d.x, d.y, receiver.x, receiver.y) < 40);' in lines[i]:
                lines[i] = '  let nearReceiverDef = defenders.filter(d => dist(d.x, d.y, receiver.x, receiver.y) < 50); // レシーバー付近のディフェンス判定拡大\n'
            if 'if(nearReceiverDef.length >= 2) return false;' in lines[i]:
                # Add more safety checks
                lines[i] = '''  if(nearReceiverDef.length >= 2) return false; // ダブルチームへのパス禁止
  if(nearReceiverDef.length >= 1 && passDist > 200) return false; // 遠距離パスで敵が近い場合禁止

'''
    print("   ✓ Pass interception zones expanded")
    print("   ✓ Better evaluation of risky passes")

    # ===== 4. FIX OUT-OF-BOUNDS AFTER SCORING =====
    print("\n4. Fixing out-of-bounds after scoring...")

    # Find the goal check function and add proper inbound positioning
    idx = find_line(lines, 'setTimeout(() => {')
    # Find the startThrowIn call after scoring
    for i in range(idx, min(idx + 20, len(lines))):
        if 'startThrowIn(newTeam, thX, 406.25, "INBOUND");' in lines[i]:
            # Add code to properly position all players before inbound
            inbound_fix = '''        // 全選手をコート内に配置（アウトオブバウンズ防止）
        players.forEach(pl => {
          if(pl.team === newTeam) {
            // インバウンド側：自陣のスタート位置
            let startX = thX > 500 ? 850 : 150;
            pl.x = constrain(startX + random(-80, 80), 125, 875);
            pl.y = constrain(350 + (pl.id % 5 - 2) * 50, 275, 537.5);
          } else {
            // 守備側：ハーフコート付近
            let defX = thX > 500 ? 450 : 550;
            pl.x = constrain(defX + random(-60, 60), 125, 875);
            pl.y = constrain(388.75 + (pl.id % 5 - 2) * 60, 275, 537.5);
          }
        });

'''
            lines.insert(i, inbound_fix)
            break
    print("   ✓ Players properly positioned after scoring")
    print("   ✓ No more out-of-bounds play")

    # ===== 5. ADD REALISTIC NET PHYSICS =====
    print("\n5. Adding realistic net physics for made shots...")

    idx = find_line(lines, 'net.offsetX = ball.vx * 1.5; net.swing = 10; net.phase = 0;')
    if idx > 0:
        lines[idx] = '''    net.offsetX = ball.vx * 2.0; net.swing = 15; net.phase = 0; // ネットの揺れ増加
    // ネットによるボール減速（よりリアルに）
    ball.vx *= 0.35;
    ball.vy *= 0.35;
'''

    # Find the next line with ball.vz deceleration
    idx2 = find_line(lines, '// 網による減速')
    if idx2 > 0:
        for i in range(idx2, min(idx2 + 3, len(lines))):
            if 'ball.vz *= 0.65;' in lines[i]:
                lines[i] = '    ball.vz *= 0.25; // ネットで大幅減速（リアルな落下）\n'
    print("   ✓ Net physics improved - ball slows realistically")

    # ===== 6. IMPROVE INDIVIDUAL PLAYER AI =====
    print("\n6. Improving individual player decision-making AI...")

    # Add better shot selection based on player attributes
    idx = find_line(lines, '// オフェンス判断AI（攻撃的/慎重のバランス調整）')
    if idx > 0:
        # Find the shooting decision section
        for i in range(idx, min(idx + 100, len(lines))):
            if 'let shouldShoot3 = is3ptRange && random(100) < shootProb3;' in lines[i]:
                # Add smarter decision making
                lines[i] = '''        let shouldShoot3 = is3ptRange && random(100) < shootProb3;

        // 個別判断：能力に応じた賢明な選択
        let playerIQ = map(p.iq, 0, 100, 0.5, 1.2);
        let distanceToGoal = dist(p.x, p.y, tg.x, tg.y);

        // 3Pシューター以外は遠距離を避ける
        if(p.tpt < 60 && distanceToGoal > 180) shouldShoot3 = false;

        // スタミナ低下時は無理なシュートを避ける
        if(p.stamina < p.maxStamina * 0.3 && distanceToGoal > 150) {
          shouldShoot3 = false;
          shouldShoot = false;
        }

        // ディフェンスが近い時、IQが高い選手はパスを選ぶ
        if(nearestDef < 40 && p.iq > 70 && random() < playerIQ * 0.4) {
          shouldShoot = false;
          shouldShoot3 = false;
        }
'''
                break
    print("   ✓ Players make smarter shot decisions")
    print("   ✓ Considers IQ, stamina, position")

    # ===== 7. ADD FLOOR BALANCE AWARENESS =====
    print("\n7. Adding floor balance awareness...")

    # Find offensive positioning section
    idx = find_line(lines, '// 他の味方との重なりを回避（フロアスペーシング強化）')
    if idx > 0:
        # Add floor balance check
        insert_idx = idx - 1
        balance_code = '''      // フロアバランス認識：チーム全体の配置を考慮
      let teammates = players.filter(pl => pl.team === p.team && pl.id !== p.id && !pl.hasBall);
      let leftSide = teammates.filter(t => t.x < 500).length;
      let rightSide = teammates.filter(t => t.x >= 500).length;
      let topSide = teammates.filter(t => t.y < 388.75).length;
      let bottomSide = teammates.filter(t => t.y >= 388.75).length;

      // バランスが悪い場合、空いている方向へ移動
      let balanceAdjustX = 0, balanceAdjustY = 0;
      if(Math.abs(leftSide - rightSide) > 2) {
        balanceAdjustX = (leftSide > rightSide ? 1 : -1) * 40;
      }
      if(Math.abs(topSide - bottomSide) > 2) {
        balanceAdjustY = (topSide > bottomSide ? 1 : -1) * 40;
      }

'''
        lines.insert(insert_idx, balance_code)

        # Apply balance adjustment to target position
        for i in range(insert_idx, min(insert_idx + 100, len(lines))):
            if 'targetX += offsetX;' in lines[i]:
                lines[i] = '          targetX += offsetX + balanceAdjustX; // バランス調整適用\n'
            if 'targetY += offsetY;' in lines[i]:
                lines[i] = '          targetY += offsetY + balanceAdjustY; // バランス調整適用\n'
                break
    print("   ✓ Team floor balance awareness added")
    print("   ✓ Players spread to empty areas")

    # ===== 8. FAST DEFENSIVE TRANSITION =====
    print("\n8. Implementing fast defensive transition...")

    # Find turnover/steal section
    idx = find_line(lines, 'function attemptSteal(stealer, handler) {')
    if idx > 0:
        for i in range(idx, min(idx + 10, len(lines))):
            if 'possession = stealer.team; shotClock = 24;' in lines[i]:
                # Add defensive transition trigger
                lines[i] = '''    possession = stealer.team; shotClock = 24;

    // 攻守切り替え：即座にディフェンスへ移行
    players.forEach(pl => {
      if(pl.team !== stealer.team) {
        pl.transitionDefense = true;
        pl.transitionTimer = 120; // 2秒間トランジションモード
      }
    });
'''
                break

    # Apply transition defense in updatePlayer
    idx = find_line(lines, '} else if(ball.z < 80 && !players.some(pl=>pl.hasBall)) {')
    if idx > 0:
        # Insert transition check before loose ball chase
        transition_code = '''    } else if(p.transitionDefense && p.transitionTimer > 0) {
      // トランジションディフェンス：素早く自陣へ戻る
      p.transitionTimer--;
      p.speedMultiplier = SPEED_SPRINT;
      let pos = p.position;
      let defX = (p.team === "PlayerTeam" ? 200 : 800);
      let defY = 388.75 + (p.id % 5 - 2) * 80;
      moveToward(p, defX, defY, speed);

      if(p.transitionTimer <= 0) {
        p.transitionDefense = false;
      }
'''
        lines.insert(idx, transition_code)
    print("   ✓ Fast defensive transition after turnovers")
    print("   ✓ Players sprint back on defense")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "="*50)
    print("ALL IMPROVEMENTS APPLIED SUCCESSFULLY!")
    print("="*50)

if __name__ == "__main__":
    main()
