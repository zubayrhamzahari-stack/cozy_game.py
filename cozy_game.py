import math
import random
import sys
import pygame

# Cozy Game - minimal Pygame prototype
# Controls: Arrow keys or WASD to move, Space to sit/stand

WIDTH, HEIGHT = 800, 600
BG_COLOR = (222, 206, 176)  # warm beige
COZY_DECAY = 0.5  # coziness points lost per second
COZY_SIT_GAIN = 6.0  # coziness points gained per second while sitting near fire
TEA_SPAWN_RATE = 0.06  # expected spawns per second (low)
TEA_MAX = 7  # maximum number of teas at once
SPAWN_EFFECT_LIFE = 1.2  # seconds for spawn notification to live
CAT_COZY_GAIN = 1.5  # coziness per second when near a friendly cat
RUG_COZY_GAIN = 2.0  # coziness per second when standing on rug
CAT_COUNT = 1
SHOP_BUTTON_RECT = pygame.Rect(WIDTH - 100, 20, 80, 28)
WINDCHIME_POS = (50, 100)  # top-left windchime
BOOKSHELF_POS = (WIDTH - 50, 100)  # top-right bookshelf
FIREPLACE_SITSPOT_RADIUS = 100  # radius around fire for sitting bonus
HIGH_COZY_THRESHOLD = 90  # coziness level that triggers celebration


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 18
        self.color = (60, 40, 20)
        self.speed = 4
        self.sitting = False
        # walking animation state
        self.walking = False
        self.walk_phase = 0  # 0 or 1
        self.walk_timer = 0.0
        self.walk_step_time = 0.22  # seconds per phase

    def move(self, dx, dy):
        if self.sitting:
            return
        self.x = max(self.r, min(WIDTH - self.r, self.x + dx))
        self.y = max(self.r, min(HEIGHT - self.r, self.y + dy))
        # walking flag for animation
        self.walking = (dx != 0 or dy != 0)
        if not self.walking:
            # reset to neutral pose when not walking
            self.walk_phase = 0
            self.walk_timer = 0.0

    def update(self, dt):
        # advance walking animation if moving
        if self.sitting:
            self.walking = False
            self.walk_phase = 0
            self.walk_timer = 0.0
            return
        if self.walking:
            self.walk_timer += dt
            if self.walk_timer >= self.walk_step_time:
                self.walk_timer -= self.walk_step_time
                self.walk_phase ^= 1
        else:
            self.walk_timer = 0.0
            self.walk_phase = 0

    def draw(self, surf):
        # Draw a stickman-style player with simple clothing
        cx = int(self.x)
        cy = int(self.y)

        head_r = 8
        torso_h = 28
        limb_w = 2

        shirt_color = (200, 140, 120)
        pants_color = (110, 70, 40)
        skin = (240, 200, 170)
        outline = self.color

        head_center = (cx, cy - head_r - 6)

        if self.sitting:
            # refined sitting pose: torso slightly forward, arms on lap, knees bent
            # head
            pygame.draw.circle(surf, skin, head_center, head_r)
            pygame.draw.circle(surf, outline, head_center, head_r, 1)
            # torso (slightly squashed)
            pygame.draw.rect(surf, shirt_color, (cx - 10, cy - 4, 20, 16))
            # shoulders (slightly wider than neutral)
            left_shoulder = (cx - 12, cy + 2)
            right_shoulder = (cx + 12, cy + 2)
            # arms folded on lap (lines to center) - wider sweep
            lap_center = (cx, cy + 8)
            pygame.draw.line(surf, outline, left_shoulder,
                             (cx - 6, cy + 6), limb_w)
            pygame.draw.line(surf, outline, (cx - 8, cy + 6),
                             lap_center, limb_w)
            pygame.draw.line(surf, outline, right_shoulder,
                             (cx + 6, cy + 6), limb_w)
            pygame.draw.line(surf, outline, (cx + 6, cy + 6),
                             lap_center, limb_w)
            # thighs (horizontal), lower legs (down)
            left_knee = (cx - 8, cy + 12)
            right_knee = (cx + 8, cy + 12)
            pygame.draw.line(surf, outline, (cx - 4, cy + 8),
                             left_knee, limb_w)
            pygame.draw.line(surf, outline, left_knee,
                             (cx - 12, cy + 20), limb_w)
            pygame.draw.line(surf, outline, (cx + 4, cy + 8),
                             right_knee, limb_w)
            pygame.draw.line(surf, outline, right_knee,
                             (cx + 12, cy + 20), limb_w)
            # pants block
            pygame.draw.rect(surf, pants_color, (cx - 9, cy + 8, 18, 10))
            # small zzz indicator above head
            font = pygame.font.SysFont(None, 14)
            img = font.render('z z', True, (100, 100, 100))
            surf.blit(img, (cx - 8, head_center[1] - head_r - 14))
        else:
            # standing stickman
            # head
            pygame.draw.circle(surf, skin, head_center, head_r)
            pygame.draw.circle(surf, outline, head_center, head_r, 1)
            # shirt (over torso) - no vertical center line to avoid 'third leg'
            pygame.draw.rect(surf, shirt_color, (cx - 10,
                             head_center[1] + head_r, 20, torso_h // 2))
            # arms and legs swing in diagonal pairs
            left_arm_start = (cx - 10, head_center[1] + head_r + 6)
            right_arm_start = (cx + 10, head_center[1] + head_r + 6)
            hip_y = head_center[1] + head_r + torso_h // 2
            if self.walking and self.walk_phase == 1:
                # frame 1: right arm + left leg forward
                left_arm_end = (cx - 14, head_center[1] + head_r + 8)
                right_arm_end = (cx + 14, head_center[1] + head_r + 14)
                left_leg_end = (cx - 8, hip_y + 16)
                right_leg_end = (cx + 10, hip_y + 20)
            else:
                # frame 0: left arm + right leg forward
                left_arm_end = (cx - 14, head_center[1] + head_r + 14)
                right_arm_end = (cx + 14, head_center[1] + head_r + 8)
                left_leg_end = (cx - 10, hip_y + 20)
                right_leg_end = (cx + 8, hip_y + 16)
            pygame.draw.line(surf, outline, left_arm_start,
                             left_arm_end, limb_w)
            pygame.draw.line(surf, outline, right_arm_start,
                             right_arm_end, limb_w)
            pygame.draw.line(surf, outline, (cx - 3, hip_y),
                             left_leg_end, limb_w)
            pygame.draw.line(surf, outline, (cx + 3, hip_y),
                             right_leg_end, limb_w)
            # pants
            pygame.draw.rect(surf, pants_color, (cx - 9, hip_y, 18, 10))


class Tea:
    def __init__(self):
        self.x = random.randint(40, WIDTH - 40)
        self.y = random.randint(120, HEIGHT - 80)
        # collision radius (used in main loop)
        self.r = 12

        # drawing dimensions for side-view mug
        self.w = 26
        self.h = 30

        self.cup_color = (245, 240, 230)  # ceramic white
        self.tea_color = (180, 120, 80)   # warm tea brown

    def draw(self, surf):
        cx, cy = self.x, self.y

        # cup body (rounded rectangle)
        cup_rect = pygame.Rect(cx - self.w//2, cy - self.h//2, self.w, self.h)
        pygame.draw.rect(surf, self.cup_color, cup_rect, border_radius=8)
        pygame.draw.rect(surf, (100, 80, 60), cup_rect, 2, border_radius=8)

        # tea surface as ellipse near the top
        tea_rect = pygame.Rect(cx - self.w//2 + 4, cy - self.h//2 + 4,
                               self.w - 8, self.h//3)
        pygame.draw.ellipse(surf, self.tea_color, tea_rect)

        # handle: thin semicircle arc, anchored to cup edge
        # Notice: the rect starts exactly at cup’s right edge (cx + self.w//2 - handle_width//2)
        handle_w, handle_h = 10, 14
        handle_rect = pygame.Rect(cx + self.w//2 - handle_w//2, cy - handle_h//2,
                                  handle_w, handle_h)
        pygame.draw.arc(surf, (100, 80, 60), handle_rect,
                        -math.pi/2, math.pi/2, 2)


class Fruit:
    """Fruit spawns on trees, can be clicked for coziness."""
    COLORS = {
        'apple': (220, 50, 50),
        'orange': (255, 140, 0),
        'lemon': (255, 220, 50),
        'grapes': (150, 80, 150),
    }

    def __init__(self, tree_x, tree_y, tree_size=1.0):
        self.tree_x = tree_x
        self.tree_y = tree_y
        self.tree_size = tree_size
        # spawn fruit near tree foliage
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(15, 25)
        self.x = tree_x + math.cos(angle) * dist
        self.y = tree_y - 20 + math.sin(angle) * dist * 0.5
        self.r = int(6 * tree_size)
        self.fruit_type = random.choice(list(self.COLORS.keys()))
        self.color = self.COLORS[self.fruit_type]
        self.collected = False

    def draw(self, surf):
        if not self.collected:
            pygame.draw.circle(
                surf, self.color, (int(self.x), int(self.y)), self.r)
            # highlight
            highlight_r = max(1, self.r - 2)
            pygame.draw.circle(surf, (255, 255, 255), (int(
                self.x - self.r // 3), int(self.y - self.r // 3)), highlight_r // 2)

    def get_value(self):
        """Return coziness value and label based on fruit type."""
        values = {
            'apple': (4, 'Apple'),
            'orange': (5, 'Orange'),
            'lemon': (3, 'Lemon'),
            'grapes': (6, 'Grapes'),
        }
        return values.get(self.fruit_type, (4, 'Apple'))


class SpawnEffect:
    def __init__(self, x, y, text='*', life=SPAWN_EFFECT_LIFE):
        self.x = x
        self.y = y
        self.text = text
        self.life = life
        self.total = life

    def update(self, dt):
        self.life -= dt
        # float upward slightly
        self.y -= 30 * dt

    def draw(self, surf, font):
        if self.life <= 0:
            return
        a = max(0.0, min(1.0, self.life / self.total))
        text_surf = font.render(self.text, True, (60, 30, 20))
        try:
            text_surf.set_alpha(int(255 * a))
        except Exception:
            pass
        surf.blit(text_surf, (int(self.x) - 12, int(self.y) - 6))


class WindChime:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 12
        self.chime_time = 0  # animation timer

    def chime(self):
        self.chime_time = 0.5  # half-second chime animation

    def update(self, dt):
        if self.chime_time > 0:
            self.chime_time -= dt

    def draw(self, surf):
        # simple wind chime
        pygame.draw.circle(surf, (180, 140, 100),
                           (int(self.x), int(self.y)), self.r)
        # strings
        for i in range(3):
            off = math.cos(self.chime_time * 8 + i) * \
                4 if self.chime_time > 0 else 0
            pygame.draw.line(surf, (100, 80, 60), (self.x, self.y),
                             (self.x - 8 + i * 8 + off, self.y + 12), 2)
        # bells
        for i in range(3):
            bell_x = self.x - 8 + i * 8
            bell_y = self.y + 16
            pygame.draw.circle(surf, (200, 160, 100), (bell_x, bell_y), 4)


class Cat:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 14
        self.color = (90, 60, 40)
        self._dir = random.random() * math.tau
        self._speed = 18  # px/sec
        self._timer = random.uniform(1.0, 3.0)
        self._tail_time = 0  # for tail animation

    def update(self, dt):
        # wander: keep a direction for a bit, occasionally pick new
        self._timer -= dt
        if self._timer <= 0:
            self._dir = random.random() * math.tau
            self._timer = random.uniform(1.0, 3.0)
        self.x += math.cos(self._dir) * self._speed * dt
        self.y += math.sin(self._dir) * self._speed * dt
        # clamp to play area
        self.x = max(40, min(WIDTH - 40, self.x))
        self.y = max(120, min(HEIGHT - 80, self.y))
        # advance tail animation
        self._tail_time += dt

    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        # body outline
        pygame.draw.circle(surf, (220, 200, 180), (cx, cy), self.r + 6)
        # body
        pygame.draw.circle(surf, self.color, (cx, cy), self.r)

        # tail (swishy)
        tail_wag = math.sin(self._tail_time * 4) * 8
        tail_base_x = cx + 8
        tail_base_y = cy
        tail_tip_x = tail_base_x + 10 + tail_wag
        tail_tip_y = tail_base_y - 6
        pygame.draw.line(surf, self.color, (tail_base_x, tail_base_y),
                         (tail_tip_x, tail_tip_y), 3)

        # left ear
        pygame.draw.polygon(surf, self.color, [
            (cx - 6, cy - 10),
            (cx - 5, cy - 18),
            (cx - 1, cy - 12)
        ])
        # right ear
        pygame.draw.polygon(surf, self.color, [
            (cx + 6, cy - 10),
            (cx + 5, cy - 18),
            (cx + 1, cy - 12)
        ])

        # eyes (simple dots)
        eye_color = (40, 30, 20)
        pygame.draw.circle(surf, eye_color, (cx - 5, cy - 2), 2)
        pygame.draw.circle(surf, eye_color, (cx + 5, cy - 2), 2)
        # eye shine
        pygame.draw.circle(surf, (200, 200, 200), (cx - 4, cy - 3), 1)
        pygame.draw.circle(surf, (200, 200, 200), (cx + 6, cy - 3), 1)


def draw_fire(surf, cx, cy, t):
    # simple animated flame using sin waves
    base_w = 80
    for i in range(5):
        a = (math.sin(t * 2.0 + i) + 1) / 2
        color = (
            int(255 - 80 * (i / 5.0) - a * 30),
            int(120 + 80 * a - i * 6),
            int(40 - i * 4),
        )
        w = int(base_w * (0.6 + 0.5 * a) * (1 - i * 0.08))
        h = int(80 * (0.7 + 0.4 * a))
        pygame.draw.ellipse(surf, color, (cx - w // 2, cy - h, w, h))
    # log
    pygame.draw.rect(surf, (80, 50, 30), (cx - 60, cy + 10, 120, 18))


def draw_tree(surf, x, y, size=1.0):
    # simple tree: trunk + foliage
    trunk_w = int(12 * size)
    trunk_h = int(30 * size)
    foliage_r = int(25 * size)

    # trunk
    pygame.draw.rect(surf, (101, 67, 33),
                     (x - trunk_w // 2, y, trunk_w, trunk_h))
    # foliage (green circle)
    pygame.draw.circle(surf, (76, 110, 60), (int(
        x), int(y - foliage_r // 2)), foliage_r)
    # lighter foliage highlight
    pygame.draw.circle(surf, (100, 140, 80), (int(
        x - foliage_r // 3), int(y - foliage_r // 3)), foliage_r // 2)


def draw_ui(surf, coziness):
    # top-left cozy meter
    pygame.draw.rect(surf, (30, 30, 30), (20, 20, 220, 28), border_radius=6)
    pygame.draw.rect(surf, (255, 230, 180), (24, 24, int(
        (coziness/100) * 212), 20), border_radius=5)
    font = pygame.font.SysFont(None, 20)
    txt = font.render(f'Cozy: {int(coziness)}', True, (40, 30, 20))
    surf.blit(txt, (250, 22))
    # shop button (top-right)
    pygame.draw.rect(surf, (190, 160, 120), SHOP_BUTTON_RECT, border_radius=6)
    shop_txt = font.render('Shop', True, (40, 30, 20))
    surf.blit(shop_txt, (SHOP_BUTTON_RECT.x + 18, SHOP_BUTTON_RECT.y + 6))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('Cozy Corner')
    # Create a fixed-size buffer surface for the game
    game_surface = pygame.Surface((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    player = Player(WIDTH // 2, HEIGHT // 2)
    teas = [Tea() for _ in range(3)]
    coziness = 10.0
    time = 0.0

    instructions_font = pygame.font.SysFont(None, 20)

    running = True
    spawn_effects = []
    teas_collected = 0

    # rug placement (right side)
    rug_rect = pygame.Rect(WIDTH - 260, HEIGHT - 220, 200, 120)
    # lantern light position
    lantern_x, lantern_y = rug_rect.centerx, rug_rect.top + 18
    # cats
    cats = [Cat(WIDTH - 200, HEIGHT - 200) for _ in range(CAT_COUNT)]

    # trees for scenery
    trees = [
        (80, 120, 1.2),      # left side tree, large
        (150, 160, 0.9),     # left side tree, medium
        (WIDTH - 120, 140, 1.1),  # right side tree, large
        (WIDTH - 200, 180, 0.8),  # right side tree, small
        (WIDTH // 2 - 100, 130, 1.0),  # center-left tree
        (WIDTH // 2 + 80, 150, 0.95),  # center-right tree
    ]

    # fruits on trees
    fruits = []
    for tree_x, tree_y, tree_size in trees:
        # spawn 2-4 fruits per tree
        for _ in range(random.randint(2, 4)):
            fruits.append(Fruit(tree_x, tree_y, tree_size))

    # interaction elements
    windchime = WindChime(WINDCHIME_POS[0], WINDCHIME_POS[1])
    bookshelf_cooldown = 0  # cooldown for bookshelf interaction
    high_cozy_reached = False  # track if player has reached high cozy
    books_read = 0  # count of bookshelf interactions

    # shop state and items
    shop_open = False
    shop_w, shop_h = 420, 340  # taller to fit more items
    shop_x = WIDTH // 2 - shop_w // 2
    shop_y = HEIGHT // 2 - shop_h // 2
    shop_scroll = 0  # scroll position for shop

    def buy_blanket():
        global RUG_COZY_GAIN
        RUG_COZY_GAIN += 1.0

    def buy_cat_treat():
        global CAT_COZY_GAIN
        CAT_COZY_GAIN += 0.8
        # spawn an extra friendly cat immediately
        cats.append(Cat(rug_rect.left - 60, rug_rect.top + 20))

    def buy_firewood():
        global COZY_SIT_GAIN
        COZY_SIT_GAIN += 3.0

    def buy_tea_kettle():
        global TEA_SPAWN_RATE
        TEA_SPAWN_RATE += 0.02  # spawn teas more frequently

    def buy_cozy_socks():
        global COZY_DECAY
        COZY_DECAY *= 0.8  # reduce decay by 20%

    def buy_lamp():
        global SPAWN_EFFECT_LIFE
        SPAWN_EFFECT_LIFE += 0.5  # extend positive effects visually

    def buy_music_box():
        # small coziness boost on purchase
        nonlocal coziness
        coziness = min(100.0, coziness + 20)

    def buy_relaxing_chair():
        global COZY_SIT_GAIN
        COZY_SIT_GAIN += 2.0

    def buy_dream_tea():
        # one-time big coziness boost
        nonlocal coziness
        coziness = min(100.0, coziness + 35)

    shop_items = [
        {'id': 'blanket', 'name': 'Cozy Blanket', 'price': 25.0,
            'desc': '+1 rug cozy', 'bought': False, 'apply': buy_blanket},
        {'id': 'treat', 'name': 'Cat Treat', 'price': 18.0,
            'desc': '+0.8 cat cozy + spawn cat', 'bought': False, 'apply': buy_cat_treat},
        {'id': 'wood', 'name': 'Firewood', 'price': 30.0,
            'desc': '+3 sit gain', 'bought': False, 'apply': buy_firewood},
        {'id': 'kettle', 'name': 'Tea Kettle', 'price': 22.0,
            'desc': 'Spawn tea faster', 'bought': False, 'apply': buy_tea_kettle},
        {'id': 'socks', 'name': 'Cozy Socks', 'price': 20.0,
            'desc': 'Decay slower (-20%)', 'bought': False, 'apply': buy_cozy_socks},
        {'id': 'lamp', 'name': 'Warm Lamp', 'price': 28.0,
            'desc': 'Effects last longer', 'bought': False, 'apply': buy_lamp},
        {'id': 'music', 'name': 'Music Box', 'price': 35.0,
            'desc': '+20 cozy instantly', 'bought': False, 'apply': buy_music_box},
        {'id': 'chair', 'name': 'Relaxing Chair', 'price': 32.0,
            'desc': '+2 sit gain', 'bought': False, 'apply': buy_relaxing_chair},
        {'id': 'dream_tea', 'name': 'Dream Tea', 'price': 50.0,
            'desc': '+35 cozy bliss', 'bought': False, 'apply': buy_dream_tea},
    ]

    while running:
        dt = clock.tick(60) / 1000.0
        time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.sitting = not player.sitting
                elif event.key == pygame.K_e:
                    # windchime interaction
                    dist_to_chime = math.hypot(
                        player.x - windchime.x, player.y - windchime.y)
                    if dist_to_chime < 80:
                        windchime.chime()
                        coziness = min(100.0, coziness + 5)
                        spawn_effects.append(SpawnEffect(
                            windchime.x, windchime.y - 20, 'Ding!'))
                    # bookshelf interaction
                    dist_to_shelf = math.hypot(
                        player.x - BOOKSHELF_POS[0], player.y - BOOKSHELF_POS[1])
                    if dist_to_shelf < 80 and bookshelf_cooldown <= 0:
                        books_read += 1
                        coziness = min(100.0, coziness + 8)
                        bookshelf_cooldown = 2.0
                        spawn_effects.append(SpawnEffect(
                            BOOKSHELF_POS[0], BOOKSHELF_POS[1] + 20, 'Read!'))
                elif event.key == pygame.K_UP and shop_open:
                    # scroll shop up
                    shop_scroll = max(0, shop_scroll - 1)
                elif event.key == pygame.K_DOWN and shop_open:
                    # scroll shop down
                    max_scroll = max(0, len(shop_items) - 7)
                    shop_scroll = min(max_scroll, shop_scroll + 1)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # click on fruits
                for fruit in fruits[:]:
                    if not fruit.collected:
                        dist = math.hypot(fruit.x - mx, fruit.y - my)
                        if dist < fruit.r + 5:  # clickable area
                            fruit.collected = True
                            fruit_value, fruit_label = fruit.get_value()
                            coziness = min(100.0, coziness + fruit_value)
                            spawn_effects.append(SpawnEffect(
                                fruit.x, fruit.y, fruit_label))
                # toggle shop
                if SHOP_BUTTON_RECT.collidepoint(mx, my):
                    shop_open = not shop_open
                    shop_scroll = 0  # reset scroll on open
                elif shop_open:
                    # check buy buttons (with scroll offset)
                    max_visible = 7
                    for idx, it in enumerate(shop_items):
                        if idx < shop_scroll or idx >= shop_scroll + max_visible:
                            continue  # skip off-screen items
                        screen_idx = idx - shop_scroll
                        bx = shop_x + 20
                        by = shop_y + 40 + screen_idx * 40
                        brect = pygame.Rect(bx + 260, by - 6, 90, 26)
                        if brect.collidepoint(mx, my) and not it['bought']:
                            if coziness >= it['price']:
                                coziness -= it['price']
                                it['bought'] = True
                                it['apply']()
                                spawn_effects.append(
                                    SpawnEffect(bx + 60, by, 'Buy!'))

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += player.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= player.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += player.speed

        player.move(dx, dy)
        player.update(dt)

        # update bookshelf cooldown
        bookshelf_cooldown = max(0, bookshelf_cooldown - dt)

        # update windchime
        windchime.update(dt)

        # collision with tea
        for t in teas[:]:
            dist = math.hypot(player.x - t.x, player.y - t.y)
            if dist < player.r + t.r:
                teas.remove(t)
                coziness = min(100, coziness + 12)
                teas_collected += 1
                spawn_effects.append(SpawnEffect(t.x, t.y, 'Sip!'))
                # spawn a new tea slowly
                if random.random() < 0.6:
                    new_tea = Tea()
                    teas.append(new_tea)
                    spawn_effects.append(
                        SpawnEffect(new_tea.x, new_tea.y, 'Tea!'))

        # passive cozy gain when sitting near fire
        fire_x, fire_y = 140, HEIGHT - 160
        if player.sitting and math.hypot(player.x - fire_x, player.y - (fire_y - 20)) < 120:
            # time-proportional sitting gain (points per second)
            coziness = min(100.0, coziness + COZY_SIT_GAIN * dt)

        # coziness decays over time
        coziness = max(0.0, coziness - COZY_DECAY * dt)

        # track high cozy milestone
        if coziness >= HIGH_COZY_THRESHOLD and not high_cozy_reached:
            high_cozy_reached = True
            spawn_effects.append(SpawnEffect(WIDTH // 2, 100, 'Cozy!'))

        # occasional random tea spawn (low rate, capped)
        if len(teas) < TEA_MAX and random.random() < TEA_SPAWN_RATE * dt:
            # try a few times to find a spawn location not too close to player or fire
            for _ in range(8):
                nx = random.randint(40, WIDTH - 40)
                ny = random.randint(120, HEIGHT - 80)
                if math.hypot(nx - player.x, ny - player.y) > 80 and math.hypot(nx - fire_x, ny - fire_y) > 100:
                    new_tea = Tea()
                    teas.append(new_tea)
                    spawn_effects.append(
                        SpawnEffect(new_tea.x, new_tea.y, 'Tea!'))
                    break

        # draw
        game_surface.fill(BG_COLOR)

        # lantern glow (simple translucent circle)
        glow = pygame.Surface((220, 220), pygame.SRCALPHA)
        gx = 110
        gy = 40
        pygame.draw.circle(glow, (255, 240, 200, 90), (gx, gy), 80)
        game_surface.blit(glow, (lantern_x - gx, lantern_y - gy))

        # distant hills
        pygame.draw.ellipse(game_surface, (200, 185, 160),
                            (-100, HEIGHT - 250, 500, 260))
        pygame.draw.ellipse(game_surface, (210, 195, 170),
                            (300, HEIGHT - 260, 600, 260))

        # trees in the background
        for tree_x, tree_y, tree_size in trees:
            draw_tree(game_surface, tree_x, tree_y, tree_size)

        # fireplace
        draw_fire(game_surface, fire_x, fire_y, time)

        # rug (cozy carpet) - more realistic
        pygame.draw.rect(game_surface, (210, 170, 140),
                         rug_rect, border_radius=12)
        pygame.draw.rect(game_surface, (195, 150, 110),
                         rug_rect.inflate(-8, -8), border_radius=10)

        # variable for tassel count
        TASSEL_COUNT = 11  # change this number to control how many tassels per side

        # fringe (tassels) on left/right edges
        for i in range(TASSEL_COUNT):
            y = rug_rect.top + (i + 0.8) * (rug_rect.height // TASSEL_COUNT)
            # left tassels
            pygame.draw.line(game_surface, (160, 120, 90),
                             (rug_rect.left, y), (rug_rect.left - 6, y), 2)
            # right tassels
            pygame.draw.line(game_surface, (160, 120, 90),
                             (rug_rect.right, y), (rug_rect.right + 6, y), 2)

        # subtle woven pattern (horizontal stripes)
        for i in range(0, rug_rect.height, 12):
            pygame.draw.line(game_surface, (180, 140, 110),
                             (rug_rect.left + 6, rug_rect.top + i),
                             (rug_rect.right - 6, rug_rect.top + i), 1)

        # windchime
        windchime.draw(game_surface)

        # bookshelf
        pygame.draw.rect(game_surface, (120, 80, 40),
                         (BOOKSHELF_POS[0] - 20, BOOKSHELF_POS[1] - 30, 40, 60), border_radius=4)
        for i in range(3):
            for j in range(2):
                book_x = BOOKSHELF_POS[0] - 12 + j * 8
                book_y = BOOKSHELF_POS[1] - 20 + i * 12
                color = (200 - i * 30, 100 + j * 40, 60 + i * 20)
                pygame.draw.rect(game_surface, color, (book_x, book_y, 6, 10))

        # teas
        for t in teas:
            t.draw(game_surface)

        # fruits on trees
        for fruit in fruits:
            fruit.draw(game_surface)
        # respawn collected fruits occasionally
        for i in range(len(fruits)):
            # ~0.2% per frame = respawn after ~8 sec on average
            if fruits[i].collected and random.random() < 0.002:
                # respawn the fruit
                tree_x, tree_y, tree_size = trees[i % len(trees)]
                fruits[i] = Fruit(tree_x, tree_y, tree_size)

        # cats update & draw
        for c in cats:
            c.update(dt)
            c.draw(game_surface)
            # if player close to cat, small cozy gain
            if math.hypot(player.x - c.x, player.y - c.y) < 60:
                coziness = min(100.0, coziness + CAT_COZY_GAIN * dt)

        # rug cozy gain when standing on it
        if rug_rect.collidepoint(int(player.x), int(player.y)):
            # standing provides a small passive boost
            coziness = min(100.0, coziness + RUG_COZY_GAIN * dt)

        # update & draw spawn effects (draw above teas/player)
        for e in spawn_effects[:]:
            e.update(dt)
            if e.life <= 0:
                spawn_effects.remove(e)
            else:
                e.draw(game_surface, instructions_font)

        player.draw(game_surface)

        draw_ui(game_surface, coziness)

        # shop panel
        if shop_open:
            # dim background
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((20, 20, 20, 120))
            game_surface.blit(overlay, (0, 0))

            # panel
            pygame.draw.rect(game_surface, (245, 230, 200), (shop_x,
                             shop_y, shop_w, shop_h), border_radius=12)
            pygame.draw.rect(game_surface, (220, 190, 150), (shop_x + 8,
                             shop_y + 8, shop_w - 16, shop_h - 16), border_radius=10)
            title_font = pygame.font.SysFont(None, 26)
            title = title_font.render('Cozy Shop', True, (60, 40, 20))
            game_surface.blit(title, (shop_x + 18, shop_y + 12))

            # items (scrollable)
            item_font = pygame.font.SysFont(None, 18)
            max_visible = 7  # show up to 7 items at a time
            for idx, it in enumerate(shop_items):
                if idx < shop_scroll or idx >= shop_scroll + max_visible:
                    continue  # skip off-screen items
                screen_idx = idx - shop_scroll
                ix = shop_x + 20
                iy = shop_y + 40 + screen_idx * 40
                # item background
                pygame.draw.rect(game_surface, (255, 245, 230),
                                 (ix, iy - 6, shop_w - 56, 34), border_radius=8)
                name = item_font.render(f"{it['name']}", True, (50, 30, 20))
                desc = item_font.render(it['desc'], True, (90, 70, 50))
                game_surface.blit(name, (ix + 6, iy))
                game_surface.blit(desc, (ix + 6, iy + 16))
                # buy button
                bx = ix + 260
                by = iy - 6
                brect = pygame.Rect(bx, by, 90, 26)
                if it['bought']:
                    pygame.draw.rect(game_surface, (170, 170, 170),
                                     brect, border_radius=6)
                    btxt = item_font.render('Owned', True, (100, 100, 100))
                else:
                    btn_color = (160, 120, 80) if coziness >= it['price'] else (
                        200, 180, 160)
                    pygame.draw.rect(game_surface, btn_color,
                                     brect, border_radius=6)
                    btxt = item_font.render(
                        f"Buy {int(it['price'])}", True, (255, 245, 230))
                game_surface.blit(btxt, (bx + 12, by + 5))

            # scroll indicator
            if len(shop_items) > max_visible:
                scroll_font = pygame.font.SysFont(None, 16)
                scroll_txt = scroll_font.render(
                    f"Scroll: {shop_scroll + 1}-{min(shop_scroll + max_visible, len(shop_items))}/{len(shop_items)}", True, (100, 80, 60))
                game_surface.blit(
                    scroll_txt, (shop_x + 20, shop_y + shop_h - 28))

        # instructions
        lines = [
            'Move: Arrow keys / WASD | Space: Sit/Stand | E: Interact (windchime/book)',
            'Sit near fire for cozy gain, collect tea, go on rug for boost',
            f'High cozy: {int(coziness)}/{HIGH_COZY_THRESHOLD} | Books read: {books_read} | Teas collected: {teas_collected}',
            'Click fruits on trees for coziness | Click "Shop" to buy upgrades'
        ]
        for i, l in enumerate(lines):
            img = instructions_font.render(l, True, (70, 50, 40))
            game_surface.blit(img, (20, HEIGHT - 24 * (len(lines) - i)))

        # scale game_surface to fit current window and display
        scaled_surface = pygame.transform.scale(
            game_surface, screen.get_size())
        screen.fill((0, 0, 0))
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
