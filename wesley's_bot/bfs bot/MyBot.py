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
        self.decay = .1
        self.max_enemy_hill = 100.0
        self.max_enemy_ant = 100.0
        self.max_home = 100.0
        self.enemy_hills=[]
        self.scouted_food=[]
        self.diffuse_runs = 2
        self.weightvector = [6,5,2,1] #[3,1,3,1]
        self.food={}
        self.food_iters=5
        self.food_step = 5
        print "setup"
    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        # track all moves, prevent collisions
        def children(node):
            answer = []
            dirs = ['n','s','e','w']
            for dir in dirs:
                if ants.passable(ants.destination(node,dir)):
                    answer.append(ants.destination(node,dir))
            return answer
        def bfs(start,iters):
            #print "bfs"
            answer = []
            visited=[]
            top=[]
            down=[]
            top.append(start)
            for i in range(iters):
                while len(top)>0:
                    node = top.pop(0)
                    visited.append(node)
                    answer.append((node,i))
                    for child in children(node):
                        if child not in visited:
                            down.append(child)
                #print down
                top = down
                down=[]
            return answer
        def update_squares():
            for row in range(ants.rows):
                for col in range(ants.cols):
                    self.maps[(row,col)]=[0.0, 0.0, 0.0, 0.0]
            for fud in self.food.keys():
                squares = self.food[fud]
                for loc in squares:
                    self.maps[loc[0]][0]=max(self.maps[loc[0]][0],100-self.food_step*loc[1])
        def processed_food():
            #print "processed"
            for fud in ants.food():
                #print "fud1"
                if fud not in self.food.keys():
                    self.food[fud]=bfs(fud,self.food_iters) 
                    update_squares()
            for fud in self.food.keys():
                if fud not in ants.food() and ants.visible(fud):
                    self.food.pop(fud)
                    update_squares()
        #bfs((1,1),10)
        #square diff structure: [food,unexplored,enemy_base,enemy_ant]
        def calcsquare(row,col):
            up=self.maps[ants.destination((row,col),'n')]
            down=self.maps[ants.destination((row,col),'s')]
            left=self.maps[ants.destination((row,col),'w')]
            right=self.maps[ants.destination((row,col),'e')]
            temp = [0.25*(up[i]+down[i]+left[i]+right[i])-self.decay for i in range(len(up))]
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
            elif (row,col) in ants.enemy_ants():
                self.maps[(row,col)][3]=self.max_enemy_ant
                return
            
        def calcmap():
            #print "pop"
            for row in range(ants.rows):
                for col in range(ants.cols):
                    calcsquare(row, col)
        def calcdecay():
            for row in range(ants.rows):
                for col in range(ants.cols):
                    temp = self.maps[(row,col)]
                    for i in range(len(temp)):
                        if temp[i]>0:
                            temp[i]=temp[i]-self.decay
                    self.maps[(row,col)]=temp
        #self.maps={}
        #for row in range(ants.rows):
        #    for col in range(ants.cols):
        #        self.unseen.append((row,col))
        #        self.maps[(row,col)]=[0.0, 0.0, 0.0, 0.0]
        #self.seen=[]
        
        processed_food()
    
        
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

#        # default move
        ant_dist = []
#        # prevent stepping on own hill ######
        for hill_loc in ants.my_hills():
            orders[hill_loc] = None
#        #unblock own hills
        for hill_loc in ants.my_hills():
            if hill_loc in ants.my_ants() and hill_loc not in orders.values():
                choices = ['s','e','w','n']
                random.shuffle(choices)
                for direction in choices:
                    if do_move_direction(hill_loc, direction):
                        break
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
                if not maxgrad==0:
                    if up == maxgrad:
                        do_move_direction(ant_loc,'n')
                    elif down == maxgrad:
                        do_move_direction(ant_loc,'s')
                    elif left == maxgrad:
                        do_move_direction(ant_loc,'w')
                    else:
                        do_move_direction(ant_loc,'e')
        for ant_loc in ants.my_ants():
            if ant_loc not in orders.values():
                choices = ['s','e','w','n']
                random.shuffle(choices)
                for direction in choices:
                    if do_move_direction(ant_loc, direction):
                        break
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
