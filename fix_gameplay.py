#!/usr/bin/env python3
"""
Fix gameplay issues:
1. Ball transition: PG carries, SG supports, SF/PF/C spread to spaces
2. Loose ball: only closest 1-2 players per team chase
3. Shooting aggression: players attack goal more actively
4. Jittering: smooth player movement with stop detection
"""

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Task 1: Increase shooting aggression (lines 519-533)
    # Find and replace shooting logic
    for i in range(len(lines)):
        # Increase shoot chance for all positions
        if "let shootDist = 160, shootChance = 0.08;" in lines[i]:
            lines[i] = "    let shootDist = 170, shootChance = 0.15; // 積極性UP\n"
        elif 'if(p.position === "SG") { shootDist = 220; shootChance = 0.12; }' in lines[i]:
            lines[i] = '    if(p.position === "SG") { shootDist = 240; shootChance = 0.22; } // SGは積極的にシュート\n'
        elif 'else if(p.position === "SF") { shootDist = 190; shootChance = 0.09; }' in lines[i]:
            lines[i] = '    else if(p.position === "SF") { shootDist = 210; shootChance = 0.18; }\n'
        elif 'else if(p.position === "C" || p.position === "PF") { shootDist = 130; shootChance = 0.12; }' in lines[i]:
            lines[i] = '    else if(p.position === "C" || p.position === "PF") { shootDist = 150; shootChance = 0.25; } // インサイドは高確率\n'
        elif 'else if(p.position === "PG") { shootDist = 200; shootChance = 0.06; }' in lines[i]:
            lines[i] = '    else if(p.position === "PG") { shootDist = 220; shootChance = 0.14; } // PGも積極的に\n'

        # Increase close-range shooting
        elif "if(!pressured && dToGoal < shootDist * 0.7) shootChance *= 2.5;" in lines[i]:
            lines[i] = "    if(!pressured && dToGoal < shootDist * 0.8) shootChance *= 3.5; // ゴール近くは超積極的\n"
        elif "if(pressured) shootChance *= 0.7;" in lines[i]:
            lines[i] = "    if(pressured) shootChance *= 0.8; // プレッシャー時も少し積極的\n"

    # Task 2: Fix jittering - add stop detection to moveToward (lines 909-928)
    for i in range(len(lines)):
        if "function moveToward(p, tx, ty, targetSpeed) {" in lines[i]:
            # Find the end of the function and replace it
            j = i + 1
            indent = "  "
            new_code = []
            new_code.append(lines[i])  # Keep function declaration
            new_code.append(f"{indent}// 目標位置に十分近い場合は停止（震え防止）\n")
            new_code.append(f"{indent}let distToTarget = dist(p.x, p.y, tx, ty);\n")
            new_code.append(f"{indent}if(distToTarget < 3) {{\n")
            new_code.append(f"{indent}  p.currentSpeed = 0;\n")
            new_code.append(f"{indent}  return;\n")
            new_code.append(f"{indent}}}\n")
            new_code.append(f"{indent}\n")

            # Copy original acceleration code
            while j < len(lines) and "p.y = constrain" not in lines[j]:
                new_code.append(lines[j])
                j += 1

            # Add modified movement with distance-based damping
            new_code.append(f"{indent}// 現在の速度で移動（近距離は減速）\n")
            new_code.append(f"{indent}let a = atan2(ty-p.y, tx-p.x);\n")
            new_code.append(f"{indent}if(p.currentSpeed > 0.3) p.facingAngle = a; // 移動中のみ向きを更新\n")
            new_code.append(f"{indent}\n")
            new_code.append(f"{indent}// 目標に近づくと自動的に減速（震え防止）\n")
            new_code.append(f"{indent}let dampingFactor = distToTarget < 20 ? map(distToTarget, 0, 20, 0.3, 1.0) : 1.0;\n")
            new_code.append(f"{indent}let actualSpeed = p.currentSpeed * dampingFactor;\n")
            new_code.append(f"{indent}\n")
            new_code.append(f"{indent}p.x = constrain(p.x + cos(a)*actualSpeed, 25, 975);\n")
            new_code.append(f"{indent}p.y = constrain(p.y + sin(a)*actualSpeed, 262.5, 550);\n")
            new_code.append("}\n")

            # Skip to next function
            while j < len(lines) and lines[j].strip() != "}":
                j += 1
            j += 1  # Skip closing brace

            # Replace the function
            lines[i:j] = new_code
            break

    # Task 3: Fix loose ball - only closest 1-2 players chase (offense side, line 714-728)
    for i in range(len(lines)):
        if "// ボール保持者がいない場合（ルーズボール/リバウンド）" in lines[i]:
            # Find the entire block and replace it
            j = i
            while j < len(lines) and "} else {" not in lines[j]:
                j += 1

            new_code = []
            new_code.append(lines[i])  # Keep comment
            new_code.append("      if(ball.z < 80 && !players.some(pl=>pl.hasBall)) {\n")
            new_code.append("        // チーム内で最も近い1-2人だけがルーズボールを追う\n")
            new_code.append("        let teammates = players.filter(pl => pl.team === p.team);\n")
            new_code.append("        let sortedByDist = teammates.sort((a, b) => \n")
            new_code.append("          dist(a.x, a.y, ball.x, ball.y) - dist(b.x, b.y, ball.x, ball.y));\n")
            new_code.append("        let myRank = sortedByDist.findIndex(pl => pl.id === p.id);\n")
            new_code.append("        \n")
            new_code.append("        if(myRank < 2) { // 最も近い2人だけ追う\n")
            new_code.append("          p.speedMultiplier = SPEED_SPRINT;\n")
            new_code.append("          moveToward(p, ball.x, ball.y, speed);\n")
            new_code.append("          if(dist(p.x,p.y,ball.x,ball.y) < 30 && ball.z < 40 && p.lock <= 0) {\n")
            new_code.append("            let reboundChance = map(p.rebound, 0, 100, 0.2, 0.7);\n")
            new_code.append("            reboundChance *= (1 + (p.jmp + p.power) / 400);\n")
            new_code.append("            reboundChance *= map(p.height, 160, 230, 0.85, 1.15);\n")
            new_code.append("            if(random() < reboundChance) {\n")
            new_code.append("              p.hasBall = true; possession = p.team; shotClock = 24;\n")
            new_code.append("              addFloatingText(p.x, p.y - 40, \"OFF REBOUND!\", [255, 200, 100]);\n")
            new_code.append("            }\n")
            new_code.append("          }\n")
            new_code.append("        } else {\n")
            new_code.append("          // 他の選手は理想位置へ移動\n")
            new_code.append("          let idealX = tg.x - (p.team === \"PlayerTeam\" ? 1 : -1) * 200;\n")
            new_code.append("          let idealY = tg.y + (p.id % 3 - 1) * 80;\n")
            new_code.append("          moveToward(p, constrain(idealX,50,950), constrain(idealY,260,550), speed*0.5);\n")
            new_code.append("        }\n")

            lines[i:j] = new_code
            break

    # Task 4: Fix defense loose ball (line 872-883)
    for i in range(len(lines)):
        if "// ルーズボール/リバウンド：全速力で追う" in lines[i]:
            j = i
            # Find the end of the block (next blank line or different logic)
            while j < len(lines) and (lines[j].strip() == "" or "reboundChance" in lines[j] or "moveToward(p, ball.x, ball.y" in lines[j] or "p.speedMultiplier = SPEED_SPRINT" in lines[j] or "if(dist(p.x,p.y,ball.x,ball.y)" in lines[j]):
                j += 1

            new_code = []
            new_code.append("      // ルーズボール/リバウンド：チーム内で最も近い2人だけが追う\n")
            new_code.append("      let teammates = players.filter(pl => pl.team === p.team);\n")
            new_code.append("      let sortedByDist = teammates.sort((a, b) => \n")
            new_code.append("        dist(a.x, a.y, ball.x, ball.y) - dist(b.x, b.y, ball.x, ball.y));\n")
            new_code.append("      let myRank = sortedByDist.findIndex(pl => pl.id === p.id);\n")
            new_code.append("      \n")
            new_code.append("      if(myRank < 2) { // 最も近い2人だけ追う\n")
            new_code.append("        p.speedMultiplier = SPEED_SPRINT;\n")
            new_code.append("        moveToward(p, ball.x, ball.y, speed);\n")
            new_code.append("        if(dist(p.x,p.y,ball.x,ball.y) < 30 && ball.z < 40 && p.lock <= 0) {\n")
            new_code.append("          let reboundChance = map(p.rebound, 0, 100, 0.3, 0.9);\n")
            new_code.append("          reboundChance *= (1 + (p.jmp + p.power) / 400);\n")
            new_code.append("          reboundChance *= map(p.height, 160, 230, 0.85, 1.15);\n")
            new_code.append("          if(random() < reboundChance) {\n")
            new_code.append("            p.hasBall = true; possession = p.team; shotClock = 24;\n")
            new_code.append("          }\n")
            new_code.append("        }\n")
            new_code.append("      } else {\n")
            new_code.append("        // 他の選手はディフェンス位置へ戻る\n")
            new_code.append("        let defX = (p.team === \"PlayerTeam\" ? 875 : 125);\n")
            new_code.append("        let defY = 400 + (p.id % 3 - 1) * 70;\n")
            new_code.append("        moveToward(p, defX, defY, speed * 0.6);\n")
            new_code.append("      }\n")

            lines[i:j] = new_code
            break

    # Task 5: Improve ball transition - PG carries, others spread
    for i in range(len(lines)):
        if '// フロアバランスを考慮したポジション別位置取り' in lines[i]:
            # Find PG logic
            j = i
            while j < len(lines) and 'if(pos === "PG")' not in lines[j]:
                j += 1

            if j < len(lines):
                # Replace PG logic
                k = j
                while k < len(lines) and "} else if(pos ===" not in lines[k]:
                    k += 1

                new_code = []
                new_code.append('      if(pos === "PG") {\n')
                new_code.append('        // PG: ボールハンドラーなら積極的に前進、そうでなければサポート位置\n')
                new_code.append('        if(handler && handler.position === "PG") {\n')
                new_code.append('          // 他のPGがハンドラーの場合はサポート\n')
                new_code.append('          targetX = tg.x - side * 250;\n')
                new_code.append('          targetY = tg.y + (p.y > tg.y ? 60 : -60);\n')
                new_code.append('          p.speedMultiplier = SPEED_JOG;\n')
                new_code.append('        } else {\n')
                new_code.append('          // PGがボールを運ぶ：積極的に前進\n')
                new_code.append('          targetX = tg.x - side * 180;\n')
                new_code.append('          targetY = tg.y;\n')
                new_code.append('          p.speedMultiplier = SPEED_RUN;\n')
                new_code.append('        }\n')

                lines[j:k] = new_code

            # Now improve SG to support PG
            for m in range(i, len(lines)):
                if '} else if(pos === "SG")' in lines[m]:
                    # Find end of SG block
                    n = m + 1
                    while n < len(lines) and "} else if(pos ===" not in lines[n]:
                        n += 1

                    new_code = []
                    new_code.append('      } else if(pos === "SG") {\n')
                    new_code.append('        // SG: パスを受けられる位置（サポート）\n')
                    new_code.append('        let handlerDist = handler ? dist(handler.x, handler.y, tg.x, tg.y) : 999;\n')
                    new_code.append('        if(handlerDist < 200) {\n')
                    new_code.append('          // ハンドラーがゴール近くならコーナー3P\n')
                    new_code.append('          targetX = tg.x - side * 90;\n')
                    new_code.append('          targetY = tg.y + (p.id % 2 === 0 ? -110 : 110);\n')
                    new_code.append('        } else {\n')
                    new_code.append('          // ハンドラーのサポート位置（パスを受けやすい）\n')
                    new_code.append('          targetX = tg.x - side * 220;\n')
                    new_code.append('          targetY = tg.y + (p.id % 2 === 0 ? -80 : 80);\n')
                    new_code.append('        }\n')
                    new_code.append('        p.speedMultiplier = SPEED_RUN;\n')

                    lines[m:n] = new_code
                    break

            # SF/PF/C spread to open spaces - already good, just add comment
            for m in range(i, len(lines)):
                if '} else if(pos === "SF")' in lines[m]:
                    lines[m] = '      } else if(pos === "SF") {\n'
                    lines[m+1] = '        // SF: 相手コートのスペースへ広がる\n'
                    break

            break

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("✓ Shooting aggression increased")
    print("✓ Jittering fixed with stop detection")
    print("✓ Loose ball: only closest 1-2 players chase")
    print("✓ Ball transition: PG carries, SG supports, SF/PF/C spread")

if __name__ == "__main__":
    main()
