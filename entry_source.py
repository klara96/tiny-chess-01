import os, sys, json, urllib.request
sys.setrecursionlimit(3000)
ENV_URL = os.environ.get("MAKEFUN_ENV_URL") or None
def post(path, data):
    req = urllib.request.Request(ENV_URL + path, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))
PIECE_VALUES = {"P":100,"N":320,"B":330,"R":500,"Q":900,"K":0,
                "p":-100,"n":-320,"b":-330,"r":-500,"q":-900,"k":0}
PAWN_D = [10,-10]
KNIGHT_D = [21,-21,19,-19,12,-12,8,-8]
P8 = KNIGHT_D
DG = [11, -11, 9, -9]
OR = [10, -10, 1, -1]
def center(f):
    return min(f, 7-f)
def mk_piece_tables():
    pa = [0,0,7,15,25,39,65,0]
    pc = [0,0,0,13,19,13,5,0]
    tables = {k:[0]*64 for k in "PNBRQKE"}
    for r in range(8):
        for f in range(8):
            i = r*8+f
            c = center(f)+center(r)
            tables["P"][i] = (pa[r]+2) + (pc[r] if f in (3,4) else 0)
            tables["N"][i] = 7*c - 19
            tables["B"][i] = 5*c - 8
            tables["R"][i] = (18 if r==6 else 0) + (8 if r==0 and f in (3,4) else 0)
            tables["Q"][i] = 4*c - 7
            tables["K"][i] = [30,34,20,6,6,20,34,30][f] if r==0 else max(-52,-15*r)
            tables["E"][i] = 8*c - 23
    return tables
PST = mk_piece_tables()
BOARD = ["x"]*120
WHITE = True
EN_PASSANT = 0
CASTLING = "KQkq"
NODES = 0
BUDGET = 300000
MATE = 100000
STOP = False
EVAL = 0
KING_SQUARES = (0,0)
PID = {p:i for i,p in enumerate("PNBRQKpnbrqk",1)}
Z = []
rand = 123456789
for _ in range(2301):
    rand = (rand*6364136223846793005 + 1442695040888963407) & 0x3FFFFFFFFFFFFFF
    Z.append(rand)
HASH_KEY_WHITE = Z[2000]
TT = {}
def rel_sq(square, white):
    row = square//10 - 2
    col = square%10 - 1
    return row*8 + col if white else (7-row)*8 + col
def piece_value(square, piece):
    if piece in ".x":
        return 0
    row = square//10 - 2
    col = square%10 - 1
    val = PIECE_VALUES[piece]
    if piece.islower():
        return -val - PST[piece.upper()][(7-row)*8 + col]
    else:
        return val + PST[piece][(row)*8 + col]
def load(fen):
    global BOARD, WHITE, EN_PASSANT, CASTLING, EVAL, HASH_KEY
    global KING_SQUARES
    BOARD = ["x"]*120
    for r in range(8):
        BOARD[21+10*r:29+10*r] = ["."]*8
    parts = fen.split()
    piece_str, stm, cr, ep = parts[:4]
    for ri, row in enumerate(piece_str.split("/")):
        f = 0
        for ch in row:
            if ch.isdigit():
                f += int(ch)
            else:
                BOARD[21 + 10*(7-ri) + f] = ch
                f += 1
    WHITE = (stm == "w")
    CASTLING = cr
    EN_PASSANT = 0 if ep == "-" else 21 + 10*(int(ep[1])-1) + (ord(ep[0]) - 97)
    EVAL = 0
    HASH_KEY = 0
    if WHITE:
        HASH_KEY ^= HASH_KEY_WHITE
    for sq in range(21, 99):
        p = BOARD[sq]
        if p not in ".x":
            if p == "K": KING_SQUARES = (sq, KING_SQUARES[1])
            if p == "k": KING_SQUARES = (KING_SQUARES[0], sq)
            EVAL += piece_value(sq, p)
            HASH_KEY ^= Z[sq*16 + PID[p]]
    if not WHITE:
        HASH_KEY ^= HASH_KEY_WHITE
def is_attacked(square, white):
    b = BOARD
    u = "PNBRQK" if white else "pnbrqk"
    pd = -1 if white else 1
    if b[square+9*pd] == u[0] or b[square+11*pd] == u[0]:
        return True
    for d in KNIGHT_D:
        if b[square+d] == u[1]:
            return True
    for d in OR + DG:
        if b[square+d] == u[5]:
            return True
    rq = u[3] + u[4]
    bq = ("BQ" if white else "bq")
    for d in OR + DG:
        t = square + d
        while 21 <= t < 99:
            p = b[t]
            if p != ".":
                if p in rq and d in (10, -10, 1, -1):
                    return True
                if p in bq and d in (11, -11, 9, -9):
                    return True
                break
            t += d
    return False
def generate_moves():
    moves = []
    b = BOARD
    own = "PNBRQK" if WHITE else "pnbrqk"
    foe = WHITE
    for sq in range(21, 99):
        p = b[sq]
        if p not in own:
            continue
        if p in "Pp":
            fwd = 10 if WHITE else -10
            target = sq + fwd
            if b[target] == ".":
                if target > 90 or target < 29:
                    for promo in "qnbr":
                        moves.append((sq, target, promo))
                else:
                    moves.append((sq, target, ""))
                    if (21 <= sq <= 38 if WHITE else 81 <= sq <= 88) and b[target+fwd] == ".":
                        moves.append((sq, target+fwd, ""))
            for dc in ((9, 11) if WHITE else (-9, -11)):
                tc = sq + dc
                c = b[tc]
                if c != "." and c != "x" and c.islower() == foe:
                    if tc > 90 or tc < 29:
                        for promo in "qnbr":
                            moves.append((sq, tc, promo))
                    else:
                        moves.append((sq, tc, ""))
                if EN_PASSANT and tc == EN_PASSANT:
                    moves.append((sq, EN_PASSANT, "e"))
        elif p in "Nn" or p in "Kk":
            dirs = P8 if p in "Nn" else OR + DG
            for d in dirs:
                t = sq + d
                c = b[t]
                if c == "." or (c != "x" and c.islower() == foe):
                    moves.append((sq, t, ""))
        else:
            dirs = OR if p in "Rr" else DG if p in "Bb" else OR + DG
            for d in dirs:
                t = sq + d
                while 21 <= t < 99:
                    c = b[t]
                    if c == "x":
                        break
                    if c == ".":
                        moves.append((sq, t, ""))
                    elif c.islower() == foe:
                        moves.append((sq, t, ""))
                        break
                    else:
                        break
                    t += d
    if WHITE:
        if "K" in CASTLING and b[25] == "K" and b[28] == "R" and b[26] == b[27] == ".":
            if not is_attacked(25, False) and not is_attacked(26, False) and not is_attacked(27, False):
                moves.append((25, 27, "c"))
        if "Q" in CASTLING and b[25] == "K" and b[21] == "R" and b[22] == b[23] == b[24] == ".":
            if not is_attacked(25, False) and not is_attacked(24, False) and not is_attacked(23, False):
                moves.append((25, 23, "c"))
    else:
        if "k" in CASTLING and b[95] == "k" and b[98] == "r" and b[96] == b[97] == ".":
            if not is_attacked(95, True) and not is_attacked(96, True) and not is_attacked(97, True):
                moves.append((95, 97, "c"))
        if "q" in CASTLING and b[95] == "k" and b[91] == "r" and b[92] == b[93] == b[94] == ".":
            if not is_attacked(95, True) and not is_attacked(94, True) and not is_attacked(93, True):
                moves.append((95, 93, "c"))
    return moves
def make_move(move):
    global EN_PASSANT, CASTLING, WHITE, EVAL, HASH_KEY
    global KING_SQUARES
    fr, to, promo = move
    b = BOARD
    piece = b[fr]
    capture = b[to]
    prev_king = KING_SQUARES[0] if WHITE else KING_SQUARES[1]
    prev_ep = EN_PASSANT
    prev_cr = CASTLING
    HASH_KEY ^= Z[fr*16 + PID[piece]]
    delta = 0
    if capture not in ".x":
        delta -= piece_value(to, capture)
        HASH_KEY ^= Z[to*16 + PID[capture]]
    if promo == "c":
        if to == 27:
            b[26], b[28] = b[28], "."
            HASH_KEY ^= Z[26*16 + PID["R"]] ^ Z[28*16 + PID["R"]]
            delta += piece_value(26, "R") - piece_value(28, "R")
        elif to == 23:
            b[24], b[21] = b[21], "."
            HASH_KEY ^= Z[24*16 + PID["R"]] ^ Z[21*16 + PID["R"]]
            delta += piece_value(24, "R") - piece_value(21, "R")
        elif to == 97:
            b[96], b[98] = b[98], "."
            HASH_KEY ^= Z[96*16 + PID["r"]] ^ Z[98*16 + PID["r"]]
            delta += piece_value(96, "r") - piece_value(98, "r")
        else:
            b[94], b[91] = b[91], "."
            HASH_KEY ^= Z[94*16 + PID["r"]] ^ Z[91*16 + PID["r"]]
            delta += piece_value(94, "r") - piece_value(91, "r")
        b[to] = piece
    elif promo == "e":
        cap_sq = to - (10 if WHITE else -10)
        cap = b[cap_sq]
        b[cap_sq] = "."
        delta -= piece_value(cap_sq, cap)
        HASH_KEY ^= Z[cap_sq*16 + PID[cap]]
        b[to] = piece
    else:
        b[to] = piece
        if promo:
            new_piece = promo.upper() if WHITE else promo
            b[to] = new_piece
            delta += piece_value(to, new_piece) - piece_value(to, piece)
    b[fr] = "."
    if piece == "K": KING_SQUARES = (to, KING_SQUARES[1])
    elif piece == "k": KING_SQUARES = (KING_SQUARES[0], to)
    if piece in "Pp" and abs(to-fr) == 20:
        EN_PASSANT = (fr + to)//2
    else:
        EN_PASSANT = 0
    if piece == "K":
        CASTLING = CASTLING.replace("K", "").replace("Q", "")
    elif piece == "k":
        CASTLING = CASTLING.replace("k", "").replace("q", "")
    if fr == 21 or to == 21:
        CASTLING = CASTLING.replace("Q", "")
    if fr == 28 or to == 28:
        CASTLING = CASTLING.replace("K", "")
    if fr == 91 or to == 91:
        CASTLING = CASTLING.replace("q", "")
    if fr == 98 or to == 98:
        CASTLING = CASTLING.replace("k", "")
    EVAL += delta
    WHITE = not WHITE
    HASH_KEY ^= HASH_KEY_WHITE
    return (capture, prev_ep, prev_cr, delta, HASH_KEY, prev_king)
def undo_move(move, undo):
    global EN_PASSANT, CASTLING, WHITE, EVAL, HASH_KEY
    global KING_SQUARES
    capture, ep, cr, delta, hkey, prev_king = undo
    WHITE = not WHITE
    fr, to, promo = move
    b = BOARD
    if promo == "e":
        cap_sq = to - (10 if WHITE else -10)
        b[cap_sq] = "p" if WHITE else "P"
        b[to] = "."
        b[fr] = "P" if WHITE else "p"
    elif promo == "c":
        b[to] = "."
        b[fr] = "K" if WHITE else "k"
        if to == 27:
            b[28], b[26] = "R", "."
        elif to == 23:
            b[21], b[24] = "R", "."
        elif to == 97:
            b[98], b[96] = "r", "."
        else:
            b[91], b[94] = "r", "."
    else:
        b[fr] = ("P" if WHITE else "p") if promo else b[to]
        b[to] = capture
    EN_PASSANT = ep
    CASTLING = cr
    EVAL -= delta
    HASH_KEY = hkey
    KING_SQUARES = (prev_king, KING_SQUARES[1]) if WHITE else (KING_SQUARES[0], prev_king)
def order_move(move):
    return -PIECE_VALUES.get(BOARD[move[1]], 1)
def quiesce(alpha, beta, depth):
    global NODES
    NODES += 1
    if depth > 6:
        return EVAL if WHITE else -EVAL
    stand_pat = EVAL if WHITE else -EVAL
    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat
    ksq = KING_SQUARES[0] if WHITE else KING_SQUARES[1]
    if is_attacked(ksq, not WHITE):
        captures = generate_moves()
    else:
        captures = [m for m in generate_moves() if BOARD[m[1]] != "."]
    captures.sort(key=order_move)
    best = -MATE
    for mv in captures:
        undo = make_move(mv)
        if is_attacked(KING_SQUARES[0] if WHITE else KING_SQUARES[1], not WHITE):
            undo_move(mv, undo)
            continue
        score = -quiesce(-beta, -alpha, depth+1)
        undo_move(mv, undo)
        if score > best:
            best = score
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha if best != -MATE else stand_pat
def search(depth, alpha, beta, ply):
    global NODES, STOP
    NODES += 1
    if NODES >= BUDGET:
        STOP = True
    if STOP:
        return EVAL if WHITE else -EVAL
    if depth <= 0:
        return quiesce(alpha, beta, 0)
    hash_key = HASH_KEY
    entry = TT.get(hash_key)
    tt_move = None
    if entry:
        tt_depth, tt_flag, tt_score, tt_move = entry
        if tt_depth >= depth:
            if tt_flag == 0:
                return tt_score
            if tt_flag == 1 and tt_score > alpha:
                alpha = tt_score
            if tt_flag == 2 and tt_score < beta:
                beta = tt_score
            if alpha >= beta:
                return beta
            tt_move = tt_move
    moves = generate_moves()
    if tt_move:
        if tt_move in moves:
            moves.remove(tt_move)
            moves.insert(0, tt_move)
    moves.sort(key=order_move)
    best_move = None
    best_score = -2*MATE
    alpha_orig = alpha
    for mv in moves:
        if STOP:
            break
        undo = make_move(mv)
        if is_attacked(KING_SQUARES[0] if WHITE else KING_SQUARES[1], not WHITE):
            undo_move(mv, undo)
            continue
        score = -search(depth-1, -beta, -alpha, ply+1)
        undo_move(mv, undo)
        if score > best_score:
            best_score = score
            best_move = mv
            if score > alpha:
                alpha = score
                if alpha >= beta:
                    break
    if best_move is None:
        ksq = KING_SQUARES[0] if WHITE else KING_SQUARES[1]
        if is_attacked(ksq, not WHITE):
            return -MATE + ply
        return 0
    if not STOP and len(TT) < 150000:
        flag = 1 if alpha >= beta else (2 if alpha <= alpha_orig else 0)
        TT[hash_key] = (depth, flag, alpha, best_move)
    return alpha
def move_to_uci(move):
    fr, to, promo = move
    return "abcdefgh"[fr%10-1] + str(fr//10-1) + "abcdefgh"[to%10-1] + str(to//10-1) + (promo if promo in "qnr" else "")
def select_best_move(legal):
    best = legal[0]
    best_val = -1
    for mv in legal:
        t = 21 + 10*(int(mv[3])-1) + (ord(mv[2])-97)
        val = PIECE_VALUES.get(BOARD[t], 1)
        if val > best_val:
            best_val = val
            best = mv
    return best
def think(budget, legal_moves):
    global NODES, BUDGET, STOP, HASH_KEY
    BUDGET = budget
    NODES = 0
    STOP = False
    TT.clear()
    legal_set = set(legal_moves)
    moves = [m for m in generate_moves() if move_to_uci(m) in legal_set]
    if not moves:
        return select_best_move(legal_moves)
    best_move = None
    prev_best = moves[0]
    for depth in range(1, 20):
        alpha = -MATE
        moves.sort(key=lambda m: 0 if m == prev_best else order_move(m))
        for mv in moves:
            if STOP:
                break
            undo = make_move(mv)
            if is_attacked(KING_SQUARES[0] if WHITE else KING_SQUARES[1], not WHITE):
                undo_move(mv, undo)
                continue
            score = -search(depth-1, -MATE, -alpha, 1)
            undo_move(mv, undo)
            if score > alpha:
                alpha = score
                best_move = mv
                prev_best = mv
            if STOP:
                break
    return move_to_uci(best_move) if best_move else select_best_move(legal_moves)




def gen(): return generate_moves()
def mk(move): return make_move(move)
def um(move, undo): return undo_move(move, undo)
def isp(square, white): return is_attacked(square, white)
if __name__ == "__main__":
    while True:
        game = post("/game", {})
        while game["status"] == "your_move":
            load(game["fen"])
            move = think(350000, game["legal_moves"])
            game = post("/move", {"game": game["game"], "move": move})
        if game["status"] == "done":
            break
        print(game.get("wins"), game.get("draws"), game.get("losses"), file=sys.stderr)
