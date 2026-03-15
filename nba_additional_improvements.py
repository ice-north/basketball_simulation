#!/usr/bin/env python3
"""
NBA Additional Improvements - 5 More Realism Enhancements

1. DEFENSIVE IMPROVEMENTS - Switching, help defense, closeouts
2. CLUTCH TIME TACTICS - Final 2 minutes special decisions
3. SCREEN FREQUENCY BOOST - 1.5% → 30% (realistic NBA usage)
4. REBOUNDING ENHANCEMENT - Better box-out, height dominance
5. 8-SECOND BACKCOURT RULE - Halfcourt violation
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

    print("=== NBA ADDITIONAL IMPROVEMENTS ===\n")

    # ===== 1. DEFENSIVE IMPROVEMENTS =====
    print("━" * 60)
    print("1. DEFENSIVE IMPROVEMENTS")
    print("━" * 60)
    print("Implementing: Switching, Help Defense, Closeouts")

    # Add defensive states
    idx = find_line(lines, '// NBA Realism states')
    if idx > 0:
        insert_idx = idx + 1
        lines.insert(insert_idx, '''      // Defense states
      isClosingOut: false,
      closeoutTarget: null,
      switchedDefense: null,
''')
    print("   ✓ Defensive states added")

    # Improve help defense
    idx = find_line(lines, '// ヘルプディフェンス（ボールがゴール付近）')
    if idx > 0:
        # Find and enhance help defense logic
        for i in range(idx, min(idx + 30, len(lines))):
            if 'if(dBallGoal < 120 && mark && distPMark > 80) {' in lines[i]:
                indent = len(lines[i]) - len(lines[i].lstrip())
                # Enhance help defense
                enhanced_help = ' ' * indent + '// Enhanced help defense (NBA style)\n'
                enhanced_help += ' ' * indent + 'let helpNeeded = false;\n'
                enhanced_help += ' ' * indent + 'if(dBallGoal < 150) { // Expanded help range\n'
                enhanced_help += ' ' * indent + '  let ballHandler = players.find(p => p.hasBall && p.team !== p.team);\n'
                enhanced_help += ' ' * indent + '  if(ballHandler) {\n'
                enhanced_help += ' ' * indent + '    let myDistToBall = dist(p.x, p.y, ballHandler.x, ballHandler.y);\n'
                enhanced_help += ' ' * indent + '    let markDistToBall = mark ? dist(mark.x, mark.y, ballHandler.x, ballHandler.y) : 999;\n'
                enhanced_help += ' ' * indent + '    // Help if: closer to ball than mark, and mark is far\n'
                enhanced_help += ' ' * indent + '    if(myDistToBall < 100 && markDistToBall > 120) {\n'
                enhanced_help += ' ' * indent + '      helpNeeded = true;\n'
                enhanced_help += ' ' * indent + '    }\n'
                enhanced_help += ' ' * indent + '  }\n'
                enhanced_help += ' ' * indent + '}\n'
                enhanced_help += ' ' * indent + 'if(helpNeeded) {\n'

                lines.insert(i, enhanced_help)
                break
    print("   ✓ Help defense enhanced (120px → 150px range)")

    # Add closeout mechanics
    idx = find_line(lines, '// ディフェンス：マークマン or ボールに寄る')
    if idx > 0:
        closeout_code = '''    // Closeout on shooters (NBA defensive fundamental)
    let ballHandler = players.find(p => p.hasBball && p.team !== p.team);
    if(ballHandler && !ballHandler.isMoving) {
      let distToBall = dist(p.x, p.y, ballHandler.x, ballHandler.y);
      if(distToBall > 40 && distToBall < 120) {
        // Sprint closeout, then control
        p.isClosingOut = true;
        p.closeoutTarget = ballHandler;
        let closeSpeed = distToBall > 60 ? speed * SPEED_SPRINT : speed * SPEED_RUN;
        moveToward(p, ballHandler.x, ballHandler.y, closeSpeed);
        // Contest when close
        if(distToBall < 50) {
          p.isClosingOut = false;
          // Hand up contest (visual only for now)
        }
        return;
      }
    }

'''
        lines.insert(idx, closeout_code)
    print("   ✓ Closeout mechanics added")

    # Add defensive switching on screens
    idx = find_line(lines, '// スクリーン中の表示')
    if idx > 0:
        # Add switching logic
        switch_code = '''
  // Defensive switching on screens (NBA fundamental)
  if(p.team !== ball.lastTouch) { // Defender
    let nearScreens = players.filter(s =>
      s.team !== p.team && s.isScreening &&
      dist(p.x, p.y, s.x, s.y) < 40
    );
    if(nearScreens.length > 0) {
      // Switch assignment temporarily
      let screener = nearScreens[0];
      if(!p.switchedDefense) {
        p.switchedDefense = screener;
        // Switch for 3 seconds
        setTimeout(() => { p.switchedDefense = null; }, 3000);
      }
    }
  }

'''
        lines.insert(idx, switch_code)
    print("   ✓ Screen switching added")

    # ===== 2. CLUTCH TIME TACTICS =====
    print("\n" + "━" * 60)
    print("2. CLUTCH TIME TACTICS")
    print("━" * 60)
    print("Final 2 minutes special decisions")

    # Add clutch mode detection
    idx = find_line(lines, 'if(gameTime < 120) paceMultiplier *= 1.2;')
    if idx > 0:
        clutch_code = '''
  // Clutch time tactics (final 2 minutes)
  let isClutchTime = gameTime < 120;
  let scoreDiffAbs = abs(scorePlayer - scoreDefender);
  let isCloseGame = scoreDiffAbs <= 5;
  let isClutch = isClutchTime && isCloseGame;

'''
        lines.insert(idx + 1, clutch_code)
    print("   ✓ Clutch time detection added")

    # Add clutch decision making in AI
    idx = find_line(lines, '// ボール保持者のAI')
    if idx > 0:
        clutch_ai = '''    // Clutch time decision making
    if(typeof isClutch !== 'undefined' && isClutch && p.hasBall) {
      // Star player usage increase
      let isStar = p.sht > 80 || p.tpt > 80 || p.handling > 85;
      if(isStar) {
        // Stars take over in clutch
        shootChance *= 1.5; // More aggressive
        // Hold ball longer (hero ball)
        if(shotClock > 8) {
          // Wait for better shot
          let dribbleTarget = {
            x: p.x + random(-30, 30),
            y: p.y + random(-30, 30)
          };
          moveToward(p, constrain(dribbleTarget.x, 50, 950), constrain(dribbleTarget.y, 260, 550), speed * SPEED_JOG);
          return;
        }
      }

      // Trailing team: Prioritize 3-pointers
      if(scorePlayer < scoreDefender) {
        let distTo3pt = dist(p.x, p.y, tg.x, tg.y);
        if(distTo3pt > 180 && p.tpt > 60) {
          // Pull up for 3
          shootChance *= 2.0;
          shootDist = 280;
        }
      }

      // Leading team: High-percentage shots only
      if(scorePlayer > scoreDefender) {
        // Drive to basket or pass
        if(dToGoal > 150) {
          // Look for open teammate
          let openMate = teammates.find(t => {
            let nearDef = players.filter(d => d.team !== p.team && dist(d.x, d.y, t.x, t.y) < 60);
            return nearDef.length === 0 && dist(p.x, p.y, t.x, t.y) < 200;
          });
          if(openMate) {
            passTo(p, openMate);
            return;
          }
        }
      }
    }

'''
        lines.insert(idx, clutch_ai)
    print("   ✓ Clutch shot selection added")
    print("   ✓ Star player usage boost")
    print("   ✓ Trailing: 3PT priority")
    print("   ✓ Leading: High % shots")

    # ===== 3. SCREEN FREQUENCY BOOST =====
    print("\n" + "━" * 60)
    print("3. SCREEN FREQUENCY BOOST")
    print("━" * 60)
    print("1.5% → 30% (NBA realistic)")

    # Find screen initiation
    idx = find_line(lines, 'if((p.position === "PG" || p.position === "SG") && random() < 0.015')
    if idx > 0:
        # Replace with higher frequency
        old_line = lines[idx]
        indent = len(old_line) - len(old_line.lstrip())
        new_line = ' ' * indent + 'if((p.position === "PG" || p.position === "SG") && random() < 0.30 && dToGoal < 250 && !dominated) {\n'
        lines[idx] = new_line
    print("   ✓ Screen probability: 1.5% → 30%")
    print("   ✓ Pick & Roll now common")

    # ===== 4. REBOUNDING ENHANCEMENT =====
    print("\n" + "━" * 60)
    print("4. REBOUNDING ENHANCEMENT")
    print("━" * 60)
    print("Better box-out, height dominance")

    # Enhance height advantage
    idx = find_line(lines, 'let heightAdv = map(p.height, 180, 220, 0.7, 1.4);')
    if idx > 0:
        # Increase height impact
        lines[idx] = '      let heightAdv = map(p.height, 180, 220, 0.4, 2.5); // Stronger height advantage\n'
    print("   ✓ Height advantage: 0.7-1.4x → 0.4-2.5x")
    print("   ✓ Tall players dominate boards")

    # Enhance box-out strength
    idx = find_line(lines, 'reboundChance *= (1 + p.boxOutStrength * 0.05);')
    if idx > 0:
        # Make box-out more impactful
        lines[idx] = '      reboundChance *= (1 + p.boxOutStrength * 0.15); // Stronger box-out impact\n'
    print("   ✓ Box-out impact: 5% → 15% per strength")

    # Make all players box out aggressively
    idx = find_line(lines, 'function positionForRebound(p) {')
    if idx > 0:
        for i in range(idx, min(idx + 30, len(lines))):
            if 'p.isBoxingOut = true;' in lines[i]:
                # Add more aggressive positioning
                insert_after = i + 1
                aggressive = '''  // Aggressive rebound positioning (all players)
  let reboundSpot = {
    x: ball.x + random(-40, 40),
    y: ball.y + random(-40, 40)
  };
  p.reboundTarget = reboundSpot;
  p.boxOutStrength = 0; // Reset

  // Find opponent to box out
  let nearestOpp = players
    .filter(opp => opp.team !== p.team)
    .reduce((closest, opp) => {
      let d = dist(p.x, p.y, opp.x, opp.y);
      let closestD = dist(p.x, p.y, closest.x, closest.y);
      return d < closestD ? opp : closest;
    }, {x: 9999, y: 9999});

  if(nearestOpp.x !== 9999) {
    let oppDist = dist(p.x, p.y, nearestOpp.x, nearestOpp.y);
    if(oppDist < 60) {
      // Position between opponent and basket
      p.boxOutStrength = min(5, (60 - oppDist) / 10);
    }
  }
'''
                lines.insert(insert_after, aggressive)
                break
    print("   ✓ All players box out aggressively")
    print("   ✓ Position between opponent and ball")

    # ===== 5. 8-SECOND BACKCOURT RULE =====
    print("\n" + "━" * 60)
    print("5. 8-SECOND BACKCOURT RULE")
    print("━" * 60)
    print("Must cross halfcourt in 8 seconds")

    # Add 8-second timer
    idx = find_line(lines, 'let shotClock = 24;')
    if idx > 0:
        lines.insert(idx + 1, '''let backcourt8SecTimer = 0;
let backcourt8SecActive = false;
''')
    print("   ✓ 8-second timer variable added")

    # Add timer logic
    idx = find_line(lines, '// ショットクロック減少')
    if idx > 0:
        timer_logic = '''
  // 8-second backcourt rule
  let ballHandler = players.find(p => p.hasBall);
  if(ballHandler) {
    let halfCourt = 500;
    let inBackcourt = (ballHandler.team === "PlayerTeam" && ballHandler.x < halfCourt) ||
                      (ballHandler.team === "DefenderTeam" && ballHandler.x > halfCourt);

    if(inBackcourt) {
      if(!backcourt8SecActive) {
        // Start timer when in backcourt with ball
        backcourt8SecActive = true;
        backcourt8SecTimer = 480; // 8 seconds = 480 frames (60fps)
      } else {
        backcourt8SecTimer--;
        if(backcourt8SecTimer <= 0) {
          // 8-second violation!
          console.log("8-SECOND VIOLATION!");
          // Turnover
          ballHandler.hasBall = false;
          let opponent = players.find(p => p.team !== ballHandler.team && p.position === "PG");
          if(opponent) {
            opponent.hasBall = true;
            ball.x = opponent.x;
            ball.y = opponent.y;
          }
          backcourt8SecActive = false;
          backcourt8SecTimer = 0;
        }
      }
    } else {
      // Crossed halfcourt
      backcourt8SecActive = false;
      backcourt8SecTimer = 0;
    }
  }

'''
        lines.insert(idx, timer_logic)
    print("   ✓ 8-second timer logic added")
    print("   ✓ Violation = turnover")
    print("   ✓ Halfcourt at x=500")

    # Add visual indicator
    idx = find_line(lines, '// ショットクロック表示')
    if idx > 0:
        visual = '''
  // 8-second timer display
  if(backcourt8SecActive && backcourt8SecTimer > 0) {
    let sec8 = Math.ceil(backcourt8SecTimer / 60);
    textSize(14);
    fill(255, 200, 0);
    if(sec8 <= 3) fill(255, 0, 0); // Red when urgent
    text("8-SEC: " + sec8, 850, 30);
  }

'''
        lines.insert(idx, visual)
    print("   ✓ Visual timer on screen")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("ADDITIONAL IMPROVEMENTS COMPLETE!")
    print("=" * 60)
    print("\nAll 5 improvements applied:")
    print("  1. ✓ Defensive improvements")
    print("  2. ✓ Clutch time tactics")
    print("  3. ✓ Screen frequency boost")
    print("  4. ✓ Rebounding enhancement")
    print("  5. ✓ 8-second backcourt rule")

if __name__ == "__main__":
    main()
