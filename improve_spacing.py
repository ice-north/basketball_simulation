#!/usr/bin/env python3
"""
Improve floor spacing to prevent clustering:
1. Increase minimum distance between players (80px → 120px)
2. Use more vertical space - spread players up/down
3. Adjust position-based spacing to use full court width
4. Reduce pass interception threshold
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

    # ===== 1. Increase minimum spacing between players =====
    idx = find_line(lines, '// 他の味方との重なりを回避（フロアスペーシング強化）')
    if idx > 0:
        # Find and replace minDist
        for i in range(idx, min(idx + 20, len(lines))):
            if 'let minDist = 80;' in lines[i]:
                lines[i] = '      let minDist = 120; // 最小スペース大幅拡大（密集防止）\n'
                break

    # ===== 2. Increase ball handler distance =====
    idx = find_line(lines, '// ボールハンドラーとの距離も確保')
    if idx > 0:
        for i in range(idx, min(idx + 10, len(lines))):
            if 'if(handlerDist < 70)' in lines[i]:
                lines[i] = '        if(handlerDist < 100) { // ボール周りの密集防止\n'
            if '(70 - handlerDist)' in lines[i]:
                lines[i] = lines[i].replace('(70 - handlerDist)', '(100 - handlerDist)')
                break

    # ===== 3. Expand position-based spacing vertically =====
    # PG positioning
    idx = find_line(lines, 'if(pos === "PG") {')
    if idx > 0:
        for i in range(idx, min(idx + 15, len(lines))):
            if 'targetY = tg.y + (p.y > tg.y ? 60 : -60);' in lines[i]:
                lines[i] = '          targetY = tg.y + (p.y > tg.y ? 100 : -100); // 上下に広がる\n'
                break

    # SG positioning - expand corners and wings
    idx = find_line(lines, '} else if(pos === "SG") {')
    if idx > 0:
        for i in range(idx, min(idx + 20, len(lines))):
            if 'targetY = tg.y + (p.id % 2 === 0 ? -120 : 120);' in lines[i]:
                lines[i] = '          targetY = tg.y + (p.id % 2 === 0 ? -140 : 140); // コーナー広く\n'
            elif 'targetY = tg.y + (p.id % 2 === 0 ? -90 : 90);' in lines[i]:
                lines[i] = '          targetY = tg.y + (p.id % 2 === 0 ? -120 : 120); // ウィング広く\n'

    # SF positioning - more vertical spread
    idx = find_line(lines, '} else if(pos === "SF") {')
    if idx > 0:
        for i in range(idx, min(idx + 20, len(lines))):
            if 'targetY = tg.y + (p.id % 2 === 0 ? 100 : -100);' in lines[i]:
                lines[i] = '          targetY = tg.y + (p.id % 2 === 0 ? 130 : -130); // 上下に大きく広がる\n'
            elif 'targetY = tg.y + (p.id % 2 === 0 ? -90 : 90);' in lines[i]:
                lines[i] = '          targetY = tg.y + (p.id % 2 === 0 ? -110 : 110);\n'

    # PF positioning
    idx = find_line(lines, '} else if(pos === "PF") {')
    if idx > 0:
        for i in range(idx, min(idx + 20, len(lines))):
            if 'targetY = tg.y + (p.id % 2 === 0 ? -80 : 80);' in lines[i]:
                lines[i] = '          targetY = tg.y + (p.id % 2 === 0 ? -100 : 100); // エルボー広く\n'
            elif 'targetY = tg.y + (p.id % 2 === 0 ? -65 : 65);' in lines[i]:
                lines[i] = '          targetY = tg.y + (p.id % 2 === 0 ? -85 : 85);\n'

    # C positioning
    idx = find_line(lines, '} else { // C')
    if idx > 0:
        for i in range(idx, min(idx + 20, len(lines))):
            if 'targetY = tg.y + (p.id % 2 === 0 ? 55 : -55);' in lines[i]:
                lines[i] = '          targetY = tg.y + (p.id % 2 === 0 ? 75 : -75); // ローポスト広く\n'
                break

    # ===== 4. Reduce pass interception threshold =====
    idx = find_line(lines, '// 危険な距離：インターセプト能力を考慮')
    if idx > 0:
        for i in range(idx, min(idx + 5, len(lines))):
            if 'let interceptThreshold = map(d.steal, 0, 100, 35, 55);' in lines[i]:
                lines[i] = '      let interceptThreshold = map(d.steal, 0, 100, 25, 40); // インターセプト難易度UP\n'
                break

    # ===== 5. Expand off-ball movement spacing =====
    idx = find_line(lines, '// オープンスペースへ移動')
    if idx > 0:
        for i in range(idx, min(idx + 10, len(lines))):
            if 'let openY = tg.y + (p.y > tg.y ? 80 : -80);' in lines[i]:
                lines[i] = '        let openY = tg.y + (p.y > tg.y ? 120 : -120); // より離れたスペースへ\n'
                break

    # ===== 6. Expand defense spacing =====
    # Find defense positioning
    idx = find_line(lines, 'p.state = "defense"')
    if idx > 0:
        # Look for defensive positioning in the next 100 lines
        for i in range(idx, min(idx + 100, len(lines))):
            # Defense spacing for guards
            if 'idealY = pos === "PG" ? 350 : 420;' in lines[i]:
                lines[i] = '        idealY = pos === "PG" ? 320 : 450; // ガード上下広く\n'
            # Defense spacing for forwards/centers
            elif 'idealY = pos === "PF" ? 340 : 430;' in lines[i]:
                lines[i] = '        idealY = pos === "PF" ? 310 : 460; // フォワード上下広く\n'

    # ===== 7. Increase teamwork spacing noise reduction =====
    idx = find_line(lines, '// チームワーク値が低いとランダムなずれ発生')
    if idx > 0:
        for i in range(idx, min(idx + 8, len(lines))):
            if 'let noise = (1.0 - teamworkFactor) * 50;' in lines[i]:
                lines[i] = '      let noise = (1.0 - teamworkFactor) * 40; // ずれを少し抑制\n'
                break

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("✓ Minimum player spacing: 80px → 120px")
    print("✓ Ball handler distance: 70px → 100px")
    print("✓ Vertical spacing expanded (all positions)")
    print("✓ Pass interception threshold reduced: 35-55 → 25-40")
    print("✓ Off-ball movement spacing expanded")
    print("✓ Defense spacing widened")

if __name__ == "__main__":
    main()
