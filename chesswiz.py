from __future__ import absolute_import, division, print_function, unicode_literals

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras

# Helper libraries
import numpy as np
import matplotlib.pyplot as plt
import random
import time

# Chess library (very important)
import chess

print(tf.__version__)

class Position:
    def __init__(self, pos, score=None, children=None):
        self.pos = pos
        if score == None:
            score = (0, 0, 0) #(white, draws, black)
        self.score = score
        if children == None:
            children = {}
        self.children = children

board = chess.Board()
print(board)

#start always points to root of game tree
start = Position(board.fen())
global start_time
start_time = time.time()

def moveScore(state, action, whiteToPlay):
    #exploration parameter
    c = 1.41
    if not action in state.children:
        return 0
    else:
        N = state.score[0] + state.score[1] + state.score[2]
        n = max(state.children[action].score[0] + state.children[action].score[1] + state.children[action].score[2], 1)
        w = 0.5 * state.children[action].score[1]
        if whiteToPlay:
            w += state.children[action].score[0]
        else:
            w += state.children[action].score[2]
        return (w/n) + (c * np.sqrt(np.log(N))/n)

def play(board):
    start_time_play = time.time()
    #set up starting position and locate root of monte carlo tree
    board.set_fen(chess.STARTING_FEN)
    moves_played = []
    current_state = start

    #loop runs once per move
    while not board.is_game_over():

        #set up to find move that optimises for moveScore function
        best_moves = []
        best_score = 0
        move_score = 0
        options = []

        #if the position is new then child nodes will not have been created so we must call board.legal_moves to figure out what the next positions could be
        if len(current_state.children) == 0:
            options = board.legal_moves
        else:
            #otherwise we already know all possible next moves so don't waste time calling board.legal_moves
            options = current_state.children.keys()

        #rate all of the moves here    
        for move in options:
            move_score = moveScore(current_state, move, board.turn)
            if move_score > best_score:
                best_moves = []
                best_score = move_score
            if move_score == best_score:
                best_moves.append(move)
            if not move in current_state.children:
                board.push(move)
                current_state.children[move] = Position(board.fen())
                board.pop()

        #randomly select one of the highest scoring moves
        move = best_moves[random.randrange(len(best_moves))]

        #play the move and update our position in the tree to reflect this
        board.push(move)
        moves_played.append(move)
        current_state = current_state.children[move]

    #print("Game Over")
    #print(board)

    #create a score tuple to return
    white = 0
    black = 0
    draws = 0

    print(board.result())
    if board.result() == "1-0":
        white = 1
    elif board.result() == "0-1":
        black = 1
    else:
        draws = 1

    times_play.append(time.time() - start_time_play)
    return (moves_played, (white, draws, black))

def record(start, game):

    #retrace steps through game tree and update scores along the way
    current_state = start

    #the game parameter is a tuple (moves, score)
    moves = game[0]
    score = game[1]

    for move in moves:
        old_score = current_state.score
        new_score = (old_score[0] + score[0], old_score[1] + score[1], old_score[2] + score[2])
        current_state.score = new_score
        current_state = current_state.children[move]

    #print(start.score)
    #print("---")
    return

times_play = []
times_record = []
for i in range(100):
    start_time = time.time()
    record(start, play(board))
    times_record.append(time.time() - start_time)
    print(str(sum(times_play)/len(times_play)) + " " + str(sum(times_record)/len(times_record)))

print(start.score)
for move in start.children.keys():
    print("*-----*")
    print(move)
    print(start.children[move].score)
