import pygame
import random
import numpy as np
import time
import sys

# Pygame 초기화
pygame.init()

# 게임 보드 크기 설정
BOARD_SIZE = 15
CELL_SIZE = 40
BOARD_WIDTH = BOARD_HEIGHT = BOARD_SIZE * CELL_SIZE

# 색상 정의
BOARD_COLOR = (128, 128, 128)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)

# 게임 상태 정의
EMPTY = 0
BLACK_STONE = 1
WHITE_STONE = 2

# 게임 보드 초기화
board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

# 화면 설정
screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
pygame.display.set_caption("Omok Game with AI")

def player_choose_color():
    choosing = True
    while choosing:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    return BLACK_STONE
                elif event.key == pygame.K_w:
                    return WHITE_STONE
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

def get_opposite_color(color):
    if color == BLACK_STONE:
        return WHITE_STONE
    else:
         return BLACK_STONE
    
# 게임 시작 전 플레이어에게 흑돌 또는 백돌을 선택하도록 요청
font = pygame.font.Font(None, 36)
game_over_text = font.render("Press 'B' for Black stones or 'W' for White stones", True, WHITE)
game_over_rect = game_over_text.get_rect()
game_over_rect.center = (BOARD_WIDTH // 2, BOARD_HEIGHT // 2)
screen.blit(game_over_text, game_over_rect)
pygame.display.flip()
player_color = player_choose_color()

# 플레이어의 선택에 따라 현재 색을 설정
if player_color == WHITE_STONE:
    current_color = BLACK_STONE  # AI가 먼저 시작
else:
    current_color = player_color

opponent_color = get_opposite_color(player_color)

def draw_board():
    for x in range(0, BOARD_WIDTH, CELL_SIZE):
        for y in range(0, BOARD_HEIGHT, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_stones(board):
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            center_x = x * CELL_SIZE + CELL_SIZE // 2
            center_y = y * CELL_SIZE + CELL_SIZE // 2
            if board[x][y] == BLACK_STONE:
                pygame.draw.circle(screen, BLACK, (center_x, center_y), CELL_SIZE // 2 - 4)
            elif board[x][y] == WHITE_STONE:
                pygame.draw.circle(screen, WHITE, (center_x, center_y), CELL_SIZE // 2 - 4)

def is_on_board(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def get_opposite_color(color):
    return opponent_color if color == player_color else player_color

def ai(color, board):
    # AI 알고리즘 구현 부분
    # 우선도 맵을 초기화
    priority = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    max_priority = float('-inf')
    max_coords = []

    def add_priority(x, y, value):
        if is_on_board(x, y) and board[x][y] == EMPTY:
            priority[x][y] += value

    def is_empty(x, y):
        return is_on_board(x, y) and board[x][y] == EMPTY

    def is_color(x, y, stone_color):
        return is_on_board(x, y) and board[x][y] == stone_color

    def check_sequence(x, y, dx, dy, target_color, length, empty_sides_required):
        count = 0
        empty_sides = 0
        for i in range(-empty_sides_required, length + empty_sides_required):
            nx, ny = x + dx * i, y + dy * i
            if is_color(nx, ny, target_color):
                count += 1
            elif is_empty(nx, ny):
                empty_sides += 1
            else:
                break
        return count == length and empty_sides >= empty_sides_required

    # 돌의 개수를 계산
    blockAmount = sum(1 for row in board for cell in row if cell != EMPTY)

    # 놓인 돌이 없거나 1개이면 바둑판 중앙의 우선도를 1000만큼 높임
    if blockAmount < 2:
        center = BOARD_SIZE // 2
        if board[center][center] == EMPTY:
            priority[center][center] += 1000
        else:
            priority[center][center+1] += 1000

    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            # 돌 주변 빈 공간에 우선도를 설정
            if board[x][y] != EMPTY:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if dx != 0 or dy != 0:
                            add_priority(x + dx, y + dy, 1)
            if is_empty(x, y):
                # 2목을 확인하고 우선도 부여
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue
                        if check_sequence(x, y, dx, dy, color, 2, 2):
                            add_priority(x, y, 20 if color == color else 18)
                        if check_sequence(x, y, dx, dy, color, 2, 2):
                            add_priority(x, y, 20 if color == get_opposite_color(color) else 18)
                # 3목을 확인하고 우선도 부여
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue
                        if check_sequence(x, y, dx, dy, color, 3, 1):
                            add_priority(x, y, 99999 if color == color else 1500)
                        if check_sequence(x, y, dx, dy, get_opposite_color(color), 3, 1):
                            add_priority(x, y, 1500 if color == get_opposite_color(color) else 99999)

    # 우선도를 기반으로 최적의 수를 찾기
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if priority[x][y] > max_priority:
                max_priority = priority[x][y]
                max_coords = [(x, y)]
            elif priority[x][y] == max_priority:
                max_coords.append((x, y))

    # 가장 높은 우선도를 가진 위치 중 하나를 무작위로 선택
    return random.choice(max_coords) if max_coords else None

def check_win(board, stone):
    directions = [(1,0), (0,1), (1,1), (1,-1)]  # 가로, 세로, 대각선 방향
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] == stone:
                for dx, dy in directions:
                    count = 1
                    for i in range(1, 5):
                        nx, ny = x + dx*i, y + dy*i
                        if is_on_board(nx, ny) and board[nx][ny] == stone:
                            count += 1
                        else:
                            break
                    if count == 5:
                        return True
    return False

# 메인 게임 루프
running = True
winner = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and current_color == player_color:  # 플레이어의 턴
            mouseX, mouseY = pygame.mouse.get_pos()
            x = mouseX // CELL_SIZE
            y = mouseY // CELL_SIZE
            if board[x][y] == EMPTY:
                board[x][y] = player_color
                if check_win(board, player_color):
                    winner = 'Player'
                    running = False
                else:
                    current_color = opponent_color  # AI의 턴으로 변경

    screen.fill(BOARD_COLOR)
    draw_board()
    draw_stones(board)
    pygame.display.flip()

    time.sleep(0.5)
    if current_color == opponent_color and not winner:  # AI의 턴
        x, y = ai(current_color, board)
        board[x][y] = opponent_color
        if check_win(board, opponent_color):
            winner = 'AI'
            running = False
        current_color = player_color  # 플레이어의 턴으로 변경

    screen.fill(BOARD_COLOR)
    draw_board()
    draw_stones(board)
    pygame.display.flip()


if winner:
    font = pygame.font.Font(None, 36)
    game_over_text = font.render(f"{winner} win!", True, YELLOW)
    game_over_rect = game_over_text.get_rect()
    game_over_rect.center = (BOARD_WIDTH // 2, BOARD_HEIGHT // 2)
    screen.blit(game_over_text, game_over_rect)
    pygame.display.flip()
    pygame.time.wait(7000)

pygame.quit()
sys.exit()