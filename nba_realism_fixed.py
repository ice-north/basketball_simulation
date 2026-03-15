#!/usr/bin/env python3
"""
NBA Realism Improvements - Fixed Version
Applies changes one at a time to avoid conflicts
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

    print("=== NBA REALISM IMPROVEMENTS (FIXED) ===\n")

    # ===== 1. ADD PLAYER STATES =====
    print("1. Adding player states...")

    idx = find_line(lines, 'dribbleMoveTimer: 0,')
    if idx > 0:
        insert_idx = idx + 1
        lines.insert(insert_idx, '''      // NBA Realism states
      jumpShooting: false,
      jumpShootPhase: 0,
      jumpShootTarget: null,
      constantMotion: false,
      motionTimer: 0,
      motionType: null,
''')
    print("   ✓ States added")

    # ===== 2. ADD PACE CONTROL VARIABLES =====
    print("\n2. Adding pace control...")

    idx = find_line(lines, 'let gameSpeed = 1;')
    if idx > 0:
        lines.insert(idx + 1, '''let desiredPace = "normal";
let paceMultiplier = 1.0;
''')
    print("   ✓ Pace variables added")

    # ===== 3. PACE CALCULATION IN DRAW =====
    print("\n3. Adding pace calculation...")

    idx = find_line(lines, 'function draw() {')
    if idx > 0:
        for i in range(idx, min(idx + 30, len(lines))):
            if 'background(34, 139, 34);' in lines[i]:
                pace_calc = '''
  // Pace control
  let scoreDiff = scorePlayer - scoreDefender;
  if(abs(scoreDiff) >= 10) {
    paceMultiplier = scoreDiff > 0 ? 0.75 : 1.3;
    desiredPace = scoreDiff > 0 ? "slow" : "fast";
  } else {
    paceMultiplier = 1.0;
    desiredPace = "normal";
  }
  if(gameTime < 120) paceMultiplier *= 1.2;

'''
                lines.insert(i + 1, pace_calc)
                break
    print("   ✓ Pace calculation added")

    # ===== 4. OFF-BALL MOVEMENT =====
    print("\n4. Adding off-ball movement...")

    idx = find_line(lines, '// 理想的なオフェンスポジションへ移動（コート全体を使用）')
    if idx > 0:
        # Add motion logic before
        motion = '''        // Constant off-ball motion
        if(!p.motionTimer || p.motionTimer <= 0) {
          p.motionTimer = 120;
          let roll = random();
          if(roll < 0.15 && !p.isCutting) {
            p.motionType = "cut";
            initiateCut(p, random() > 0.5 ? "backdoor" : "baseline");
          } else if(roll < 0.35 && pos !== "C" && pos !== "PF") {
            p.motionType = "spot";
          } else {
            p.motionType = null;
          }
        }
        p.motionTimer--;

        if(p.motionType === "spot") {
          let spotX = tg.x + (tg.x > 500 ? -200 : 200);
          let spotY = tg.y + (p.id % 2 === 0 ? -120 : 120);
          moveToward(p, constrain(spotX, 50, 950), constrain(spotY, 260, 550), speed * 0.6);
          return;
        }

'''
        lines.insert(idx, motion)
    print("   ✓ Off-ball movement added")

    # ===== 5. JUMP SHOT PHYSICS =====
    print("\n5. Adding jump shot animation...")

    idx = find_line(lines, '// アイソレーション表示')
    if idx > 0:
        jump_anim = '''
  // Jump shot animation
  if(p.jumpShooting) {
    p.jumpShootPhase++;
    if(p.jumpShootPhase <= 60) {
      let progress = p.jumpShootPhase / 60;
      p.z = sin(progress * PI) * map(p.jmp, 0, 100, 25, 50);

      if(p.jumpShootPhase === 30 && p.jumpShootTarget && p.hasBall) {
        // Release at apex
        let tgt = p.jumpShootTarget;
        shoot(p, tgt.x, tgt.y, tgt.is3pt);
      }
    } else {
      p.jumpShooting = false;
      p.jumpShootPhase = 0;
      p.z = 0;
    }
  }

'''
        lines.insert(idx, jump_anim)
    print("   ✓ Jump shot animation added")

    # ===== 6. MODIFY SHOOT TO USE JUMP =====
    print("\n6. Modifying shoot function...")

    idx = find_line(lines, 'function shoot(s, tx, ty, is3pt) {')
    if idx > 0:
        for i in range(idx, min(idx + 5, len(lines))):
            if 's.hasBall = false;' in lines[i] and 'mustShoot' in lines[i]:
                # Add jump shot initiation before this line
                old_line = lines[i]
                indent = '  '
                new_code = indent + 'if(!s.jumpShooting) {\n'
                new_code += indent + '  s.jumpShooting = true;\n'
                new_code += indent + '  s.jumpShootPhase = 0;\n'
                new_code += indent + '  s.jumpShootTarget = {x: tx, y: ty, is3pt: is3pt};\n'
                new_code += indent + '  s.lock = 60;\n'
                new_code += indent + '  return;\n'
                new_code += indent + '}\n'
                new_code += indent + '// Actual shot release\n'
                new_code += old_line
                lines[i] = new_code
                break
    print("   ✓ Shoot function modified")

    # ===== 7. DRIBBLE SPEED LIMIT =====
    print("\n7. Adding dribble speed limitation...")

    # Find where ball handler sets sprint speed
    idx = find_line(lines, '// ③速攻機会があれば突撃')
    if idx > 0:
        for i in range(idx, min(idx + 20, len(lines))):
            if 'p.speedMultiplier = SPEED_SPRINT;' in lines[i]:
                indent = len(lines[i]) - len(lines[i].lstrip())
                limit_code = ' ' * indent + '// Dribble speed limit\n'
                limit_code += ' ' * indent + 'if(p.hasBall && p.handling < 90) {\n'
                limit_code += ' ' * indent + '  let maxSpeed = map(p.handling, 0, 100, SPEED_JOG, SPEED_SPRINT);\n'
                limit_code += ' ' * indent + '  p.speedMultiplier = min(p.speedMultiplier, maxSpeed);\n'
                limit_code += ' ' * indent + '} else {\n'
                limit_code += ' ' * indent + '  '

                lines[i] = limit_code + lines[i]

                # Add closing brace
                for j in range(i + 1, min(i + 10, len(lines))):
                    if 'moveToward(p, tg.x, tg.y' in lines[j]:
                        lines[j] = lines[j].rstrip() + '\n' + ' ' * indent + '}\n'
                        break
                break
    print("   ✓ Dribble speed limit added")

    # ===== 8. FAST BREAK ADVANTAGE =====
    print("\n8. Adding fast break advantage detection...")

    idx = find_line(lines, '// ③速攻機会があれば突撃')
    if idx > 0:
        # Add before the fast break logic
        advantage_code = '''    // Fast break advantage detection
    let attackers = teammates.filter(t => {
      let ahead = p.team === "PlayerTeam" ? t.x > 600 : t.x < 400;
      return ahead && dist(t.x, t.y, tg.x, tg.y) < 300;
    }).length + 1;
    let defenders = players.filter(d => {
      if(d.team === p.team) return false;
      let back = p.team === "PlayerTeam" ? d.x > 600 : d.x < 400;
      return back && dist(d.x, d.y, tg.x, tg.y) < 300;
    }).length;
    let hasAdvantage = attackers > defenders;
    let isBreakaway = attackers === 1 && defenders === 0;

'''
        lines.insert(idx, advantage_code)
    print("   ✓ Fast break detection added")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("NBA REALISM IMPROVEMENTS APPLIED!")
    print("=" * 60)

if __name__ == "__main__":
    main()
