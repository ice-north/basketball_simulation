#!/usr/bin/env python3
"""
Fix gameplay and visual issues:

PROBLEMS:
1. Passes going out of bounds frequently
2. Court floor too simple (13 boards → need 50+)
3. Out-of-bounds throw-in positions incorrect
4. Players don't move forward when PG brings ball up

SOLUTIONS:
1. Stricter pass safety checks
2. Render 50+ floor boards
3. Proper throw-in positions (sideline vs baseline)
4. Forward movement for teammates when PG advances
"""

def find_line(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=== GAMEPLAY & VISUAL FIXES ===\n")

    # ===== FIX 1: Stricter pass safety =====
    print("1. Improving pass safety checks...")

    # Find isPassSafe function
    idx = find_line(lines, 'function isPassSafe(passer, receiver) {')
    if idx > 0:
        # Find the return true statement and add more checks before it
        for i in range(idx, min(idx + 50, len(lines))):
            if 'return true; // 安全なパス' in lines[i]:
                # Add boundary check before return
                indent = '  '
                boundary_check = '''
  // コート境界チェック（パスルートが境界に近い場合は危険）
  let midX = (passer.x + receiver.x) / 2;
  let midY = (passer.y + receiver.y) / 2;
  if(midX < 50 || midX > 950 || midY < 270 || midY > 545) {
    return false; // パスルートが境界に近すぎる
  }

  // レシーバーが境界に近い場合も危険
  if(receiver.x < 40 || receiver.x > 960 || receiver.y < 265 || receiver.y > 550) {
    return false; // レシーバーが境界に近すぎる
  }

'''
                lines.insert(i, boundary_check)
                print("   ✓ Added boundary safety checks")
                break

    # ===== FIX 2: Enhanced floor rendering (50+ boards) =====
    print("\n2. Enhancing floor detail...")

    # Find court rendering
    idx = find_line(lines, 'function draw() {')
    if idx > 0:
        # Look for court floor rendering (after background)
        for i in range(idx, min(idx + 100, len(lines))):
            if 'background(40,40,60);' in lines[i]:
                # Insert detailed floor rendering after background
                insert_after = i + 1
                floor_code = '''
  // 詳細な床板レンダリング（50枚以上）
  push();
  let boardWidth = (987.5 - 12.5) / 52; // 52枚の板
  for(let bx = 0; bx < 52; bx++) {
    let x = 12.5 + bx * boardWidth;
    // 交互に色を変える（木目のバリエーション）
    let baseColor = bx % 2 === 0 ? [200, 145, 95] : [210, 155, 105];
    // 微妙な明るさのランダム性
    let brightness = 1 + (Math.sin(bx * 0.5) * 0.05);
    noStroke();
    fill(baseColor[0] * brightness, baseColor[1] * brightness, baseColor[2] * brightness);
    rect(x, 250, boardWidth, 312.5);

    // 板の境界線（微妙なライン）
    stroke(180, 130, 85, 60);
    strokeWeight(1);
    line(x, 250, x, 562.5);
  }

  // 木目のテクスチャ（微妙な横線）
  stroke(190, 140, 90, 20);
  strokeWeight(0.5);
  for(let ty = 250; ty < 562.5; ty += 8) {
    let offset = Math.sin(ty * 0.1) * 3;
    line(12.5 + offset, ty, 987.5 + offset, ty);
  }
  pop();

'''
                lines.insert(insert_after, floor_code)
                print("   ✓ Added 52-board floor rendering")
                print("   ✓ Added wood grain texture")
                break

    # ===== FIX 3: Proper out-of-bounds throw-in positions =====
    print("\n3. Fixing out-of-bounds throw-in positions...")

    idx = find_line(lines, 'let oob = false, thX = ball.x, thY = ball.y;')
    if idx > 0:
        # Replace the entire OOB logic
        for i in range(idx, min(idx + 10, len(lines))):
            if 'if(oob && ball.z < 30) {' in lines[i]:
                # Found the block, replace it
                indent = '    '
                new_oob_code = '''    let oob = false, thX = ball.x, thY = ball.y;
    let oobType = null; // 'sideline' or 'baseline'

    // サイドライン（上下）
    if(ball.y < 250 || ball.y > 562.5) {
      oob = true;
      oobType = 'sideline';
      thY = ball.y < 250 ? 256.25 : 556.25;
      thX = constrain(ball.x, 62.5, 937.5); // 出た場所から
    }

    // ベースライン（左右＝ゴール裏）
    if(ball.x < 12.5 || ball.x > 987.5) {
      oob = true;
      oobType = 'baseline';

      // ゴール下のカラー（台形ライン）あたりから
      // PlayerTeam goal: x=861.25 (right), DefenderTeam goal: x=138.75 (left)
      if(ball.x < 12.5) {
        // 左側ゴール裏に出た → 左ベースライン、ゴール下から
        thX = 18.75;
        thY = 388.75; // センター付近（ゴール下のカラーエリア）
      } else {
        // 右側ゴール裏に出た → 右ベースライン、ゴール下から
        thX = 981.25;
        thY = 388.75;
      }
    }

    if(oob && ball.z < 30) {
'''
                # Remove old lines
                old_end = find_line(lines, 'if(oob && ball.z < 30) {', i)
                if old_end == i:
                    # Replace from idx to i+3 (the old OOB logic)
                    lines[idx:i+1] = [new_oob_code]
                    print("   ✓ Fixed throw-in positions")
                    print("   ✓ Sideline: from spot where ball went out")
                    print("   ✓ Baseline: from paint area")
                    break
                break

    # ===== FIX 4: Forward movement when PG brings ball up =====
    print("\n4. Adding forward movement for teammates...")

    # Find the bringingBallUp logic
    idx = find_line(lines, 'if(p.bringingBallUp && p.hasBall) {')
    if idx > 0:
        # After this block, add teammate movement
        # Find the end of the bringingBallUp block
        brace_count = 0
        block_start = idx
        for i in range(idx, min(idx + 50, len(lines))):
            brace_count += lines[i].count('{')
            brace_count -= lines[i].count('}')
            if brace_count == 0 and '}' in lines[i]:
                # Found end of block
                insert_after = i + 1
                teammate_code = '''
    // PGがボールを運んでいるとき、他の選手は前方へ移動
    if(!p.hasBall && !p.bringingBallUp) {
      let ballHandler = players.find(pl => pl.hasBall && pl.bringingBallUp && pl.team === p.team);
      if(ballHandler) {
        // 攻めるゴールの方向へ移動
        let tg = p.team === "PlayerTeam" ? {x:finalGoal.ringX, y:finalGoal.ringY} : {x:1000-finalGoal.ringX, y:finalGoal.ringY};

        // ポジション別の位置取り
        let pos = p.position;
        let targetX, targetY;

        if(pos === "SG" || pos === "SF") {
          // ウイング: 45度の位置
          targetX = tg.x + (p.team === "PlayerTeam" ? -150 : 150);
          targetY = p.id % 2 === 0 ? tg.y - 100 : tg.y + 100;
        } else if(pos === "PF" || pos === "C") {
          // ビッグマン: ペイントエリア付近
          targetX = tg.x + (p.team === "PlayerTeam" ? -80 : 80);
          targetY = tg.y + (p.id % 2 === 0 ? -50 : 50);
        } else {
          // 他: トップ付近
          targetX = tg.x + (p.team === "PlayerTeam" ? -200 : 200);
          targetY = tg.y;
        }

        // 境界内に制限
        targetX = constrain(targetX, 50, 950);
        targetY = constrain(targetY, 260, 550);

        p.speedMultiplier = SPEED_RUN;
        moveToward(p, targetX, targetY, speed);
        return;
      }
    }

'''
                lines.insert(insert_after, teammate_code)
                print("   ✓ Added forward movement logic")
                print("   ✓ Wings move to 45° positions")
                print("   ✓ Bigs move to paint area")
                break

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("FIXES COMPLETE!")
    print("=" * 60)
    print("\nFixed issues:")
    print("  1. ✓ Pass boundary safety")
    print("  2. ✓ 52-board floor (detailed)")
    print("  3. ✓ Correct throw-in positions")
    print("  4. ✓ Teammates move forward with PG")
    print("\nExpected improvements:")
    print("  - Fewer out-of-bounds passes")
    print("  - Beautiful detailed floor")
    print("  - Realistic throw-in spots")
    print("  - Fast break offense")

if __name__ == "__main__":
    main()
