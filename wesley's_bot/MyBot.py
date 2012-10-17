#!/usr/bin/env python
from ants import *
import random

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
class MyBot:
    def __init__(self):
        # define class level variables, will be remembered between turns
        pass
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        #unexplored map
        self.unseen=[]
        self.maps={}
        #self.seen=[]
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row,col))
                self.maps[(row,col)]=[0.0, 0.0, 0.0, 0.0]
        #anthills
        self.hills = []
        self.possible_dirs = ["n","s","e","w"]
        self.largest_dist = ants.cols+ants.rows
        self.max_food = 100.0
        self.max_unseen = 100.0
        self.decay = .8
        
        self.max_enemy_hill = 100.0
        self.max_enemy_ant = 100.0
        self.max_home = 100.0
        self.enemy_hills=[]
        self.scouted_food=[]
        self.diffuse_runs = 10
        self.weightvector = [8,5,4,1] #[3,1,3,1]
    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        # track all moves, prevent collisions
        
        time = ants.time_remaining()
        #square diff structure: [food,unexplored,enemy_base,enemy_ant]
        def calcsquare(row,col):
            up=self.maps[ants.destination((row,col),'n')]
            down=self.maps[ants.destination((row,col),'s')]
            left=self.maps[ants.destination((row,col),'w')]
            right=self.maps[ants.destination((row,col),'e')]
            temp = [0.25*(up[i]+down[i]+left[i]+right[i])*self.decay for i in range(len(up))]
            self.maps[(row,col)]=temp
            if not ants.passable((row,col)):# or not ants.unoccupied((row,col)):
                self.maps[(row,col)]=[0.0, 0.0, 0.0, 0.0]
                return
            #elif (row,col) in ants.food() or (row,col) in self.scouted_food:
            #    if (row,col) not in self.scouted_food:
            #        self.scouted_food.append((row,col))
            #    elif ants.visible((row,col)) and (row,col) in self.scouted_food and (row,col) not in ants.food():
            #        self.scouted_food.remove((row,col))
            #    self.maps[(row,col)][0]=self.max_food
            #    return
            elif not ants.visible((row,col)):
                self.maps[(row,col)][1]=self.max_unseen
                return
            elif (row,col) in ants.enemy_hills() or (row,col) in self.enemy_hills:
                if (row,col) not in self.enemy_hills:
                    self.enemy_hills.append((row,col))
                self.maps[(row,col)][2]=self.max_enemy_hill
                return
            #elif (row,col) in ants.enemy_ants():
            #    self.maps[(row,col)][3]=self.max_enemy_ant
            #    return
        def calc_food_squares():
            for fud in ants.food():
                self.maps[fud][0]=self.max_food
        def calc_enemy_squares():
            for enemy in ants.enemy_ants():
                self.maps[enemy[0]][3]=self.max_enemy_ant
        def calcmap():
            #print "pop"
            for ant in ants.my_ants():
                self.maps[ant]=[0.0,0.0,0.0,0.0]
            calc_food_squares()
            calc_enemy_squares()
            for row in range(ants.rows):
                for col in range(ants.cols):
                    calcsquare(row, col)
        def calcdecay():
            for row in range(ants.rows):
                for col in range(ants.cols):
                    temp = self.maps[(row,col)]
                    for i in range(len(temp)):
                        if temp[i]>0.0:
                            temp[i]=temp[i]*self.decay
                    self.maps[(row,col)]=temp
        #self.maps={}
        #for row in range(ants.rows):
        #    for col in range(ants.cols):
        #        self.unseen.append((row,col))
        #        self.maps[(row,col)]=[0.0, 0.0, 0.0, 0.0]
        #self.seen=[]
        calcmap()
        for i in range(self.diffuse_runs):
            if ants.time_remaining()<(time*4/7):
                break
            else:
                calcmap()
        #calcdecay()
        orders = {}
        def do_move_direction(loc, direction):
            new_loc = ants.destination(loc, direction)
            if (ants.unoccupied(new_loc) and new_loc not in orders):
                ants.issue_order((loc, direction))
                orders[new_loc] = loc
                return True
            else:
                return False

        targets = {}
        def do_move_location(loc, dest):
            directions = ants.direction(loc, dest)
            for direction in directions:
                if do_move_direction(loc, direction):
                    targets[dest] = loc
                    return True
            return False

        def in_sight(start,end):
            for col in range(min(start[0],end[0]),max(start[0],end[0])):
                for row in range(min(start[1],end[1]),max(start[1],end[1])):
                    if not ants.unoccupied([col,row]):
                        return False
            return True
        def bestmove(ant):
            up=self.maps[ants.destination(ant,'n')]
            down=self.maps[ants.destination(ant,'s')]
            left=self.maps[ants.destination(ant,'w')]
            right=self.maps[ants.destination(ant,'e')]
            maxgrad = max(up,down,left,right)
            if up == maxgrad:
                do_move_direction(ant,'n')
            elif down == maxgrad:
                do_move_direction(ant,'s')
            elif left == maxgrad:
                do_move_direction(ant,'w')
            else:
                do_move_direction(ant,'e')
#        # default move
        ant_dist = []
#        # prevent stepping on own hill ######
        for hill_loc in ants.my_hills():
            orders[hill_loc] = None
#        #unblock own hills
        
        #print max(self.maps.values())
        for ant_loc in ants.my_ants():
            if ant_loc not in orders.values():
                up=self.maps[ants.destination(ant_loc,'n')]
                down=self.maps[ants.destination(ant_loc,'s')]
                left=self.maps[ants.destination(ant_loc,'w')]
                right=self.maps[ants.destination(ant_loc,'e')]
                up = sum([up[i]*self.weightvector[i] for i in range(len(up))])
                down = sum([down[i]*self.weightvector[i] for i in range(len(down))])
                left = sum([left[i]*self.weightvector[i] for i in range(len(left))])
                right = sum([right[i]*self.weightvector[i] for i in range(len(right))])
                maxgrad = max(up,down,left,right)
                #print maxgrad
                if maxgrad==0:
                    maxgrad=999
                if up == maxgrad:
                    do_move_direction(ant_loc,'n')
                elif down == maxgrad:
                    do_move_direction(ant_loc,'s')
                elif left == maxgrad:
                    do_move_direction(ant_loc,'w')
                elif right == maxgrad:
                    do_move_direction(ant_loc,'e')
        for ant_loc in ants.my_ants():
            if ant_loc not in orders.values():
                choices = ['s','e','w','n']
                random.shuffle(choices)
                for direction in choices:
                    if do_move_direction(ant_loc, direction):
                        break
        #for hill_loc in ants.my_hills():
        #    if hill_loc in ants.my_ants() and hill_loc not in orders.values():
        #        choices = ['s','e','w','n']
        #        random.shuffle(choices)
        #        for direction in choices:
        #            if do_move_direction(hill_loc, direction):
        #                break
##        # look for food ######
#        for food_loc in ants.food():
#            for ant_loc in ants.my_ants():
#                dist = ants.distance(ant_loc, food_loc)
#                ant_dist.append((dist, ant_loc, food_loc))
#        ant_dist.sort()
#        for dist, ant_loc, food_loc in ant_dist:
#            if food_loc not in targets and ant_loc not in targets.values():
#                do_move_location(ant_loc, food_loc)
#        # attack hills ######
#        for hill_loc, hill_owner in ants.enemy_hills():
#            if hill_loc not in self.hills:
#                self.hills.append(hill_loc)        
#        ant_dist = []
#        for hill_loc in self.hills:
#            for ant_loc in ants.my_ants():
#                if ant_loc not in orders.values():
#                    dist = ants.distance(ant_loc, hill_loc)
#                    ant_dist.append((dist, ant_loc))
#        ant_dist.sort()
#        for dist, ant_loc in ant_dist:
#            if in_sight(ant_loc, hill_loc):
#                do_move_location(ant_loc, hill_loc)

#        # unblock own hill ######


            
if __name__ == '__main__':
    # psyco will speed up python a little, but is not needed
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        Ants.run(MyBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
