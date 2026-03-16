#!/usr/bin/env python3
"""
Major game improvements:

PROBLEMS:
1. 攻める方向が変 / スローインの位置が逆
2. PGがスローイン → C/PFがスローインすべき
3. 守備が浅い → もっとゴール近くで守るべき
4. グラフィックが質素

SOLUTIONS:
1. Fix throw-in position (reverse thX calculation)
2. Change thrower: PG → C/PF (PG receives)
3. Deeper defense positioning (closer to goal)
4. Enhanced graphics: shadows, better court, particles
"""

def find_line(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=== MAJOR GAME IMPROVEMENTS ===\n")

    # ===== FIX 1: Reverse throw-in position =====
    print("1. Fixing throw-in direction...")

    idx = find_line(lines, 'let thX = side === 1 ? 975 : 25;')
    if idx > 0:
        # REVERSE: side === 1 (right goal scored) → throw from left (25)
        lines[idx] = '      let thX = side === 1 ? 25 : 975; // 逆側のベースラインから\n'
        print("   ✓ Fixed throw-in position (reversed)")
        print("   ✓ Now throws from own baseline correctly")

    # ===== FIX 2: C/PF throws, PG receives =====
    print("\n2. Changing thrower to C/PF...")

    # Find startThrowIn function
    idx = find_line(lines, 'function startThrowIn(team, x, y, reason) {')
    if idx > 0:
        for i in range(idx, min(idx + 10, len(lines))):
            if "thrower = players.find(p => p.team === team && p.position === 'PG')" in lines[i]:
                # Change from PG to C or PF
                indent = len(lines[i]) - len(lines[i].lstrip())
                new_line = ' ' * indent + '// C/PFがスローイン（PGが受け取る）\n'
                new_line += ' ' * indent + 'let thrower = players.find(p => p.team === team && (p.position === "C" || p.position === "PF"));\n'
                new_line += ' ' * indent + 'if(!thrower) thrower = players.find(p => p.team === team && p.position === "PG"); // フォールバック\n'
                lines[i] = new_line
                print("   ✓ C/PF now throws in (PG receives)")
                break

    # ===== FIX 3: Deeper defense positioning =====
    print("\n3. Implementing deeper defense...")

    # Find defensive positioning code
    idx = find_line(lines, 'if(pos === "PG" || pos === "SG") {')
    if idx > 0:
        # Look for defensive ideal positions
        found = False
        for i in range(idx, min(idx + 100, len(lines))):
            if 'idealX = p.team === "PlayerTeam" ? 300 : 700;' in lines[i]:
                # Make defense deeper (closer to goal)
                indent = len(lines[i]) - len(lines[i].lstrip())
                # Old: 300/700 (shallow)
                # New: 750/250 (deep, near goal)
                lines[i] = ' ' * indent + 'idealX = p.team === "PlayerTeam" ? 750 : 250; // ゴール近く\n'
                found = True
                print("   ✓ Guards defend deeper (300/700 → 750/250)")
                break

    # Find more defensive positions
    idx = find_line(lines, 'else if(pos === "SF")')
    if idx > 0:
        for i in range(idx, min(idx + 5, len(lines))):
            if 'idealX = p.team === "PlayerTeam" ? 400 : 600;' in lines[i]:
                indent = len(lines[i]) - len(lines[i].lstrip())
                lines[i] = ' ' * indent + 'idealX = p.team === "PlayerTeam" ? 700 : 300; // より深く\n'
                print("   ✓ SF defends deeper (400/600 → 700/300)")
                break

    idx = find_line(lines, 'else { // PF, C')
    if idx > 0:
        for i in range(idx, min(idx + 5, len(lines))):
            if 'idealX = p.team === "PlayerTeam" ? 500 : 500;' in lines[i]:
                indent = len(lines[i]) - len(lines[i].lstrip())
                lines[i] = ' ' * indent + 'idealX = p.team === "PlayerTeam" ? 820 : 180; // ペイントエリア付近\n'
                print("   ✓ Bigs defend deeper (500 → 820/180)")
                break

    # ===== FIX 4: Enhanced graphics =====
    print("\n4. Enhancing graphics...")

    # Add player shadows
    idx = find_line(lines, 'function renderPlayer(p) {')
    if idx > 0:
        # Find the start of the function body
        for i in range(idx, min(idx + 5, len(lines))):
            if '{' in lines[i]:
                insert_after = i + 1
                shadow_code = '''  // 選手の影（リアル）
  let shadowSize = 12 + p.z * 0.15;
  noStroke();
  fill(0, 0, 0, 60);
  ellipse(p.x, p.y, shadowSize, shadowSize * 0.4);

'''
                lines.insert(insert_after, shadow_code)
                print("   ✓ Added realistic player shadows")
                break

    # Enhance ball shadow
    idx = find_line(lines, 'function renderBall() {')
    if idx > 0:
        for i in range(idx, min(idx + 10, len(lines))):
            if 'fill(0,0,0,30);' in lines[i] and 'shadow' in lines[i-1].lower():
                # Enhance shadow
                indent = len(lines[i]) - len(lines[i].lstrip())
                lines[i] = ' ' * indent + 'fill(0, 0, 0, 50 + ball.z * 0.3); // 動的な影\n'
                # Next line is the shadow ellipse
                if 'ellipse(ball.x, ball.y,' in lines[i+1]:
                    lines[i+1] = ' ' * indent + 'ellipse(ball.x, ball.y, 10 + ball.z * 0.1, (10 + ball.z * 0.1) * 0.3);\n'
                print("   ✓ Enhanced ball shadow (dynamic)")
                break

    # Add court shine/reflection
    idx = find_line(lines, 'function renderCourt() {')
    if idx > 0:
        for i in range(idx, min(idx + 20, len(lines))):
            if 'fill(200,150,100);' in lines[i] or 'fill(210,160,110);' in lines[i]:
                # Add subtle gradient for shine
                insert_after = i + 1
                shine_code = '''  // コートの光沢（微妙なグラデーション）
  for(let gx = 12.5; gx < 987.5; gx += 50) {
    let alpha = abs(sin(gx * 0.01)) * 8;
    noStroke();
    fill(255, 255, 255, alpha);
    rect(gx, 250, 50, 312.5);
  }

'''
                lines.insert(insert_after, shine_code)
                print("   ✓ Added court shine effect")
                break

    # Enhance score particles
    idx = find_line(lines, 'for(let i=0;i<30;i++)')
    if idx > 0 and 'particles.push' in lines[idx]:
        # Increase particle count
        lines[idx] = lines[idx].replace('i<30', 'i<50')
        print("   ✓ Increased score particles (30 → 50)")

    # Add player jersey numbers
    idx = find_line(lines, 'function renderPlayer(p) {')
    if idx > 0:
        # Find end of function
        for i in range(idx, min(idx + 50, len(lines))):
            if '  text(p.position' in lines[i]:
                # Add jersey number above position
                insert_before = i
                jersey_code = '''  // ジャージ番号
  fill(255, 255, 255, 180);
  textSize(10);
  textAlign(CENTER);
  text("#" + (p.id + 1), p.x, p.y - p.z - 25);

'''
                lines.insert(insert_before, jersey_code)
                print("   ✓ Added jersey numbers")
                break

    # Add glow effect on ball handler
    idx = find_line(lines, 'if(p.hasBall) {')
    if idx > 0:
        for i in range(idx, min(idx + 10, len(lines))):
            if 'stroke(' in lines[i] and 'strokeWeight(3)' in lines[i+1]:
                # Add glow before existing stroke
                insert_before = i
                indent = len(lines[i]) - len(lines[i].lstrip())
                glow_code = ' ' * indent + '// ボール保持者のグロー効果\n'
                glow_code += ' ' * indent + 'noStroke();\n'
                glow_code += ' ' * indent + 'fill(p.team === "PlayerTeam" ? [100, 150, 255, 40] : [255, 100, 100, 40]);\n'
                glow_code += ' ' * indent + 'ellipse(p.x, p.y - p.z, sz + 8, (sz + 8) * 0.5);\n'
                glow_code += ' ' * indent + '\n'
                lines.insert(insert_before, glow_code)
                print("   ✓ Added glow effect for ball handler")
                break

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("MAJOR IMPROVEMENTS COMPLETE!")
    print("=" * 60)
    print("\nFixed issues:")
    print("  1. ✓ Throw-in direction fixed (now from own baseline)")
    print("  2. ✓ C/PF throws in, PG receives")
    print("  3. ✓ Defense much deeper (near goal)")
    print("  4. ✓ Graphics enhanced:")
    print("      - Player shadows")
    print("      - Dynamic ball shadow")
    print("      - Court shine")
    print("      - More particles")
    print("      - Jersey numbers")
    print("      - Ball handler glow")
    print("\nExpected improvements:")
    print("  - Correct attack direction")
    print("  - Realistic inbound plays (C/PF → PG)")
    print("  - Tighter defense (space protection)")
    print("  - Professional visual quality")

if __name__ == "__main__":
    main()
