import numpy as np
import pandas as pd
import random
import sys

flags = '''
Flags:
    -h --help            help page
    -r --random-user     generate a random user board
    -c --cheat           print enemy board to speed up game
    -q --quiet           suppress intro message
    -a --automated       automated gameplay
'''
intro = '''
Welcome to my humble battleship game.
You will have an enemy cpu that you will play against. The cpu
will chose ship placement and shots fully at random without any
thought (for now).
You will be prompted to enter the coordinates of your ships if
you have not activated the -r flag which will generate a board
for you fully at random. The ships available are:

+------------+-----+------------+
| Name       | Key | Unit value |
+------------+-----+------------+
| Carrier    | C   | 5          |
+------------+-----+------------+
| Battleship | b   | 4          |
+------------+-----+------------+
| Cruiser    | c   | 3          |
+------------+-----+------------+
| Submarine  | s   | 3          |
+------------+-----+------------+
| Destroyer  | d   | 2          |
+------------+-----+------------+

The key values are the in-game values that are used for the
different ships.
The coordinates go by row and column value respectively. The
input for the coordinate should be two numbers separated by a
single comma i.e. 1,2 corresponds to the row index 1 and column
index 2. Note these are pythonic indexes so they are 0 based.
On the board 0 corresponds to empty spaces, M is missed hits,
X is a good hit and then there will be the respective ship labels.

If you wish to exit at any point you can input exit and the game
will exit.

Good luck...
'''

class Battleship:
    # this is a customized method for pretty printing pandas dataframes on the terminal
    # just needed it to be a bit more organized
    def print_board(self, df):
        print("+---+---+---+---+---+---+---+---+---+---+---+")
        print("|   | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |")
        print("|---+---+---+---+---+---+---+---+---+---+---|")
        for row in df.index:
            text = '| {} |'.format(row)
            for col in df.columns:
                text += ' {} |'.format(df.loc[row,col])
            print(text)
            # check if we are at the last line
            if row != self.n:
                print("|---+---+---+---+---+---+---+---+---+---+---|")
        print("+---+---+---+---+---+---+---+---+---+---+---+")

    def _check_for_existing_ship(self, coord, direc, size, df):
        '''
        Method to check if the ship to be placed will intersect with any
        other ship already on the board. If so it goes back to coordinate
        selection.
        '''
        # check which direction the ship will be facing
        # 0 for horizontally
        # 1 for vertically
        if direc == 0:
            # grab the slice of the data to later check its values
            slice = df.loc[coord[0], range(coord[1], coord[1]+size)]
        else:
            slice = df.loc[range(coord[0], coord[0]+size), coord[1]]
        # determine if any of the values in the slice are a string
        # this is safe to do as we are at the initialization step and only have integers or the existing
        # ships on the board
        vals = [isinstance(i, str) for i in slice]
        # return if we found any true values
        return any(vals)

    def _place_enemy_ship(self, size, label):
        conflict = True
        while conflict:
            # set first coord
            coord_1 = random.randint(0,self.n-size)
            # set second coord
            coord_2 = random.randint(0,self.n-size)
            # set direction
            direc = random.randint(0, 1)
            # check if there is a ship there already
            conflict = self._check_for_existing_ship([coord_1, coord_2], direc, size, self.enem_board)
            # if there is no ship in the way record the ship position
            if not conflict:
                if direc == 0:
                    self.enem_board.loc[coord_1, range(coord_2, coord_2+size)] = label
                else:
                    self.enem_board.loc[range(coord_1, coord_1+size), coord_2] = label

    def place_enemy_pieces(self):
        '''
        Method to randomly place the enemy ships on the board
        '''
        print("Placing enemy pieces")
        # place enemy carrier
        self._place_enemy_ship(5, 'C')
        # place enemy Battleship
        self._place_enemy_ship(4, 'b')
        # place enemy Cruiser
        self._place_enemy_ship(3, 'c')
        # place enemy Submarine
        self._place_enemy_ship(3, 's')
        # place enemy Destroyer
        self._place_enemy_ship(2, 'd')

    def place_user_piece(self, c1, c2, label):
        # try block to account for a possible user key misspress and have a safe
        # way for the program to go back without aborting
        try:
            if self.user_pieces.loc[label,'exists']:
                print("==================================================================")
                print("You have already set the coordinates for that ship")
                print("==================================================================")
                return False
        except KeyError:
            print("==================================================================")
            print("Sorry, I did not understand your ship selection {}".format(label))
            print("==================================================================")
            return False
        # set the direction of placement
        if c2 == 0:
            # check if the ship will fit given the chosen coordinates
            if c1[1] + self.user_pieces.loc[label, 'size'] >= self.n:
                print("==================================================================")
                print("Sorry, the starting coordinate you have chosen will not allow\nfor the ship to fit on the board.")
                print("==================================================================")
                return False
        else:
            # check if the ship will fit given the chosen coordinates
            if c1[0] + self.user_pieces.loc[label, 'size'] >= self.n:
                print("==================================================================")
                print("Sorry, the starting coordinate you have chosen will not allow\nfor the ship to fit on the board.")
                print("==================================================================")
                return False
        # get the size of the ship
        size = self.user_pieces.loc[label, 'size']
        # check for a ship in the way
        conflict = self._check_for_existing_ship(c1, c2, size, self.user_board)
        if conflict:
            print("==================================================================")
            print("Sorry, there is a ship in the way.")
            print("==================================================================")
            return False
        else:
            # save position of new ship on the board
            if c2 == 0:
                self.user_board.loc[c1[0], range(c1[1], c1[1]+size)] = label
            else:
                self.user_board.loc[range(c1[0], c1[0]+size), c1[1]] = label
        self.user_pieces.loc[label, 'exists'] = True
        # print the board that has been made so far for the user
        print("User board so far")
        self.print_board(self.user_board)
        # returns a successful execution
        return True

    def _stop_game(self):
        '''
        Central method to exit out of game.
        Turned out to be a godd idea as we do this quite often.
        '''
        print("==================================================================")
        print("Please play again\nExiting.....")
        print("==================================================================")
        sys.exit()

    def _is_game_over(self):
        '''
        Method to check if one of the players ships have all been sunk.
        '''
        user_lost = False
        enem_lost = False
        # check to see if the user lost
        for ship in self.pieces.index.values:
            tmp = ship in self.user_board.values
            if tmp:
                user_lost = False
                break
            else:
                user_lost = True
        # check if the enemy lost
        for ship in self.pieces.index.values:
            tmp = ship in self.enem_board.values
            if tmp:
                enem_lost = False
                break
            else:
                enem_lost = True
        return user_lost, enem_lost

    def user_turn(self):
        '''
        Game mechanic for the users turn.
        '''
        conflict = True
        while conflict:
            # get coordinates for strike
            coords = input("Input coordinates to strike. ")
            if coords == 'exit':
                self._stop_game()
            # format the string
            d = coords.split(',')
            # check for the right format
            if len(d) != 2:
                print("==================================================================")
                print("Must give two coordinates to anchor ship")
                print("==================================================================")
                success = False
                continue
            # convert strings to list of integers
            coords = [int(i.strip()) for i in d]
            # create new variables to store them
            c1, c2 = coords
            # check for an existing miss or hit
            if self.user_guess.loc[c1,c2] != 'X' and self.user_guess.loc[c1,c2] != 'M':
                # we already know that this guess is a new one
                # need to determine if its a hit or miss
                conflict = False
                if isinstance(self.enem_board.loc[c1,c2], str):
                    # give output as to what got hit
                    print("Hurrah!!\nWe have hit the enemy {}".format(self.pieces[self.enem_board.loc[c1,c2]]))
                    a = input("Press enter to continue....")
                    if a == 'exit':
                        self._stop_game()
                    self.enem_board.loc[c1,c2] = 'X'
                    self.user_guess.loc[c1,c2] = 'X'
                else:
                    print("We have missed the enemy!")
                    a = input("Press enter to continue....")
                    if a == 'exit':
                        self._stop_game()
                    self.enem_board.loc[c1,c2] = 'M'
                    self.user_guess.loc[c1,c2] = 'M'
            else:
                conflict = True
                print("==================================================================")
                print("We have already struck those coordinates.")
                print("==================================================================")
        return

    def auto_user_turn(self):
        '''
        Automated user turn.
        '''
        conflict = True
        while conflict:
            # get the coordinates as a random integer
            c1 = random.randint(0,self.n)
            c2 = random.randint(0,self.n)
            # check for existing guess
            if self.user_guess.loc[c1,c2] != 'X' and self.user_guess.loc[c1,c2] != 'M':
                conflict = False
                # determine if its a hit or miss
                if isinstance(self.enem_board.loc[c1,c2], str):
                    print("Hurrah!!\nWe have hit the enemy {}".format(self.pieces[self.enem_board.loc[c1,c2]]))
                    self.enem_board.loc[c1,c2] = 'X'
                    self.user_guess.loc[c1,c2] = 'X'
                else:
                    print("We have missed the enemy!")
                    self.enem_board.loc[c1,c2] = 'M'
                    self.user_guess.loc[c1,c2] = 'M'
            else:
                conflict = True
        return

    def enemy_turn(self):
        '''
        Automated enemy turn.
        '''
        conflict = True
        while conflict:
            # get the coordinates as a random integer
            c1 = random.randint(0,self.n)
            c2 = random.randint(0,self.n)
            # check for existing guess
            if self.enem_guess.loc[c1,c2] != 'X' and self.enem_guess.loc[c1,c2] != 'M':
                conflict = False
                # determine if its a hit or miss
                if isinstance(self.user_board.loc[c1,c2], str):
                    # give some output as to what got hit
                    print("Oh no!!\nOur {} has been hit".format(self.pieces[self.user_board.loc[c1,c2]]))
                    if not self.auto:
                        a = input("Press enter to continue....")
                        if a == 'exit':
                            self._stop_game()
                    self.user_board.loc[c1,c2] = 'X'
                    self.enem_guess.loc[c1,c2] = 'X'
                else:
                    print("The enemy has missed our ships!")
                    if not self.auto:
                        a = input("Press enter to continue....")
                        if a == 'exit':
                            self._stop_game()
                    self.user_board.loc[c1,c2] = 'M'
                    self.enem_guess.loc[c1,c2] = 'M'
            else:
                conflict = True
        return

    def _place_random_user_ship(self, size, label):
        '''
        Method to place the users ships at random thorugh the -r flag.
        '''
        conflict = True
        while conflict:
            # set first coord
            coord_1 = random.randint(0,self.n-size)
            # set second coord
            coord_2 = random.randint(0,self.n-size)
            # set direction
            direc = random.randint(0, 1)
            # check if there is a ship there already
            conflict = self._check_for_existing_ship([coord_1, coord_2], direc, size, self.user_board)
            if not conflict:
                if direc == 0:
                    self.user_board.loc[coord_1, range(coord_2, coord_2+size)] = label
                else:
                    self.user_board.loc[range(coord_1, coord_1+size), coord_2] = label

    def random_user_board(self):
        '''
        Place the users ships.
        '''
        print("Placing user pieces at random")
        # place enemy carrier
        self._place_random_user_ship(5, 'C')
        # place random_user Battleship
        self._place_random_user_ship(4, 'b')
        # place random_user Cruiser
        self._place_random_user_ship(3, 'c')
        # place random_user Submarine
        self._place_random_user_ship(3, 's')
        # place random_user Destroyer
        #print("Placing Destroyer")
        self._place_random_user_ship(2, 'd')
        print("---Generated user board---")
        self.print_board(self.user_board)

    def __init__(self, n=10):
        '''
        Initialization of program through creation of boards and other variables
        '''
        print("Generating {} x {} board".format(n,n))
        self.n = n-1
        # initialize user board
        self.user_board = pd.DataFrame(np.zeros((n,n),dtype=int))
        # initialize the users guess board
        # just created it so that the user can know where they have guessed without
        # looking at the enemy board
        self.user_guess = pd.DataFrame(np.zeros((n,n),dtype=int))
        # initialize enemy board
        self.enem_board = pd.DataFrame(np.zeros((n,n),dtype=int))
        # initialize enemy guess board
        self.enem_guess = pd.DataFrame(np.zeros((n,n),dtype=int))
        # this controls what has already been placed, sizes, and names of the ships
        self.user_pieces = pd.DataFrame(np.transpose([[False, False, False, False, False], [5,4,3,3,2],
                                         ['Carrier (C)', 'Battleship (b)', 'Cruiser(c)', 'Submarine (s)',
                                                                                            'Destroyer (d)']]),
                                        index=['C','b','c','s','d'], columns=['exists', 'size', 'full_name'])
        # explicitly define types
        self.user_pieces['exists'] = np.array([False, False, False, False, False]).astype(bool)
        self.user_pieces['size'] = self.user_pieces['size'].astype(int)
        # create legend for the pieces labels
        self.pieces = pd.Series(['Carrier', 'Battleship', 'Cruiser', 'Submarine', 'Destroyer'],
                                index=['C','b','c','s','d'])

# a whole bunch of flag parsing stuff
# for randomly chosen user ship placement
rand = False
# to be allowed to view the enemy board to make things go faster
cheat = False
# do not print introductory message
quiet = False
# print help page
help = False
# carry out game in an automated fashion
# the user will not have any input as to the shots taken
auto = False
if len(sys.argv) > 1:
    for i in sys.argv:
        if i[0] == '-' and not i[1] == '-':
            for j in i[1:]:
                if j == 'r':
                    rand = True
                elif j == 'q':
                    quiet = True
                elif j == 'h':
                    help = True
                elif j == 'c':
                    cheat = True
                elif j == 'a':
                    auto = True
                    rand = True
                else:
                    print("Did not understand given flag {}".format(j))
                    print("Available flags")
                    print(flags)
                    sys.exit()
        elif i[0] == '-' and i[1] == '-':
            if i[2:] == 'random-user':
                rand = True
            elif i[2:] == 'cheat':
                cheat = True
            elif i[2:] == 'quiet':
                quiet = True
            elif i[2:] == 'help':
                help = True
            elif i[2:] == 'automated':
                auto = True
                rand = True
            else:
                print("Did not understand given flag {}".format(j))
                print("Available flags")
                print(flags)
                sys.exit()
# print help page (flags really)
if help:
    print(flags)
    sys.exit()

if not quiet:
    print(intro)

# create class instance
battle = Battleship()
#battle.generate_board()
# place the enemy pieces
battle.place_enemy_pieces()
# set class attribute if auto was selected
if auto:
    battle.auto = True
else:
    battle.auto = False
# go thorugh ship placement if -r flag not given
if not rand:
    placed_all = False
    while not placed_all:
        # give input as to what remains to be placed
        print("Remaining pieces to place:")
        for ship in battle.user_pieces.values:
            if ship[0]:
                continue
            else:
                print(ship[2])
        print("Now we will begin by placing your pieces")
        success = False
        while not success:
            # get which ship to add
            ship = input("Which ship would you like to add? (C, b, c, s, or d) ")
            if ship == 'exit':
                battle._stop_game()
            # get the coordinates to place them on the board
            c1 = input("Input the coordinates to anchor ship on. ")
            if c1 == 'exit':
                battle._stop_game()
            # check the string formatiing and parse the string
            d = c1.split(',')
            if len(d) != 2:
                print("==================================================================")
                print("Must give two coordinates to anchor ship")
                print("==================================================================")
                success = False
                continue
            # create array of int
            c1 = [int(i.strip()) for i in d]
            # get the direction to place the ship
            c2 = input("Input direction which the ship will assume.\nHorizontal (0), or Vertical (1). ")
            if c2 == 'exit':
                battle._stop_game()
            # transform to int
            c2 = int(c2)
            # try to place the piece
            success = battle.place_user_piece(c1, c2, ship)
        # check that all the pieces have been placed on the board
        temp = True
        for exist in battle.user_pieces['exists'].values:
            temp *= exist
        placed_all = temp
else:
    # executes when -r flag is given
    battle.random_user_board()
# Start of game
print("==================================================================")
print("We will now begin the game!\nGood luck....")
print("==================================================================")
game_over = False
turns = 0
# loop until we get the game_over condition when one player has all of their ships sunk
while not game_over:
    # start with the users turn
    print("==================================================================")
    print("Users turn")
    print("==================================================================")
    if not auto:
        battle.user_turn()
    else:
        battle.auto_user_turn()
    # check win condition
    user_lost, enem_lost = battle._is_game_over()
    if user_lost or enem_lost:
        game_over = True
        continue 
    # enemy turn
    print("==================================================================")
    print("Enemy turn")
    print("==================================================================")
    battle.enemy_turn()
    # check win condition
    user_lost, enem_lost = battle._is_game_over()
    if user_lost or enem_lost:
        game_over = True
        continue
    # print out the board containing the users guesses
    print("----User guess board (X are hits, M are misses)")
    battle.print_board(battle.user_guess)
    # print out the users board
    print("----User game board (X are hits, M are misses)")
    battle.print_board(battle.user_board)
    # only gets shown when -c flag is present
    if cheat:
        # Cheat mode allows you to see the enemies ships
        print("---Enemy game board")
        battle.print_board(battle.enem_board)
    # increment turn counter
    turns += 1
# game over
print("==================================================================")
print(" Game over.\n {} won after {} turns.\n Please Play Again....".format("User" if enem_lost else "Enemy", turns))
print("==================================================================")

