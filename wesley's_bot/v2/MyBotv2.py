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
        #self.seen=[]
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row,col))
        #anthills
        self.hills = []
        self.possible_dirs = ["n","s","e","w"]
        self.largest_dist = ants.cols+ants.rows
    
    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        # track all moves, prevent collisions
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

                        
                
            
#        # look for food ######
        for food_loc in ants.food():
            for ant_loc in ants.my_ants():
                dist = ants.distance(ant_loc, food_loc)
                ant_dist.append((dist, ant_loc, food_loc))
        ant_dist.sort()
        for dist, ant_loc, food_loc in ant_dist:
            if food_loc not in targets and ant_loc not in targets.values():
                do_move_location(ant_loc, food_loc)
#        # attack hills ######
        for hill_loc, hill_owner in ants.enemy_hills():
            if hill_loc not in self.hills:
                self.hills.append(hill_loc)        
        ant_dist = []
        for hill_loc in self.hills:
            for ant_loc in ants.my_ants():
                if ant_loc not in orders.values():
                    dist = ants.distance(ant_loc, hill_loc)
                    ant_dist.append((dist, ant_loc))
        ant_dist.sort()
        for dist, ant_loc in ant_dist:
            if in_sight(ant_loc, hill_loc):
                do_move_location(ant_loc, hill_loc)

#        # unblock own hill ######
        for hill_loc in ants.my_hills():
            if hill_loc in ants.my_ants() and hill_loc not in orders.values():
                for direction in ('s','e','w','n'):
                    if do_move_direction(hill_loc, direction):
                        break
#        # diffuse outwards
        for ant_loc in ants.my_ants():
            if ant_loc not in orders.values():
                hill_dist_rat = ants.distance(ant_loc,ants.my_hills()[0])/self.largest_dist
                temprand = random.random()*.01
                if temprand>=hill_dist_rat:
                    choices = ants.direction(ant_loc,ants.my_hills()[0])
                    random.shuffle(choices);
                    for one_choice in choices:
                        if do_move_direction(ant_loc,one_choice)==True:
                            bit = 1
                            break
#        # explore unseen areas ######
        for loc in self.unseen[:]:
            if ants.visible(loc):
         #       self.seen.append(loc)
                self.unseen.remove(loc)
        #for loc in self.seen[:]:
        #    if not ants.visible(loc):
       #         self.unseen.append(loc)
        #        self.seen.remove(loc)
        for ant_loc in ants.my_ants():
            if ant_loc not in orders.values():
                unseen_dist = []
                for unseen_loc in self.unseen:
                    dist = ants.distance(ant_loc, unseen_loc)
                    unseen_dist.append((dist, unseen_loc))
                unseen_dist.sort()
                for dist, unseen_loc in unseen_dist:
                    if do_move_location(ant_loc, unseen_loc):
                        break
            
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
