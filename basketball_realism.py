#!/usr/bin/env python3
"""
Comprehensive basketball realism improvements:
1. Position-based spacing (PG/SG outside 3P, PF/C near goal)
2. Prevent centers from ball handling
3. Off-ball movement after passing
4. Player collision and positioning battles
5. Pass interception risk assessment
6. Additional basketball elements
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

    # ===== 1. Fix position-based spacing =====
    # Find and replace position-specific positioning
    idx = find_line(lines, '// NBAスタイル：各ポジションの理想的なスポット')
    if idx > 0:
        # Find PG block
        pg_start = find_line(lines, 'if(pos === "PG")', idx)
        sg_start = find_line(lines, '} else if(pos === "SG")', pg_start)

        # Replace PG positioning
        new_pg = []
        new_pg.append('      if(pos === "PG") {\n')
        new_pg.append('        // PG: 3Pライン外（トップオブザキー）\n')
        new_pg.append('        if(handler && handler.position === "PG") {\n')
        new_pg.append('          targetX = tg.x - side * 280; // 3Pライン外\n')
        new_pg.append('          targetY = tg.y + (p.y > tg.y ? 60 : -60);\n')
        new_pg.append('          p.speedMultiplier = SPEED_JOG;\n')
        new_pg.append('        } else {\n')
        new_pg.append('          targetX = tg.x - side * 250; // 前進も3Pライン外\n')
        new_pg.append('          targetY = tg.y;\n')
        new_pg.append('          p.speedMultiplier = SPEED_RUN;\n')
        new_pg.append('        }\n')
        lines[pg_start:sg_start] = new_pg

        # Find SG block
        sg_start = find_line(lines, '} else if(pos === "SG")', idx)
        sf_start = find_line(lines, '} else if(pos === "SF")', sg_start)

        new_sg = []
        new_sg.append('      } else if(pos === "SG") {\n')
        new_sg.append('        // SG: 3Pライン外（ウィング/コーナー）\n')
        new_sg.append('        let handlerDist = handler ? dist(handler.x, handler.y, tg.x, tg.y) : 999;\n')
        new_sg.append('        if(handlerDist < 150) {\n')
        new_sg.append('          // コーナー3P\n')
        new_sg.append('          targetX = tg.x - side * 100;\n')
        new_sg.append('          targetY = tg.y + (p.id % 2 === 0 ? -120 : 120);\n')
        new_sg.append('        } else {\n')
        new_sg.append('          // ウィング3P\n')
        new_sg.append('          targetX = tg.x - side * 260;\n')
        new_sg.append('          targetY = tg.y + (p.id % 2 === 0 ? -90 : 90);\n')
        new_sg.append('        }\n')
        new_sg.append('        p.speedMultiplier = SPEED_RUN;\n')
        lines[sg_start:sf_start] = new_sg

        # Find SF block
        sf_start = find_line(lines, '} else if(pos === "SF")', idx)
        pf_start = find_line(lines, '} else if(pos === "PF")', sf_start)

        new_sf = []
        new_sf.append('      } else if(pos === "SF") {\n')
        new_sf.append('        // SF: ミッドレンジ〜ウィング（柔軟に動く）\n')
        new_sf.append('        let cycle = (frameCount % 600) / 600;\n')
        new_sf.append('        if(cycle > 0.5) {\n')
        new_sf.append('          targetX = tg.x - side * 220; // ウィング\n')
        new_sf.append('          targetY = tg.y + (p.id % 2 === 0 ? 100 : -100);\n')
        new_sf.append('        } else {\n')
        new_sf.append('          targetX = tg.x - side * 140; // ミッドレンジ\n')
        new_sf.append('          targetY = tg.y + (p.id % 2 === 0 ? -90 : 90);\n')
        new_sf.append('        }\n')
        new_sf.append('        p.speedMultiplier = SPEED_RUN;\n')
        lines[sf_start:pf_start] = new_sf

        # Find PF block
        pf_start = find_line(lines, '} else if(pos === "PF")', idx)
        c_start = find_line(lines, '} else { // C', pf_start)

        new_pf = []
        new_pf.append('      } else if(pos === "PF") {\n')
        new_pf.append('        // PF: エルボー〜ハイポスト（ゴールに近い）\n')
        new_pf.append('        let cycle = (frameCount % 480) / 480;\n')
        new_pf.append('        let toElbow = cycle > 0.6;\n')
        new_pf.append('        if(toElbow) {\n')
        new_pf.append('          targetX = tg.x - side * 90; // エルボー\n')
        new_pf.append('          targetY = tg.y + (p.id % 2 === 0 ? -80 : 80);\n')
        new_pf.append('        } else {\n')
        new_pf.append('          targetX = tg.x - side * 130; // ハイポスト\n')
        new_pf.append('          targetY = tg.y + (p.id % 2 === 0 ? -65 : 65);\n')
        new_pf.append('        }\n')
        new_pf.append('        p.speedMultiplier = SPEED_RUN;\n')
        lines[pf_start:c_start] = new_pf

        # Find C block
        c_start = find_line(lines, '} else { // C', idx)
        teamwork_line = find_line(lines, '// チームワーク値が低いとランダムなずれ発生', c_start)

        new_c = []
        new_c.append('      } else { // C\n')
        new_c.append('        // C: ペイント〜ローポスト（最もゴールに近い）\n')
        new_c.append('        let cycle = (frameCount % 300) / 300;\n')
        new_c.append('        if(cycle < 0.7) {\n')
        new_c.append('          // ローポスト（ペイント内）\n')
        new_c.append('          targetX = tg.x - side * 55;\n')
        new_c.append('          targetY = tg.y + (p.id % 2 === 0 ? 55 : -55);\n')
        new_c.append('        } else {\n')
        new_c.append('          // ハイポスト\n')
        new_c.append('          targetX = tg.x - side * 100;\n')
        new_c.append('          targetY = tg.y;\n')
        new_c.append('        }\n')
        new_c.append('        p.speedMultiplier = SPEED_JOG;\n')
        new_c.append('      }\n')
        new_c.append('\n')
        lines[c_start:teamwork_line] = new_c

    # ===== 2. Improve spacing collision avoidance =====
    # Find spacing code
    idx = find_line(lines, '// 他の味方との重なりを回避（フロアスペーシング）')
    if idx > 0:
        j = idx
        while j < len(lines) and 'moveToward(p, constrain(targetX' not in lines[j]:
            j += 1

        new_spacing = []
        new_spacing.append('      // 他の味方との重なりを回避（フロアスペーシング強化）\n')
        new_spacing.append('      let myTeammates = players.filter(t => t.team === p.team && t.id !== p.id && (!handler || t.id !== handler.id));\n')
        new_spacing.append('      for(let t of myTeammates) {\n')
        new_spacing.append('        let dd = dist(targetX, targetY, t.x, t.y);\n')
        new_spacing.append('        let minDist = 80; // 最小スペース拡大\n')
        new_spacing.append('        if(dd < minDist && dd > 0) {\n')
        new_spacing.append('          let pushAng = atan2(targetY - t.y, targetX - t.x);\n')
        new_spacing.append('          let pushStrength = (minDist - dd) * 0.7 * teamworkFactor;\n')
        new_spacing.append('          targetX += cos(pushAng) * pushStrength;\n')
        new_spacing.append('          targetY += sin(pushAng) * pushStrength;\n')
        new_spacing.append('        }\n')
        new_spacing.append('      }\n')
        new_spacing.append('\n')
        new_spacing.append('      // ボールハンドラーとの距離も確保\n')
        new_spacing.append('      if(handler) {\n')
        new_spacing.append('        let handlerDist = dist(targetX, targetY, handler.x, handler.y);\n')
        new_spacing.append('        if(handlerDist < 70) {\n')
        new_spacing.append('          let pushAng = atan2(targetY - handler.y, targetX - handler.x);\n')
        new_spacing.append('          targetX += cos(pushAng) * (70 - handlerDist) * 0.8;\n')
        new_spacing.append('          targetY += sin(pushAng) * (70 - handlerDist) * 0.8;\n')
        new_spacing.append('        }\n')
        new_spacing.append('      }\n')
        new_spacing.append('\n')
        new_spacing.append('\n')
        lines[idx:j] = new_spacing

    # ===== 3. Add pass interception risk assessment =====
    # Find passTo function and add risk check before it's called
    idx = find_line(lines, 'function passTo(passer, receiver) {')
    if idx > 0:
        # Insert new function before passTo
        new_func = []
        new_func.append('function isPassSafe(passer, receiver) {\n')
        new_func.append('  // パスコースの安全性を評価\n')
        new_func.append('  let passX1 = passer.x, passY1 = passer.y;\n')
        new_func.append('  let passX2 = receiver.x, passY2 = receiver.y;\n')
        new_func.append('  let passDist = dist(passX1, passY1, passX2, passY2);\n')
        new_func.append('  \n')
        new_func.append('  // パスコース上のディフェンダーをチェック\n')
        new_func.append('  let defenders = players.filter(d => d.team !== passer.team);\n')
        new_func.append('  for(let d of defenders) {\n')
        new_func.append('    // ディフェンダーとパスラインの距離を計算\n')
        new_func.append('    let lineX = passX2 - passX1;\n')
        new_func.append('    let lineY = passY2 - passY1;\n')
        new_func.append('    let dotProduct = ((d.x - passX1) * lineX + (d.y - passY1) * lineY) / (passDist * passDist);\n')
        new_func.append('    \n')
        new_func.append('    if(dotProduct > 0 && dotProduct < 1) { // ディフェンダーがパスライン上\n')
        new_func.append('      let projX = passX1 + dotProduct * lineX;\n')
        new_func.append('      let projY = passY1 + dotProduct * lineY;\n')
        new_func.append('      let distToLine = dist(d.x, d.y, projX, projY);\n')
        new_func.append('      \n')
        new_func.append('      // 危険な距離：インターセプト能力を考慮\n')
        new_func.append('      let interceptThreshold = map(d.steal, 0, 100, 35, 55);\n')
        new_func.append('      interceptThreshold *= map(d.speed, 0, 100, 0.8, 1.3);\n')
        new_func.append('      \n')
        new_func.append('      if(distToLine < interceptThreshold) {\n')
        new_func.append('        return false; // 危険なパス\n')
        new_func.append('      }\n')
        new_func.append('    }\n')
        new_func.append('  }\n')
        new_func.append('  \n')
        new_func.append('  // レシーバーに近いディフェンダーもチェック\n')
        new_func.append('  let nearReceiverDef = defenders.filter(d => dist(d.x, d.y, receiver.x, receiver.y) < 40);\n')
        new_func.append('  if(nearReceiverDef.length >= 2) return false; // ダブルチーム状態への危険なパス\n')
        new_func.append('  \n')
        new_func.append('  return true; // 安全なパス\n')
        new_func.append('}\n')
        new_func.append('\n')

        lines.insert(idx, ''.join(new_func))

    # ===== 4. Update all passTo calls to check safety first =====
    # Find passTo calls and wrap with safety check
    for i in range(len(lines)):
        if 'passTo(p,' in lines[i] and 'function passTo' not in lines[i] and 'isPassSafe' not in lines[i]:
            # Extract the passTo call
            indent = len(lines[i]) - len(lines[i].lstrip())
            spaces = ' ' * indent

            if 'passTo(p, cuttingMate)' in lines[i]:
                lines[i] = f'{spaces}if(isPassSafe(p, cuttingMate)) {{ passTo(p, cuttingMate); return; }}\n'
            elif 'passTo(p, bestPass)' in lines[i]:
                lines[i] = f'{spaces}if(bestPass && isPassSafe(p, bestPass)) {{ passTo(p, bestPass); return; }}\n'
            elif 'passTo(p, nearest)' in lines[i]:
                lines[i] = f'{spaces}if(nearest && isPassSafe(p, nearest)) {{ passTo(p, nearest); return; }}\n'
            elif 'passTo(p, fwdMate)' in lines[i]:
                lines[i] = f'{spaces}if(fwdMate && isPassSafe(p, fwdMate)) {{ passTo(p, fwdMate); return; }}\n'
            elif 'passTo(p, pgMate)' in lines[i]:
                lines[i] = f'{spaces}if(pgMate && isPassSafe(p, pgMate)) {{ passTo(p, pgMate); return; }}\n'

    # ===== 5. Add off-ball movement after passing =====
    # Modify passTo to trigger movement
    idx = find_line(lines, 'function passTo(passer, receiver) {')
    if idx > 0:
        j = idx
        while j < len(lines) and lines[j].strip() != '}':
            j += 1

        # Before closing brace, add off-ball action
        new_lines = []
        new_lines.append('  \n')
        new_lines.append('  // パス後の動き：Give & Go または スペーシング\n')
        new_lines.append('  if(random() < 0.35 && passer.position !== "C") { // Cは動きが遅いのでカットしない\n')
        new_lines.append('    // Give & Go: ゴールに向かってカット\n')
        new_lines.append('    passer.offBallAction = "cut";\n')
        new_lines.append('    passer.offBallTimer = 90;\n')
        new_lines.append('  } else {\n')
        new_lines.append('    // スペーシング調整：オープンスペースへ移動\n')
        new_lines.append('    passer.offBallAction = "space";\n')
        new_lines.append('    passer.offBallTimer = 60;\n')
        new_lines.append('  }\n')

        lines.insert(j, ''.join(new_lines))

    # ===== 6. Implement off-ball action in support logic =====
    idx = find_line(lines, 'p.state = "support"')
    if idx > 0:
        # After state declaration, add off-ball check
        new_check = []
        new_check.append('    \n')
        new_check.append('    // オフボールアクション実行中\n')
        new_check.append('    if(p.offBallTimer > 0) {\n')
        new_check.append('      p.offBallTimer--;\n')
        new_check.append('      if(p.offBallAction === "cut") {\n')
        new_check.append('        // ゴールへカット\n')
        new_check.append('        p.speedMultiplier = SPEED_SPRINT;\n')
        new_check.append('        let tg = p.team === "PlayerTeam" ? goalR : goalL;\n')
        new_check.append('        moveToward(p, tg.x, tg.y + (p.id % 2 === 0 ? -40 : 40), speed);\n')
        new_check.append('        return;\n')
        new_check.append('      } else if(p.offBallAction === "space") {\n')
        new_check.append('        // オープンスペースへ移動\n')
        new_check.append('        let side = p.team === "PlayerTeam" ? 1 : -1;\n')
        new_check.append('        let tg = p.team === "PlayerTeam" ? goalR : goalL;\n')
        new_check.append('        let openX = tg.x - side * 200;\n')
        new_check.append('        let openY = tg.y + (p.y > tg.y ? 80 : -80);\n')
        new_check.append('        p.speedMultiplier = SPEED_RUN;\n')
        new_check.append('        moveToward(p, openX, openY, speed * 0.7);\n')
        new_check.append('        return;\n')
        new_check.append('      }\n')
        new_check.append('    }\n')
        new_check.append('    \n')

        lines.insert(idx + 2, ''.join(new_check))

    # ===== 7. Add shot clock awareness =====
    idx = find_line(lines, '// ②シュート判断（高優先度')
    if idx > 0:
        # Add shot clock urgency before shoot logic
        new_lines = []
        new_lines.append('    \n')
        new_lines.append('    // ショットクロック急迫時は強制シュート\n')
        new_lines.append('    if(shotClock < 5 && dToGoal < 300) {\n')
        new_lines.append('      shootChance = 0.95; // ほぼ確実にシュート\n')
        new_lines.append('      shootDist = 300; // 距離制限緩和\n')
        new_lines.append('    } else if(shotClock < 8 && dToGoal < shootDist * 1.2) {\n')
        new_lines.append('      shootChance *= 2.0; // 積極的に\n')
        new_lines.append('    }\n')
        new_lines.append('    \n')

        lines.insert(idx, ''.join(new_lines))

    # ===== 8. Add help defense =====
    idx = find_line(lines, 'p.state = "defense"')
    if idx > 0:
        # Find the defense logic section
        j = idx
        while j < len(lines) and 'let assignment' not in lines[j]:
            j += 1

        if j < len(lines):
            # Insert help defense before assignment
            new_help = []
            new_help.append('    \n')
            new_help.append('    // ヘルプディフェンス：味方がやられている時にカバー\n')
            new_help.append('    let teammates = players.filter(pl => pl.team === p.team && pl.id !== p.id);\n')
            new_help.append('    let needsHelp = null;\n')
            new_help.append('    for(let t of teammates) {\n')
            new_help.append('      if(t.assignment) {\n')
            new_help.append('        let attacker = players.find(pl => pl.id === t.assignment);\n')
            new_help.append('        if(attacker && attacker.hasBall) {\n')
            new_help.append('          let defDist = dist(t.x, t.y, attacker.x, attacker.y);\n')
            new_help.append('          let tg = p.team === "PlayerTeam" ? goalL : goalR;\n')
            new_help.append('          let attackerToGoal = dist(attacker.x, attacker.y, tg.x, tg.y);\n')
            new_help.append('          // ペイント侵入時はヘルプ\n')
            new_help.append('          if(defDist > 50 && attackerToGoal < 150) {\n')
            new_help.append('            needsHelp = attacker;\n')
            new_help.append('            break;\n')
            new_help.append('          }\n')
            new_help.append('        }\n')
            new_help.append('      }\n')
            new_help.append('    }\n')
            new_help.append('    \n')
            new_help.append('    if(needsHelp && (p.position === "PF" || p.position === "C")) {\n')
            new_help.append('      // ビッグマンがペイントをプロテクト\n')
            new_help.append('      p.speedMultiplier = SPEED_SPRINT;\n')
            new_help.append('      let tg = p.team === "PlayerTeam" ? goalL : goalR;\n')
            new_help.append('      let helpX = (needsHelp.x + tg.x) / 2;\n')
            new_help.append('      let helpY = (needsHelp.y + tg.y) / 2;\n')
            new_help.append('      moveToward(p, helpX, helpY, speed);\n')
            new_help.append('      return;\n')
            new_help.append('    }\n')
            new_help.append('    \n')

            lines.insert(j, ''.join(new_help))

    # ===== 9. Prevent C/PF from handling ball in backcourt =====
    # Find loose ball logic and prioritize guards
    for i in range(len(lines)):
        if 'if(random() < reboundChance) {' in lines[i] and 'p.hasBall = true' in lines[i+1]:
            # Add position-based chance modifier before the check
            indent = len(lines[i]) - len(lines[i].lstrip())
            spaces = ' ' * indent

            new_lines = []
            new_lines.append(f'{spaces}// ポジション別のボール獲得優先度\n')
            new_lines.append(f'{spaces}if(p.position === "C" || p.position === "PF") reboundChance *= 0.6; // ビッグマンは運ばない\n')
            new_lines.append(f'{spaces}if(p.position === "PG") reboundChance *= 1.4; // PG優先\n')
            new_lines.append(f'{spaces}if(p.position === "SG") reboundChance *= 1.2; // SG次点\n')
            new_lines.append(f'{spaces}\n')

            lines.insert(i, ''.join(new_lines))
            break

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("✓ Position-based spacing: PG/SG outside 3P line, PF/C near goal")
    print("✓ Centers prevented from ball handling (PG priority)")
    print("✓ Off-ball movement: Give & Go and spacing adjustment")
    print("✓ Pass interception risk assessment added")
    print("✓ Shot clock awareness added")
    print("✓ Help defense and paint protection added")
    print("✓ Improved player spacing (80px minimum)")

if __name__ == "__main__":
    main()
