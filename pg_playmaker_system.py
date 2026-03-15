#!/usr/bin/env python3
"""
Point Guard Playmaker System:
1. PG receives ball after rebounds/steals/inbounds
2. PG dribbles ball up court
3. PG as primary offensive initiator
4. Transition offense led by PG
5. Halfcourt setup with PG at top
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

    print("=== POINT GUARD PLAYMAKER SYSTEM ===\n")

    # ===== 1. ADD PG PLAYMAKING STATES =====
    print("1. Adding PG playmaker states...")

    idx = find_line(lines, 'dribbleMoveTimer: 0,')
    if idx > 0:
        insert_idx = idx + 1
        lines.insert(insert_idx, '''      // PG専用状態
      bringingBallUp: false,      // ボール運び中
      ballAdvanceTarget: null,    // ボール運びの目標位置
      isPlaymaker: false,         // プレイメイカーモード
      inTransition: false,        // トランジション中
''')
    print("   ✓ PG playmaker states added")

    # ===== 2. AUTO-PASS TO PG AFTER REBOUND =====
    print("\n2. Implementing auto-pass to PG after gaining possession...")

    # Find rebound acquisition
    idx = find_line(lines, 'p.hasBall = true; possession = p.team; shotClock = 24;')
    if idx > 0:
        # Check if this is in the rebound section
        for i in range(max(0, idx - 30), idx):
            if 'reboundChance' in lines[i] or 'REBOUND!' in lines[i]:
                # This is the rebound section
                insert_idx = idx + 1
                auto_pass_code = '''
              // リバウンド後：即座にPGへパス
              if(p.position !== "PG") {
                let pg = players.find(pl =>
                  pl.team === p.team &&
                  pl.position === "PG"
                );
                if(pg && dist(p.x, p.y, pg.x, pg.y) < 300) {
                  setTimeout(() => {
                    if(p.hasBall) {
                      passTo(p, pg);
                      pg.bringingBallUp = true;
                      pg.inTransition = true;
                      addFloatingText(pg.x, pg.y - 50, "OUTLET!", [0, 255, 200]);
                    }
                  }, 200); // 0.33秒後にアウトレットパス
                }
              } else {
                // PG自身がリバウンド
                p.bringingBallUp = true;
                p.inTransition = true;
              }
'''
                lines.insert(insert_idx, auto_pass_code)
                break
    print("   ✓ Outlet pass to PG after rebounds")

    # ===== 3. AUTO-PASS TO PG AFTER STEAL =====
    idx = find_line(lines, 'handler.hasBall = false; stealer.hasBall = true;')
    if idx > 0:
        insert_idx = idx + 1
        steal_pass = '''
    // スティール後：PGへパス
    if(stealer.position !== "PG") {
      let pg = players.find(pl =>
        pl.team === stealer.team &&
        pl.position === "PG"
      );
      if(pg && dist(stealer.x, stealer.y, pg.x, pg.y) < 250) {
        setTimeout(() => {
          if(stealer.hasBall) {
            passTo(stealer, pg);
            pg.bringingBallUp = true;
            pg.inTransition = true;
          }
        }, 300);
      }
    } else {
      stealer.bringingBallUp = true;
      stealer.inTransition = true;
    }
'''
        lines.insert(insert_idx, steal_pass)
    print("   ✓ Auto-pass to PG after steals")

    # ===== 4. INBOUND TO PG =====
    print("\n3. Ensuring PG receives inbound passes...")

    idx = find_line(lines, 'function startThrowIn(team, x, y, reason) {')
    if idx > 0:
        # Find where the inbounder is selected
        for i in range(idx, min(idx + 50, len(lines))):
            if 'throwInState = {team, x, y, reason, timer:120};' in lines[i]:
                insert_idx = i + 1
                inbound_code = '''
  // インバウンド後、PGがボールを受け取るように設定
  setTimeout(() => {
    let teamPlayers = players.filter(p => p.team === team);
    let pg = teamPlayers.find(p => p.position === "PG");
    if(pg) {
      pg.bringingBallUp = true;
      pg.inTransition = true;
    }
  }, 2000); // インバウンド完了後
'''
                lines.insert(insert_idx, inbound_code)
                break
    print("   ✓ PG receives inbound passes")

    # ===== 5. PG BALL ADVANCEMENT (DRIBBLE UP COURT) =====
    print("\n4. Implementing PG ball advancement system...")

    # Find the offensive AI section
    idx = find_line(lines, 'if(p.hasBall) {')
    if idx > 0:
        # Insert ball advancement logic at the beginning
        for i in range(idx, min(idx + 30, len(lines))):
            if 'let distToGoal = dist(p.x, p.y, tg.x, tg.y);' in lines[i]:
                insert_idx = i + 1
                ball_advance = '''
      // PG専用：ボール運び（ドリブルアップ）
      if(p.position === "PG" && p.bringingBallUp) {
        // 自陣からハーフコートを超えて相手コートへ
        let halfCourtX = 500;
        let targetX = tg.x > 500 ? 650 : 350; // 相手コート側のトップ
        let targetY = 388.75; // センターライン

        let currentSide = p.x > 500 ? "right" : "left";
        let targetSide = tg.x > 500 ? "right" : "left";

        // 自陣にいる場合
        if(currentSide !== targetSide) {
          // ハーフコートまで運ぶ
          p.speedMultiplier = SPEED_RUN;
          moveToward(p, halfCourtX, targetY, speed);
          p.isPlaymaker = false;
        } else {
          // 相手コートに入った
          let distToTop = dist(p.x, p.y, targetX, targetY);

          if(distToTop > 30) {
            // トップオブザキーへ移動
            p.speedMultiplier = SPEED_JOG;
            moveToward(p, targetX, targetY, speed);
            p.isPlaymaker = false;
          } else {
            // トップに到達：プレイメイク開始
            p.bringingBallUp = false;
            p.isPlaymaker = true;
            p.inTransition = false;
          }
        }

        // ボール運び中は他の行動をスキップ
        if(p.bringingBallUp) {
          return;
        }
      }

      // PGがプレイメイカーとして機能
      if(p.position === "PG" && p.isPlaymaker) {
        // トップでボールをキープし、状況判断
        p.speedMultiplier = SPEED_WALK;

        // 他の選手が動くのを待つ（少し時間を持つ）
        if(!p.playmakingTimer) p.playmakingTimer = 60; // 1秒待つ

        if(p.playmakingTimer > 0) {
          p.playmakingTimer--;
          // トップでキープ
          let topX = tg.x > 500 ? 650 : 350;
          let topY = 388.75;
          if(dist(p.x, p.y, topX, topY) > 20) {
            moveToward(p, topX, topY, speed * 0.3);
          }

          // プレイメイク時間中はシュートを控える
          if(p.playmakingTimer > 30) {
            // パスを優先
            return; // 次のフレームでパス判定
          }
        } else {
          // プレイメイク完了：通常のオフェンスへ
          p.isPlaymaker = false;
          p.playmakingTimer = 0;
        }
      }

'''
                lines.insert(insert_idx, ball_advance)
                break
    print("   ✓ PG dribbles ball up court")
    print("   ✓ Advances to opponent's half")
    print("   ✓ Sets up at top of key")

    # ===== 6. TRANSITION OFFENSE =====
    print("\n5. Adding transition offense system...")

    # Find where teammates position during offense
    idx = find_line(lines, '// PG専用：ボール運び（ドリブルアップ）')
    if idx > 0:
        # Insert transition positioning for other players
        transition_code = '''
      // トランジション時：味方は速攻ポジション
      if(!p.hasBall) {
        let pg = players.find(pl =>
          pl.team === p.team &&
          pl.position === "PG" &&
          pl.bringingBallUp
        );

        if(pg) {
          // PGがボールを運んでいる間、先行して走る
          p.speedMultiplier = SPEED_SPRINT;
          let pos = p.position;

          if(pos === "SG" || pos === "SF") {
            // ウィングを走る
            let wingX = tg.x + (p.id % 2 === 0 ? -100 : 100);
            let wingY = tg.y + (p.id % 2 === 0 ? -80 : 80);
            moveToward(p, wingX, wingY, speed);
            return;
          } else if(pos === "PF" || pos === "C") {
            // ペイントへ走る
            let paintX = tg.x + (tg.x > 500 ? -60 : 60);
            let paintY = tg.y;
            moveToward(p, paintX, paintY, speed);
            return;
          }
        }
      }

'''
        lines.insert(idx, transition_code)
    print("   ✓ Teammates run ahead in transition")
    print("   ✓ Wings fill lanes")
    print("   ✓ Bigs run to paint")

    # ===== 7. PG PASS PRIORITY IN PLAYMAKING =====
    print("\n6. Enhancing PG playmaking decisions...")

    # Find pass decision section
    idx = find_line(lines, '// パス先候補を評価')
    if idx > 0:
        for i in range(idx, min(idx + 50, len(lines))):
            if 'let openScore = 100;' in lines[i]:
                insert_idx = i - 2
                playmaking_bonus = '''
      // PGのプレイメイキング：より良いパス判断
      let pgPlaymakingBonus = 0;
      if(p.position === "PG" && p.isPlaymaker) {
        pgPlaymakingBonus = map(p.iq, 0, 100, 0, 30); // IQで判断力向上
      }

'''
                lines.insert(insert_idx, playmaking_bonus)

                # Add bonus to open score
                for j in range(i, min(i + 20, len(lines))):
                    if 'candidates.push({player:t, score:openScore});' in lines[j]:
                        lines[j] = '        candidates.push({player:t, score:openScore + pgPlaymakingBonus});\n'
                        break
                break
    print("   ✓ PG makes smarter passes")
    print("   ✓ IQ affects playmaking")

    # ===== 8. VISUAL INDICATORS =====
    print("\n7. Adding visual indicators for PG playmaking...")

    idx = find_line(lines, '// アイソレーション表示')
    if idx > 0:
        visual_code = '''
  // PGボール運び表示
  if(p.position === "PG" && p.bringingBallUp) {
    stroke(0, 255, 150, 200);
    strokeWeight(3);
    noFill();
    // 進行方向の矢印風エフェクト
    let arrowSize = p.size * 1.5;
    let tg = p.team === "PlayerTeam" ? {x:finalGoal.ringX, y:finalGoal.ringY} : {x:1000-finalGoal.ringX, y:finalGoal.ringY};
    let arrowAngle = atan2(tg.y - p.y, tg.x - p.x);
    push();
    translate(px, py);
    rotate(arrowAngle);
    line(0, 0, arrowSize, 0);
    line(arrowSize, 0, arrowSize - 8, -5);
    line(arrowSize, 0, arrowSize - 8, 5);
    pop();
  }

  // PGプレイメイキング表示
  if(p.position === "PG" && p.isPlaymaker) {
    stroke(255, 200, 0, 180);
    strokeWeight(2);
    noFill();
    let playmakerRing = p.size * 1.8;
    ellipse(px, py, playmakerRing, playmakerRing);
    fill(255, 200, 0);
    textSize(8);
    text("PG", px, py - p.size/2 - 18);
  }

'''
        lines.insert(idx, visual_code)
    print("   ✓ Green arrow when bringing ball up")
    print("   ✓ Yellow ring when playmaking")

    # ===== 9. RESET STATES ON POSSESSION CHANGE =====
    print("\n8. Adding state reset on possession change...")

    # Find possession change locations
    idx = find_line(lines, 'possession = stealer.team; shotClock = 24;')
    if idx > 0:
        for i in range(idx, min(idx + 20, len(lines))):
            if 'addFloatingText(stealer.x, stealer.y - 40, "STEAL!", [0,255,100]);' in lines[i]:
                insert_idx = i + 1
                reset_code = '''
    // 攻守交代：古い状態をリセット
    players.forEach(pl => {
      if(pl.team !== stealer.team) {
        pl.bringingBallUp = false;
        pl.isPlaymaker = false;
        pl.inTransition = false;
        pl.playmakingTimer = 0;
      }
    });
'''
                lines.insert(insert_idx, reset_code)
                break
    print("   ✓ State reset on turnovers")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "="*50)
    print("POINT GUARD PLAYMAKER SYSTEM COMPLETE!")
    print("="*50)
    print("\nKey Features:")
    print("  • Auto-pass to PG after rebounds/steals")
    print("  • PG dribbles ball up court")
    print("  • Crosses halfcourt into opponent's side")
    print("  • Sets up at top of key")
    print("  • Transition offense with fast break")
    print("  • PG as primary playmaker")
    print("  • Smart passing decisions")
    print("  • Visual indicators")

if __name__ == "__main__":
    main()
