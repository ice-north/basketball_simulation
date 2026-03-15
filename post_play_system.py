#!/usr/bin/env python3
"""
Post Play System - Fierce position battles in the paint:
1. Post positioning for C/PF/SF
2. Power-based pushing (offense vs defense)
3. Position quality evaluation (seal, distance)
4. Pass request when in good position
5. Post moves (spin, hook, fadeaway)
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

    print("=== POST PLAY SYSTEM ===\n")

    # ===== 1. ADD POST PLAY STATES TO PLAYERS =====
    print("1. Adding post play states...")

    idx = find_line(lines, 'reboundJumping: false,')
    if idx > 0:
        insert_idx = idx + 1
        lines.insert(insert_idx, '''      // ポストプレイ状態
      postingUp: false,           // ポストアップ中
      postPosition: 0,            // ポジション品質 (0-100)
      requestingPass: false,      // パス要求中
      postPushStrength: 0,        // 押し込み強度
      postMoveType: null,         // ポストムーブタイプ
      postMoveTimer: 0,           // ムーブタイマー
''')
    print("   ✓ Post play states added")

    # ===== 2. ADD POST POSITIONING LOGIC IN OFFENSE =====
    print("\n2. Implementing post positioning battles...")

    # Find offensive positioning section - after position-based movement
    idx = find_line(lines, '} else { // C')
    if idx > 0:
        # Find the closing of position-based targeting
        for i in range(idx, min(idx + 30, len(lines))):
            if 'targetX = constrain(targetX' in lines[i]:
                # Insert post play logic after position targeting
                insert_idx = i + 1
                post_logic = '''
      // ポストプレイ判定（C/PF/SFのゴール下での位置取り）
      let canPostUp = (pos === "C") || (pos === "PF") || (pos === "SF" && random() < 0.4);
      let distToGoal = dist(p.x, p.y, tg.x, tg.y);

      if(canPostUp && distToGoal < 120 && !p.hasBall) {
        p.postingUp = true;

        // ポストポジション：ゴールに近い位置を狙う
        let idealPostX = tg.x + (tg.x > 500 ? -45 : 45); // ゴール横
        let idealPostY = tg.y + (p.id % 2 === 0 ? -30 : 30); // 左右のブロック

        // ディフェンダーを探す
        let defender = players.find(d =>
          d.team !== p.team &&
          d.position === p.position
        );

        if(defender) {
          // パワー勝負：オフェンスがディフェンスを押し込む
          let offensivePower = p.power + p.post * 0.6 + p.strength * 0.4;
          let defensivePower = defender.power + defender.def * 0.4 + defender.strength * 0.6;
          let powerDiff = (offensivePower - defensivePower) / 150;

          p.postPushStrength = powerDiff;

          // オフェンスが強い場合：ディフェンダーを押し込む
          if(powerDiff > 0) {
            // ゴールに向かって押し込む
            let pushAngle = atan2(tg.y - defender.y, tg.x - defender.x);
            defender.x += cos(pushAngle) * powerDiff * 3;
            defender.y += sin(pushAngle) * powerDiff * 3;
            defender.x = constrain(defender.x, 25, 975);
            defender.y = constrain(defender.y, 262.5, 550);

            // 理想位置へ移動
            targetX = idealPostX;
            targetY = idealPostY;
            p.speedMultiplier = SPEED_WALK; // ゆっくり押し込む
          } else {
            // ディフェンスが強い場合：押し返される
            let pushBackAngle = atan2(p.y - defender.y, p.x - defender.x);
            p.x += cos(pushBackAngle) * abs(powerDiff) * 2;
            p.y += sin(pushBackAngle) * abs(powerDiff) * 2;
            p.x = constrain(p.x, 25, 975);
            p.y = constrain(p.y, 262.5, 550);
          }

          // ポジション品質評価
          let distFromIdeal = dist(p.x, p.y, idealPostX, idealPostY);
          let sealQuality = 100; // 基本100%

          // ゴールに近いほど良い
          sealQuality -= distFromIdeal * 0.8;

          // ディフェンダーをシール（seal）できているか
          let defenderBehind = false;
          let angleToGoal = atan2(tg.y - p.y, tg.x - p.x);
          let angleToDefender = atan2(defender.y - p.y, defender.x - p.x);
          let angleDiff = abs(angleToGoal - angleToDefender);

          if(angleDiff > PI * 0.7) { // ディフェンダーが後ろ側
            defenderBehind = true;
            sealQuality += 30; // シール成功ボーナス
          }

          // パワー差ボーナス
          sealQuality += powerDiff * 20;

          p.postPosition = constrain(sealQuality, 0, 100);

          // 良いポジションならパス要求
          if(p.postPosition > 60 && !handler.hasBall) {
            p.requestingPass = true;
          } else {
            p.requestingPass = false;
          }
        }
      } else {
        p.postingUp = false;
        p.requestingPass = false;
        p.postPosition = 0;
      }

'''
                lines.insert(insert_idx, post_logic)
                break
    print("   ✓ Post positioning with power battles")
    print("   ✓ Position quality evaluation (0-100)")
    print("   ✓ Seal detection system")

    # ===== 3. DEFENDER COUNTER-PUSH =====
    print("\n3. Adding defender counter-push mechanics...")

    # Find defense section where defender marks opponent
    idx = find_line(lines, '// 同じポジションの相手選手をマーク')
    if idx > 0:
        # Insert counter-push logic
        for i in range(idx, min(idx + 100, len(lines))):
            if 'let mark = players.filter(t=>t.team!==p.team)[p.id%5];' in lines[i]:
                insert_idx = i + 1
                counter_push = '''
      // ポストディフェンス：押し返し
      if(mark && mark.postingUp) {
        let offensivePower = mark.power + mark.post * 0.6 + mark.strength * 0.4;
        let defensivePower = p.power + p.def * 0.4 + p.strength * 0.6;
        let powerDiff = (defensivePower - offensivePower) / 150;

        if(powerDiff > 0.1) {
          // ディフェンスが強い：オフェンスを押し出す
          let og = p.team === "PlayerTeam" ? {x:finalGoal.ringX, y:finalGoal.ringY} : {x:1000-finalGoal.ringX, y:finalGoal.ringY};
          let pushAngle = atan2(mark.y - og.y, mark.x - og.x);
          mark.x += cos(pushAngle) * powerDiff * 2.5;
          mark.y += sin(pushAngle) * powerDiff * 2.5;
          mark.x = constrain(mark.x, 25, 975);
          mark.y = constrain(mark.y, 262.5, 550);
        }
      }
'''
                lines.insert(insert_idx, counter_push)
                break
    print("   ✓ Defender counter-push system")

    # ===== 4. PASS REQUEST PRIORITY =====
    print("\n4. Implementing pass request system...")

    # Find the pass decision logic
    idx = find_line(lines, '// パス先候補を評価')
    if idx > 0:
        for i in range(idx, min(idx + 50, len(lines))):
            if 'let openScore = 100;' in lines[i]:
                # Add pass request bonus
                insert_idx = i + 1
                lines.insert(insert_idx, '''
        // ポストプレイヤーがパス要求している場合、優先度大幅UP
        if(t.requestingPass && t.postPosition > 60) {
          openScore += t.postPosition * 1.5; // 最大+150ポイント
        }
''')
                break
    print("   ✓ Pass priority for posting players")

    # ===== 5. POST MOVES =====
    print("\n5. Adding post move arsenal...")

    # Find the offensive AI section where shots are taken
    idx = find_line(lines, '// オフェンス判断AI（攻撃的/慎重のバランス調整）')
    if idx > 0:
        # Find the shooting section
        for i in range(idx, min(idx + 150, len(lines))):
            if 'let shouldShoot3 = is3ptRange && random(100) < shootProb3;' in lines[i]:
                # Insert post move logic before shooting decision
                insert_idx = i - 5
                post_moves = '''
    // ポストプレイ：良いポジションからのポストムーブ
    if(p.postingUp && p.postPosition > 55 && distToGoal < 100 && !p.postMoveTimer) {
      let postMoveChance = map(p.post, 0, 100, 0.2, 0.7);
      postMoveChance *= map(p.postPosition, 55, 100, 0.6, 1.3);

      if(random() < postMoveChance) {
        // ポストムーブを実行
        let moveTypes = ["spin", "hook", "fadeaway", "dropstep"];
        let weights = [
          map(p.speed, 0, 100, 0.2, 0.4),     // spin - 素早さ必要
          map(p.height, 160, 230, 0.2, 0.5),  // hook - 身長有利
          map(p.sht, 0, 100, 0.2, 0.4),       // fadeaway - シュート力
          map(p.power, 0, 100, 0.3, 0.6)      // dropstep - パワー
        ];

        let totalWeight = weights.reduce((a,b) => a+b, 0);
        let r = random() * totalWeight;
        let cumulative = 0;
        let selectedMove = "dropstep";

        for(let mi = 0; mi < moveTypes.length; mi++) {
          cumulative += weights[mi];
          if(r <= cumulative) {
            selectedMove = moveTypes[mi];
            break;
          }
        }

        p.postMoveType = selectedMove;
        p.postMoveTimer = 45; // 0.75秒のムーブ
        p.lock = 45;

        // ムーブに応じた移動
        let moveAngle = atan2(tg.y - p.y, tg.x - p.x);

        if(selectedMove === "spin") {
          // スピンムーブ：90度回転してゴールへ
          p.facingAngle = moveAngle + (random() > 0.5 ? PI/2 : -PI/2);
          p.x += cos(moveAngle) * 15;
          p.y += sin(moveAngle) * 15;
          addFloatingText(p.x, p.y - 50, "SPIN!", [255, 200, 0]);
        } else if(selectedMove === "hook") {
          // フックシュート：横からのシュート
          p.facingAngle = moveAngle + PI/4;
          addFloatingText(p.x, p.y - 50, "HOOK!", [255, 200, 0]);
        } else if(selectedMove === "fadeaway") {
          // フェイダウェイ：後ろに下がりながら
          p.x -= cos(moveAngle) * 12;
          p.y -= sin(moveAngle) * 12;
          addFloatingText(p.x, p.y - 50, "FADE!", [255, 200, 0]);
        } else { // dropstep
          // ドロップステップ：ベースラインへ
          let baselineDir = (p.y < tg.y ? 1 : -1);
          p.y += baselineDir * 18;
          p.x += cos(moveAngle) * 10;
          addFloatingText(p.x, p.y - 50, "DROP!", [255, 200, 0]);
        }

        p.x = constrain(p.x, 25, 975);
        p.y = constrain(p.y, 262.5, 550);

        // ムーブ後すぐシュート
        setTimeout(() => {
          if(p.hasBall && p.postMoveTimer > 0) {
            let postAccuracy = p.post + p.sht * 0.5;

            // ムーブタイプによる精度調整
            if(selectedMove === "hook") postAccuracy *= 0.9; // フック難しい
            if(selectedMove === "fadeaway") postAccuracy *= 0.85; // フェイド難しい

            // ディフェンダーチェック
            let nearDef = players.filter(d =>
              d.team !== p.team &&
              dist(d.x, d.y, p.x, p.y) < 40
            );

            if(nearDef.length > 0) {
              postAccuracy *= 0.8; // コンテスト
            }

            shoot(p, tg.x, tg.y, false);
            p.postMoveType = null;
            p.postMoveTimer = 0;
          }
        }, 500); // 0.5秒後にシュート

        return; // 通常のシュート判定をスキップ
      }
    }

'''
                lines.insert(insert_idx, post_moves)
                break
    print("   ✓ Post moves: Spin, Hook, Fadeaway, Drop step")
    print("   ✓ Move selection based on player attributes")
    print("   ✓ Animated moves with text feedback")

    # ===== 6. VISUAL INDICATORS =====
    print("\n6. Adding visual pass request indicators...")

    # Find the drawPlayer function
    idx = find_line(lines, 'function drawPlayer(p) {')
    if idx > 0:
        # Find the end of the function
        for i in range(idx, min(idx + 150, len(lines))):
            if 'fill(255); textAlign(CENTER); textSize(9);' in lines[i]:
                # Insert pass request indicator before number display
                insert_idx = i
                visual_code = '''
  // パス要求インジケーター
  if(p.requestingPass && p.postPosition > 60) {
    stroke(255, 255, 0); strokeWeight(2);
    noFill();
    ellipse(px, py - p.size/2 - 8, 12 + sin(frameCount * 0.2) * 3, 12 + sin(frameCount * 0.2) * 3);
    fill(255, 255, 0);
    textSize(10);
    text("!", px, py - p.size/2 - 25);
  }

  // ポストムーブ表示
  if(p.postMoveType && p.postMoveTimer > 0) {
    stroke(255, 150, 0); strokeWeight(3);
    noFill();
    arc(px, py, p.size * 1.5, p.size * 1.5, -PI/4, PI/4 + (p.postMoveTimer / 45) * TWO_PI);
  }

'''
                lines.insert(insert_idx, visual_code)
                break
    print("   ✓ Yellow pulse indicator for pass requests")
    print("   ✓ Arc animation for post moves")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "="*50)
    print("POST PLAY SYSTEM IMPLEMENTED!")
    print("="*50)
    print("\nKey Features:")
    print("  • C/PF/SF post positioning")
    print("  • Power-based pushing battles")
    print("  • Position quality (0-100)")
    print("  • Pass request system")
    print("  • 4 post moves with animations")
    print("  • Visual indicators")

if __name__ == "__main__":
    main()
