from abc import ABC, abstractmethod
from copy import deepcopy
import os

N = 8
WHITE, BLACK = 0, 1
COLORS = ['white', 'black']
SYMBOLS = {
    'pawn': ['P', 'p'], 'rook': ['R', 'r'], 'knight': ['N', 'n'],
    'bishop': ['B', 'b'], 'queen': ['Q', 'q'], 'king': ['K', 'k'],
    'camel': ['C', 'c'], 'griffin': ['G', 'g'], 'elephant': ['E', 'e'],
}
CHECKER_SYMS = {'man': ['O', 'X'], 'king': ['W', 'M']}
FILE_TO_COL = {chr(97 + i): i for i in range(N)}


class Pos:
    __slots__ = ('row', 'col')

    def __init__(self, row: int, col: int):
        self.row, self.col = row, col

    def __eq__(self, o):
        return self.row == o.row and self.col == o.col

    def __hash__(self):
        return (self.row << 3) | self.col

    def __repr__(self):
        return f"{chr(self.col + 97)}{N - self.row}"

    def valid(self):
        return 0 <= self.row < N and 0 <= self.col < N

    @staticmethod
    def from_str(s: str):
        if len(s) != 2 or s[0] not in FILE_TO_COL: return None
        try:
            return Pos(N - int(s[1]), FILE_TO_COL[s[0]])
        except:
            return None


class Move:
    __slots__ = ('piece', 'from_pos', 'to_pos', 'captured', 'captured_pos', 'en_passant', 'promo')

    def __init__(self, piece, frm, to, captured=None, captured_pos=None, ep=False, promo=None):
        self.piece, self.from_pos, self.to_pos = piece, frm, to
        self.captured, self.captured_pos = captured, captured_pos
        self.en_passant, self.promo = ep, promo


class Piece(ABC):
    __slots__ = ('color', 'pos', 'moved')

    def __init__(self, color: int, row: int, col: int):
        self.color, self.pos, self.moved = color, Pos(row, col), False

    @property
    @abstractmethod
    def type(self): pass

    @property
    def symbol(self): return SYMBOLS[self.type][self.color]

    def enemy(self, other): return other and other.color != self.color

    def move_to(self, pos): self.pos, self.moved = pos, True

    @abstractmethod
    def moves(self, board): pass


class Pawn(Piece):
    type = 'pawn'

    def moves(self, b):
        m = set()
        d = -1 if self.color == WHITE else 1
        start_row = 6 if self.color == WHITE else 1

        one = Pos(self.pos.row + d, self.pos.col)
        if one.valid() and not b.get(one):
            m.add(one)
            two = Pos(self.pos.row + 2 * d, self.pos.col)
            if self.pos.row == start_row and not b.get(two):
                m.add(two)

        for dc in (-1, 1):
            cap = Pos(self.pos.row + d, self.pos.col + dc)
            if cap.valid():
                t = b.get(cap)
                if t and self.enemy(t): m.add(cap)

        ep = b.ep_target
        if ep and ep.row == self.pos.row and abs(ep.col - self.pos.col) == 1:
            m.add(Pos(self.pos.row + d, ep.col))
        return m


class Rook(Piece):
    type = 'rook'

    def moves(self, b):
        m = set()
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            for s in range(1, N):
                p = Pos(self.pos.row + dr * s, self.pos.col + dc * s)
                if not p.valid(): break
                t = b.get(p)
                if not t:
                    m.add(p)
                elif self.enemy(t):
                    m.add(p);
                    break
                else:
                    break
        return m


class Knight(Piece):
    type = 'knight'

    def moves(self, b):
        m = set()
        for dr, dc in ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)):
            p = Pos(self.pos.row + dr, self.pos.col + dc)
            if p.valid():
                t = b.get(p)
                if not t or self.enemy(t): m.add(p)
        return m


class Bishop(Piece):
    type = 'bishop'

    def moves(self, b):
        m = set()
        for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            for s in range(1, N):
                p = Pos(self.pos.row + dr * s, self.pos.col + dc * s)
                if not p.valid(): break
                t = b.get(p)
                if not t:
                    m.add(p)
                elif self.enemy(t):
                    m.add(p);
                    break
                else:
                    break
        return m


class Queen(Piece):
    type = 'queen'

    def moves(self, b):
        m = set()
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for s in range(1, N):
                p = Pos(self.pos.row + dr * s, self.pos.col + dc * s)
                if not p.valid(): break
                t = b.get(p)
                if not t:
                    m.add(p)
                elif self.enemy(t):
                    m.add(p)
                    break
                else:
                    break
        return m


class King(Piece):
    type = 'king'

    def moves(self, b):
        m = set()
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0: continue
                p = Pos(self.pos.row + dr, self.pos.col + dc)
                if p.valid():
                    t = b.get(p)
                    if not t or self.enemy(t): m.add(p)
        return m


class Camel(Piece):
    type = 'camel'

    def moves(self, b):
        m = set()
        for dr, dc in ((-3, -1), (-3, 1), (-1, -3), (-1, 3), (1, -3), (1, 3), (3, -1), (3, 1)):
            p = Pos(self.pos.row + dr, self.pos.col + dc)
            if p.valid():
                t = b.get(p)
                if not t or self.enemy(t): m.add(p)
        return m


class Griffin(Piece):
    type = 'griffin'

    def moves(self, b):
        m = set()
        for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            for s in range(1, N):
                p = Pos(self.pos.row + dr * s, self.pos.col + dc * s)
                if not p.valid(): break
                t = b.get(p)
                if not t:
                    m.add(p)
                elif self.enemy(t):
                    m.add(p);
                    break
                else:
                    break
        for dr, dc in ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)):
            p = Pos(self.pos.row + dr, self.pos.col + dc)
            if p.valid():
                t = b.get(p)
                if not t or self.enemy(t): m.add(p)
        return m


class Elephant(Piece):
    type = 'elephant'

    def moves(self, b):
        m = set()
        for dr, dc in ((2, 2), (2, -2), (-2, 2), (-2, -2)):
            p = Pos(self.pos.row + dr, self.pos.col + dc)
            if p.valid():
                t = b.get(p)
                if not t or self.enemy(t): m.add(p)
        return m


class Checker(Piece):
    type = 'man'

    @property
    def symbol(self):
        return CHECKER_SYMS['man'][self.color]

    def moves(self, b):
        m = set()
        d = -1 if self.color == WHITE else 1
        for dc in (-1, 1):
            p = Pos(self.pos.row + d, self.pos.col + dc)
            if p.valid() and not b.get(p): m.add(p)
        for dc in (-1, 1):
            mid = Pos(self.pos.row + d, self.pos.col + dc)
            land = Pos(self.pos.row + 2 * d, self.pos.col + 2 * dc)
            if land.valid():
                t = b.get(mid)
                if t and self.enemy(t) and not b.get(land):
                    m.add(land)
        return m


class CheckerKing(Piece):
    type = 'king'

    @property
    def symbol(self):
        return CHECKER_SYMS['king'][self.color]

    def moves(self, b):
        m = set()
        for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            for s in range(1, N):
                p = Pos(self.pos.row + dr * s, self.pos.col + dc * s)
                if not p.valid(): break
                t = b.get(p)
                if not t:
                    m.add(p)
                elif self.enemy(t):
                    j = Pos(p.row + dr, p.col + dc)
                    if j.valid() and not b.get(j):
                        m.add(j)
                    break
                else:
                    break
        return m


class Board:
    def __init__(self, game='chess', variant='classic', custom=None):
        self.grid = [[None] * N for _ in range(N)]
        self.history = []
        self.turn = WHITE
        self.game, self.variant = game, variant
        self.custom = custom or {}
        self.ep_target = None
        self.king_pos = [None, None]
        self.over, self.winner = False, None
        self._setup()

    def get(self, p):
        return self.grid[p.row][p.col] if p.valid() else None

    def set(self, p, piece):
        if p.valid():
            self.grid[p.row][p.col] = piece
            if piece: piece.pos = p

    def _setup(self):
        for i in range(N):
            for j in range(N): self.grid[i][j] = None
        if self.game == 'checkers':
            self._setup_checkers()
        else:
            self._setup_chess()

    def _setup_chess(self):
        for c in range(N):
            self.grid[6][c] = Pawn(WHITE, 6, c)
            self.grid[1][c] = Pawn(BLACK, 1, c)
        back = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        if self.variant == 'classic':
            for c, cls in enumerate(back):
                self.grid[7][c] = cls(WHITE, 7, c)
                self.grid[0][c] = cls(BLACK, 0, c)
        else:
            for c, cls in enumerate(back):
                wc = self.custom.get((7, c), cls)
                bc = self.custom.get((0, c), cls)
                self.grid[7][c] = wc(WHITE, 7, c)
                self.grid[0][c] = bc(BLACK, 0, c)

        self.king_pos[WHITE] = Pos(7, 4)
        self.king_pos[BLACK] = Pos(0, 4)

    def _setup_checkers(self):
        for r in range(3):
            for c in range(N):
                if (r + c) % 2: self.grid[r][c] = Checker(BLACK, r, c)
        for r in range(5, N):
            for c in range(N):
                if (r + c) % 2: self.grid[r][c] = Checker(WHITE, r, c)

    def attacked(self, pos, color):
        for r in range(N):
            for c in range(N):
                p = self.grid[r][c]
                if p and p.color != color and pos in p.moves(self):
                    return True
        return False

    def would_be_check(self, move):
        if self.game != 'chess': return False
        old = self.get(move.to_pos)
        old_ep = self.ep_target
        old_king = self.king_pos[move.piece.color]

        self.set(move.to_pos, move.piece)
        self.set(move.from_pos, None)
        move.piece.pos = move.to_pos
        if move.en_passant:
            self.set(Pos(move.from_pos.row, move.to_pos.col), None)
        if isinstance(move.piece, King):
            self.king_pos[move.piece.color] = move.to_pos

        check = self.attacked(self.king_pos[move.piece.color], move.piece.color)

        self.set(move.from_pos, move.piece)
        self.set(move.to_pos, old)
        move.piece.pos = move.from_pos
        if isinstance(move.piece, King):
            self.king_pos[move.piece.color] = old_king
        if move.en_passant:
            self.set(Pos(move.from_pos.row, move.to_pos.col), move.captured)
        self.ep_target = old_ep
        return check

    def has_moves(self, color):
        for r in range(N):
            for c in range(N):
                p = self.grid[r][c]
                if p and p.color == color:
                    for to in p.moves(self):
                        m = Move(p, p.pos, to)
                        if not (self.game == 'chess' and self.would_be_check(m)):
                            return True
        return False

    def is_legal(self, move):
        if not move.to_pos.valid(): return False
        t = self.get(move.to_pos)
        if t and t.color == move.piece.color: return False
        if move.to_pos not in move.piece.moves(self): return False
        if self.game == 'chess' and self.would_be_check(move): return False
        return True

    def make_move(self, move):
        if not self.is_legal(move): return False

        self.history.append(deepcopy(move))

        if move.captured:
            if move.captured_pos:
                self.set(move.captured_pos, None)
            else:
                pass

        self.set(move.to_pos, move.piece)
        self.set(move.from_pos, None)
        move.piece.move_to(move.to_pos)

        if move.en_passant and move.captured:
            captured_pos = Pos(move.from_pos.row, move.to_pos.col)
            self.set(captured_pos, None)

        if self.game == 'checkers' and move.captured:
            dr = (move.to_pos.row - move.from_pos.row) // 2
            dc = (move.to_pos.col - move.from_pos.col) // 2
            mid_pos = Pos(move.from_pos.row + dr, move.from_pos.col + dc)
            self.set(mid_pos, None)

        if isinstance(move.piece, King):
            self.king_pos[move.piece.color] = move.to_pos

        if move.promo:
            self.set(move.to_pos, move.promo(move.piece.color, move.to_pos.row, move.to_pos.col))

        self.ep_target = None
        if isinstance(move.piece, Pawn) and abs(move.to_pos.row - move.from_pos.row) == 2:
            self.ep_target = Pos((move.from_pos.row + move.to_pos.row) // 2, move.to_pos.col)

        if self.game == 'checkers':
            if isinstance(move.piece, Checker):
                if (move.piece.color == WHITE and move.to_pos.row == 0) or \
                        (move.piece.color == BLACK and move.to_pos.row == N - 1):
                    self.set(move.to_pos, CheckerKing(move.piece.color, move.to_pos.row, move.to_pos.col))

        self.turn ^= 1

        if not self.has_moves(self.turn):
            self.over = True
            self.winner = self.turn ^ 1
        return True

    def undo(self):
        if not self.history: return False
        m = self.history.pop()

        self.set(m.from_pos, m.piece)
        self.set(m.to_pos, m.captured)
        m.piece.pos = m.from_pos

        if self.game == 'checkers' and m.captured:
            dr = (m.to_pos.row - m.from_pos.row) // 2
            dc = (m.to_pos.col - m.from_pos.col) // 2
            mid_pos = Pos(m.from_pos.row + dr, m.from_pos.col + dc)
            self.set(mid_pos, m.captured)

        if m.en_passant and m.captured:
            captured_pos = Pos(m.from_pos.row, m.to_pos.col)
            self.set(captured_pos, m.captured)

        if isinstance(m.piece, King):
            self.king_pos[m.piece.color] = m.from_pos

        self.turn ^= 1
        self.over = False
        return True

    def display(self, sel=None, moves=None):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n    a   b   c   d   e   f   g   h")
        print("  +---+---+---+---+---+---+---+---+")
        for r in range(N):
            print(f"{N - r} ", end="")
            for c in range(N):
                p = self.grid[r][c]
                pos = Pos(r, c)
                if sel and pos == sel:
                    s = f"[{p.symbol if p else ' '}]"
                elif moves and pos in moves:
                    s = f" {p.symbol if p else '+'} "
                else:
                    s = f" {p.symbol if p else '.'} "
                print(f"|{s}", end="")
            print("|")
            print("  +---+---+---+---+---+---+---+---+")
        print("    a   b   c   d   e   f   g   h")

        print(f"\nИгра: {'Шахматы' if self.game == 'chess' else 'Шашки'}")
        if self.game == 'chess':
            print(f"Режим: {'Классические' if self.variant == 'classic' else 'С новыми'}")
        print(f"Ход: {'Белые' if self.turn == WHITE else 'Черные'}")
        if self.game == 'chess' and self.attacked(self.king_pos[self.turn], self.turn):
            print("ШАХ!")
        print("\nКоманды: e2 — выбор, e4 — ход, undo — откат, exit — выход")


class Game:
    def __init__(self):
        self.board = None
        self.sel = None
        self.moves = set()

    def run(self):
        self._menu()
        while not self.board.over:
            self.board.display(self.sel, self.moves)
            if self.board.over:
                print(f"\nПОБЕДИТЕЛЬ: {'Белые' if self.board.winner == WHITE else 'Черные'}")
                break
            cmd = input("\n> ").strip().lower()
            if cmd == 'exit':
                break
            elif cmd == 'undo':
                if self.board.undo():
                    self.sel, self.moves = None, set();
                    print("Отменено")
                else:
                    print("Нечего отменять")
            elif len(cmd) == 2:
                p = Pos.from_str(cmd)
                if p:
                    self._handle(p)
                else:
                    print("Неверный формат")
            else:
                print("Неизвестно")

    def _menu(self):
        print("1. Классические шахматы\n2. Шахматы с новыми фигурами\n3. Шашки")
        while True:
            ch = input("\n> ")
            if ch == '1':
                self.board = Board('chess', 'classic');
                break
            elif ch == '2':
                self._custom();
                break
            elif ch == '3':
                self.board = Board('checkers');
                break

    def _custom(self):
        print("\nНовые фигуры (заменяют коней):")
        print("1. Верблюд (C) — ходит (3,1)")
        print("2. Грифон (G) — слон + конь")
        print("3. Слонобой (E) — на 2 клетки по диагонали")
        pieces = {'1': Camel, '2': Griffin, '3': Elephant}
        custom = {}
        for col in (1, 6):
            print(f"\nПозиция {Pos(0, col)} (чёрные) и {Pos(7, col)} (белые):")
            while True:
                ch = input("Выбор (1-3): ")
                if ch in pieces:
                    custom[(0, col)], custom[(7, col)] = pieces[ch], pieces[ch]
                    break
        self.board = Board('chess', 'custom', custom)

    def _handle(self, pos):
        if not self.sel:
            p = self.board.get(pos)
            if p and p.color == self.board.turn:
                self.sel, self.moves = pos, p.moves(self.board)
                print(f"Выбрана {p.symbol}, ходов: {len(self.moves)}")
            else:
                print("Нельзя выбрать эту фигуру")
        else:
            if self._move(self.sel, pos):
                self.sel, self.moves = None, set()
                print("Ход выполнен")
            else:
                input("Нажмите Enter...")

    def _move(self, frm, to):
        p = self.board.get(frm)
        if not p: return False

        is_capture = abs(to.row - frm.row) > 1

        cap = self.board.get(to)
        ep, promo = False, None
        captured_piece = None
        captured_pos = None

        if self.board.game == 'checkers' and is_capture:
            dr = (to.row - frm.row) // 2
            dc = (to.col - frm.col) // 2
            mid_pos = Pos(frm.row + dr, frm.col + dc)
            captured_piece = self.board.get(mid_pos)
            captured_pos = mid_pos
        else:
            captured_piece = cap

        if isinstance(p, Pawn) and not cap:
            ep_t = self.board.ep_target
            if ep_t and to == Pos(ep_t.row + (-1 if p.color == WHITE else 1), ep_t.col):
                ep, captured_piece = True, self.board.get(ep_t)

        if isinstance(p, Pawn):
            last = 0 if p.color == WHITE else N - 1
            if to.row == last:
                promo = self._promo()
                if not promo: return False

        move = Move(p, frm, to, captured_piece, captured_pos, ep, promo)
        return self.board.make_move(move)

    def _promo(self):
        print("\nПревращение пешки:")
        print("1. Ферзь   2. Ладья   3. Слон   4. Конь")
        if self.board.variant == 'custom':
            print("5. Верблюд   6. Грифон   7. Слонобой")
        pieces = {'1': Queen, '2': Rook, '3': Bishop, '4': Knight,
                  '5': Camel, '6': Griffin, '7': Elephant}
        while True:
            ch = input("> ")
            if ch in pieces: return pieces[ch]


if __name__ == "__main__":
    Game().run()
