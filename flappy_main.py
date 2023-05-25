import pygame
import random
from pypresence import Presence
import time

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 1600, 900
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird · Made by Lolo280374 w/ chatGPT")

# Load icon
icon = pygame.image.load("assets/sprites/flappy.ico")
pygame.display.set_icon(icon)

# Load images
background_img = pygame.transform.scale(pygame.image.load("assets/sprites/background.png"), (WIDTH, HEIGHT))
bird_img = pygame.transform.scale(pygame.image.load("assets/sprites/bird.png"), (100, 70))
pipe_img = pygame.transform.scale(pygame.image.load("assets/sprites/pipe.png"), (200, 700))
game_over_img = pygame.transform.scale(pygame.image.load("assets/sprites/game_over.png"), (800, 400))
pause_img = pygame.transform.scale(pygame.image.load("assets/sprites/pause.png"), (800, 400))

# Game variables
clock = pygame.time.Clock()
fps_limit = 144  # Set the desired FPS limit
gravity = 0.25
bird_movement = 0
score = 0
high_score = 0

# Set up the bird
bird_rect = bird_img.get_rect(center=(200, HEIGHT // 2))

# Set up pipes
pipe_heights = [400, 500, 600]
pipe_gap = 300
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)

# Game over flag
game_over = False

# Pause flag
game_paused = False

# Load font
font = pygame.font.Font("assets/fonts/04B_19.ttf", 120)
fps_font = pygame.font.Font(None, 36)  # Font for FPS counter

# Discord RPC
RPC = Presence('1109435413036281876')  # Replace 'YOUR_CLIENT_ID' with your Discord application's client ID
RPC.connect()

# Set the game details and start time
start_time = time.time()
presence_details = {
    'details': 'Playing Flappy Bird',
    'start': start_time,
    'large_image': 'flappy_icon',  # Unique key for the large icon asset in your Discord application
}
RPC.update(**presence_details)

def draw_background():
    display.blit(background_img, (0, 0))

def draw_bird():
    display.blit(bird_img, bird_rect)

def draw_pipes():
    for pipe in pipe_list:
        if pipe.bottom >= HEIGHT:
            display.blit(pipe_img, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_img, False, True)
            display.blit(flip_pipe, pipe)

def move_pipes():
    for pipe in pipe_list:
        pipe.centerx -= 5
    return pipe_list

def check_collision():
    for pipe in pipe_list:
        if bird_rect.colliderect(pipe):
            return True

    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
        return True

    return False

def update_score(score, high_score):
    if score > high_score:
        high_score = score
    score_surface = font.render(str(score), True, (255, 255, 255))

    high_score_surface = font.render("High Score: " + str(high_score), True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(WIDTH // 2, 100))
    high_score_rect = high_score_surface.get_rect(center=(WIDTH // 2, 800))
    display.blit(score_surface, score_rect)
    display.blit(high_score_surface, high_score_rect)
    return high_score

def restart_game():
    bird_rect.center = (200, HEIGHT // 2)
    bird_movement = 0
    pipe_list.clear()
    score = 0
    return score

def create_pipe():
    random_pipe_pos = random.choice(pipe_heights)
    bottom_pipe = pipe_img.get_rect(midtop=(WIDTH + 200, random_pipe_pos + pipe_gap // 2))
    top_pipe = pipe_img.get_rect(midbottom=(WIDTH + 200, random_pipe_pos - pipe_gap // 2))
    return bottom_pipe, top_pipe

def show_pause_screen():
    display.blit(pause_img, (WIDTH // 2 - pause_img.get_width() // 2, HEIGHT // 2 - pause_img.get_height() // 2))

def show_game_over_screen():
    display.blit(game_over_img, (WIDTH // 2 - game_over_img.get_width() // 2, HEIGHT // 2 - game_over_img.get_height() // 2))

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over and not game_paused:
                bird_movement = 0
                bird_movement -= 6

            if event.key == pygame.K_SPACE and (game_over or game_paused):
                game_over = False
                game_paused = False
                score = restart_game()

            if event.key == pygame.K_ESCAPE:
                game_paused = not game_paused

        if event.type == SPAWNPIPE:
            if not game_over and not game_paused:
                pipe_list.extend(create_pipe())

    if not game_over:
        # Draw the background
        draw_background()

        if not game_paused:
            # Bird movement
            bird_movement += gravity
            bird_rect.centery += bird_movement
            draw_bird()

            # Pipe movement
            pipe_list = move_pipes()
            draw_pipes()

            # Collision detection
            game_over = check_collision()

            # Update score
            score += 0.01
            high_score = update_score(int(score), high_score)

            # Calculate FPS
            fps = clock.get_fps()
            fps_text = fps_font.render(f"FPS: {int(fps)}", True, (255, 255, 255))

            # Draw FPS counter
            display.blit(fps_text, (10, 10))

            # Update Discord presence state with score
            presence_state = {
                'state': f'Score: {int(score)} · High Score: {int(high_score)}',
                'start': start_time,
            }
            RPC.update(**presence_state)

        else:
            # Display pause screen
            show_pause_screen()

    else:
        # Display game over screen
        show_game_over_screen()
        high_score = update_score(int(score), high_score)

    # Cap the FPS
    clock.tick(fps_limit)

    # Display
    pygame.display.update()

# Close the connection to the Discord RPC
RPC.close()

# Quit the game
pygame.quit()
