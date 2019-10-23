import chess
import chess.pgn
import time

#file where processed information goes
SAVE_FILE = "board_scores.txt"

pgn = open("lichess/lichess_db_standard_rated_2019-08.pgn")

run_time = int(input("Run for how long? (seconds)"))

positions = []  #positions are stored in an array of dictionaries
                #the FEN is the key, the key is a tuple: (white_won, reached)
                #must have occured more than a certain number of times

rare = []       #positions that have only occured a certain number of times or fewer

new = []        #to store new positions

games_done = 0  #if following on from previous reading then this number is found at top of file
SKIP = 0


def record(file, FEN, white, reached):
    file.write("\n")
    file.write(state)
    file.write("\n")
    file.write(str(won_white))
    file.write("\n")
    file.write(str(reached))

#open file and collect preprocessed information
start_preprocessing = time.time()

try:
    previous = open(SAVE_FILE)
    previous.close()
except:
    previous = open(SAVE_FILE, "w")
    previous.write("0") #file didn't exist so 0 games have already been processed
    previous.close()
    previos = open(SAVE_FILE)

previous = open(SAVE_FILE)

linenum = 0

rarity = 1 #if the position has been seen this many times or fewer it goes into the rare array when reading from preprocessed positions

FEN = ""
white = 0
reached = 0
for line in previous:
    if linenum == 0: #if top of file
        games_done = int(line)
        SKIP = games_done
        print("Skipping past " + str(SKIP) + " games...")
    elif linenum % 3 == 1:  #board position
        FEN = line[:-1]
    elif linenum % 3 == 2:  #white score
        white = float(line)
    else:
        reached = int(line)
        #all data about position is collected so add to positions array
        board = chess.Board(FEN)
        fm = board.fullmove_number
        hm = 2*(fm - 1) #calculate number of halfmoves since start of game
        if not board.turn:
            hm += 1

        if len(positions) <= hm:
            positions.append({})
            rare.append({})
            new.append({})
        if reached <= rarity:
            rare[hm][FEN] = (white, reached)
        else:
            positions[hm][FEN] = (white, reached)

    #increment at end of loop
    linenum += 1

#first reach point where we were last time program ran
completed = 0
while completed < games_done:
    game = chess.pgn.read_game(pgn) #iterate over games in the PGN file
    completed += 1

end_preprocessing = time.time()
print("Skipped past " + str(SKIP) + " games in " + str(end_preprocessing - start_preprocessing) + " seconds.")

start = time.time()
#print games out until an error occurs - due to reaching EOF
while time.time() - start < run_time:
    games_done += 1
    if games_done % 2500 == 0:
        print("Another 2500 games done in time: " + str(time.time() - start))
    game = chess.pgn.read_game(pgn) #record data for one game at a time
    if game == None: #will only occur if EOF is reached
        print("No more games")
        break
    
    board = chess.Board()
    num = 0
    white = 0
    if game.headers["Result"] == "1-0":
        white = 1
    elif game.headers["Result"] == "0-1":
        white = 0
    else:
        white = 0.5
        
    for move in game.mainline_moves():
        #for each move played this game:
        if len(positions) <= num:
            #if this is the longest game viewed so far the position is new so lengthen the new list
            if len(new) <= num:
                new.append({board.fen(): (white, 1)})
            else:
                new[num][board.fen()] = (white, 1)
        elif board.fen() in positions[num]:
            #if position seen before then update data
            old = positions[num][board.fen()]
            positions[num][board.fen()] = (old[0] + white, old[1] + 1)
        elif board.fen() in rare[num]:
            old = rare[num][board.fen()]
            rare[num][board.fen()] = (old[0] + white, old[1] + 1)
        else:
            #else add new position to array
            new[num][board.fen()] = (white, 1)
        board.push(move)
        num += 1
    

total = time.time() - start

print("Time taken: " + str(total) + " counting " + str(games_done) + " games.")

#save scores of each position
pos = 0
unique = 0
reaches = 0

save = open(SAVE_FILE, "w")
threshold = 0 #number of times a position should have been reached
num = 0
save.write(str(games_done))
for turn in range(len(new)):
    if turn < len(positions):
        for state in positions[turn]:
            reached = positions[turn][state][1]
            won_white = positions[turn][state][0]
            record(save, state, won_white, reached) #write to file
            pos += 1
            if reached == 1:
                unique += 1
            reaches += reached
        for state in rare[turn]:
            reached = rare[turn][state][1]
            won_white = rare[turn][state][0]
            record(save, state, won_white, reached) #write to file
            pos += 1
            if reached == 1:
                unique += 1
            reaches += reached
    for state in new[turn]:
        reached = new[turn][state][1]
        won_white = new[turn][state][0]
        record(save, state, won_white, reached) #write to file
        pos += 1
        if reached == 1:
            unique += 1
        reaches += reached

print("Save time: " + str(time.time() - start - total))
print("Total of " + str(pos) + " positions each reached an average of " + str(reaches/pos) + " with " + str(unique) + " positions only being seen once.")
save.close()
