#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bugs to fix:
#    Add Header to the game
#    Fix the Player vs computer mode
#    Add turn printing throughout while playing the game

# ספרייה זה אוסף של קודם שיש שם מחלקות ופונקציות שעוזרת למתכנתים בתחום מסוים
# ספריה לטיפול במערכים
import numpy as np
# ספריה לייצור מספרים רנדומליים
import random
# ספרייה שיש בה פונקציות ומחלקות שעוזרות לפתחת משחקים
import pygame
# ספריה עם פונקציות שעוזרות לעבוד עם מערכת ההפעלה כמו למשל לשמור קובץ
import sys
# ספריה שעוזרת לפעולות מתמטיות
import math
import time
from threading import Thread
import socket
# ספרייה של גרפיקה
import pygame_gui









#מכניסה לשחקנים ערכים בשביל לבדוק של מי התור
PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

#כמה יש בשורה פחות 3 (בשביל להשוות אחכ את העיגולים)
WINDOW_LENGTH = 4



def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score
#פיס זה המגיק נמבר אחד או שניים (אם זה השחקן או המחשב)
#בודקת כמה יש ברצף
def score_position(board, piece):
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3
    #מחפש לשים בסדר של שורה, כמה יש בשורה
    for r in range(ROW_COUNT):
                #נקודותיים בשביל לאמר על כל השורה
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
                        #נקודיים זה ממקום מסוים עד קום מסוים
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    #מחפש לשים בסדר של עמודה, כמה יש בעמודה
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    #מחפש לשים באלכסון בשיפוע חיובי, כמה יש באלכסון כזה
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
        #מחפש לשים באלכסון בשיפוע שלילי, כמה יש באלכסון כזה
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value
#מחזירה את המיקום המיקום הפנוי הראשון בעמודה
def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

#מה הרצף הכי גבוה
def pick_best_move(board, piece):
        #מכניסה למשתנה את הרצפים
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
                #מה השורה הפנויה באותה העמודה
        row = get_next_open_row(board, col)
        #מעתיקה את הלוח למשתנה נוסף
        temp_board = board.copy()
        #שם את העיגול במקום שאני אומרת
        drop_piece(temp_board, row, col, piece)
        #כה יש ברצף באותו הצבע
        score = score_position(temp_board, piece)
        #אם יש יותר במה שהכנסתי עכשיו מאשר הבסט, תכניס לבסט את כמות הרץ הנוכחית ותשנה את הבסט עמודה להיות הנוכחית
        if score > best_score:
            best_score = score
            best_col = col

    return best_col




def computer(turn):
        # בגלל שהפעולה מחזירה את הלוח אני רוצה להכניס למשתנה בשם לוח את הלוח
    board = create_board()
    # מכניסה לפעולה את הלוח
    print_board(board)
    # בנתיים כשהמשחק עדיין לא נגמר
    game_over = False


    size = (width, height)

    # לפי הגודל שהגדרתי מייצר את המשטח שעליו מציירת את המשחק
    screen = pygame.display.set_mode(size)
    # קורא לפונקציה לצייר עם המערך
    draw_board(board, screen)
    pygame.display.update()
    # סוג האותיות והגודל
    # מונו ספייס אומר אותו רוחב לכל אות
    myfont = pygame.font.SysFont("monospace", 75)
    game_over=False
        
    #כאשר המחשק עדיין לא נגמר, פעולה המבינה את פעולות הלחיצה בעכבר
    while not game_over:
            #אם פעולת העכבר על משהו שנגמר- משחק מסתיים
            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                            sys.exit()
                    #אם פעולת העכבר היא תזוזה
                    if event.type == pygame.MOUSEMOTION:
                            #מצייר את התא שהוא מרובע לתזוזה
                            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                            #מיקומו על ציר האיקס
                            posx = event.pos[0]
                            #אם התור הוא של השחקן ולא של המחשב
                            if turn == PLAYER:
                                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                                    aaa = myfont.render("turn PLAYER 1!", 1,RED)
                                    screen.blit(aaa, (40,10))
                    #מעדכן את התצוגה
                    pygame.display.update()
                    #בודק אם לחצו בעכבר ותור של מי
                    if event.type == pygame.MOUSEBUTTONDOWN:
                            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                            #אם תור השחקן ולא המחשב
                            if turn == PLAYER:
                                    
                                    #מיקומו על ציר האיקס - מספר הפיקסלים
                                    posx = event.pos[0]
                                    #איזה עמודה - מספר הפיקסלים של השורה לחלק למאה ובלי שבר
                                    col = int(math.floor(posx/SQUARESIZE))
                                    #האם המיקום עדיין בתוקף כלומר ריק תכניס את העיגול
                                    if is_valid_location(board, col):
                                            row = get_next_open_row(board, col)
                                            drop_piece(board, row, col, PLAYER_PIECE)
                                            #אם יש ניצחון של ארבע ברצף גייםאובר שווה לטרו
                                            if winning_move(board, PLAYER_PIECE):
                                                    label = myfont.render("Player 1 wins!!", 1, RED)
                                                    screen.blit(label, (40,10))
                                                    game_over = True
                                            #מחליף תורות 
                                            turn += 1
                                            turn = turn % 2
                                            #מכניס את הלוח לפונקציות שיצרוו את הלוח
                                            print_board(board)
                                            draw_board(board,screen)
 

            #אם תור המחשב והמשחק עדיין לא נגמר
            if turn == AI and not game_over:                

                    #col = random.randint(0, COLUMN_COUNT-1)
                    #col = pick_best_move(board, AI_PIECE)
                    col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

                    if is_valid_location(board, col):
                            #pygame.time.wait(500)
                            row = get_next_open_row(board, col)
                            drop_piece(board, row, col, AI_PIECE)

                            if winning_move(board, AI_PIECE):
                                    label = myfont.render("Player 2 wins!!", 1, YELLOW)
                                    screen.blit(label, (40,10))
                                    game_over = True
                            #מכניס את הלוח לפונקציות שיצרוו את הלוח
                            print_board(board)
                            draw_board(board,screen)
                            #מחליף את התורות
                            turn += 1
                            turn = turn % 2
    #אחרי שנגמר המחשק, ממתין שלוש שניות
            if game_over:
                    pygame.time.wait(3000)
        


def draw_board_instractions(board,screen):
        #מקבלת את המערך ועל ידי שני לולאות נכנסת למערך ובסוף בעצם יוצרת את השטח הכחול והעיגולים השחורים
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
                        #פונקציה ליצירת מלבן, מוכנס המסך, צבע כחול, מאיפה עד איפה (מספר עמודות כפול גודל המרובע של כל עיגול שהוא מאה)
                        #מספר השורות כפול גודל המרובע של כל עיגול מאה ועוד מאה כי השורה הראשונה רוצה שתהיה ריקה והמרחק מאה
			pygame.draw.rect(screen, PINK, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			#פונקציה ליצירת העיגול השחור, מוכנס שטח המסך, צבע שחור, מאיפה עד איפה
			#מספר העמודות כפול הגודל שהוא מאה ועוד חמישים כי זה מתחיל ממכרז העיגול
			#המרחק שהוא מספר השורות כפול מאה ועוד מאה (כי מתחיל משורה שנייה) ועוד חמישים, ומוכנס הרדיוס שהגדרתי
			pygame.draw.circle(screen, PINK2, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
        #מקבלת את המערך ועל ידי שני לולאות נכנסת למערך ומציירת את העיגול באותו הצבע של תור השחקן
	
        #בשביל שיגיד שעכשיו ממש יצייר את מה שהגדרתי על המסך
	pygame.display.update()

PINK = (246, 191, 179)
PINK2 = (247, 225, 220)
def Instructions():
    
#בגלל שהפעולה מחזירה את הלוח אני רוצה להכניס למשתנה בשם לוח את הלוח
    board = create_board()
#מכניסה לפעולה את הלוח
    print_board(board)
#בנתיים כשהמשחק עדיין לא נגמר
    game_over = False

    



    size = (width, height)

#לפי הגודל שהגדרתי מייצר את המשטח שעליו מציירת את המשחק
    screen = pygame.display.set_mode(size)
#קורא לפונקציה לצייר עם המערך
    draw_board_instractions(board,screen)
    pygame.display.update()
#סוג האותיות והגודל
#מונו ספייס אומר אותו רוחב לכל אות
    myfont = pygame.font.SysFont("monospace", 75)
    myfont2= pygame.font.SysFont("arial", 40)
    myfont3 = pygame.font.SysFont("monospace", 20)
    
#כאשר המחשק עדיין לא נגמר, פעולה המבינה את פעולות הלחיצה בעכבר
    while not game_over:
        
        #אם פעולת העכבר על משהו שנגמר- משחק מסתיים
            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                            sys.exit()
                    
                #אם פעולת העכבר היא תזוזה
                    if event.type == pygame.MOUSEMOTION:
                        #מצייר את התא שהוא מרובע לתזוזה
                            pygame.draw.rect(screen, PINK2, (0,0, width, SQUARESIZE))
			#מיקומו על ציר האיקס
                            posx = event.pos[0]
			#לפי התור של מי, מצייר את העיגול
                            
                #מעדכן את התצוגה
                    
                    aaa = myfont.render("Instructions", 1,BLACK)
                    screen.blit(aaa, (50,10))
                    Content_instructions = myfont2.render("The four in a row rules are very simple.",1,BLACK)
                    screen.blit(Content_instructions, (50,150))
                    Content_instructions = myfont2.render("It's always played with 2 players and in a",1,BLACK)
                    screen.blit(Content_instructions, (50,200))
                    Content_instructions = myfont2.render("grid 7x6.",1,BLACK)
                    screen.blit(Content_instructions, (50,250))
                    Content_instructions = myfont2.render("Each turn each player puts a piece of his",1,BLACK)
                    screen.blit(Content_instructions, (50,300))
                    Content_instructions = myfont2.render("color inside a column and it will fall until it",1,BLACK)
                    screen.blit(Content_instructions, (50,350))
                    Content_instructions = myfont2.render( "reaches the lowest available spot.",1,BLACK) 
                    screen.blit(Content_instructions, (50,400))
                    Content_instructions = myfont2.render("The one who can put 4 pieces of the same ", 1,BLACK)
                    screen.blit(Content_instructions, (50,450))
                    Content_instructions = myfont2.render("color in a row horizontally, vertically or ",1,BLACK)
                    screen.blit(Content_instructions, (50,500))
                    Content_instructions = myfont2.render("diagonally wins.",1,BLACK)
                    screen.blit(Content_instructions, (50,550))
                    Content_instructions = myfont3.render("press to back",1,BLACK)
                    screen.blit(Content_instructions, (50,610))
                    pygame.display.update()
                
                




SERVER = True
CLIENT = not SERVER
# משתנים לצבעים של המשחק
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# מספר שורות
ROW_COUNT = 6
# מספר עמודות
COLUMN_COUNT = 7

# מספר הפיקסלים בריבוע של כל עיגול
SQUARESIZE = 100

# גודל הרדיוס של העיגול- פחות חמש כי רוצים שהעיגול לא יתפרס על כל חתיכת הריבוע
RADIUS = int(SQUARESIZE / 2 - 5)

# גודל הרוחב
width = COLUMN_COUNT * SQUARESIZE
# פלוס 1 בשביל השורה העליונה
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)

# יוצר מערך- לפי כמות השורות וכמות הטורים
# מלא באפסים


def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board
# פעולה שמקבלת את המערך המלא באפסים, מספר השורה, העמודה, ואת העיגול ומניחה את העיגול במקום שאני רוצה במערך


def drop_piece(board, row, col, piece):
    board[row][col] = piece
# פעולה- האם המיקום תקף- מקבלת את המערך הדו מימדי ואת העמודה וומחזירה טרו אם העמודה ריקה (שווה לאפס) ואחרת מחזירה פולס


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0
# פעולה הבודקת את השורה הפנויה , מקבלת את המערך ואת מספר העמודה
# על ידי לולאת פור (רנג עושה מאפס עד מספר מסוים- מספר השורות שש) ומציב תנאי שאם הלוח ריק במספר השורה ומספר העמודה תחזיר את מספר השורה


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r
# בשביל שרוצים שהעיגולים יהיו למטה ולא יצופו למעלה (היה אפשר לשנות את זה גם ברנג)


def print_board(board):
    print(np.flip(board, 0))
# פונקציה הבודקת אם יש רצף של ארבעה עיגולים


def winning_move(board, piece):
    # בודק אם יש ניצחון בשורה (אופקי)
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True

    # בודק אם יש ניצחון בטור (אנכי)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # בודק אם יש ניצחון בשיפוע חיובי
    # מתקדם כל פעם גם בשורה וגם בעמודה בהשוואה
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True

    # בודק אם יש ניצחון בשיפוע שלילי
    # מתקדם כל פעם בעמודה ויורד בשורה
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True


# פעולה המציירת את הלוח על ידי קבלת המערך
def draw_board(board, screen):
        # מקבלת את המערך ועל ידי שני לולאות נכנסת למערך ובסוף בעצם יוצרת את השטח הכחול והעיגולים השחורים
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
                        # פונקציה ליצירת מלבן, מוכנס המסך, צבע כחול, מאיפה עד איפה (מספר עמודות כפול גודל המרובע של כל עיגול שהוא מאה)
                        # מספר השורות כפול גודל המרובע של כל עיגול מאה ועוד מאה כי השורה הראשונה רוצה שתהיה ריקה והמרחק מאה
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r *
                             SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            # פונקציה ליצירת העיגול השחור, מוכנס שטח המסך, צבע שחור, מאיפה עד איפה
            # מספר העמודות כפול הגודל שהוא מאה ועוד חמישים כי זה מתחיל ממכרז העיגול
            # המרחק שהוא מספר השורות כפול מאה ועוד מאה (כי מתחיל משורה שנייה) ועוד חמישים, ומוכנס הרדיוס שהגדרתי
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE / 2),
                               int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
        # מקבלת את המערך ועל ידי שני לולאות נכנסת למערך ומציירת את העיגול באותו הצבע של תור השחקן
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
                        # אם במיקום הזה במערך שווה לאחת אז תצייר עיגול אדום
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2),
                                   height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            # אם במיקום הזה במערך שווה לשתיים אז תצייר עיגול צהוב
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2),
                                   height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
        # בשביל שיגיד שעכשיו ממש יצייר את מה שהגדרתי על המסך
    pygame.display.update()


def wait_for_msg(conn_socket, ):
    global network_msg
    print("before")
    network_msg = conn_socket.recv(128)
    print("after: thread received " + network_msg.decode())


def OnlineGame(turn, role, conn_socket, server_socket):
    # בגלל שהפעולה מחזירה את הלוח אני רוצה להכניס למשתנה בשם לוח את הלוח
    board = create_board()
    global network_msg
# מכניסה לפעולה את הלוח
    print_board(board)
# בנתיים כשהמשחק עדיין לא נגמר
    game_over = False
# התור של מי
# אם השרת עונה אז הוא מגריל את הפורט
# מספר הפיקסלים בריבוע של כל עיגול
    SQUARESIZE = 100
# גודל הרוחב
# גודל הרדיוס של העיגול- פחות חמש כי רוצים שהעיגול לא יתפרס על כל חתיכת הריבוע
    RADIUS = int(SQUARESIZE / 2 - 5)
# לפי הגודל שהגדרתי מייצר את המשטח שעליו מציירת את המשחק
    screen = pygame.display.set_mode(size)
# קורא לפונקציה לצייר עם המערך
    draw_board(board, screen)
    pygame.display.update()
# סוג האותיות והגודל
# מונו ספייס אומר אותו רוחב לכל אות
    myfont = pygame.font.SysFont("monospace", 75)
    thread = None
# כאשר המחשק עדיין לא נגמר, פעולה המבינה את פעולות הלחיצה בעכבר
    while not game_over:
    # אם פעולת העכבר על משהו שנגמר- משחק מסתיים
        if (role != turn):
            if (thread == None):
                thread = Thread(target=wait_for_msg, args = [conn_socket])
                thread.start()
                print("I started a thread")
            if (network_msg != ""):
                print("Just recieved a message")
                thread.join()
                thread = None
                col, row = eval(network_msg)
                drop_piece(board, row, col, int(role) + 1)
                print_board(board)
                draw_board(board, screen)
                if winning_move(board, int(role) + 1):
                    label = myfont.render(
                        "Player " + str(int(role) + 1) + " wins!!", 1, RED)
                    screen.blit(label, (40, 10))
                    draw_board(board, screen)
                    print("Game Over. Now waiting...")

                    pygame.time.wait(10000)
                    game_over = True
                turn = not turn
                if (turn == SERVER):
                    print("Now turn is SERVER")
                else:
                    print("Now turn is CLIENT")
                network_msg = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if (role == SERVER):
                    server_socket.close()
                    conn_socket.close()
                if (role == CLIENT):
                    conn_socket.close()
                sys.exit()

    # אם פעולת העכבר היא תזוזה
            if event.type == pygame.MOUSEMOTION:
            # מצייר את התא שהוא מרובע לתזוזה
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            # מיקומו על ציר האיקס
                posx = event.pos[0]
            # לפי התור של מי, מצייר את העיגול
                if role == SERVER:
                    pygame.draw.circle(
                        screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                else:
                    pygame.draw.circle(
                        screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)

        # בודק אם לחצו בעכבר ותור של מי
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                if (role == turn):
                # מיקומו על ציר האיקס - מספר הפיקסלים
                    posx = event.pos[0]
            # איזה עמודה - מספר הפיקסלים של השורה לחלק למאה ובלי שבר
                    col = int(math.floor(posx / SQUARESIZE))
            # האם המיקום עדיין בתוקף כלומר ריק תכניס את העיגול
                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, int(not role) + 1)
                        print_board(board)
                        draw_board(board,screen)
                    # אם יש ניצחון של ארבע ברצף גייםאובר שווה לטרו
##                        to_send = str((col, row)).encode(encoding='UTF-8')
##                        conn_socket.send(to_send)
                        if winning_move(board, int(not role) + 1):
##                            label = myfont.render(
##                                "Player " + str(int(not role) + 1) + " wins!!", 1, RED)
##                            screen.blit(label, (40, 10))
##                            draw_board(board, screen)
##                            print("Game Over. Now waiting...")
##                            pygame.time.wait(10000)
                            game_over = True
                        else:
                            turn = not turn
                        to_send = str((col, row)).encode(encoding = 'UTF-8')
                        conn_socket.send(to_send)
##                        if (turn == SERVER):
##                            print("Now turn is SERVER")
##                        else:
##                            print("Now turn is CLIENT")
                        
                # אם תור שחקן שני
            # אחרי שנגמר המחשק, ממתין שלוש שניות
                if game_over:
                    pygame.time.wait(3000)
        #pygame.display.update()

                            
        if (turn == SERVER and game_over == False):
            aaa = myfont.render("turn PLAYER 1!", 1,RED)
            screen.blit(aaa, (40,10))

        elif (game_over == False):
            aaa = myfont.render("turn PLAYER 2!", 1,YELLOW)
            screen.blit(aaa, (40,10))
        pygame.display.update()

    screen.fill(BLACK)
    if (turn == SERVER):
        label = myfont.render("Player 1 wins!!", 1, RED)
        screen.blit(label, (40, 10))
    else:
        label = myfont.render("Player 2 wins!!", 1, YELLOW)
        screen.blit(label, (40, 10))
    pygame.display.update()
    time.sleep(10)
                # אם תור שחקן שני
            # אחרי שנגמר המחשק, ממתין שלוש שניות
    
    if (role == SERVER):
        server_socket.close()
        conn_socket.close()
    if (role == CLIENT):
        conn_socket.close()


def TwoPlayers():

# בגלל שהפעולה מחזירה את הלוח אני רוצה להכניס למשתנה בשם לוח את הלוח
    board = create_board()
# מכניסה לפעולה את הלוח
    print_board(board)
# בנתיים כשהמשחק עדיין לא נגמר
    game_over = False
# התור של מי
    turn = 0

    size = (width, height)

# לפי הגודל שהגדרתי מייצר את המשטח שעליו מציירת את המשחק
    screen = pygame.display.set_mode(size)
# קורא לפונקציה לצייר עם המערך
    draw_board(board, screen)
    pygame.display.update()
# סוג האותיות והגודל
# מונו ספייס אומר אותו רוחב לכל אות
    myfont = pygame.font.SysFont("monospace", 75)
# כאשר המחשק עדיין לא נגמר, פעולה המבינה את פעולות הלחיצה בעכבר
    while not game_over:
        # אם פעולת העכבר על משהו שנגמר- משחק מסתיים
            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                            sys.exit()
                # אם פעולת העכבר היא תזוזה
                    if event.type == pygame.MOUSEMOTION:
                        # מצייר את התא שהוא מרובע לתזוזה
                            pygame.draw.rect(
                                screen, BLACK, (0, 0, width, SQUARESIZE))
            # מיקומו על ציר האיקס
                            posx = event.pos[0]
            # לפי התור של מי, מצייר את העיגול
                            if turn == 0:
                                    pygame.draw.circle(
                                        screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                                    aaa = myfont.render("turn PLAYER 1!", 1, RED)
                                    screen.blit(aaa, (40,10))
                            else:
                                    pygame.draw.circle(
                                        screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)
                                    aaa = myfont.render("turn PLAYER 2!", 1, YELLOW)
                                    screen.blit(aaa, (40,10))
                # מעדכן את התצוגה
                    pygame.display.update()

                # בודק אם לחצו בעכבר ותור של מי
                    if event.type == pygame.MOUSEBUTTONDOWN:
                            pygame.draw.rect(
                                screen, BLACK, (0, 0, width, SQUARESIZE))
            # אם תור שחקן ראשון
                            if turn == 0:
                                # מיקומו על ציר האיקס - מספר הפיקסלים
                                    posx = event.pos[0]
                # איזה עמודה - מספר הפיקסלים של השורה לחלק למאה ובלי שבר
                                    col = int(math.floor(posx / SQUARESIZE))
                                # האם המיקום עדיין בתוקף כלומר ריק תכניס את העיגול
                                    if is_valid_location(board, col):
                                            row = get_next_open_row(board, col)
                                            drop_piece(board, row, col, 1)
                                        # אם יש ניצחון של ארבע ברצף גייםאובר שווה לטרו
                                            if winning_move(board, 1):
                                                    label = myfont.render(
                                                        "Player 1 wins!!", 1, RED)
                                                    screen.blit(
                                                        label, (40, 10))
                                                    game_over = True

            # אם תור שחקן שני
                            else:
                                # מיקומו על ציר האיקס - מספר הפיקסלים
                                    posx = event.pos[0]
                # איזה עמודה - מספר הפיקסלים של השורה לחלק למאה ובלי שבר
                                    col = int(math.floor(posx / SQUARESIZE))
                                # האם המיקום עדיין בתוקף כלומר ריק תכניס את העיגול
                                    if is_valid_location(board, col):
                                            row = get_next_open_row(board, col)
                                            drop_piece(board, row, col, 2)
                                        # אם יש ניצחון של ארבע ברצף גייםאובר שווה לטרו
                                            if winning_move(board, 2):
                                                    label = myfont.render(
                                                        "Player 2 wins!!", 1, YELLOW)
                                                    screen.blit(
                                                        label, (40, 10))
                                                    game_over = True
                        # מכניס את הלוח לפונקציות שיצרוו את הלוח
                            print_board(board)
                            draw_board(board, screen)
                        # מחליף את התורות
                            turn += 1
                            turn = turn % 2
                        # אחרי שנגמר המחשק, ממתין שלוש שניות
                            if game_over:
                                    pygame.time.wait(3000)


def main():
    # לאתחל
    pygame.init()
    # דיספליי- להציג. זאת הכותרת
    pygame.display.set_caption("Noa's Game")
    # גודל החלון
    window_surface = pygame.display.set_mode(size)

    background = pygame.Surface(size)
    # איז צבע הרקע
    background.fill(pygame.Color('#5F9EA0'))
    # יוצרת אובייקט מנגר שלמד את כל הדברים של המחלקה
    manager = pygame_gui.UIManager(size)
    button_width = 250
    button_height = 50
    # ההגדרות של איך הכפתור יראה גודל, מיקום, מה יהיה רשום
    TwoPlayersButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
        (width // 2 - button_width // 2, 210), (button_width, button_height)), text='2 players', manager=manager)
    # 2 players from another computer
    ServerButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
        (width // 2 - button_width // 2, 285), (button_width, button_height)), text='server', manager=manager)
    ClientButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
        (width // 2 - button_width // 2, 360), (button_width, button_height)), text='client', manager=manager)
    ComputerButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
        (width // 2 - button_width // 2, 435), (button_width, button_height)), text='play against the computer', manager=manager)
    instuctions = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
        (width // 2 - button_width // 2, 510), (button_width, button_height)),text='Instruction',manager=manager)
    portEnterExists = False
    clock = pygame.time.Clock()
    is_running = True

    #כותרת למשחק
    title = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
        (width // 2 - button_width // 0.75, 100), (button_width+410, button_height-17)), text='Four in a Row', manager=manager)
    
    while is_running:
        # שישים לחלק לאלף- שיהיה כל שנייה
        time_delta = clock.tick(60) / 1000.0
        # כשאשר מתבצעת פעולת יציאה- רנינג שווה לפולס
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            
            

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    # כפתור ראשון
                    if event.ui_element == TwoPlayersButton:
                        TwoPlayers()

                    # כפתור שני
                    if event.ui_element == ServerButton:
                        turn = bool(random.getrandbits(1))
                        role = SERVER
                        RandNum = random.randint(1024, 65535)
                        PortLabel = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
                            (width // 2 + button_width // 2 + 25, 275), (175, 50)), text= "Port Number is: " + str(RandNum), manager=manager)  # 575, 275
                        manager.update(time_delta)
                        window_surface.blit(background, (0, 0))
                        manager.draw_ui(window_surface)
                        pygame.display.update()
                        server_socket = socket.socket()
                        server_socket.bind(("0.0.0.0", RandNum))
                        server_socket.listen(1)
                        (conn_socket, client_address) = server_socket.accept()
                        time.sleep(1)
                        to_send = str(turn).encode(encoding = 'UTF-8')
                        conn_socket.send(to_send)
                        OnlineGame(turn, role, conn_socket, server_socket)
                        manager.clear_and_reset()
                        #בשביל שיחזור למסך פתיחה
                        TwoPlayersButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                            (width // 2 - button_width // 2, 210), (button_width, button_height)), text='2 players', manager=manager)
    # 2 players from another computer
                        ServerButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                            (width // 2 - button_width // 2, 285), (button_width, button_height)), text='server', manager=manager)
                        ClientButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                            (width // 2 - button_width // 2, 360), (button_width, button_height)), text='client', manager=manager)
                        ComputerButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                            (width // 2 - button_width // 2, 435), (button_width, button_height)), text='play against the computer', manager=manager)
                        instuctions = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                            (width // 2 - button_width // 2, 510), (button_width, button_height)),text='Instruction',manager=manager)
                        title = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
                            (width // 2 - button_width // 0.75, 100), (button_width+410, button_height-17)), text='Four in a Row', manager=manager)


    # אם הלקוח עונה אז שהוא יכתוב פורט והשרת יתחבר לאותו הפורט
                    if event.ui_element == ClientButton:
                        PortEntry =  pygame_gui.elements.ui_text_entry_line.UITextEntryLine(relative_rect=pygame.Rect(
                            (width // 2 + button_width // 2 + 25, 350), (175, 25)), manager=manager)  # 575, 275
                        PortEnter =  pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                            (width // 2 + button_width // 2 + 25, 375), (175, 25)), text='Enter Port', manager=manager)# 575, 275
                        PortEntry.set_text("")
                        PortEntry.set_allowed_characters('numbers')
                        PortEntry.focus()
                        portEnterExists = True

                    if portEnterExists == True and event.ui_element == PortEnter:
                        portNum = int(PortEntry.get_text())
                        conn_socket = socket.socket()
                        conn_socket.connect(("127.0.0.1", portNum))
                        role = CLIENT
                        turn = eval(conn_socket.recv(128))
                        OnlineGame(turn, role, conn_socket, None)
                        portEnterExists = False
                        manager.clear_and_reset()
                        
                        #בשביל שיחזור למסך פתיחה
                        TwoPlayersButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                            (width // 2 - button_width // 2, 210), (button_width, button_height)), text='2 players', manager=manager)
    # 2 players from another computer
                        ServerButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                            (width // 2 - button_width // 2, 285), (button_width, button_height)), text='server', manager=manager)
                        ClientButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                            (width // 2 - button_width // 2, 360), (button_width, button_height)), text='client', manager=manager)
                        ComputerButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                            (width // 2 - button_width // 2, 435), (button_width, button_height)), text='play against the computer', manager=manager)
                        instuctions = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                            (width // 2 - button_width // 2, 510), (button_width, button_height)),text='Instruction',manager=manager)
                        title = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
                            (width // 2 - button_width // 0.75, 100), (button_width+410, button_height-17)), text='Four in a Row', manager=manager)



                    if event.ui_element == ComputerButton:
                                #מגריל של מי התור ראשון
                                turn = random.randint(PLAYER, AI)
                                computer(turn)
                                
                    if event.ui_element == instuctions:
                        print(Instructions())
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            manager.clear_and_reset()
                                #בשביל שיחזור למסך פתיחה
                            TwoPlayersButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                                (width // 2 - button_width // 2, 210), (button_width, button_height)), text='2 players', manager=manager)
    # 2 players from another computer
                            ServerButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                                (width // 2 - button_width // 2, 285), (button_width, button_height)), text='server', manager=manager)
                            ClientButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                                (width // 2 - button_width // 2, 360), (button_width, button_height)), text='client', manager=manager)
                            ComputerButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                                (width // 2 - button_width // 2, 435), (button_width, button_height)), text='play against the computer', manager=manager)
                            instuctions = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                                (width // 2 - button_width // 2, 510), (button_width, button_height)),text='Instruction',manager=manager)
                            title = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
                                (width // 2 - button_width // 0.75, 100), (button_width+410, button_height-17)), text='Four in a Row', manager=manager)


            manager.process_events(event)

        manager.update(time_delta)
    # מאיזה נקודה החלון מתחיל לצייר
        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()
network_msg = ""
main()
