import pygame
import random
import numpy as np

# Pygame 초기화
pygame.init()

# 게임 보드 크기 설정
BOARD_SIZE = 15
CELL_SIZE = 40
BOARD_WIDTH = BOARD_HEIGHT = BOARD_SIZE * CELL_SIZE

# 색상 정의
bg_color = (128, 128, 128)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
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
    return BLACK_STONE if color == WHITE_STONE else WHITE_STONE

def ai(color, board):
    # AI 알고리즘 구현 부분
    # 우선도 맵을 초기화합니다.
    priority = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    max_priority = float('-inf')
    max_coords = []

    def add_priority(x, y, value):
        if is_on_board(x, y) and board[x][y] == EMPTY:
            priority[x][y] += value

    # 돌 주변 빈 공간에 우선도를 설정합니다.
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] != EMPTY:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if dx != 0 or dy != 0:
                            add_priority(x + dx, y + dy, 1)

    # 우선도를 기반으로 최적의 수를 찾습니다.
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if priority[x][y] > max_priority:
                max_priority = priority[x][y]
                max_coords = [(x, y)]
            elif priority[x][y] == max_priority:
                max_coords.append((x, y))

    # 가장 높은 우선도를 가진 위치 중 하나를 무작위로 선택합니다.
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
current_color = BLACK_STONE  # 게임을 시작하는 색
winner = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and current_color == BLACK_STONE:  # 플레이어의 턴
            mouseX, mouseY = pygame.mouse.get_pos()
            x = mouseX // CELL_SIZE
            y = mouseY // CELL_SIZE
            if board[x][y] == EMPTY:
                board[x][y] = BLACK_STONE
                if check_win(board, BLACK_STONE):
                    winner = 'Black'
                    running = False
                else:
                    current_color = WHITE_STONE  # AI의 턴으로 변경

    if current_color == WHITE_STONE and not winner:  # AI의 턴
        x, y = ai(current_color, board)
        board[x][y] = WHITE_STONE
        if check_win(board, WHITE_STONE):
            winner = 'White'
            running = False
        current_color = BLACK_STONE  # 플레이어의 턴으로 변경

    # 화면 그리기
    screen.fill(bg_color)
    draw_board()
    draw_stones(board)
    pygame.display.flip()

pygame.quit()
if winner:
    print(f"{winner} wins!")
