import pygame
import sys
from random import randint

pygame.init()

WIDTH, HEIGHT = 1000, 1000
SQUARE_SIZE = WIDTH // 8

WHITE = (238, 238, 210)
BROWN = (118, 150, 86)
HIGHLIGHT = (90, 110, 90)
HIGHLIGHT_MOVE = (90, 110, 90)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Шахматы')

pieces_images = {}
pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk',
          'bp', 'bn', 'bb', 'br', 'bq', 'bk']
for piece in pieces:
    image = pygame.image.load(f'images/{piece}.png')
    image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
    pieces_images[piece] = image

logo_frames = []
for i in range(1, 5 + 1):
    frame = pygame.image.load(f"logo/logo_{i}.png")
    frame = pygame.transform.scale(frame, (200, 40))
    logo_frames.append(frame)
logo_x = randint(0, WIDTH - 200)
logo_y = randint(0, HEIGHT - 40)
logo_x_speed = 3
logo_y_speed = 3
logo_frame_index = 0

board = [
    ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
    ['bp'] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    ['wp'] * 8,
    ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
]

selected_piece = None
possible_moves = []
player_turn = 'w'  

def draw_board():
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)
            if (row, col) in possible_moves:
                if board[row][col]:
                    pygame.draw.circle(
                        screen,
                        HIGHLIGHT_MOVE,
                        ((col + 0.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE),
                        60,
                        8,
                    )
                else:
                    pygame.draw.circle(
                        screen,
                        HIGHLIGHT_MOVE,
                        ((col + 0.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE),
                        20,
                    )
            piece = board[row][col]
            if piece:
                screen.blit(pieces_images[piece], rect)
    if selected_piece:
        r, c = selected_piece
        rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, HIGHLIGHT, rect, 4)


def handle_logo():
    global logo_x, logo_y, logo_x_speed, logo_y_speed, logo_frame_index
    logo_frame_index = (logo_frame_index + 1) % len(logo_frames)
    logo = logo_frames[logo_frame_index]
    screen.blit(logo, (logo_x, logo_y))

    logo_x += logo_x_speed
    logo_y += logo_y_speed

    if logo_x <= 0 or logo_x >= WIDTH - 200:
        logo_x_speed = -logo_x_speed
    if logo_y <= 0 or logo_y >= HEIGHT - 40:
        logo_y_speed = -logo_y_speed


def get_square(pos):
    x, y = pos
    return y // SQUARE_SIZE, x // SQUARE_SIZE

def is_in_bounds(row, col):
    return 0 <= row < 8 and 0 <= col < 8

def get_piece_moves(row, col):
    piece = board[row][col]
    if not piece:
        return []
    color = piece[0]
    p_type = piece[1]
    moves = []

    directions = []

    if p_type == 'p':  
        dir = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        if is_in_bounds(row + dir, col) and not board[row + dir][col]:
            moves.append((row + dir, col))
            if row == start_row and not board[row + 2 * dir][col]:
                moves.append((row + 2 * dir, col))
        for dc in [-1, 1]:
            nr, nc = row + dir, col + dc
            if is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target and target[0] != color:
                    moves.append((nr, nc))
    elif p_type == 'r':  
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
    elif p_type == 'b':  
        directions = [(-1,-1),(-1,1),(1,-1),(1,1)]
    elif p_type == 'q':  
        directions = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    elif p_type == 'k':  
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if is_in_bounds(nr, nc):
                    target = board[nr][nc]
                    if not target or target[0] != color:
                        moves.append((nr, nc))
    elif p_type == 'n':  
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            nr, nc = row + dr, col + dc
            if is_in_bounds(nr, nc):
                target = board[nr][nc]
                if not target or target[0] != color:
                    moves.append((nr, nc))
    if p_type in ['r','b','q']:
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            while is_in_bounds(nr, nc):
                target = board[nr][nc]
                if not target:
                    moves.append((nr, nc))
                else:
                    if target[0] != color:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc
    return moves

def is_check(color):
    king_pos = None
    for r in range(8):
        for c in range(8):
            if board[r][c] == color + 'k':
                king_pos = (r, c)
                break
        if king_pos:
            break
    opponent_color = 'b' if color == 'w' else 'w'
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece[0] == opponent_color:
                moves = get_piece_moves(r, c)
                if king_pos in moves:
                    return True
    return False

def move_piece(r1, c1, r2, c2):
    captured = board[r2][c2]
    board[r2][c2] = board[r1][c1]
    board[r1][c1] = None
    return captured

def main():
    global selected_piece, possible_moves, player_turn
    clock = pygame.time.Clock()

    while True:
        draw_board()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_square(pygame.mouse.get_pos())
                piece = board[row][col]
                if selected_piece:
                    if (row, col) in possible_moves:
                        r1, c1 = selected_piece
                        captured = move_piece(r1, c1, row, col)
                        if not is_check(player_turn):
                            player_turn = 'b' if player_turn == 'w' else 'w'
                        else:
                            move_piece(row, col, r1, c1)
                            board[row][col] = captured
                        selected_piece = None
                        possible_moves = []
                    elif piece and piece[0] == player_turn:
                        selected_piece = (row, col)
                        possible_moves = get_piece_moves(row, col)
                    else:
                        selected_piece = None
                        possible_moves = []
                else:
                    if piece and piece[0] == player_turn:
                        selected_piece = (row, col)
                        possible_moves = get_piece_moves(row, col)
        handle_logo()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
