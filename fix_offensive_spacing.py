#!/usr/bin/env python3
"""
Fix offensive spacing - spread wider to use full court

USER REPORT:
  攻めている側の選手が、中心に近い位置でパスを回し合って
  ボールを失う場面が多くみられます。攻めている側はコートを
  広く使い（ライン近くまで移動するように）拡がるようにしてください。

PROBLEM ANALYSIS:
  Current positioning (in basketball-sim.html around line 890-950):

  SG (Shooting Guard):
    - Corner 3P: targetX = tg.x - side * 100  (too close!)
    - Corner: targetY = ±140 (too narrow!)
    - Wing: targetY = ±120 (too narrow!)

  SF (Small Forward):
    - Wing: targetY = ±100 (too narrow!)
    - Midrange: targetY = ±90 (too narrow!)

  PF (Power Forward):
    - Elbow: targetY = ±100 (could be wider)

  Result: Players cluster in the middle, easy to defend

COURT DIMENSIONS:
  - Width (X): 12.5 ~ 987.5 (975 units total)
  - Height (Y): 250 ~ 562.5 (312.5 units total)
  - Center Y: 406.25
  - Sideline distance from center: ±156.25

GOAL POSITIONS:
  - PlayerTeam (right): ringX ≈ 861.25, ringY = 406.25
  - DefenderTeam (left): ringX ≈ 138.75, ringY = 406.25

IDEAL SPACING (NBA style):

  Position | Location      | X from goal | Y from center | Notes
  ---------|---------------|-------------|---------------|------------------
  PG       | Top of key    | -300        | ±0-50         | Primary handler
  SG       | Wing/Corner   | -150-250    | ±130-150      | 3PT shooter
  SF       | Wing/Midrange | -200-250    | ±100-130      | Versatile
  PF       | Elbow/High    | -100-150    | ±90-120       | Mid/post
  C        | Low post      | -60-100     | ±70-90        | Paint area

SOLUTION:
  Increase Y-axis spread (move closer to sidelines):
  - SG corners: Y = ±145-155 (near sideline 156.25)
  - SG wings: Y = ±130-140
  - SF wings: Y = ±120-130
  - PF elbows: Y = ±110-120
  - C low post: Y = ±80-90

  Benefits:
  - Wider spacing → harder to defend
  - More passing lanes
  - Better 3PT opportunities
  - Prevents clustering
"""

def find_line(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("=== OFFENSIVE SPACING FIX ===\n")

    # ===== FIX 1: SG positioning (wider spread) =====
    print("1. Widening SG positioning...")

    idx = find_line(lines, '} else if(pos === "SG") {')
    if idx > 0:
        # Find the corner 3P section
        for i in range(idx, idx + 15):
            if 'targetY = tg.y + (p.id % 2 === 0 ? -140 : 140);' in lines[i] and 'コーナー広く' in lines[i]:
                # Increase corner spread
                lines[i] = lines[i].replace('-140 : 140', '-150 : 150')
                print(f"   ✓ SG corner spread: ±140 → ±150 (line {i+1})")
                break

        # Find the wing section
        for i in range(idx, idx + 15):
            if 'targetY = tg.y + (p.id % 2 === 0 ? -120 : 120);' in lines[i] and 'ウィング広く' in lines[i]:
                # Increase wing spread
                lines[i] = lines[i].replace('-120 : 120', '-135 : 135')
                print(f"   ✓ SG wing spread: ±120 → ±135 (line {i+1})")
                break

    # ===== FIX 2: SF positioning (wider spread) =====
    print("\n2. Widening SF positioning...")

    idx = find_line(lines, '} else if(pos === "SF") {')
    if idx > 0:
        # Find wing position
        for i in range(idx, idx + 15):
            if 'targetY = tg.y + (p.id % 2 === 0 ? 100 : -100);' in lines[i]:
                # Increase wing spread
                lines[i] = lines[i].replace('100 : -100', '125 : -125')
                print(f"   ✓ SF wing spread: ±100 → ±125 (line {i+1})")
                break

        # Find midrange position
        for i in range(idx, idx + 15):
            if 'targetY = tg.y + (p.id % 2 === 0 ? -90 : 90);' in lines[i]:
                # Increase midrange spread
                lines[i] = lines[i].replace('-90 : 90', '-110 : 110')
                print(f"   ✓ SF midrange spread: ±90 → ±110 (line {i+1})")
                break

    # ===== FIX 3: PF positioning (wider spread) =====
    print("\n3. Widening PF positioning...")

    idx = find_line(lines, '} else if(pos === "PF") {')
    if idx > 0:
        # Find elbow position
        for i in range(idx, idx + 15):
            if 'targetY = tg.y + (p.id % 2 === 0 ? -100 : 100);' in lines[i] and 'エルボー広く' in lines[i]:
                # Increase elbow spread
                lines[i] = lines[i].replace('-100 : 100', '-115 : 115')
                print(f"   ✓ PF elbow spread: ±100 → ±115 (line {i+1})")
                break

        # Find high post position
        for i in range(idx, idx + 15):
            if 'targetY = tg.y + (p.id % 2 === 0 ? -85 : 85);' in lines[i]:
                # Increase high post spread
                lines[i] = lines[i].replace('-85 : 85', '-100 : 100')
                print(f"   ✓ PF high post spread: ±85 → ±100 (line {i+1})")
                break

    # ===== FIX 4: C positioning (slight adjustment) =====
    print("\n4. Adjusting C positioning...")

    idx = find_line(lines, '} else { // C')
    if idx > 0:
        # Find low post position
        for i in range(idx, idx + 15):
            if 'targetY = tg.y + (p.id % 2 === 0 ? 75 : -75);' in lines[i] and 'ローポスト広く' in lines[i]:
                # Increase low post spread
                lines[i] = lines[i].replace('75 : -75', '85 : -85')
                print(f"   ✓ C low post spread: ±75 → ±85 (line {i+1})")
                break

    # ===== FIX 5: PG transition positioning (wider) =====
    print("\n5. Widening PG transition positioning...")

    idx = find_line(lines, 'if(pos === "SG" || pos === "SF") {')
    if idx > 0:
        # This is in the bringingBallUp section
        for i in range(idx - 5, idx + 5):
            if '// ウイング: 45度の位置' in lines[i]:
                # Find the targetY line
                for j in range(i, i + 3):
                    if 'targetY = p.id % 2 === 0 ? tg.y - 100 : tg.y + 100;' in lines[j]:
                        lines[j] = lines[j].replace('tg.y - 100 : tg.y + 100', 'tg.y - 120 : tg.y + 120')
                        print(f"   ✓ Wing transition spread: ±100 → ±120 (line {j+1})")
                        break
                break

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 60)
    print("SPACING IMPROVEMENTS COMPLETE!")
    print("=" * 60)
    print("\nBefore → After (Y-axis spread from center):")
    print("  SG corner:   ±140 → ±150 (closer to sideline ±156)")
    print("  SG wing:     ±120 → ±135")
    print("  SF wing:     ±100 → ±125")
    print("  SF midrange: ±90  → ±110")
    print("  PF elbow:    ±100 → ±115")
    print("  PF high:     ±85  → ±100")
    print("  C low post:  ±75  → ±85")
    print("\nExpected improvements:")
    print("  ✓ Wider offensive spacing")
    print("  ✓ Players closer to sidelines")
    print("  ✓ More passing lanes")
    print("  ✓ Harder to defend (spread out)")
    print("  ✓ Better 3PT opportunities")
    print("  ✓ Less clustering in middle")
    print("  ✓ Use full court width")

if __name__ == "__main__":
    main()
