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
CHECK_RED = (255, 50, 50)

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

king_moved = {'w': False, 'b': False}
rook_moved = {'w': {'left': False, 'right': False}, 'b': {'left': False, 'right': False}}

pawn_promotion_pending = None

def draw_board():
    global player_turn
    king_in_check = is_check(player_turn)
    king_pos = None
    if king_in_check:
        for r in range(8):
            for c in range(8):
                if board[r][c] == player_turn + 'k':
                    king_pos = (r, c)
                    break
            if king_pos:
                break
    
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
            
            if king_pos and (row, col) == king_pos:
                highlight_rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(screen, CHECK_RED, highlight_rect, 8)
            
            piece = board[row][col]
            if piece:
                screen.blit(pieces_images[piece], rect)
    
    if selected_piece:
        r, c = selected_piece
        rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, HIGHLIGHT, rect, 4)

def show_promotion_menu(row, col, color):
    menu_width = SQUARE_SIZE * 4
    menu_height = SQUARE_SIZE
    menu_x = col * SQUARE_SIZE
    menu_y = row * SQUARE_SIZE
    
    if row == 0:
        menu_y = row * SQUARE_SIZE
    else:
        menu_y = (row - 1) * SQUARE_SIZE
    
    if menu_y < 0:
        menu_y = 0
    if menu_y + menu_height > HEIGHT:
        menu_y = HEIGHT - menu_height
    
    pygame.draw.rect(screen, (50, 50, 50), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, (200, 200, 200), (menu_x, menu_y, menu_width, menu_height), 3)
    
    pieces_order = ['q', 'n', 'r', 'b']
    
    for i, piece_type in enumerate(pieces_order):
        piece_code = color + piece_type
        if piece_code in pieces_images:
            x = menu_x + i * SQUARE_SIZE
            y = menu_y
            screen.blit(pieces_images[piece_code], (x, y))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if menu_y <= mouse_y <= menu_y + menu_height:
                    piece_index = (mouse_x - menu_x) // SQUARE_SIZE
                    if 0 <= piece_index < 4:
                        piece_type = pieces_order[piece_index]
                        return color + piece_type
        pygame.display.flip()
    
    return color + 'q'