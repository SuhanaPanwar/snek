import pygame
import cv2

pygame.init()

screen = pygame.display.set_mode((800, 600))
running = True
dt = 0
clock = pygame.time.Clock()
pygame.display.set_caption("☆bubbl3wr4p!☆")

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
facing = pygame.Vector2(1,0)

froggie = pygame.image.load("imgs/magic froggie.png").convert_alpha()
froggie = pygame.transform.scale(froggie, (160, 175))

froggie_red = froggie.copy()
froggie_red.fill((255, 60, 60, 255), special_flags = pygame.BLEND_RGBA_MULT)

potion = pygame.image.load("imgs/potion bottle.png").convert_alpha()
potion = pygame.transform.scale(potion, (150, 150))

potion_red = potion.copy()
potion_red.fill((255, 60, 60, 255), special_flags = pygame.BLEND_RGBA_MULT)

potion_pos = pygame.Vector2(650, 200)
potion_speed = 200
potion_direction = -1

charge_direction = pygame.Vector2(0, 0)
charge_state = "aim"
charge_timer = 0
charge_speed = 450
potion_mode = "float"
mode_timer = 0

spells = []
spell_speed = 400

enemy_spells = []
enemy_spell_speed = 250
enemy_shoot_timer = 0

potion_health = 5
potion_flash_timer = 0

froggie_health = 3 
froggie_invincible_timer = 0

game_state = "playing"
font = pygame.font.Font(None, 65)

victory_overlay = pygame.Surface((800, 600))
victory_overlay.set_alpha(190)
victory_overlay.fill((0, 0, 0))

victory_text = font.render("FROGGIE WINS!", True, "plum1")
victory_rect = victory_text.get_rect(center = (400, 300))

game_over_text = font.render("GAME OVER!", True, "plum1")
game_over_rect = game_over_text.get_rect(center = (400, 300))

def play_intro():
    video = cv2.VideoCapture("intro.mp4")

    if not video.isOpened():
        print("Couldn't open intro.mp4")
        return True

    fps = video.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    intro_clock = pygame.time.Clock()

    while video.isOpened():

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                video.release()
                return False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    video.release()
                    return True

        success, frame = video.read()

        if not success:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (800, 600))

        surface = pygame.image.frombuffer(
            frame.tobytes(), (800, 600), "RGB"
        )        

        screen.blit(surface, (0, 0))
        pygame.display.flip()

        intro_clock.tick(fps)

    video.release()
    return True

running = play_intro()

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == "playing":
                spells.append([player_pos.copy(), facing.copy()])

    if game_state == "playing":

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            player_pos.y -= 300 * dt
            facing = pygame.Vector2(0, -1)

        if keys[pygame.K_s]:
            player_pos.y += 300 * dt
            facing = pygame.Vector2(0, 1)

        if keys[pygame.K_a]:
            player_pos.x -= 300 * dt
            facing = pygame.Vector2(-1, 0)

        if keys[pygame.K_d]:
            player_pos.x += 300 * dt
            facing = pygame.Vector2(1, 0)

        player_pos.x = max(39, min(player_pos.x, 746))
        player_pos.y = max(39, min(player_pos.y, 560))

        enemy_shoot_timer += dt

        if enemy_shoot_timer > 2:
            enemy_shoot_timer = 0

            direction = player_pos - potion_pos

            if direction.length() > 0:
                direction = direction.normalize()
                enemy_spells.append([potion_pos.copy(), direction])
        
        mode_timer += dt

        if mode_timer >= 3:
            mode_timer = 0

            if potion_mode == "float":
                potion_mode = "chase"

            elif potion_mode == "chase":
                potion_mode = "charge"
                charge_state = "aim"
                charge_timer = 0

            else:
                potion_mode = "float"

        if potion_mode == "float":
            potion_pos.x += 120 * potion_direction * dt

            if potion_pos.x <= 75:
                potion_direction = 1

            elif potion_pos.x >= 725:
                potion_direction = -1

        elif potion_mode == "chase":
            direction = player_pos - potion_pos

            if direction.length() > 0:
                direction = direction.normalize()
                potion_pos += direction * potion_speed * dt

        elif potion_mode == "charge":
            charge_timer += dt

            if charge_state == "aim":
                if charge_timer >= 0.8:
                    charge_direction = player_pos - potion_pos

                    if charge_direction.length() > 0:
                        charge_direction = charge_direction.normalize()

                    charge_state = "dash"
                    charge_timer = 0

            elif charge_state == "dash":
                potion_pos += charge_direction * charge_speed * dt

                if charge_timer >= 0.5:
                    charge_state = "aim"
                    charge_timer = 0

        potion_pos.x = max(75, min(potion_pos.x, 725))
        potion_pos.y = max(75, min(potion_pos.y, 525))

        for spell in spells:
            spell[0] += spell[1] * spell_speed * dt

        for enemy_spell in enemy_spells:
            enemy_spell[0] += enemy_spell[1] * enemy_spell_speed * dt

        for enemy_spell in enemy_spells[:]:
            enemy_spell_pos = enemy_spell[0]

            if enemy_spell_pos.distance_to(player_pos) < 45:
                enemy_spells.remove(enemy_spell)

                if froggie_invincible_timer <= 0:
                    froggie_health = max(0, froggie_health - 1)
                    froggie_invincible_timer = 1.0
                    print("Froggie HP:", froggie_health)

                    if froggie_health == 0:
                        game_state = "game_over"

        for spell in spells[:]:
            spell_pos = spell[0]

            if game_state == "playing" and potion_health > 0 and spell_pos.distance_to(potion_pos) < 65:
                potion_health = max(0, potion_health -1)
                potion_flash_timer = 0.3
                spells.remove(spell)
                print("Potion health:", potion_health)

                if potion_health == 0:
                    game_state = "victory"

    if potion_flash_timer > 0:
        potion_flash_timer = max(0, potion_flash_timer - dt)

    if froggie_invincible_timer > 0:
        froggie_invincible_timer = max(0, froggie_invincible_timer - dt)

    screen.fill("darkolivegreen4")
    pygame.display.set_caption(f"☆bubbl3wr4p!☆ | Froggie HP: {froggie_health} | Potion HP: {potion_health}")

    if froggie_invincible_timer > 0:
        screen.blit(froggie_red, froggie_red.get_rect(center = player_pos))

    else:
        screen.blit(froggie, froggie.get_rect(center = player_pos))

    if potion_flash_timer > 0:
        screen.blit(potion_red, potion_red.get_rect(center = potion_pos))

    else:
        screen.blit(potion, potion.get_rect(center = potion_pos))

    
    for spell in spells:
        pygame.draw.circle(screen, "darkorchid4", spell[0], 10)

    for enemy_spell in enemy_spells:
        pygame.draw.circle(screen, "hotpink2", enemy_spell[0], 12)

    if game_state == "victory":

        screen.blit(victory_overlay, (0, 0))
        screen.blit(victory_text, victory_rect)

    elif game_state == "game_over":

        screen.blit(victory_overlay, (0, 0))
        screen.blit(game_over_text, game_over_rect)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()
