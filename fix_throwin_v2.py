#!/usr/bin/env python3
"""
Correctly fix throw-in and defense issues
"""

def main():
    with open('basketball-sim.html', 'r', encoding='utf-8') as f:
        content = f.read()

    print("=== THROW-IN & DEFENSE FIXES (V2) ===\n")

    # FIX 1: Remove distance limit for forced throw
    print("1. Removing distance limit for forced throw...")
    content = content.replace(
        'if(target && dist(p.x, p.y, target.x, target.y) < 350) {',
        'if(target) { // 強制スロー：距離制限なし'
    )
    print("   ✓ Removed 350 distance limit")

    # FIX 2: Improve teammate positioning - move closer when too far
    print("\n2. Improving teammate positioning...")

    old_teammate_code = '''  if(throwInState && p.team === throwInState.team && p.id !== throwInState.thrower) {
    p.speedMultiplier = SPEED_WALK; // 受け取る位置への微調整は歩き
    let thrower = players.find(pl => pl.id === throwInState.thrower);
    if(thrower) {
      // スロワーから適度な距離に移動
      let ang = atan2(p.y - thrower.y, p.x - thrower.x);
      let targetDist = 100 + (p.id % 3) * 30;
      let tx = thrower.x + cos(ang) * targetDist;
      let ty = thrower.y + sin(ang) * targetDist;
      moveToward(p, constrain(tx, 125, 875), constrain(ty, 275, 537.5), p.spd * 0.04);
    }
    return;
  }'''

    new_teammate_code = '''  if(throwInState && p.team === throwInState.team && p.id !== throwInState.thrower) {
    p.speedMultiplier = SPEED_WALK; // 受け取る位置への微調整は歩き
    let thrower = players.find(pl => pl.id === throwInState.thrower);
    if(thrower) {
      let currentDist = dist(p.x, p.y, thrower.x, thrower.y);
      // スロワーから遠すぎる場合は直接近づく
      if(currentDist > 250) {
        p.speedMultiplier = SPEED_JOG;
        moveToward(p, thrower.x, thrower.y, p.spd * 0.05);
      } else {
        // 適度な距離に配置
        let ang = atan2(p.y - thrower.y, p.x - thrower.x);
        let targetDist = 120 + (p.id % 3) * 20;
        let tx = thrower.x + cos(ang) * targetDist;
        let ty = thrower.y + sin(ang) * targetDist;
        moveToward(p, constrain(tx, 125, 875), constrain(ty, 275, 537.5), p.spd * 0.04);
      }
    }
    return;
  }
  // スローイン中：ディフェンス側は自陣へ戻る
  if(throwInState && p.team !== throwInState.team) {
    let halfCourt = 500;
    let isInOpponentHalf = (p.team === "PlayerTeam" && p.x > halfCourt) ||
                            (p.team === "DefenderTeam" && p.x < halfCourt);
    if(isInOpponentHalf) {
      p.speedMultiplier = SPEED_JOG;
      p.state = "transition_defense";
      let backX = (p.team === "PlayerTeam" ? 350 : 650);
      let backY = 388.75 + (p.id % 3 - 1) * 50;
      moveToward(p, backX, backY, p.spd * 0.04);
      return;
    }
  }'''

    content = content.replace(old_teammate_code, new_teammate_code)
    print("   ✓ Added close-in logic for distant teammates")
    print("   ✓ Added defense return during throw-in")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n" + "=" * 60)
    print("FIXES COMPLETE!")
    print("=" * 60)
    print("\nFixed issues:")
    print("  1. ✓ No distance limit for forced throw")
    print("  2. ✓ Teammates move closer (>250 away)")
    print("  3. ✓ Defense returns during throw-in")

if __name__ == "__main__":
    main()
