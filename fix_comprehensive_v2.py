#!/usr/bin/env python3
"""
Comprehensive fixes for three major issues:

1. Allow out-of-bounds movement (still restricted)
2. Proper offensive positioning (PG ball handler, SF/PF/C near goal, SG support)
3. Pressure escape (dribble away or pass when defender close)

USER REQUESTS:
  1. アウトオブバウンズ時、選手はコート外にも行けるようにしてください。
     やはりボールを拾いにいけません
  2. 攻め側のチームは、SF、PF、Cは相手ゴールの近くまで移動。
     PGがメインでボール運び、SGが補助的役割
  3. ボールを保持している選手にディフェンスが近づいてきたら、
     ドリブルで逃げる、或いは味方にパスをして危険を回避してください

ISSUE 1 ANALYSIS:
  Current constraints in moveToward() line 1435-1436:
    // Collision avoidance
    p.x += cos(pushAngle) * pushForce;
    p.y += sin(pushAngle) * pushForce;
    p.x = constrain(p.x, 25, 975);  ← BLOCKS out-of-bounds
    p.y = constrain(p.y, 262.5, 550); ← BLOCKS out-of-bounds

  Even with fetching phase expansion at line 1462-1467,
  collision avoidance re-applies normal bounds!

  Solution: Apply same expansion logic to collision code

ISSUE 2 ANALYSIS:
  Current offensive positioning (line 815-987):
    - All positions spread out
    - No clear role distinction
    - Centers already fixed (30 units from goal)
    - Need to push SF/PF closer to goal
    - PG should stay back as primary ball handler
    - SG supports between PG and forwards

ISSUE 3 ANALYSIS:
  No pressure escape currently exists
  Need to add logic when defender < 40 units from ball handler:
    Option 1: Dribble escape (speed burst away)
    Option 2: Emergency pass (safer)
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
    print("COMPREHENSIVE FIX: Bounds + Positioning + Pressure")
    print("=" * 70)
    print()

    # ===== FIX 1: Collision avoidance bounds during fetch =====
    print("1. Fixing collision bounds during ball fetch...")

    idx = find_line(lines, '// 押し出し（衝突回避）')
    if idx > 0:
        # Find the constrain lines after collision
        for i in range(idx, min(idx + 15, len(lines))):
            if 'p.x = constrain(p.x, 25, 975);' in lines[i]:
                # Replace both X and Y constraints
                indent = len(lines[i]) - len(lines[i].lstrip())
                new_code = ' ' * indent + '// OPUS FIX: Allow out-of-bounds during fetch (same as movement)\n'
                new_code += ' ' * indent + 'let collMinX = 25, collMaxX = 975, collMinY = 262.5, collMaxY = 550;\n'
                new_code += ' ' * indent + 'if(throwInState && throwInState.thrower === p.id && throwInState.phase === "fetching") {\n'
                new_code += ' ' * indent + '  collMinX = 0; collMaxX = 1000; collMinY = 240; collMaxY = 575;\n'
                new_code += ' ' * indent + '}\n'
                new_code += ' ' * indent + 'p.x = constrain(p.x, collMinX, collMaxX);\n'

                # Check next line for Y constraint
                if i + 1 < len(lines) and 'p.y = constrain(p.y, 262.5, 550);' in lines[i + 1]:
                    new_code += ' ' * indent + 'p.y = constrain(p.y, collMinY, collMaxY);\n'
                    lines[i] = new_code
                    lines[i + 1] = ''  # Remove old Y line
                    print("   ✓ Collision bounds expand during ball fetch")
                    break

    # ===== FIX 2: Adjust SF/PF positioning closer to goal =====
    print("\n2. Moving SF/PF closer to goal (offensive role)...")

    # SF positioning
    idx = find_line(lines, '} else if(pos === "SF") {')
    if idx > 0:
        for i in range(idx, min(idx + 20, len(lines))):
            if 'targetX = tg.x - side * 220;' in lines[i] and 'ウィング' in lines[i]:
                # Move closer for wing
                lines[i] = lines[i].replace('side * 220', 'side * 180')
                print("   ✓ SF wing: 220 → 180 (closer to goal)")
                break

        for i in range(idx, min(idx + 20, len(lines))):
            if 'targetX = tg.x - side * 140;' in lines[i] and 'ミッドレンジ' in lines[i]:
                # Move closer for midrange
                lines[i] = lines[i].replace('side * 140', 'side * 100')
                print("   ✓ SF midrange: 140 → 100 (closer to goal)")
                break

    # PF positioning
    idx = find_line(lines, '} else if(pos === "PF") {')
    if idx > 0:
        for i in range(idx, min(idx + 20, len(lines))):
            if 'targetX = tg.x - side * 90;' in lines[i] and 'エルボー' in lines[i]:
                # Already close, keep it
                print("   ✓ PF elbow: 90 (good position)")
                break

        for i in range(idx, min(idx + 20, len(lines))):
            if 'targetX = tg.x - side * 70;' in lines[i] and 'ハイポスト' in lines[i]:
                # Move closer
                lines[i] = lines[i].replace('side * 70', 'side * 50')
                print("   ✓ PF high post: 70 → 50 (closer to goal)")
                break

    # PG positioning - keep back as ball handler
    idx = find_line(lines, 'if(pos === "PG") {')
    if idx > 0:
        for i in range(idx, min(idx + 15, len(lines))):
            if 'targetX = tg.x - side * 280;' in lines[i]:
                # Keep far back (already good)
                print("   ✓ PG stays back: 280 (ball handler position)")
                break

    # SG positioning - support role
    idx = find_line(lines, '} else if(pos === "SG") {')
    if idx > 0:
        # SG should be between PG and forwards
        for i in range(idx, min(idx + 20, len(lines))):
            if 'targetX = tg.x - side * 100;' in lines[i] and 'コーナー3P' in lines[i]:
                # Adjust corner position
                lines[i] = lines[i].replace('side * 100', 'side * 120')
                print("   ✓ SG corner: 100 → 120 (support position)")
                break

        for i in range(idx, min(idx + 20, len(lines))):
            if 'targetX = tg.x - side * 260;' in lines[i] and 'ウィング3P' in lines[i]:
                # Adjust wing position (closer support)
                lines[i] = lines[i].replace('side * 260', 'side * 200')
                print("   ✓ SG wing: 260 → 200 (support PG)")
                break

    # ===== FIX 3: Add pressure escape logic =====
    print("\n3. Adding pressure escape (dribble/pass)...")

    # Find where ball handler logic is
    idx = find_line(lines, 'if(p.hasBall) {')
    if idx > 0:
        # Insert pressure escape at beginning of ball handler logic
        indent = len(lines[idx]) - len(lines[idx].lstrip())

        pressure_code = '\n' + ' ' * indent + '// OPUS FIX: Pressure escape\n'
        pressure_code += ' ' * indent + 'let nearDefenders = players.filter(d => d.team !== p.team && dist(d.x, d.y, p.x, p.y) < 60);\n'
        pressure_code += ' ' * indent + 'let pressured = nearDefenders.length > 0 && nearDefenders[0] && dist(p.x, p.y, nearDefenders[0].x, nearDefenders[0].y) < 40;\n'
        pressure_code += ' ' * indent + '\n'
        pressure_code += ' ' * indent + 'if(pressured && !p.pressureEscaping) {\n'
        pressure_code += ' ' * indent + '  let defender = nearDefenders[0];\n'
        pressure_code += ' ' * indent + '  let teammates = players.filter(t => t.team === p.team && t.id !== p.id && !t.hasBall);\n'
        pressure_code += ' ' * indent + '  \n'
        pressure_code += ' ' * indent + '  // Option 1: Find safe pass (preferred)\n'
        pressure_code += ' ' * indent + '  let safeTeammates = teammates.filter(t => {\n'
        pressure_code += ' ' * indent + '    let defDist = dist(t.x, t.y, defender.x, defender.y);\n'
        pressure_code += ' ' * indent + '    return defDist > 80 && isPassSafe(p, t);\n'
        pressure_code += ' ' * indent + '  });\n'
        pressure_code += ' ' * indent + '  \n'
        pressure_code += ' ' * indent + '  if(safeTeammates.length > 0 && random() < 0.7) {\n'
        pressure_code += ' ' * indent + '    // Emergency pass to open teammate\n'
        pressure_code += ' ' * indent + '    let target = safeTeammates.sort((a,b) => \n'
        pressure_code += ' ' * indent + '      dist(b.x, b.y, defender.x, defender.y) - dist(a.x, a.y, defender.x, defender.y))[0];\n'
        pressure_code += ' ' * indent + '    passTo(p, target);\n'
        pressure_code += ' ' * indent + '    addFloatingText(p.x, p.y - 30, \"ESCAPE PASS\", [100, 255, 255]);\n'
        pressure_code += ' ' * indent + '    p.pressureEscaping = false;\n'
        pressure_code += ' ' * indent + '    return;\n'
        pressure_code += ' ' * indent + '  } else {\n'
        pressure_code += ' ' * indent + '    // Option 2: Dribble escape (no safe pass)\n'
        pressure_code += ' ' * indent + '    p.pressureEscaping = true;\n'
        pressure_code += ' ' * indent + '    p.escapeTimer = 30; // 0.5 seconds\n'
        pressure_code += ' ' * indent + '    \n'
        pressure_code += ' ' * indent + '    // Calculate escape direction (away from defender)\n'
        pressure_code += ' ' * indent + '    let escapeAngle = atan2(p.y - defender.y, p.x - defender.x);\n'
        pressure_code += ' ' * indent + '    let escapeX = p.x + cos(escapeAngle) * 100;\n'
        pressure_code += ' ' * indent + '    let escapeY = p.y + sin(escapeAngle) * 100;\n'
        pressure_code += ' ' * indent + '    p.escapeTarget = {x: constrain(escapeX, 50, 950), y: constrain(escapeY, 270, 540)};\n'
        pressure_code += ' ' * indent + '    addFloatingText(p.x, p.y - 30, \"DRIBBLE ESCAPE\", [255, 255, 100]);\n'
        pressure_code += ' ' * indent + '  }\n'
        pressure_code += ' ' * indent + '}\n'
        pressure_code += ' ' * indent + '\n'
        pressure_code += ' ' * indent + '// Execute dribble escape\n'
        pressure_code += ' ' * indent + 'if(p.pressureEscaping && p.escapeTimer > 0) {\n'
        pressure_code += ' ' * indent + '  p.escapeTimer--;\n'
        pressure_code += ' ' * indent + '  p.speedMultiplier = SPEED_SPRINT; // Fast escape\n'
        pressure_code += ' ' * indent + '  moveToward(p, p.escapeTarget.x, p.escapeTarget.y, speed);\n'
        pressure_code += ' ' * indent + '  if(p.escapeTimer <= 0 || dist(p.x, p.y, p.escapeTarget.x, p.escapeTarget.y) < 20) {\n'
        pressure_code += ' ' * indent + '    p.pressureEscaping = false;\n'
        pressure_code += ' ' * indent + '  }\n'
        pressure_code += ' ' * indent + '  return;\n'
        pressure_code += ' ' * indent + '}\n'

        lines.insert(idx + 1, pressure_code)
        print("   ✓ Pressure escape logic added")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 70)
    print("FIXES COMPLETE")
    print("=" * 70)
    print("\nFix 1: Out-of-Bounds Movement")
    print("  ✓ Collision avoidance also allows out-of-bounds during fetch")
    print("  ✓ No more blocking from collision constraints")
    print("\nFix 2: Offensive Positioning")
    print("  Position  | Before | After  | Role")
    print("  ----------|--------|--------|------------------")
    print("  PG        | 280    | 280    | Ball handler (back)")
    print("  SG corner | 100    | 120    | Support role")
    print("  SG wing   | 260    | 200    | Support PG")
    print("  SF wing   | 220    | 180    | Closer to goal")
    print("  SF mid    | 140    | 100    | Attack position")
    print("  PF high   | 70     | 50     | Very close")
    print("  C low     | 30     | 30     | In the paint")
    print("\nFix 3: Pressure Escape")
    print("  When defender within 40 units:")
    print("    Priority 1: Find safe teammate → Emergency pass")
    print("    Priority 2: No safe pass → Dribble escape")
    print("  ✓ Speed burst away from pressure")
    print("  ✓ Visual feedback (\"ESCAPE PASS\" / \"DRIBBLE ESCAPE\")")

if __name__ == "__main__":
    main()
