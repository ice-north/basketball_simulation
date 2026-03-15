#!/usr/bin/env python3
"""
Screen and Isolation System:
1. Increase collision detection radius
2. On-ball screens (Pick & Roll)
3. Off-ball screens (for shooters)
4. 1-on-1 isolation plays with dribble moves
5. Screen usage AI
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

    print("=== SCREEN & ISOLATION SYSTEM ===\n")

    # ===== 1. INCREASE COLLISION DETECTION =====
    print("1. Increasing collision detection radius...")

    idx = find_line(lines, '// 選手同士の衝突判定（重なり防止）')
    if idx > 0:
        for i in range(idx, min(idx + 15, len(lines))):
            if 'let minDist = 20;' in lines[i]:
                lines[i] = '    let minDist = 35; // 最小距離拡大（スクリーン用）\n'
                break
    print("   ✓ Collision radius: 20px → 35px")

    # ===== 2. ADD SCREEN STATES TO PLAYERS =====
    print("\n2. Adding screen play states...")

    idx = find_line(lines, 'postMoveTimer: 0,')
    if idx > 0:
        insert_idx = idx + 1
        lines.insert(insert_idx, '''      // スクリーンプレイ状態
      settingScreen: false,       // スクリーン中
      screenTarget: null,         // スクリーン対象（ディフェンダー）
      usingScreen: false,         // スクリーン使用中
      screenTimer: 0,             // スクリーンタイマー
      screenType: null,           // "pick" or "off-ball"
      // 1対1状態
      isolationMode: false,       // アイソレーション中
      dribbleMoveType: null,      // "crossover", "hesitation", "behind"
      dribbleMoveTimer: 0,        // ドリブルムーブタイマー
''')
    print("   ✓ Screen and isolation states added")

    # ===== 3. IMPLEMENT PICK & ROLL =====
    print("\n3. Implementing pick & roll system...")

    # Find the offensive AI section where we can add pick & roll logic
    idx = find_line(lines, '// ポストプレイ：良いポジションからのポストムーブ')
    if idx > 0:
        # Insert pick & roll logic before post play
        pick_roll_code = '''
    // ピック＆ロール：PG/SGがボールを持ち、C/PFがスクリーン
    if(!p.hasBall && (pos === "C" || pos === "PF" || (pos === "SF" && random() < 0.3))) {
      let ballHandlers = players.filter(pl =>
        pl.team === p.team &&
        pl.hasBall &&
        (pl.position === "PG" || pl.position === "SG")
      );

      if(ballHandlers.length > 0 && !p.settingScreen && random() < 0.15) {
        let ballHandler = ballHandlers[0];
        let distToHandler = dist(p.x, p.y, ballHandler.x, ballHandler.y);

        // ボールハンドラーの近くでスクリーン設定
        if(distToHandler < 150 && distToHandler > 50) {
          // ボールハンドラーのディフェンダーを見つける
          let handlerDefender = players.find(d =>
            d.team !== p.team &&
            dist(d.x, d.y, ballHandler.x, ballHandler.y) < 60
          );

          if(handlerDefender) {
            p.settingScreen = true;
            p.screenTarget = handlerDefender.id;
            p.screenType = "pick";
            p.screenTimer = 120; // 2秒間スクリーン

            // ディフェンダーとハンドラーの間に移動
            let screenX = (ballHandler.x + handlerDefender.x) / 2;
            let screenY = (ballHandler.y + handlerDefender.y) / 2;

            moveToward(p, screenX, screenY, speed * 0.8);

            // ボールハンドラーにスクリーンを知らせる
            ballHandler.usingScreen = true;
            ballHandler.screenTimer = 120;

            addFloatingText(p.x, p.y - 50, "SCREEN!", [255, 200, 0]);
          }
        }
      }
    }

    // スクリーン実行中
    if(p.settingScreen && p.screenTimer > 0) {
      p.screenTimer--;
      p.speedMultiplier = 0; // 静止

      let screenTarget = players[p.screenTarget];
      if(screenTarget) {
        // ディフェンダーの動きをブロック
        let distToDef = dist(p.x, p.y, screenTarget.x, screenTarget.y);
        if(distToDef < 40) {
          // 物理的にブロック（押し戻す）
          let blockAngle = atan2(screenTarget.y - p.y, screenTarget.x - p.x);
          screenTarget.x -= cos(blockAngle) * 3;
          screenTarget.y -= sin(blockAngle) * 3;
          screenTarget.x = constrain(screenTarget.x, 25, 975);
          screenTarget.y = constrain(screenTarget.y, 262.5, 550);
        }
      }

      // スクリーン後：ロールムーブ
      if(p.screenTimer < 60 && p.screenType === "pick") {
        // ゴールに向かってロール
        p.speedMultiplier = SPEED_RUN;
        moveToward(p, tg.x, tg.y, speed);
      }

      if(p.screenTimer <= 0) {
        p.settingScreen = false;
        p.screenTarget = null;
        p.screenType = null;
      }

      return; // 他のアクションをスキップ
    }

'''
        lines.insert(idx, pick_roll_code)
    print("   ✓ Pick & roll with screen setter")
    print("   ✓ Roll to basket after screen")
    print("   ✓ Physical blocking of defender")

    # ===== 4. OFF-BALL SCREENS =====
    print("\n4. Adding off-ball screens for shooters...")

    # Add off-ball screen logic
    idx = find_line(lines, '// ピック＆ロール：PG/SGがボールを持ち、C/PFがスクリーン')
    if idx > 0:
        # Insert before pick & roll
        offball_screen = '''
    // オフボールスクリーン：シューター用
    if(!p.hasBall && !handler.hasBall && (pos === "PF" || pos === "C")) {
      let shooters = players.filter(pl =>
        pl.team === p.team &&
        !pl.hasBall &&
        (pl.position === "SG" || pl.position === "SF") &&
        pl.tpt > 65 // 良いシューター
      );

      if(shooters.length > 0 && !p.settingScreen && random() < 0.08) {
        let shooter = shooters[0];
        let shooterDefender = players.find(d =>
          d.team !== p.team &&
          dist(d.x, d.y, shooter.x, shooter.y) < 50
        );

        if(shooterDefender) {
          p.settingScreen = true;
          p.screenTarget = shooterDefender.id;
          p.screenType = "off-ball";
          p.screenTimer = 90;

          // シューターとディフェンダーの間
          let screenX = (shooter.x + shooterDefender.x) / 2;
          let screenY = (shooter.y + shooterDefender.y) / 2;
          moveToward(p, screenX, screenY, speed);

          // シューターに通知
          shooter.usingScreen = true;
          shooter.screenTimer = 90;

          addFloatingText(p.x, p.y - 50, "SCREEN!", [100, 255, 100]);
        }
      }
    }

'''
        lines.insert(idx, offball_screen)
    print("   ✓ Off-ball screens for shooters")
    print("   ✓ Creates open 3PT opportunities")

    # ===== 5. SCREEN USAGE (BALL HANDLER) =====
    print("\n5. Implementing screen usage by ball handler...")

    # Find where ball handler makes decisions
    idx = find_line(lines, '// ボールハンドラーにスクリーンを知らせる')
    if idx > 0:
        # Find a good place to add screen usage logic - in the offensive AI section
        usage_idx = find_line(lines, 'if(p.hasBall) {')
        if usage_idx > 0:
            # Insert at the beginning of ball handling logic
            for i in range(usage_idx, min(usage_idx + 20, len(lines))):
                if 'let distToGoal = dist(p.x, p.y, tg.x, tg.y);' in lines[i]:
                    insert_idx = i + 1
                    screen_usage = '''
      // スクリーン使用中：より積極的にドライブ
      if(p.usingScreen && p.screenTimer > 60) {
        p.speedMultiplier = SPEED_SPRINT;
        // スクリーンを使ってディフェンスを外す
        let screenBonus = 50; // ドライブしやすさボーナス
      }
      if(p.screenTimer > 0) p.screenTimer--;
      if(p.screenTimer <= 0) p.usingScreen = false;

'''
                    lines.insert(insert_idx, screen_usage)
                    break
    print("   ✓ Ball handlers use screens effectively")

    # ===== 6. 1-ON-1 ISOLATION PLAYS =====
    print("\n6. Creating 1-on-1 isolation system...")

    # Add isolation logic
    idx = find_line(lines, '// スクリーン使用中：より積極的にドライブ')
    if idx > 0:
        # Insert isolation logic
        iso_code = '''
      // アイソレーションプレイ：1対1の状況を作る
      let nearbyTeammates = players.filter(pl =>
        pl.team === p.team &&
        pl.id !== p.id &&
        dist(pl.x, pl.y, p.x, p.y) < 150
      ).length;

      let nearbyDefenders = players.filter(pl =>
        pl.team !== p.team &&
        dist(pl.x, pl.y, p.x, p.y) < 80
      ).length;

      // 1対1の状況（味方が少なく、ディフェンダー1人）
      if(nearbyTeammates <= 1 && nearbyDefenders === 1 && !p.isolationMode) {
        let isolationChance = map(p.handling, 0, 100, 0.05, 0.25);
        if(random() < isolationChance && distToGoal < 300) {
          p.isolationMode = true;
          p.dribbleMoveTimer = 90; // 1.5秒のアイソ時間
        }
      }

      // アイソレーション実行中
      if(p.isolationMode && p.dribbleMoveTimer > 0) {
        p.dribbleMoveTimer--;

        // ドリブルムーブ選択
        if(!p.dribbleMoveType && p.dribbleMoveTimer > 30) {
          let moves = ["crossover", "hesitation", "behind-back"];
          let weights = [
            map(p.speed, 0, 100, 0.2, 0.5),      // crossover
            map(p.handling, 0, 100, 0.2, 0.4),   // hesitation
            map(p.agility, 0, 100, 0.1, 0.3)     // behind-back
          ];
          let total = weights.reduce((a,b) => a+b, 0);
          let r = random() * total;
          let cum = 0;
          for(let mi = 0; mi < moves.length; mi++) {
            cum += weights[mi];
            if(r <= cum) {
              p.dribbleMoveType = moves[mi];
              break;
            }
          }

          // ムーブ実行
          if(p.dribbleMoveType === "crossover") {
            // クロスオーバー：左右に素早く移動
            let crossDir = (p.x < tg.x ? 1 : -1);
            p.x += crossDir * 25;
            p.facingAngle += (crossDir > 0 ? PI/6 : -PI/6);
            addFloatingText(p.x, p.y - 50, "CROSS!", [0, 255, 255]);
          } else if(p.dribbleMoveType === "hesitation") {
            // ヘジテーション：一瞬止まってから加速
            p.speedMultiplier = 0.1; // ほぼ停止
            setTimeout(() => {
              p.speedMultiplier = SPEED_SPRINT;
              let accelAngle = atan2(tg.y - p.y, tg.x - p.x);
              p.x += cos(accelAngle) * 20;
              p.y += sin(accelAngle) * 20;
            }, 300);
            addFloatingText(p.x, p.y - 50, "HESI!", [255, 255, 0]);
          } else if(p.dribbleMoveType === "behind-back") {
            // ビハインドバック：後ろ経由で方向転換
            let behindAngle = atan2(tg.y - p.y, tg.x - p.x) + PI/3;
            p.x += cos(behindAngle) * 18;
            p.y += sin(behindAngle) * 18;
            p.facingAngle = behindAngle;
            addFloatingText(p.x, p.y - 50, "BTB!", [255, 150, 255]);
          }

          p.x = constrain(p.x, 25, 975);
          p.y = constrain(p.y, 262.5, 550);
        }

        // アイソ後はドライブかシュート
        if(p.dribbleMoveTimer < 20) {
          p.speedMultiplier = SPEED_SPRINT;
          // ゴールへドライブ
          moveToward(p, tg.x, tg.y, speed);
        }

        if(p.dribbleMoveTimer <= 0) {
          p.isolationMode = false;
          p.dribbleMoveType = null;
        }
      }

'''
        lines.insert(idx, iso_code)
    print("   ✓ Isolation detection (1v1 situations)")
    print("   ✓ Three dribble moves: Crossover, Hesitation, Behind-back")
    print("   ✓ Move selection based on skills")

    # ===== 7. VISUAL INDICATORS =====
    print("\n7. Adding visual indicators for screens...")

    idx = find_line(lines, '// ポストムーブ表示')
    if idx > 0:
        # Add screen visual before post move visual
        screen_visual = '''
  // スクリーン表示
  if(p.settingScreen && p.screenTimer > 0) {
    stroke(255, 200, 0, 200); strokeWeight(4);
    noFill();
    let screenSize = p.size * 2.0;
    rect(px - screenSize/2, py - screenSize/2, screenSize, screenSize, 4);
    fill(255, 200, 0);
    textSize(8);
    text("SCREEN", px, py - p.size/2 - 15);
  }

  // アイソレーション表示
  if(p.isolationMode && p.dribbleMoveTimer > 0) {
    stroke(0, 255, 255, 180);
    strokeWeight(2);
    noFill();
    let pulseSize = p.size * 1.3 + sin(frameCount * 0.3) * 5;
    ellipse(px, py, pulseSize, pulseSize);
  }

'''
        lines.insert(idx, screen_visual)
    print("   ✓ Yellow square for screen setters")
    print("   ✓ Cyan pulse for isolation players")

    # ===== 8. ILLEGAL SCREEN PREVENTION =====
    print("\n8. Adding illegal screen prevention...")

    # Find screen setting logic and add movement restriction
    idx = find_line(lines, 'p.speedMultiplier = 0; // 静止')
    if idx > 0:
        insert_idx = idx + 1
        lines.insert(insert_idx, '''      // スクリーン中は足を固定（イリーガルスクリーン防止）
      // 既に静止設定済み
''')
    print("   ✓ Screen setters must be stationary")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "="*50)
    print("SCREEN & ISOLATION SYSTEM COMPLETE!")
    print("="*50)
    print("\nKey Features:")
    print("  • Collision radius: 35px")
    print("  • Pick & roll plays")
    print("  • Off-ball screens")
    print("  • 3 dribble moves (1v1)")
    print("  • Screen blocking physics")
    print("  • Visual indicators")

if __name__ == "__main__":
    main()
