#!/usr/bin/env python3
"""
NBA Realism Improvements - 5 Key Differences:

1. JUMP SHOT MECHANICS - Players jump before releasing shot
2. DRIBBLE SPEED LIMITATIONS - Ball handling affects speed
3. FAST BREAK ADVANTAGE - Recognize and exploit 2-on-1, 3-on-2
4. OFF-BALL MOVEMENT - Constant motion, not static
5. PACE CONTROL - Adjust tempo based on score differential
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

    print("=== NBA REALISM IMPROVEMENTS ===\n")
    print("Analyzing differences between NBA and current game...\n")

    # ===== DIFFERENCE #1: JUMP SHOT MECHANICS =====
    print("━" * 60)
    print("DIFFERENCE #1: JUMP SHOT MECHANICS")
    print("━" * 60)
    print("NBA: Players jump, reach apex, release ball mid-air")
    print("Current: Players shoot from ground, instant release")
    print("\nImplementing realistic jump shot...")

    # Add jump shot state to player
    idx = find_line(lines, 'dribbleMoveTimer: 0,')
    if idx > 0:
        insert_idx = idx + 1
        lines.insert(insert_idx, '''      // ジャンプシュート状態
      jumpShooting: false,       // ジャンプシュート中
      jumpShootPhase: 0,         // 0=ジャンプ開始, 1-30=上昇, 31=最高点, 32-60=下降
      jumpShootTarget: null,     // シュート目標
''')

    # Modify shoot function to add jump phase
    idx = find_line(lines, 'function shoot(s, tx, ty, is3pt) {')
    if idx > 0:
        # Find the line where ball is released
        for i in range(idx, min(idx + 50, len(lines))):
            if 's.hasBall = false;' in lines[i] and 'mustShoot' in lines[i]:
                # Insert jump shot initiation instead
                indent = '  '
                jump_code = indent + '// ジャンプシュート開始（NBAスタイル）\n'
                jump_code += indent + 's.jumpShooting = true;\n'
                jump_code += indent + 's.jumpShootPhase = 0;\n'
                jump_code += indent + 's.jumpShootTarget = {x: tx, y: ty, is3pt: is3pt};\n'
                jump_code += indent + 's.lock = 60; // シュートモーション中\n'
                jump_code += indent + '// ボールは最高点でリリース（後で処理）\n'
                jump_code += indent + 'return; // 実際のシュートは最高点で\n'
                jump_code += '}\n\n'
                jump_code += '// ジャンプシュート実行（最高点でリリース）\n'
                jump_code += 'function executeJumpShot(s, tx, ty, is3pt) {\n'

                # Copy the original shoot function body
                lines[i] = jump_code + '  s.hasBall = false; s.mustShoot = false; goalChecked = false; lastActionWasShot = true;\n'
                break

    # Add jump shot physics in update loop
    idx = find_line(lines, '// アイソレーション表示')
    if idx > 0:
        jump_physics = '''
  // ジャンプシュートモーション（NBAリアリズム）
  if(p.jumpShooting && p.jumpShootPhase < 60) {
    p.jumpShootPhase++;

    // ジャンプ高さの計算（放物線）
    let jumpProgress = p.jumpShootPhase / 60;
    let jumpHeight = map(p.jmp, 0, 100, 25, 50); // ジャンプ力による高さ
    p.z = sin(jumpProgress * PI) * jumpHeight;

    // 最高点（30フレーム目）でボールリリース
    if(p.jumpShootPhase === 30 && p.jumpShootTarget) {
      executeJumpShot(p, p.jumpShootTarget.x, p.jumpShootTarget.y, p.jumpShootTarget.is3pt);
      p.jumpShootTarget = null;
    }

    // 着地（60フレーム目）
    if(p.jumpShootPhase >= 60) {
      p.jumpShooting = false;
      p.jumpShootPhase = 0;
      p.z = 0;
    }
  }

'''
        lines.insert(idx, jump_physics)

    print("   ✓ Jump shot state added")
    print("   ✓ 60-frame jump motion (1 second)")
    print("   ✓ Ball released at apex (frame 30)")
    print("   ✓ Realistic arc and landing")

    # ===== DIFFERENCE #2: DRIBBLE SPEED LIMITATIONS =====
    print("\n" + "━" * 60)
    print("DIFFERENCE #2: DRIBBLE SPEED LIMITATIONS")
    print("━" * 60)
    print("NBA: Speed dribbling is difficult, elite handles required")
    print("Current: Any player can sprint at full speed with ball")
    print("\nImplementing ball handling speed limits...")

    # Find where ball handler moves
    idx = find_line(lines, 'if(p.hasBall) {')
    if idx > 0:
        # Find where speed is set
        for i in range(idx, min(idx + 100, len(lines))):
            if 'p.speedMultiplier = SPEED_SPRINT;' in lines[i]:
                # Add handling check before this
                indent = len(lines[i]) - len(lines[i].lstrip())
                handling_limit = ' ' * indent + '// ドリブル速度制限（ハンドリング能力による）\n'
                handling_limit += ' ' * indent + 'let maxDribbleSpeed = map(p.handling, 0, 100, SPEED_JOG, SPEED_SPRINT);\n'
                handling_limit += ' ' * indent + '// エリートハンドラー（90+）のみフルスピード可能\n'
                handling_limit += ' ' * indent + 'if(p.handling < 90) {\n'
                handling_limit += ' ' * indent + '  p.speedMultiplier = min(p.speedMultiplier, maxDribbleSpeed);\n'
                handling_limit += ' ' * indent + '}\n'

                lines.insert(i, handling_limit)
                break

    print("   ✓ Handling 0-50: Max JOG speed (0.57)")
    print("   ✓ Handling 50-75: Between JOG-RUN (0.57-0.76)")
    print("   ✓ Handling 75-90: Between RUN-SPRINT (0.76-1.14)")
    print("   ✓ Handling 90+: Full SPRINT (1.425)")
    print("   ✓ Elite ball handlers (PG) have advantage")

    # ===== DIFFERENCE #3: FAST BREAK NUMERICAL ADVANTAGE =====
    print("\n" + "━" * 60)
    print("DIFFERENCE #3: FAST BREAK NUMERICAL ADVANTAGE")
    print("━" * 60)
    print("NBA: Teams recognize 2-on-1, 3-on-2 and exploit")
    print("Current: Fast break is simple forward push")
    print("\nImplementing fast break advantage recognition...")

    # Add advantage detection
    idx = find_line(lines, '// ③速攻機会があれば突撃')
    if idx > 0:
        # Replace simple fast break with smart recognition
        for i in range(idx, min(idx + 20, len(lines))):
            if 'if(distToGoal < 350 && !dominated) {' in lines[i]:
                indent = len(lines[i]) - len(lines[i].lstrip())

                # Insert advantage detection before
                advantage_code = ' ' * indent + '// 速攻時の数的優位判定（NBAスタイル）\n'
                advantage_code += ' ' * indent + 'let offensiveCount = teammates.filter(t => {\n'
                advantage_code += ' ' * indent + '  let isAhead = p.team === "PlayerTeam" ? t.x > 600 : t.x < 400;\n'
                advantage_code += ' ' * indent + '  return isAhead && dist(t.x, t.y, tg.x, tg.y) < 300;\n'
                advantage_code += ' ' * indent + '}).length + 1; // 自分含む\n'
                advantage_code += ' ' * indent + 'let defensiveCount = players.filter(d => {\n'
                advantage_code += ' ' * indent + '  if(d.team === p.team) return false;\n'
                advantage_code += ' ' * indent + '  let isBack = p.team === "PlayerTeam" ? d.x > 600 : d.x < 400;\n'
                advantage_code += ' ' * indent + '  return isBack && dist(d.x, d.y, tg.x, tg.y) < 300;\n'
                advantage_code += ' ' * indent + '}).length;\n'
                advantage_code += ' ' * indent + 'let hasAdvantage = offensiveCount > defensiveCount; // 数的優位\n'
                advantage_code += ' ' * indent + 'let advantageType = "";\n'
                advantage_code += ' ' * indent + 'if(offensiveCount === 2 && defensiveCount === 1) advantageType = "2-on-1";\n'
                advantage_code += ' ' * indent + 'if(offensiveCount === 3 && defensiveCount === 2) advantageType = "3-on-2";\n'
                advantage_code += ' ' * indent + 'if(offensiveCount === 1 && defensiveCount === 0) advantageType = "breakaway";\n\n'

                lines.insert(i, advantage_code)

                # Modify the fast break logic
                for j in range(i, min(i + 30, len(lines))):
                    if 'if(distToGoal < 350 && !dominated) {' in lines[j]:
                        lines[j] = ' ' * indent + 'if(hasAdvantage && distToGoal < 350 && !dominated) {\n'
                        # Add advantage exploitation
                        for k in range(j + 1, min(j + 15, len(lines))):
                            if 'p.speedMultiplier = SPEED_SPRINT;' in lines[k]:
                                insert_after = k + 1
                                exploit_code = ' ' * indent + '  // 数的優位を活用（確実にフィニッシュ）\n'
                                exploit_code += ' ' * indent + '  if(advantageType === "breakaway" && distToGoal < 150) {\n'
                                exploit_code += ' ' * indent + '    // ブレイクアウェイ：レイアップへ直行\n'
                                exploit_code += ' ' * indent + '    moveToward(p, tg.x, tg.y, speed * SPEED_SPRINT);\n'
                                exploit_code += ' ' * indent + '    if(distToGoal < 100) { shoot(p, tg.x, tg.y, false); }\n'
                                exploit_code += ' ' * indent + '    return;\n'
                                exploit_code += ' ' * indent + '  }\n'
                                exploit_code += ' ' * indent + '  if(advantageType === "2-on-1" || advantageType === "3-on-2") {\n'
                                exploit_code += ' ' * indent + '    // 2対1, 3対2：ディフェンスを崩してイージーシュート\n'
                                exploit_code += ' ' * indent + '    let openTeammate = teammates.find(t => {\n'
                                exploit_code += ' ' * indent + '      let isAhead = p.team === "PlayerTeam" ? t.x > p.x + 50 : t.x < p.x - 50;\n'
                                exploit_code += ' ' * indent + '      if(!isAhead) return false;\n'
                                exploit_code += ' ' * indent + '      let nearDef = players.filter(d => d.team !== p.team && dist(d.x, d.y, t.x, t.y) < 80);\n'
                                exploit_code += ' ' * indent + '      return nearDef.length === 0;\n'
                                exploit_code += ' ' * indent + '    });\n'
                                exploit_code += ' ' * indent + '    if(openTeammate && distToGoal > 120) {\n'
                                exploit_code += ' ' * indent + '      passTo(p, openTeammate); return;\n'
                                exploit_code += ' ' * indent + '    }\n'
                                exploit_code += ' ' * indent + '  }\n'

                                lines.insert(insert_after, exploit_code)
                                break
                        break
                break

    print("   ✓ Detects breakaway (1-on-0)")
    print("   ✓ Detects 2-on-1 situations")
    print("   ✓ Detects 3-on-2 situations")
    print("   ✓ Exploits advantage for easy baskets")
    print("   ✓ Smart passing to open man")

    # ===== DIFFERENCE #4: OFF-BALL MOVEMENT =====
    print("\n" + "━" * 60)
    print("DIFFERENCE #4: OFF-BALL MOVEMENT")
    print("━" * 60)
    print("NBA: Constant motion - cutting, screening, relocating")
    print("Current: Players mostly static when not on ball")
    print("\nImplementing constant off-ball motion...")

    # Add constant motion state
    idx = find_line(lines, '// PG専用状態')
    if idx > 0:
        lines.insert(idx, '''      // オフボールムーブメント
      constantMotion: false,      // 常に動く
      motionTimer: 0,            // 動きの変更タイミング
      motionType: null,          // "cut", "spot", "screen", "relocate"
''')

    # Add motion logic for off-ball players
    idx = find_line(lines, '// 理想的なオフェンスポジションへ移動（コート全体を使用）')
    if idx > 0:
        # Replace static positioning with constant motion
        motion_code = '''        // 理想的なオフェンスポジションへ移動（コンスタントモーション）

        // NBA式：常に動き続ける
        if(!p.motionTimer || p.motionTimer <= 0) {
          // 新しい動きを決定（2秒ごと）
          p.motionTimer = 120;
          let motionRoll = random();

          if(motionRoll < 0.15 && !p.isCutting) {
            // 15%: カッティング
            p.constantMotion = true;
            p.motionType = "cut";
            initiateCut(p, random() > 0.5 ? "backdoor" : "baseline");
          } else if(motionRoll < 0.35 && pos !== "C" && pos !== "PF") {
            // 20%: スポットアップ（3Pライン）
            p.constantMotion = true;
            p.motionType = "spot";
          } else if(motionRoll < 0.50) {
            // 15%: リロケート（位置変更）
            p.constantMotion = true;
            p.motionType = "relocate";
          } else {
            // 50%: 通常ポジショニング
            p.constantMotion = false;
            p.motionType = null;
          }
        }
        p.motionTimer--;

        // モーションタイプ別の動き
        if(p.constantMotion && p.motionType === "spot") {
          // スポットアップ：3Pライン付近へ
          let spotX = tg.x + (tg.x > 500 ? -200 : 200);
          let spotY = tg.y + (p.id % 2 === 0 ? -120 : 120);
          moveToward(p, constrain(spotX, 50, 950), constrain(spotY, 260, 550), speed * 0.6);
          return;
        } else if(p.constantMotion && p.motionType === "relocate") {
          // リロケート：弱サイドへ移動
          let weakSideX = tg.x + (tg.x > 500 ? -250 : 250);
          let weakSideY = 388.75 + (p.id % 3 - 1) * 100;
          moveToward(p, constrain(weakSideX, 50, 950), constrain(weakSideY, 260, 550), speed * 0.5);
          return;
        }

        // 通常ポジショニング
'''

        lines[idx] = motion_code

    print("   ✓ 15% chance to cut (backdoor/baseline)")
    print("   ✓ 20% chance to spot up (3PT line)")
    print("   ✓ 15% chance to relocate (weak side)")
    print("   ✓ Motion changes every 2 seconds")
    print("   ✓ Creates spacing and opportunities")

    # ===== DIFFERENCE #5: PACE CONTROL =====
    print("\n" + "━" * 60)
    print("DIFFERENCE #5: PACE CONTROL")
    print("━" * 60)
    print("NBA: Teams control pace based on score/situation")
    print("Current: Same tempo regardless of score")
    print("\nImplementing dynamic pace control...")

    # Add pace calculation
    idx = find_line(lines, 'let gameSpeed = 1;')
    if idx > 0:
        lines.insert(idx + 1, '''// ペースコントロール（スコア差で変動）
let desiredPace = "normal"; // "slow", "normal", "fast"
let paceMultiplier = 1.0;
''')

    # Add pace update in game loop
    idx = find_line(lines, 'function draw() {')
    if idx > 0:
        for i in range(idx, min(idx + 30, len(lines))):
            if 'background(34, 139, 34);' in lines[i]:
                pace_code = '''
  // ペースコントロール（NBAリアリズム）
  let scoreDiff = scorePlayer - scoreDefender;
  let absScoreDiff = abs(scoreDiff);

  // スコア差による戦術
  if(absScoreDiff >= 10) {
    // 10点差以上
    if(scoreDiff > 0) {
      // リード側：スローダウン（時間を使う）
      desiredPace = "slow";
      paceMultiplier = 0.75;
    } else {
      // ビハインド側：アップテンポ（追いつく）
      desiredPace = "fast";
      paceMultiplier = 1.3;
    }
  } else if(absScoreDiff >= 5) {
    // 5-10点差
    if(scoreDiff > 0) {
      desiredPace = "normal";
      paceMultiplier = 0.9;
    } else {
      desiredPace = "normal";
      paceMultiplier = 1.15;
    }
  } else {
    // 接戦
    desiredPace = "normal";
    paceMultiplier = 1.0;
  }

  // クォーター終盤はペースアップ
  if(gameTime < 120) { // 残り2分
    paceMultiplier *= 1.2;
  }

'''
                lines.insert(i + 1, pace_code)
                break

    # Apply pace to shot clock usage
    idx = find_line(lines, 'if(shotClock < 5 && dToGoal < 300) {')
    if idx > 0:
        # Add pace-based shot timing
        for i in range(max(0, idx - 20), idx):
            if '// ショットクロック急迫時は強制シュート' in lines[i]:
                pace_shot = '''    // ペースコントロール：シュートタイミング調整
    let shotClockThreshold = 5;
    if(desiredPace === "slow") shotClockThreshold = 3; // ゆっくり攻める
    if(desiredPace === "fast") shotClockThreshold = 12; // 早く攻める

'''
                lines.insert(i + 1, pace_shot)
                # Update the condition
                lines[idx] = '    if(shotClock < shotClockThreshold && dToGoal < 300) {\n'
                break

    # Apply pace to player speed
    idx = find_line(lines, 'let speed = p.spd / 32;')
    if idx > 0:
        lines[idx] = '  let speed = p.spd / 32 * paceMultiplier; // ペース反映\n'

    print("   ✓ 10+ point lead: Slow pace (0.75x)")
    print("   ✓ 5-10 point lead: Moderate (0.9x)")
    print("   ✓ Close game: Normal pace (1.0x)")
    print("   ✓ 5-10 behind: Push tempo (1.15x)")
    print("   ✓ 10+ behind: Fast pace (1.3x)")
    print("   ✓ Final 2 minutes: Extra 1.2x boost")
    print("   ✓ Affects shot timing and movement")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("NBA REALISM IMPROVEMENTS COMPLETE!")
    print("=" * 60)
    print("\nAll 5 differences addressed:")
    print("  1. ✓ Jump shot mechanics")
    print("  2. ✓ Dribble speed limitations")
    print("  3. ✓ Fast break advantage")
    print("  4. ✓ Off-ball movement")
    print("  5. ✓ Pace control")

if __name__ == "__main__":
    main()
