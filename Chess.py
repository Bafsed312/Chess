import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8

WHITE = (245, 245, 220)
BROWN = (139, 69, 19)
HIGHLIGHT = (0, 255, 0)
HIGHLIGHT_MOVE = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Шахматы')

pieces_images = {}
pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk',
          'bp', 'bn', 'bb', 'br', 'bq', 'bk']
for piece in pieces:
    image = pygame.image.load(f'images/{piece}.png')
    image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
    pieces_images[piece] = image

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
                pygame.draw.rect(screen, HIGHLIGHT_MOVE, rect, 4)
            piece = board[row][col]
            if piece:
                screen.blit(pieces_images[piece], rect)
    if selected_piece:
        r, c = selected_piece
        rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, HIGHLIGHT, rect, 4)

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