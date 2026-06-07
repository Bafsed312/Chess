import pygame
import sys
from random import randint, choice
import copy

# Инициализация Pygame
pygame.init()

# Константы экрана и доски
WIDTH, HEIGHT = 1000, 1000
SQUARE_SIZE = WIDTH // 8  # Размер одной клетки (125x125 пикселей)

# Цвета (RGB)
WHITE = (238, 238, 210)      # Светлые клетки
BROWN = (118, 150, 86)       # Темные клетки
HIGHLIGHT = (90, 110, 90)    # Подсветка выбранной фигуры
HIGHLIGHT_MOVE = (90, 110, 90)  # Подсветка возможных ходов
CHECK_RED = (255, 50, 50)    # Цвет подсветки короля под шахом
MENU_BG = (50, 50, 50)       # Фон меню
MENU_BORDER = (200, 200, 200) # Граница меню
BUTTON_COLOR = (100, 100, 150) # Цвет кнопки
BUTTON_HOVER = (130, 130, 180) # Цвет кнопки при наведении
BUTTON_TEXT = (255, 255, 255)  # Цвет текста кнопки

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Шахматы')

# Загрузка изображений фигур
pieces_images = {}
pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk',  # Белые фигуры
          'bp', 'bn', 'bb', 'br', 'bq', 'bk']  # Черные фигуры
for piece in pieces:
    image = pygame.image.load(f'images/{piece}.png')
    image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
    pieces_images[piece] = image

# Анимация логотипа (летающий по экрану текст)
logo_frames = []
for i in range(1, 5 + 1):
    frame = pygame.image.load(f"logo/logo_{i}.png")
    frame = pygame.transform.scale(frame, (200, 40))
    frame = frame.convert_alpha()
    logo_frames.append(frame)

# Параметры движения логотипа
logo_x = randint(0, WIDTH - 200)  # Случайная начальная позиция X
logo_y = randint(0, HEIGHT - 40)  # Случайная начальная позиция Y
logo_x_speed = 3  # Скорость по X
logo_y_speed = 3  # Скорость по Y
logo_frame_index = 0  # Текущий кадр анимации

# Начальная расстановка фигур на доске
# board[ряд][колонка] - ряд 0 сверху (черные), ряд 7 снизу (белые)
board = [
    ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],  # 0: черные фигуры
    ['bp'] * 8,                                          # 1: черные пешки
    [None] * 8,                                          # 2: пустые клетки
    [None] * 8,                                          # 3: пустые клетки
    [None] * 8,                                          # 4: пустые клетки
    [None] * 8,                                          # 5: пустые клетки
    ['wp'] * 8,                                          # 6: белые пешки
    ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']    # 7: белые фигуры
]

# Игровые переменные
selected_piece = None        # Выбранная фигура (ряд, колонка)
possible_moves = []          # Список возможных ходов для выбранной фигуры
player_turn = 'w'            # Чей ход: 'w' - белые, 'b' - черные
game_mode = None             # Режим игры: 'pvp' или 'pve'
bot_color = 'b'              # Цвет бота (черные)

# Флаги рокировки
king_moved = {'w': False, 'b': False}  # Двигался ли король
rook_moved = {'w': {'left': False, 'right': False},  # Двигались ли ладьи
              'b': {'left': False, 'right': False}}

# Превращение пешки
pawn_promotion_pending = None  # Ожидающее превращение пешки (ряд, колонка, цвет)
bot_thinking = False           # Флаг, что бот обдумывает ход
waiting_for_promotion = False  # Флаг ожидания выбора фигуры для превращения

# Веса фигур для оценки позиции (условные единицы)
piece_values = {
    'p': 10,   # Пешка
    'n': 30,   # Конь
    'b': 30,   # Слон
    'r': 50,   # Ладья
    'q': 90,   # Ферзь
    'k': 900   # Король (очень высокая ценность, чтобы избегать его потери)
}

CAPTURE_BONUS = 5  # Бонус за взятие фигуры

# Позиционные бонусы для пешек (поощряет продвижение вперед)
pawn_position_bonus = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [0,  0,  0,  0,  0,  0,  0,  0]
]

# Позиционные бонусы для коней (центр доски ценнее)
knight_position_bonus = [
    [-5, -4, -3, -2, -2, -3, -4, -5],
    [-4, -2,  0,  1,  1,  0, -2, -4],
    [-3,  0,  2,  3,  3,  2,  0, -3],
    [-2,  1,  3,  4,  4,  3,  1, -2],
    [-2,  1,  3,  4,  4,  3,  1, -2],
    [-3,  0,  2,  3,  3,  2,  0, -3],
    [-4, -2,  0,  1,  1,  0, -2, -4],
    [-5, -4, -3, -2, -2, -3, -4, -5]
]

def draw_menu():
    """Отрисовка главного меню с выбором режима игры"""
    screen.fill((30, 30, 40))
    
    # Заголовок
    font_title = pygame.font.Font(None, 72)
    font_button = pygame.font.Font(None, 48)
    
    title = font_title.render("Шахматы", True, (255, 255, 255))
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title, title_rect)
    
    # Кнопка "Игрок vs Игрок"
    pvp_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 80)
    mouse_pos = pygame.mouse.get_pos()
    
    # Эффект наведения на кнопку
    if pvp_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER, pvp_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, pvp_rect)
    
    pygame.draw.rect(screen, MENU_BORDER, pvp_rect, 3)
    pvp_text = font_button.render("Игрок vs Игрок", True, BUTTON_TEXT)
    pvp_text_rect = pvp_text.get_rect(center=pvp_rect.center)
    screen.blit(pvp_text, pvp_text_rect)
    
    # Кнопка "Игрок vs Компьютер"
    pve_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 60, 300, 80)
    
    if pve_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER, pve_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, pve_rect)
    
    pygame.draw.rect(screen, MENU_BORDER, pve_rect, 3)
    pve_text = font_button.render("Игрок vs Компьютер", True, BUTTON_TEXT)
    pve_text_rect = pve_text.get_rect(center=pve_rect.center)
    screen.blit(pve_text, pve_text_rect)
    
    # Анимация логотипа
    handle_logo()
    pygame.display.flip()
    
    return pvp_rect, pve_rect

def get_game_mode():
    """Получение выбранного режима игры от пользователя"""
    global game_mode
    pvp_rect, pve_rect = draw_menu()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pvp_rect.collidepoint(event.pos):
                    game_mode = 'pvp'
                    waiting = False
                elif pve_rect.collidepoint(event.pos):
                    game_mode = 'pve'
                    waiting = False
        
        # Обновляем меню для анимации логотипа
        pvp_rect, pve_rect = draw_menu()
        pygame.display.flip()
        pygame.time.delay(50)

def draw_board():
    """Отрисовка шахматной доски, фигур и интерфейса"""
    global player_turn
    
    # Проверка шаха для текущего игрока
    king_in_check = is_check(player_turn)
    king_pos = None
    if king_in_check:
        # Находим позицию короля для подсветки
        for r in range(8):
            for c in range(8):
                if board[r][c] == player_turn + 'k':
                    king_pos = (r, c)
                    break
            if king_pos:
                break
    
    # Отрисовка клеток доски и возможных ходов
    for row in range(8):
        for col in range(8):
            # Цвет клетки
            color = WHITE if (row + col) % 2 == 0 else BROWN
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)
            
            # Подсветка возможных ходов
            if (row, col) in possible_moves:
                if board[row][col]:
                    # Если на клетке есть фигура - показываем кружок для взятия
                    pygame.draw.circle(
                        screen,
                        HIGHLIGHT_MOVE,
                        ((col + 0.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE),
                        60,
                        8,
                    )
                else:
                    # Если клетка пустая - маленький кружок
                    pygame.draw.circle(
                        screen,
                        HIGHLIGHT_MOVE,
                        ((col + 0.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE),
                        20,
                    )
            
            # Подсветка короля под шахом
            if king_pos and (row, col) == king_pos:
                highlight_rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(screen, CHECK_RED, highlight_rect, 8)
            
            # Отрисовка фигуры
            piece = board[row][col]
            if piece:
                screen.blit(pieces_images[piece], rect)
    
    # Подсветка выбранной фигуры
    if selected_piece:
        r, c = selected_piece
        rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, HIGHLIGHT, rect, 4)
    
    # Отображение информации о режиме и текущем ходе
    font = pygame.font.Font(None, 36)
    if game_mode == 'pvp':
        mode_text = font.render("Режим: Игрок vs Игрок", True, (255, 255, 255))
    else:
        mode_text = font.render("Режим: Игрок vs Компьютер", True, (255, 255, 255))
    screen.blit(mode_text, (10, 10))
    
    if not waiting_for_promotion:
        turn_text = font.render(f"Ход: {'Белые' if player_turn == 'w' else 'Черные'}", True, (255, 255, 255))
        screen.blit(turn_text, (10, 50))

def show_promotion_menu(row, col, color):
    """
    Меню выбора фигуры для превращения пешки (для игрока)
    row, col - позиция пешки
    color - цвет пешки ('w' или 'b')
    """
    menu_width = SQUARE_SIZE * 4
    menu_height = SQUARE_SIZE
    menu_x = col * SQUARE_SIZE
    menu_y = row * SQUARE_SIZE
    
    # Корректировка позиции меню, чтобы не выходило за экран
    if row == 0:
        menu_y = row * SQUARE_SIZE
    else:
        menu_y = (row - 1) * SQUARE_SIZE
    
    if menu_y < 0:
        menu_y = 0
    if menu_y + menu_height > HEIGHT:
        menu_y = HEIGHT - menu_height
    
    # Полупрозрачный фон меню
    s = pygame.Surface((menu_width, menu_height))
    s.set_alpha(200)
    s.fill(MENU_BG)
    screen.blit(s, (menu_x, menu_y))
    
    # Граница меню
    pygame.draw.rect(screen, MENU_BORDER, (menu_x, menu_y, menu_width, menu_height), 3)
    
    # Фигуры для выбора (в порядке: ферзь, конь, ладья, слон)
    pieces_order = ['q', 'n', 'r', 'b']
    
    for i, piece_type in enumerate(pieces_order):
        piece_code = color + piece_type
        if piece_code in pieces_images:
            x = menu_x + i * SQUARE_SIZE
            y = menu_y
            screen.blit(pieces_images[piece_code], (x, y))
    
    pygame.display.flip()
    
    # Ожидание выбора пользователя
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
    
    return color + 'q'  # По умолчанию ферзь

def auto_promote_to_queen(row, col, color):
    """Автоматическое превращение пешки в ферзя (для бота)"""
    board[row][col] = color + 'q'

def handle_logo():
    """Анимация летающего логотипа (отскакивает от стен)"""
    global logo_x, logo_y, logo_x_speed, logo_y_speed, logo_frame_index
    
    # Смена кадра анимации
    logo_frame_index = (logo_frame_index + 1) % len(logo_frames)
    logo = logo_frames[logo_frame_index]
    screen.blit(logo, (logo_x, logo_y))
    
    # Движение
    logo_x += logo_x_speed
    logo_y += logo_y_speed
    
    # Отскок от границ экрана
    if logo_x <= 0:
        logo_x = 0
        logo_x_speed = -logo_x_speed
    if logo_x >= WIDTH - 200:
        logo_x = WIDTH - 200
        logo_x_speed = -logo_x_speed
    if logo_y <= 0:
        logo_y = 0
        logo_y_speed = -logo_y_speed
    if logo_y >= HEIGHT - 40:
        logo_y = HEIGHT - 40
        logo_y_speed = -logo_y_speed

def get_square(pos):
    """Преобразование координат мыши в индексы клетки доски"""
    x, y = pos
    return y // SQUARE_SIZE, x // SQUARE_SIZE

def is_in_bounds(row, col):
    """Проверка, находятся ли координаты в пределах доски"""
    return 0 <= row < 8 and 0 <= col < 8

def is_square_attacked(row, col, color):
    """Проверка, атакована ли клетка (row, col) фигурой противника"""
    opponent_color = 'b' if color == 'w' else 'w'
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece[0] == opponent_color:
                # Получаем все ходы фигуры без проверки на шах
                moves = get_piece_moves(r, c, check_check=False)
                if (row, col) in moves:
                    return True
    return False

def get_piece_moves(row, col, check_check=True):
    """
    Возвращает список возможных ходов для фигуры на позиции (row, col)
    check_check - если True, исключает ходы, которые оставляют/ставят короля под шах
    """
    piece = board[row][col]
    if not piece:
        return []
    color = piece[0]
    p_type = piece[1]
    moves = []

    # Ходы пешки
    if p_type == 'p':
        dir = -1 if color == 'w' else 1  # Направление движения: белые вверх (-1), черные вниз (+1)
        start_row = 6 if color == 'w' else 1  # Начальный ряд для двойного хода
        
        # Ход на одну клетку вперед
        if is_in_bounds(row + dir, col) and not board[row + dir][col]:
            moves.append((row + dir, col))
            # Ход на две клетки вперед
            if row == start_row and not board[row + 2 * dir][col]:
                moves.append((row + 2 * dir, col))
        
        # Взятие по диагонали
        for dc in [-1, 1]:
            nr, nc = row + dir, col + dc
            if is_in_bounds(nr, nc):
                target = board[nr][nc]
                if target and target[0] != color:
                    moves.append((nr, nc))
    
    # Ходы коня
    elif p_type == 'n':
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            nr, nc = row + dr, col + dc
            if is_in_bounds(nr, nc):
                target = board[nr][nc]
                if not target or target[0] != color:
                    moves.append((nr, nc))
    
    # Ходы короля (включая рокировку)
    elif p_type == 'k':
        # Обычные ходы на соседние клетки
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if is_in_bounds(nr, nc):
                    target = board[nr][nc]
                    if not target or target[0] != color:
                        moves.append((nr, nc))
        
        # Короткая рокировка
        if not king_moved[color]:
            if not rook_moved[color]['right']:
                if color == 'w':
                    # Проверка пути и атакованных клеток
                    if (board[7][5] is None and board[7][6] is None and 
                        board[7][7] == 'wr'):
                        if (not is_square_attacked(7, 4, color) and 
                            not is_square_attacked(7, 5, color) and 
                            not is_square_attacked(7, 6, color)):
                            moves.append((7, 6))
                else:
                    if (board[0][5] is None and board[0][6] is None and 
                        board[0][7] == 'br'):
                        if (not is_square_attacked(0, 4, color) and 
                            not is_square_attacked(0, 5, color) and 
                            not is_square_attacked(0, 6, color)):
                            moves.append((0, 6))
            
            # Длинная рокировка
            if not rook_moved[color]['left']:
                if color == 'w':
                    if (board[7][1] is None and board[7][2] is None and 
                        board[7][3] is None and board[7][0] == 'wr'):
                        if (not is_square_attacked(7, 4, color) and 
                            not is_square_attacked(7, 3, color) and 
                            not is_square_attacked(7, 2, color)):
                            moves.append((7, 2))
                else:
                    if (board[0][1] is None and board[0][2] is None and 
                        board[0][3] is None and board[0][0] == 'br'):
                        if (not is_square_attacked(0, 4, color) and 
                            not is_square_attacked(0, 3, color) and 
                            not is_square_attacked(0, 2, color)):
                            moves.append((0, 2))
    
    # Ходы ладьи, слона и ферзя (линейные фигуры)
    elif p_type in ['r', 'b', 'q']:
        # Направления движения
        if p_type == 'r':
            directions = [(-1,0),(1,0),(0,-1),(0,1)]  # Вертикаль и горизонталь
        elif p_type == 'b':
            directions = [(-1,-1),(-1,1),(1,-1),(1,1)]  # Диагонали
        else:  # Ферзь
            directions = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        
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
    
    # Фильтрация ходов, которые ставят/оставляют короля под шах
    if check_check:
        valid_moves = []
        for move in moves:
            r2, c2 = move
            # Сохраняем состояние перед ходом
            captured = board[r2][c2]
            board[r2][c2] = board[row][col]
            board[row][col] = None
            
            # Проверяем, не под шахом ли король после хода
            if not is_check(color):
                valid_moves.append(move)
            
            # Откатываем ход
            board[row][col] = board[r2][c2]
            board[r2][c2] = captured
        
        return valid_moves
    
    return moves

def is_check(color):
    """Проверка, находится ли король цвета color под шахом"""
    # Находим позицию короля
    king_pos = None
    for r in range(8):
        for c in range(8):
            if board[r][c] == color + 'k':
                king_pos = (r, c)
                break
        if king_pos:
            break
    
    if not king_pos:
        return False
    
    # Проверяем, атакуют ли фигуры противника позицию короля
    opponent_color = 'b' if color == 'w' else 'w'
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece[0] == opponent_color:
                # Получаем все ходы без проверки на шах (избегаем рекурсии)
                moves = get_piece_moves(r, c, check_check=False)
                if king_pos in moves:
                    return True
    return False

def is_checkmate(color):
    """Проверка мата для игрока цвета color"""
    # Если нет шаха - не может быть мата
    if not is_check(color):
        return False
    
    # Проверяем, есть ли хоть один возможный ход
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece[0] == color:
                moves = get_piece_moves(r, c)
                if moves:
                    return False
    return True

def move_piece(r1, c1, r2, c2):
    """
    Выполняет перемещение фигуры с (r1,c1) на (r2,c2)
    Возвращает взятую фигуру (если была)
    """
    global king_moved, rook_moved, pawn_promotion_pending
    piece = board[r1][c1]
    if not piece:
        return None
    
    piece_type = piece[1]
    piece_color = piece[0]
    
    # Обработка рокировки (перемещение ладьи)
    if piece_type == 'k':
        king_moved[piece_color] = True
        # Короткая рокировка
        if c2 == c1 + 2:
            if piece_color == 'w':
                board[7][7] = None
                board[7][5] = 'wr'
            else:
                board[0][7] = None
                board[0][5] = 'br'
        # Длинная рокировка
        elif c2 == c1 - 2:
            if piece_color == 'w':
                board[7][0] = None
                board[7][3] = 'wr'
            else:
                board[0][0] = None
                board[0][3] = 'br'
    
    # Запоминаем, что ладья двигалась
    if piece_type == 'r':
        if c1 == 0:
            rook_moved[piece_color]['left'] = True
        elif c1 == 7:
            rook_moved[piece_color]['right'] = True
    
    # Выполняем перемещение
    captured = board[r2][c2]
    board[r2][c2] = board[r1][c1]
    board[r1][c1] = None
    
    # Проверка на превращение пешки
    if board[r2][c2] and board[r2][c2][1] == 'p':
        if (board[r2][c2][0] == 'w' and r2 == 0) or (board[r2][c2][0] == 'b' and r2 == 7):
            pawn_promotion_pending = (r2, c2, board[r2][c2][0])
    
    return captured

def promote_pawn(row, col, color):
    """
    Обработка превращения пешки
    Для человека - показывает меню выбора
    Для бота - автоматически превращает в ферзя
    """
    if color == 'w' or game_mode == 'pvp':
        # Для человека показываем меню
        new_piece = show_promotion_menu(row, col, color)
        board[row][col] = new_piece
    else:
        # Для бота автоматически в ферзя
        auto_promote_to_queen(row, col, color)

def evaluate_board():
    """Оценка текущей позиции на доске (положительная - лучше для белых)"""
    score = 0
    
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece:
                color = piece[0]
                p_type = piece[1]
                value = piece_values[p_type]
                
                # Позиционные бонусы
                position_bonus = 0
                if p_type == 'p':
                    if color == 'w':
                        position_bonus = pawn_position_bonus[7 - r][c]
                    else:
                        position_bonus = pawn_position_bonus[r][c]
                elif p_type == 'n':
                    if color == 'w':
                        position_bonus = knight_position_bonus[7 - r][c]
                    else:
                        position_bonus = knight_position_bonus[r][c]
                
                # Белые увеличивают счет, черные уменьшают
                if color == 'w':
                    score += value + position_bonus
                else:
                    score -= value + position_bonus
    
    return score

def get_all_moves(color):
    """
    Получает все возможные ходы для фигур цвета color
    Возвращает список кортежей (приоритет, r1, c1, r2, c2)
    Приоритет выше для взятий ценных фигур
    """
    all_moves = []
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece[0] == color:
                moves = get_piece_moves(r, c)
                for move in moves:
                    r2, c2 = move
                    move_score = 0
                    target = board[r2][c2]
                    if target:
                        # Бонус за взятие фигуры
                        target_value = piece_values.get(target[1], 0)
                        move_score = target_value + CAPTURE_BONUS
                    
                    all_moves.append((move_score, r, c, r2, c2))
    
    # Сортируем по убыванию приоритета (взятия идут первыми)
    all_moves.sort(reverse=True)
    return all_moves

def get_best_move():
    """
    Выбирает лучший ход для бота
    Использует приоритет взятий и проверку на безопасность
    """
    bot_moves = get_all_moves(bot_color)
    
    if not bot_moves:
        return None
    
    # Сначала пробуем ходы с высоким приоритетом (взятия)
    for score, r1, c1, r2, c2 in bot_moves[:5]:
        captured = board[r2][c2]
        # Временно выполняем ход
        board[r2][c2] = board[r1][c1]
        board[r1][c1] = None
        
        # Если ход не оставляет короля под шахом - принимаем
        if not is_check(bot_color):
            # Откатываем
            board[r1][c1] = board[r2][c2]
            board[r2][c2] = captured
            return (r1, c1, r2, c2)
        
        # Откатываем
        board[r1][c1] = board[r2][c2]
        board[r2][c2] = captured
    
    # Если все хорошие ходы опасны, пробуем любые безопасные
    for score, r1, c1, r2, c2 in bot_moves:
        captured = board[r2][c2]
        board[r2][c2] = board[r1][c1]
        board[r1][c1] = None
        
        if not is_check(bot_color):
            board[r1][c1] = board[r2][c2]
            board[r2][c2] = captured
            return (r1, c1, r2, c2)
        
        board[r1][c1] = board[r2][c2]
        board[r2][c2] = captured
    
    return None

def make_bot_move():
    """Выполняет ход бота с небольшой задержкой"""
    global player_turn, selected_piece, possible_moves, pawn_promotion_pending, bot_thinking
    
    # Проверяем, что очередь бота и нет ожидающих действий
    if player_turn == bot_color and not pawn_promotion_pending and not bot_thinking and not waiting_for_promotion:
        bot_thinking = True
        
        # Искусственная задержка для имитации "мышления"
        pygame.time.wait(300)
        pygame.display.flip()
        
        best_move = get_best_move()
        
        if best_move:
            r1, c1, r2, c2 = best_move
            
            # Выполняем ход
            captured = move_piece(r1, c1, r2, c2)
            
            # Если нужно превращение пешки
            if pawn_promotion_pending:
                # Автоматически превращаем в ферзя
                row, col, color = pawn_promotion_pending
                auto_promote_to_queen(row, col, color)
                pawn_promotion_pending = None
                
                # Меняем ход
                player_turn = 'w' if player_turn == 'b' else 'b'
                selected_piece = None
                possible_moves = []
                bot_thinking = False
                return
            
            # Меняем ход
            player_turn = 'w' if player_turn == 'b' else 'b'
            selected_piece = None
            possible_moves = []
        
        bot_thinking = False

def show_game_over(message):
    """Показывает сообщение о конце игры с возможностью начать заново"""
    font = pygame.font.Font(None, 74)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Затемняющий оверлей    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    screen.blit(text, text_rect)
    
    # Инструкция
    font_small = pygame.font.Font(None, 36)
    restart_text = font_small.render("Нажмите R для новой игры или ESC для выхода", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()
    
    # Ожидание нажатия клавиши
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def reset_game():
    """Сброс игры до начального состояния"""
    global board, selected_piece, possible_moves, player_turn, king_moved, rook_moved, pawn_promotion_pending, bot_thinking, waiting_for_promotion
    
    # Восстанавливаем начальную расстановку
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
    
    # Сбрасываем все переменные
    selected_piece = None
    possible_moves = []
    player_turn = 'w'
    king_moved = {'w': False, 'b': False}
    rook_moved = {'w': {'left': False, 'right': False}, 'b': {'left': False, 'right': False}}
    pawn_promotion_pending = None
    bot_thinking = False
    waiting_for_promotion = False

def main():
    """Главный игровой цикл"""
    global selected_piece, possible_moves, player_turn, pawn_promotion_pending, waiting_for_promotion
    
    # Получаем режим игры в начале
    get_game_mode()
    
    clock = pygame.time.Clock()
    
    while True:
        # Отрисовка доски и интерфейса
        draw_board()
        
        # Проверка на мат
        if is_checkmate('w'):
            show_game_over("Черные победили! (Мат)")
            continue
        elif is_checkmate('b'):
            show_game_over("Белые победили! (Мат)")
            continue
        
        # Обработка превращения пешки
        if pawn_promotion_pending:
            waiting_for_promotion = True
            row, col, color = pawn_promotion_pending
            
            # Для черных (бота) - автоматическое превращение
            if color == 'b' and game_mode == 'pve':
                auto_promote_to_queen(row, col, color)
                pawn_promotion_pending = None
                waiting_for_promotion = False
                # Меняем ход после превращения
                player_turn = 'b' if player_turn == 'w' else 'w'
            else:
                # Для человека - показываем меню выбора
                promote_pawn(row, col, color)
                pawn_promotion_pending = None
                waiting_for_promotion = False
                # Меняем ход после превращения
                player_turn = 'b' if player_turn == 'w' else 'w'
            continue
        
        # Ход бота (если включен режим PvE и очередь бота)
        if game_mode == 'pve' and player_turn == bot_color and not pawn_promotion_pending and not waiting_for_promotion:
            make_bot_move()
        
        # Обработка событий (ход человека)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Если ход бота или ожидание превращения - игрок не может ходить
                if (game_mode == 'pve' and player_turn == bot_color) or waiting_for_promotion:
                    continue
                
                row, col = get_square(pygame.mouse.get_pos())
                piece = board[row][col]
                
                if selected_piece:
                    # Если фигура уже выбрана
                    if (row, col) in possible_moves:
                        # Выполняем ход
                        r1, c1 = selected_piece
                        captured = move_piece(r1, c1, row, col)
                        
                        # Проверяем, не под шахом ли после хода
                        if not is_check(player_turn):
                            # Меняем игрока
                            if not pawn_promotion_pending:
                                player_turn = 'b' if player_turn == 'w' else 'w'
                        else:
                            # Откатываем ход, если он оставляет короля под шахом
                            move_piece(row, col, r1, c1)
                            board[row][col] = captured
                        
                        selected_piece = None
                        possible_moves = []
                    elif piece and piece[0] == player_turn:
                        # Выбираем другую фигуру
                        selected_piece = (row, col)
                        possible_moves = get_piece_moves(row, col)
                    else:
                        # Снимаем выделение
                        selected_piece = None
                        possible_moves = []
                else:
                    # Выбираем фигуру
                    if piece and piece[0] == player_turn:
                        selected_piece = (row, col)
                        possible_moves = get_piece_moves(row, col)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
        
        # Анимация логотипа
        handle_logo()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
