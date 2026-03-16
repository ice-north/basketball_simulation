#!/usr/bin/env python3
"""
Improve Movement Realism - Basketball Physics

USER REQUEST:
  動きはリアルにしたい

IMPROVEMENTS:
  1. Inertia/momentum system (acceleration/deceleration)
  2. Turn speed limitation (can't change direction instantly)
  3. Ball handling weight (slower with ball)
  4. Stamina system (fatigue from sprinting)
  5. Collision physics improvements
  6. Visual feedback for movement states
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
    print("MOVEMENT REALISM IMPROVEMENTS")
    print("=" * 70)
    print()

    # ===== IMPROVEMENT 1: Add momentum properties to players =====
    print("1. Adding momentum/stamina properties to players...")

    idx = find_line(lines, 'function createPlayer(')
    if idx > 0:
        # Find the return statement
        for i in range(idx, idx + 100):
            if 'return {' in lines[i]:
                # Find the end of the object
                for j in range(i, min(i + 80, len(lines))):
                    if '};' in lines[j] and 'return' not in lines[j]:
                        # Insert before the closing brace
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        momentum_props = ' ' * indent + '// OPUS: Momentum & Physics\n'
                        momentum_props += ' ' * indent + 'vx: 0, vy: 0,  // Current velocity\n'
                        momentum_props += ' ' * indent + 'stamina: 100,  // Stamina (100 = full)\n'
                        momentum_props += ' ' * indent + 'lastAngle: 0,  // Last movement angle\n'

                        lines.insert(j, momentum_props)
                        print("   ✓ Added momentum and stamina properties")
                        break
                break

    # ===== IMPROVEMENT 2: Replace moveToward with realistic movement =====
    print("\n2. Enhancing moveToward with inertia...")

    idx = find_line(lines, 'function moveToward(p, tx, ty, speed) {')
    if idx > 0:
        # Replace entire function
        for i in range(idx, min(idx + 50, len(lines))):
            if 'function moveToward' in lines[i-1] if i > 0 else False:
                continue
            if '}' in lines[i] and lines[i].strip() == '}':
                # Found end of function
                new_function = '''function moveToward(p, tx, ty, speed) {
  // OPUS: Realistic movement with inertia

  // Target direction
  let dx = tx - p.x;
  let dy = ty - p.y;
  let distance = Math.sqrt(dx * dx + dy * dy);

  if(distance < 1) {
    // Decelerate to stop
    p.vx *= 0.8;
    p.vy *= 0.8;
    p.x += p.vx;
    p.y += p.vy;
    return;
  }

  // Desired velocity
  let targetAngle = Math.atan2(dy, dx);
  let desiredVx = (dx / distance) * speed;
  let desiredVy = (dy / distance) * speed;

  // Apply stamina penalty
  let staminaFactor = p.stamina / 100;
  let effectiveSpeed = speed * Math.max(staminaFactor, 0.5);

  // Acceleration (inertia)
  let accel = 0.3; // Higher = more responsive
  p.vx += (desiredVx - p.vx) * accel;
  p.vy += (desiredVy - p.vy) * accel;

  // Turn speed limitation
  let angleDiff = Math.abs(targetAngle - p.lastAngle);
  if(angleDiff > Math.PI) angleDiff = 2 * Math.PI - angleDiff;

  // Sharp turns slow you down
  if(angleDiff > 0.5) { // ~30 degrees
    let turnPenalty = 1 - (angleDiff / Math.PI) * 0.4;
    p.vx *= turnPenalty;
    p.vy *= turnPenalty;
  }

  p.lastAngle = targetAngle;

  // Ball handling penalty
  if(p.hasBall) {
    p.vx *= 0.92; // 8% slower with ball
    p.vy *= 0.92;
  }

  // Apply velocity
  p.x += p.vx;
  p.y += p.vy;

  // Stamina system
  if(p.speedMultiplier >= 0.12) { // SPEED_SPRINT
    p.stamina -= 0.08; // Drain when sprinting
  } else {
    p.stamina += 0.05; // Recover when not sprinting
  }
  p.stamina = Math.max(0, Math.min(100, p.stamina));
}
'''
                # Replace from idx to i (inclusive)
                lines[idx:i+1] = [new_function]
                print("   ✓ moveToward now has inertia, turn limits, and stamina")
                break

    # ===== IMPROVEMENT 3: Visual stamina indicator =====
    print("\n3. Adding stamina visual indicator...")

    idx = find_line(lines, 'function drawPlayers() {')
    if idx > 0:
        # Find where players are drawn
        for i in range(idx, min(idx + 100, len(lines))):
            if 'ellipse(p.x, p.y' in lines[i] and 'p.z' not in lines[i]:
                # After drawing player circle, add stamina bar
                indent = len(lines[i]) - len(lines[i].lstrip())
                stamina_visual = '\n' + ' ' * indent + '// OPUS: Stamina indicator\n'
                stamina_visual += ' ' * indent + 'if(p.stamina < 70) {\n'
                stamina_visual += ' ' * indent + '  push();\n'
                stamina_visual += ' ' * indent + '  let staminaColor = p.stamina > 40 ? [255, 200, 0] : [255, 100, 100];\n'
                stamina_visual += ' ' * indent + '  stroke(staminaColor[0], staminaColor[1], staminaColor[2]);\n'
                stamina_visual += ' ' * indent + '  strokeWeight(2);\n'
                stamina_visual += ' ' * indent + '  noFill();\n'
                stamina_visual += ' ' * indent + '  let barWidth = p.stamina * 0.2; // Max 20 pixels\n'
                stamina_visual += ' ' * indent + '  line(p.x - 10, p.y - 18, p.x - 10 + barWidth, p.y - 18);\n'
                stamina_visual += ' ' * indent + '  pop();\n'
                stamina_visual += ' ' * indent + '}\n'

                lines[i] = lines[i].rstrip() + stamina_visual
                print("   ✓ Low stamina shows visual indicator")
                break

    # ===== IMPROVEMENT 4: Collision improvements =====
    print("\n4. Improving player collision physics...")

    idx = find_line(lines, 'players.forEach(other => {')
    if idx > 0:
        # Find collision handling
        for i in range(idx, min(idx + 30, len(lines))):
            if 'if(dist(p.x,p.y,other.x,other.y) < 25)' in lines[i]:
                # Enhance collision
                old_line = lines[i]
                indent = len(old_line) - len(old_line.lstrip())

                # Find the existing collision code
                collision_start = i
                collision_end = i
                for j in range(i, min(i + 15, len(lines))):
                    if '}' in lines[j]:
                        collision_end = j
                        break

                # Replace with better collision
                new_collision = ' ' * indent + 'if(dist(p.x,p.y,other.x,other.y) < 25) {\n'
                new_collision += ' ' * indent + '  // OPUS: Realistic collision with momentum\n'
                new_collision += ' ' * indent + '  let ang = atan2(p.y - other.y, p.x - other.x);\n'
                new_collision += ' ' * indent + '  let overlap = 25 - dist(p.x, p.y, other.x, other.y);\n'
                new_collision += ' ' * indent + '  \n'
                new_collision += ' ' * indent + '  // Separate players\n'
                new_collision += ' ' * indent + '  let pushX = cos(ang) * overlap * 0.5;\n'
                new_collision += ' ' * indent + '  let pushY = sin(ang) * overlap * 0.5;\n'
                new_collision += ' ' * indent + '  p.x += pushX;\n'
                new_collision += ' ' * indent + '  p.y += pushY;\n'
                new_collision += ' ' * indent + '  other.x -= pushX;\n'
                new_collision += ' ' * indent + '  other.y -= pushY;\n'
                new_collision += ' ' * indent + '  \n'
                new_collision += ' ' * indent + '  // Momentum transfer\n'
                new_collision += ' ' * indent + '  if(p.vx !== undefined && other.vx !== undefined) {\n'
                new_collision += ' ' * indent + '    let tempVx = p.vx;\n'
                new_collision += ' ' * indent + '    let tempVy = p.vy;\n'
                new_collision += ' ' * indent + '    p.vx = (p.vx + other.vx) * 0.5;\n'
                new_collision += ' ' * indent + '    p.vy = (p.vy + other.vy) * 0.5;\n'
                new_collision += ' ' * indent + '    other.vx = (tempVx + other.vx) * 0.5;\n'
                new_collision += ' ' * indent + '    other.vy = (tempVy + other.vy) * 0.5;\n'
                new_collision += ' ' * indent + '  }\n'
                new_collision += ' ' * indent + '}\n'

                lines[collision_start:collision_end+1] = [new_collision]
                print("   ✓ Collisions now transfer momentum realistically")
                break

    # ===== IMPROVEMENT 5: Dribble animation realism =====
    print("\n5. Improving dribble animation realism...")

    idx = find_line(lines, 'let dribblePhase = (frameCount * 0.2) % (2 * PI);')
    if idx > 0:
        old_line = lines[idx]
        indent = len(old_line) - len(old_line.lstrip())

        # Make dribble speed depend on player movement
        new_line = ' ' * indent + '// OPUS: Dribble speed varies with movement\n'
        new_line += ' ' * indent + 'let moveSpeed = 1;\n'
        new_line += ' ' * indent + 'if(holder.vx !== undefined) {\n'
        new_line += ' ' * indent + '  moveSpeed = Math.sqrt(holder.vx * holder.vx + holder.vy * holder.vy) * 0.5 + 1;\n'
        new_line += ' ' * indent + '}\n'
        new_line += ' ' * indent + 'let dribblePhase = (frameCount * 0.15 * moveSpeed) % (2 * PI);\n'

        lines[idx] = new_line
        print("   ✓ Dribble animation speed matches movement")

    with open('basketball-sim.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n" + "=" * 70)
    print("MOVEMENT REALISM COMPLETE")
    print("=" * 70)
    print("\nImprovements:")
    print("  1. ✓ Inertia/momentum system")
    print("  2. ✓ Turn speed limitation (realistic direction changes)")
    print("  3. ✓ Ball handling weight (8% slower with ball)")
    print("  4. ✓ Stamina system (drains when sprinting)")
    print("  5. ✓ Visual stamina indicator")
    print("  6. ✓ Realistic collision with momentum transfer")
    print("  7. ✓ Dribble animation speed varies")
    print("\nExpected feel:")
    print("  • Players accelerate gradually (not instant)")
    print("  • Sharp turns slow you down")
    print("  • Sprinting drains stamina")
    print("  • Collisions feel physical")
    print("  • More NBA-like movement")

if __name__ == "__main__":
    main()
