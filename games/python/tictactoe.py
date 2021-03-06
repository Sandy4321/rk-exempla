import re
import itertools as it
import random

import cStringIO

import Tkinter as tk

BLANK = 0x0
NOUGHT = 0x1
CROSS = 0x2

VALID = set((NOUGHT, CROSS))

SYMBOLS = {
    BLANK: '_',
    NOUGHT: 'O',
    CROSS: 'X'
}

def _pair_to_index(x_pos, y_pos):
    return x_pos + 3 * y_pos

def _index_to_pair(pos):
    pair = divmod(pos, 3)
    return pair[1], pair[0]

def sure_win(three):
    return len(set(three)) == 1

def close_win(three):
    blanks = three.count(BLANK)
    if blanks > 1:
        return False
    elif blank == 1 and three.count(NOUGHT) == 2:
        return True
    elif blank == 1 and three.count(CROSS) == 2:
        return True
    else:
        return False



class Board(object):
    def __init__(self):
        self._board = [BLANK, ] * 9

    def __getitem__(self, pos):
        try:
            x_pos, y_pos = pos
        except ValueError:
            return self._board[pos]
        else:
            return self._board[_pair_to_index(x_pos, y_pos)]

    def __setitem__(self, pos, val):
        if val in VALID:
            try:
                x_pos, y_pos = pos
            except ValueError: pass
            else:
                pos = _pair_to_index(x_pos, y_pos)
            if self._board[pos] in VALID:
                raise ValueError('Already set position')
            else:
                self._board[pos] = val
        else:
            raise ValueError('Not a valid move')

    def col(self, index):
        return self._board[index::3]

    def row(self, index):
        return self._board[3*index:3*index+3]

    def cols(self):
        return it.imap(self.col, range(3))

    def rows(self):
        return it.imap(self.row, range(3))

    def diag(self):
        return [self._board[0], self._board[4], self._board[8]]

    def antidiag(self):
        return [self._board[6], self._board[4], self._board[2]]

    def threes(self):
        return it.chain(self.rows(), self.cols(),
                        (self.diag(), self.antidiag()))

    def winner(self):
        for three in self.threes():
            if sure_win(three):
                return three.pop()
        else:
            return None

    def draw(self):
        '''Nobody can win'''
        # try to discover draws asap
        return BLANK not in self._board

    def possible_moves(self):
        for i, v in enumerate(self._board):
            if v == BLANK:
                yield _index_to_pair(i)

    def __str__(self):
        sio = cStringIO.StringIO()
        for row in self.rows():
            print >>sio, SYMBOLS[row[0]], SYMBOLS[row[1]], SYMBOLS[row[2]]
        sio.seek(0)
        return sio.read()


class Player(object):
    def __init__(self, whoami, strategy):
        assert whoami in VALID
        self.board = Board()
        self.strategy = strategy
        self.whoami = whoami

    def notify_move(self, move):
        pos, value = move
        self.board[pos] = value

    def next_move(self):
        return self.strategy.next_move(self.whoami, self.board)


class TerminalAskTheHuman(object):
    rex = re.compile('(\d+),\s*(\d+)')

    def tentative_move(self, tentative, whoami, board):
        line = raw_input('P%s: %s> ' % (whoami, tentative)).strip()
        match = self.rex.match(line)
        if match:
            return tuple(int(g) for g in match.groups())
        else:
            try:
                return _index_to_pair(int(line))
            except ValueError:
                pass

    def next_move(self, whoami, board):
        for tentative in it.count(1):
            move = self.tentative_move(tentative, whoami, board)
            if board[move] == BLANK:
                return move
            else:
                print "[ERROR] Invalid move!"

class RandomPlayer(object):
    def next_move(self, _whoami, board):
        moves = list(board.possible_moves())
        move = random.choice(moves)
        return move
    
class Game(object):
    def __init__(self, ui, *args):
        self.board = Board()
        self.ui = ui
        self.players = args

    def next_move(self, turn):
        player = self.players[turn % 2]
        move = player.next_move()
        return (move, player.whoami)

    def perform_move(self, move):
        self.board.__setitem__(*move)

    def notify_move(self, move):
        for p in self.players:
            p.notify_move(move)

    def play(self):
        for turn in it.count(1):
            ui.show_board(self.board)
            if self.board.draw():
                ui.draw()
                break
            possible_winner = self.board.winner()
            if possible_winner:
                ui.present_winner(possible_winner)
                break
            move = self.next_move(turn)
            try:
                self.perform_move(move)
            except ValueError:
                ui.error('Invalid move!')
                break
            else:
                self.notify_move(move)

class TextualInterface(object):
    def present_winner(self, winner):
        print 'Player %s won!' % winner

    def error(self, message):
        print message

    def draw(self):
        print 'DRAW!'

    def show_board(self, board):
        print board


class TkInterface(tk.Frame):
    HEIGHT = 300
    WIDTH = 300
    def __init__(self, root):
        tk.Frame.__init__(self, root, 
                          height=TkInterface.HEIGHT, 
                          width=TkInterface.WIDTH)
        self.canvas = tk.Canvas(self, 
                                height=TkInterface.HEIGHT, 
                                width=TkInterface.WIDTH)
        self.canvas.pack()
        self.draw_frame()
        self.bind_events()
        self.pack()

    def draw_frame(self):
        height_first_third = TkInterface.HEIGHT / 3
        height_second_third = 2 * height_first_third
        width_first_third = TkInterface.WIDTH / 3
        width_second_third = 2 * width_first_third
        self.canvas.create_line(0, width_first_third, 
                                TkInterface.HEIGHT, width_first_third,
                                width=3)
        self.canvas.create_line(0, width_second_third, 
                                TkInterface.HEIGHT, width_second_third,
                                width=3)
        self.canvas.create_line(height_first_third, 0,
                                height_first_third, TkInterface.WIDTH,
                                width=3)
        self.canvas.create_line(height_second_third, 0,
                                height_second_third, TkInterface.WIDTH,
                                width=3)

    def bind_events(self):
        self.canvas.bind("<Button-1>", self._user_click)
        
    def _user_click(self, event):
        print event.x/100, event.y/100

if __name__ == '__main__':
    root = tk.Tk()
    tkframe = TkInterface(root)
    tkframe.mainloop()
    exit(0)
    ui = TextualInterface()
    game = Game(ui,
                Player(NOUGHT, RandomPlayer()),
                Player(CROSS, RandomPlayer()))
    game.play()
    game = Game(ui,
                Player(NOUGHT, TerminalAskTheHuman()),
                Player(CROSS, RandomPlayer()))
    game.play()

