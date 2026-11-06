import pygame

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

potion = pygame.image.load("imgs/potion bottle.png").convert_alpha()
potion = pygame.transform.scale(potion, (150, 150))
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

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                spells.append([player_pos.copy(), facing.copy()])

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

    screen.fill("darkolivegreen4")
    screen.blit(froggie, froggie.get_rect(center = player_pos))
    screen.blit(potion, potion.get_rect(center = potion_pos))

    for spell in spells:
        pygame.draw.circle(screen, "darkorchid4", spell[0], 10)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()
