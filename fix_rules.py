#!/usr/bin/env python3
"""
Fix basketball rule violations and gameplay issues:
1. Jump ball: Centers participate instead of SF
2. Throw-in: Force pass within time limit
3. Throw-in: Players stay behind goal image
4. Transition defense: Return to own court
5. Prevent throw-in dribble violation
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

    # ===== 1. Fix jump ball: Centers participate =====
    idx = find_line(lines, 'function startJumpBall() {')
    if idx > 0:
        j = idx
        while j < len(lines) and 'jumpBallState = {' not in lines[j]:
            j += 1

        new_code = []
        new_code.append('function startJumpBall() {\n')
        new_code.append('  // センター優先でジャンプボール参加者を選択\n')
        new_code.append('  let playerTeamC = players.find(p => p.team === "PlayerTeam" && p.position === "C");\n')
        new_code.append('  let defenderTeamC = players.find(p => p.team === "DefenderTeam" && p.position === "C");\n')
        new_code.append('  \n')
        new_code.append('  // センターがいない場合はPF、さらにいなければ最も背が高い選手\n')
        new_code.append('  let playerTeamJumper = playerTeamC || \n')
        new_code.append('    players.find(p => p.team === "PlayerTeam" && p.position === "PF") ||\n')
        new_code.append('    players.filter(p => p.team === "PlayerTeam")\n')
        new_code.append('      .sort((a, b) => (b.height + b.jmp) - (a.height + a.jmp))[0];\n')
        new_code.append('  let defenderTeamJumper = defenderTeamC ||\n')
        new_code.append('    players.find(p => p.team === "DefenderTeam" && p.position === "PF") ||\n')
        new_code.append('    players.filter(p => p.team === "DefenderTeam")\n')
        new_code.append('      .sort((a, b) => (b.height + b.jmp) - (a.height + a.jmp))[0];\n')
        new_code.append('\n')

        lines[idx:j] = new_code

    # ===== 2. Fix throw-in: Force pass and prevent dribble =====
    idx = find_line(lines, '// スローイン時：スロワーは指定位置へ、パスを出す')
    if idx > 0:
        # Find the entire throw-in block
        j = idx
        while j < len(lines) and 'if(throwInState && p.team === throwInState.team && p.id !== throwInState.thrower)' not in lines[j]:
            j += 1

        new_code = []
        new_code.append('  // スローイン時：スロワーは指定位置へ、パスを出す（5秒以内必須）\n')
        new_code.append('  if(throwInState && throwInState.thrower === p.id) {\n')
        new_code.append('    p.speedMultiplier = SPEED_JOG;\n')
        new_code.append('    p.hasBall = false; // スローイン中はドリブル禁止（バイオレーション防止）\n')
        new_code.append('    \n')
        new_code.append('    moveToward(p, throwInState.x, throwInState.y, p.spd * 0.06);\n')
        new_code.append('    \n')
        new_code.append('    if(dist(p.x, p.y, throwInState.x, throwInState.y) < 20) {\n')
        new_code.append('      // タイマー初期化\n')
        new_code.append('      if(!throwInState.timer) throwInState.timer = 0;\n')
        new_code.append('      throwInState.timer++;\n')
        new_code.append('      \n')
        new_code.append('      // 5秒ルール（300フレーム = 5秒）\n')
        new_code.append('      if(throwInState.timer > 300) {\n')
        new_code.append('        // 5秒バイオレーション：相手ボールに\n')
        new_code.append('        let newTeam = throwInState.team === "PlayerTeam" ? "DefenderTeam" : "PlayerTeam";\n')
        new_code.append('        addFloatingText(throwInState.x, throwInState.y - 40, "5-SEC VIOLATION!", [255, 100, 100]);\n')
        new_code.append('        startThrowIn(newTeam, throwInState.x, throwInState.y, "5-SEC VIOLATION");\n')
        new_code.append('        return;\n')
        new_code.append('      }\n')
        new_code.append('      \n')
        new_code.append('      // 近くの味方にパスを出す（即座に判定）\n')
        new_code.append('      let teammates = players.filter(t => t.team === p.team && t.id !== p.id);\n')
        new_code.append('      // オープンな味方を優先\n')
        new_code.append('      let openTeammates = teammates.filter(t => {\n')
        new_code.append('        let nearDef = players.filter(d => d.team !== p.team && dist(d.x, d.y, t.x, t.y) < 50);\n')
        new_code.append('        return nearDef.length === 0;\n')
        new_code.append('      });\n')
        new_code.append('      let target = openTeammates.length > 0 ? \n')
        new_code.append('        openTeammates.sort((a,b) => dist(p.x,p.y,a.x,a.y) - dist(p.x,p.y,b.x,b.y))[0] :\n')
        new_code.append('        teammates.sort((a,b) => dist(p.x,p.y,a.x,a.y) - dist(p.x,p.y,b.x,b.y))[0];\n')
        new_code.append('      \n')
        new_code.append('      if(target && dist(p.x, p.y, target.x, target.y) < 250 && throwInState.timer > 30) {\n')
        new_code.append('        if(isPassSafe(p, target)) {\n')
        new_code.append('          // スローイン専用のパス処理\n')
        new_code.append('          let d = dist(p.x, p.y, target.x, target.y);\n')
        new_code.append('          let spd = 7, t = d / spd;\n')
        new_code.append('          ball.x = p.x; ball.y = p.y; ball.z = 45;\n')
        new_code.append('          ball.vx = (target.x - ball.x) / t;\n')
        new_code.append('          ball.vy = (target.y - ball.y) / t;\n')
        new_code.append('          ball.vz = 2.5;\n')
        new_code.append('          ball.passTarget = target.id;\n')
        new_code.append('          ball.lastTouch = p.team;\n')
        new_code.append('          throwInState = null; // スローイン完了\n')
        new_code.append('          return;\n')
        new_code.append('        }\n')
        new_code.append('      }\n')
        new_code.append('    }\n')
        new_code.append('    return;\n')
        new_code.append('  }\n')

        lines[idx:j] = new_code

    # ===== 3. Fix throw-in positioning: Stay away from goal =====
    idx = find_line(lines, '// スローイン時：スロワー以外の味方は受け取りやすい位置へ')
    if idx > 0:
        j = idx
        while j < len(lines) and 'return;' not in lines[j]:
            j += 1
        j += 1  # Include return

        new_code = []
        new_code.append('  // スローイン時：スロワー以外の味方は受け取りやすい位置へ（ゴールから離れる）\n')
        new_code.append('  if(throwInState && p.team === throwInState.team && p.id !== throwInState.thrower) {\n')
        new_code.append('    p.speedMultiplier = SPEED_WALK;\n')
        new_code.append('    let thrower = players.find(pl => pl.id === throwInState.thrower);\n')
        new_code.append('    if(thrower) {\n')
        new_code.append('      // スロワーから適度な距離、かつゴール画像の前に位置取り\n')
        new_code.append('      let ang = atan2(p.y - thrower.y, p.x - thrower.x);\n')
        new_code.append('      let targetDist = 80 + (p.id % 3) * 25;\n')
        new_code.append('      let tx = thrower.x + cos(ang) * targetDist;\n')
        new_code.append('      let ty = thrower.y + sin(ang) * targetDist;\n')
        new_code.append('      \n')
        new_code.append('      // ゴール画像に重ならないように制約（ゴールから50px以上離れる）\n')
        new_code.append('      let goalX = p.team === "PlayerTeam" ? finalGoal.ringX : 1000 - finalGoal.ringX;\n')
        new_code.append('      let goalY = finalGoal.ringY;\n')
        new_code.append('      if(dist(tx, ty, goalX, goalY) < 80) {\n')
        new_code.append('        // ゴールから離れる方向に調整\n')
        new_code.append('        let awayAng = atan2(ty - goalY, tx - goalX);\n')
        new_code.append('        tx = goalX + cos(awayAng) * 90;\n')
        new_code.append('        ty = goalY + sin(awayAng) * 90;\n')
        new_code.append('      }\n')
        new_code.append('      \n')
        new_code.append('      moveToward(p, constrain(tx, 100, 900), constrain(ty, 280, 530), p.spd * 0.04);\n')
        new_code.append('    }\n')
        new_code.append('    return;\n')
        new_code.append('  }\n')
        new_code.append('  \n')
        new_code.append('  // 相手ボール時のトランジションディフェンス\n')
        new_code.append('  if(throwInState && p.team !== throwInState.team) {\n')
        new_code.append('    // 相手スローイン時：自陣に戻る\n')
        new_code.append('    p.speedMultiplier = SPEED_RUN;\n')
        new_code.append('    let defX = (p.team === "PlayerTeam" ? 300 : 700);\n')
        new_code.append('    let defY = 388.75 + (p.id % 3 - 1) * 60;\n')
        new_code.append('    moveToward(p, defX, defY, p.spd * 0.06);\n')
        new_code.append('    return;\n')
        new_code.append('  }\n')

        lines[idx:j] = new_code

    # ===== 4. Add transition defense when losing possession =====
    idx = find_line(lines, 'let isOffense = p.team === possession;')
    if idx > 0:
        # Add transition check after this line
        new_code = []
        new_code.append('  let isOffense = p.team === possession;\n')
        new_code.append('  \n')
        new_code.append('  // トランジションディフェンス：相手ボールになったら即座に自陣へ戻る\n')
        new_code.append('  if(!isOffense && !p.hasBall) {\n')
        new_code.append('    let ballHandler = players.find(pl => pl.hasBall);\n')
        new_code.append('    if(ballHandler && ballHandler.team !== p.team) {\n')
        new_code.append('      // 自陣のハーフコートより前にいる場合は戻る\n')
        new_code.append('      let halfCourt = 500;\n')
        new_code.append('      let isInOpponentHalf = (p.team === "PlayerTeam" && p.x > halfCourt) || \n')
        new_code.append('                              (p.team === "DefenderTeam" && p.x < halfCourt);\n')
        new_code.append('      if(isInOpponentHalf) {\n')
        new_code.append('        // 速やかに自陣へ戻る\n')
        new_code.append('        p.speedMultiplier = SPEED_SPRINT;\n')
        new_code.append('        p.state = "transition_defense";\n')
        new_code.append('        let backX = (p.team === "PlayerTeam" ? 350 : 650);\n')
        new_code.append('        let backY = 388.75 + (p.id % 3 - 1) * 50;\n')
        new_code.append('        moveToward(p, backX, backY, speed * SPEED_SPRINT);\n')
        new_code.append('        // 自陣に戻ったら通常ディフェンスへ\n')
        new_code.append('        if((p.team === "PlayerTeam" && p.x < halfCourt + 20) ||\n')
        new_code.append('           (p.team === "DefenderTeam" && p.x > halfCourt - 20)) {\n')
        new_code.append('          // 戻り完了、通常ディフェンスへ\n')
        new_code.append('        } else {\n')
        new_code.append('          return; // 戻り中は他の行動をしない\n')
        new_code.append('        }\n')
        new_code.append('      }\n')
        new_code.append('    }\n')
        new_code.append('  }\n')
        new_code.append('  \n')

        lines[idx] = ''.join(new_code)

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("✓ Jump ball: Centers participate (C → PF → tallest)")
    print("✓ Throw-in: 5-second rule enforced, pass required")
    print("✓ Throw-in: Dribble violation prevented")
    print("✓ Throw-in: Players stay away from goal image (80px+)")
    print("✓ Transition defense: Players return to own court")

if __name__ == "__main__":
    main()
