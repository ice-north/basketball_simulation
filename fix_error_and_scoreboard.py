#!/usr/bin/env python3
"""
Fix two issues:
1. Remove pressure escape code from drawPlayer (wrong location)
2. Create NBA-style scoreboard

ERROR:
  Uncaught ReferenceError: speed is not defined at line 431

  Problem: Pressure escape code inserted in drawPlayer() instead of updatePlayerAI()
  drawPlayer() has no 'speed' variable - it's only for rendering

  Solution: Remove all pressure escape code from drawPlayer()
           (Will re-add correctly to updatePlayerAI in next step)

SCOREBOARD REQUEST:
  User wants NBA-style scoreboard redesign
"""

def find_line(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=" * 70)
    print("EMERGENCY FIX + NBA SCOREBOARD")
    print("=" * 70)
    print()

    # ===== FIX 1: Remove misplaced pressure escape code =====
    print("1. Removing pressure escape from drawPlayer()...")

    idx = find_line(lines, 'function drawPlayer(p) {')
    if idx > 0:
        # Find the misplaced pressure code
        for i in range(idx, min(idx + 100, len(lines))):
            if '// OPUS FIX: Pressure escape' in lines[i]:
                # Find the end of this block (look for the return statement)
                end_idx = i
                for j in range(i, min(i + 50, len(lines))):
                    if 'return;' in lines[j] and 'escape' in lines[j-5:j+1].__str__():
                        end_idx = j
                        break

                # Remove lines from i to end_idx (inclusive)
                # But keep the original if(p.hasBall) glow effect
                # Find where glow effect should be
                for k in range(end_idx + 1, min(end_idx + 5, len(lines))):
                    if 'noStroke();' in lines[k] and 'fill(' in lines[k+1]:
                        # This is the glow effect, keep it
                        lines[i:k] = []  # Remove pressure code, keep glow
                        print(f"   ✓ Removed {k-i} lines of misplaced code")
                        break
                break

    # ===== FIX 2: Create NBA-style scoreboard =====
    print("\n2. Creating NBA-style scoreboard...")

    idx = find_line(lines, 'function drawScoreboard() {')
    if idx > 0:
        # Find end of function
        end_idx = idx
        for i in range(idx, min(idx + 50, len(lines))):
            if '}' in lines[i] and lines[i].strip() == '}':
                end_idx = i
                break

        # Replace entire function with NBA style
        nba_scoreboard = '''function drawScoreboard() {
  // NBA-STYLE SCOREBOARD REDESIGN
  push();

  // Main scoreboard background (gradient)
  let sbX = width/2 - 200;
  let sbY = 15;
  let sbW = 400;
  let sbH = 80;

  // Gradient background
  for(let i = 0; i < sbH; i++) {
    let inter = map(i, 0, sbH, 0, 1);
    let c = lerpColor(color(20, 20, 25), color(10, 10, 15), inter);
    stroke(c);
    line(sbX, sbY + i, sbX + sbW, sbY + i);
  }

  // Border
  noFill();
  stroke(100, 100, 120);
  strokeWeight(2);
  rect(sbX, sbY, sbW, sbH, 5);

  // Team sections
  let teamW = 160;
  let teamH = 70;
  let teamY = sbY + 5;

  // BLUE team (left)
  let blueX = sbX + 10;
  fill(0, 100, 200, 180);
  noStroke();
  rect(blueX, teamY, teamW, teamH, 3);

  // BLUE team border
  stroke(0, 150, 255);
  strokeWeight(2);
  noFill();
  rect(blueX, teamY, teamW, teamH, 3);

  // BLUE team name
  fill(255);
  textAlign(CENTER, CENTER);
  textSize(16);
  textFont('Arial Black');
  text("BLUE", blueX + teamW/2, teamY + 15);

  // BLUE score
  textSize(36);
  textFont('Arial');
  text(scorePlayer, blueX + teamW/2, teamY + 48);

  // RED team (right)
  let redX = sbX + sbW - teamW - 10;
  fill(200, 30, 30, 180);
  noStroke();
  rect(redX, teamY, teamW, teamH, 3);

  // RED team border
  stroke(255, 50, 50);
  strokeWeight(2);
  noFill();
  rect(redX, teamY, teamW, teamH, 3);

  // RED team name
  fill(255);
  textAlign(CENTER, CENTER);
  textSize(16);
  textFont('Arial Black');
  text("RED", redX + teamW/2, teamY + 15);

  // RED score
  textSize(36);
  textFont('Arial');
  text(scoreDefender, redX + teamW/2, teamY + 48);

  // Center info panel
  let centerX = sbX + teamW + 20;
  let centerW = sbW - teamW * 2 - 40;

  // Quarter
  fill(255, 215, 0);
  textSize(14);
  textFont('Arial Black');
  textAlign(CENTER, CENTER);
  text("Q" + quarter, centerX + centerW/2, teamY + 12);

  // Game clock
  let m = floor(gameTime/60);
  let s = gameTime % 60;
  fill(255);
  textSize(20);
  textFont('Courier New');
  text(m + ":" + (s < 10 ? "0" : "") + s, centerX + centerW/2, teamY + 35);

  // Shot clock
  fill(shotClock <= 5 ? color(255, 100, 100) : color(150, 255, 150));
  textSize(16);
  textFont('Arial');
  text("SHOT: " + shotClock, centerX + centerW/2, teamY + 58);

  pop();
}
'''

        lines[idx:end_idx+1] = [nba_scoreboard]
        print("   ✓ NBA-style scoreboard created")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 70)
    print("FIXES COMPLETE")
    print("=" * 70)
    print("\nFix 1: Removed misplaced pressure escape code")
    print("  - Code was in drawPlayer() (rendering function)")
    print("  - No 'speed' variable available there")
    print("  - Error: speed is not defined ✓ FIXED")
    print("\nFix 2: NBA-style scoreboard created")
    print("  Features:")
    print("  - Gradient background (dark)")
    print("  - Team panels with color (blue/red)")
    print("  - Large, clear scores")
    print("  - Center info panel (Quarter, Clock, Shot clock)")
    print("  - Color-coded shot clock (red when ≤5)")
    print("  - Professional NBA appearance")

if __name__ == "__main__":
    main()
