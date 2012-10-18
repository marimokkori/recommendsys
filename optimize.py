# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="fengzhiming"
__date__ ="$2012-8-15 8:10:00$"

import time
import random
import math

people = [('Seymour','BOS'),
          ('Franny','DAL'),
          ('Zooey','CAK'),
          ('Walt','MIA'),
          ('Buddy','ORD'),
          ('Les','OMA')]
# Laguardia
destination='LGA'

flights = {}

for line in file('../data/data.txt'):
    ( origin, dest, depart, arrive, price ) = line.strip().split(',')
    flights.setdefault( (origin, dest), [] )
    
    # add details to the list of possible flights
    flights[(origin, dest)].append( (depart, arrive, int(price)) )

def get_minutes( t ):
    x = time.strptime(t, '%H:%M')
    return x[3]*60 + x[4]

def print_schedule( r ):
    for d in range( len(r)/2 ):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][int(r[d])]
        ret = flights[(destination, origin)][int(r[d+1])]
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % ( name, origin,
                                                       out[0], out[1], out[2],
                                                       ret[0], ret[1], ret[2] )
        
def schedule_cost( sol ):
    totalprice = 0
    latestarrival = 0
    earliestdep = 24*60
    
    for d in range( len(sol)/2 ):
        # Get the inbound and outbound flights
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d])]
        returnf = flights[(destination, origin)][int(sol[d+1])]
        
        # total price by summing the people in the solution
        totalprice += outbound[2]
        totalprice += returnf[2]
        
        # record the latest arrival time and the earliest depart time
        if latestarrival < get_minutes( outbound[1] ): latestarrival = get_minutes( outbound[1] )
        if earliestdep > get_minutes( returnf[0] ): earliestdep = get_minutes( returnf[0] )
        
    # caculate the time needed to wait to leave or arrive the airport in the same time
    totalwait = 0
    for d in range( len(sol)/2 ):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d])]
        returnf = flights[(destination, origin)][int(sol[d+1])]
        totalwait += latestarrival - get_minutes( outbound[1] )
        totalwait += get_minutes( returnf[0] ) - earliestdep
        
    # check if there is need to pay an extra for car rent because across the time line
    if latestarrival < earliestdep: totalprice += 50
    
    return totalprice + totalwait
        
# find the best solution by check by random 
def random_optimize( domain, costf ):
    best = 9999
    bestr = None
    
    for i in range( 0, 10000 ):
        # create an random solution
        r = [float(random.randint(domain[i][0], domain[i][1])) 
             for i in range(len(domain))]
        
        # get the cost of the random solution
        cost = costf( r )
        
        # compare the cost with the best so far
        if cost < best:
            best = cost
            bestr = r 
            
    return bestr

# optimize function: Hill Climb, use schedule_cost as cost function
def hill_climb( domain, costf ):
    # create a random solution
    sol = [ random.randint( domain[i][0], domain[i][1] ) for i in range( len(domain ) ) ]
    
    # main loop
    while 1:
        neighbors = []
        
        for j in range( len(domain) ):
            # change one element in the solution each time to produce a new solution
            if sol[j] > domain[j][0]:
                neighbors.append( sol[0:j] + [sol[j]-1] + sol[j+1:] )
            if sol[j] < domain[j][1]:
                neighbors.append( sol[0:j] + [sol[j]+1] + sol[j+1:] )
                
        # find the best solution among the neighbors
        current_random_cost = costf( sol )
        bestc = current_random_cost
        
        for j in range( len( neighbors ) ):
            cost = costf( neighbors[j] )
            if cost < bestc:
                bestc = cost
                sol = neighbors[j]
            
        if bestc == current_random_cost:
            break
            
    return sol

# optimize function: Annealing, use schedule_cost as the cost function
def annealing_optimize( domain, costf, temperature=10000.0, cool=0.95, step=1 ):
    # create a random soltion
    sol = [ float( random.randint( domain[i][0], domain[i][1] ) ) for i \
            in range( len( domain ) ) ]
            
    # mian loop
    while temperature > 0.1:
        # choose one of the indices
        i = random.randint( 0, len( domain ) - 1 )
        
        # choose an direction( positive or negtive ) and a step to change
        dir = random.randint( -step, step )
        
        # create a new list with one of the values changed
        sol_temp = sol[:]
        sol_temp[i] += dir
        if sol_temp[i] < domain[i][0]: sol_temp[i] = domain[i][0]
        if sol_temp[i] > domain[i][1]: sol_temp[i] = domain[i][1]
        
        # calculate the current cost and the new cost
        sol_cost = costf( sol )
        sol_temp_cost = costf( sol_temp )
        annealing_func_val = pow( math.e, -(sol_temp_cost-sol_cost) / temperature )
        
        # see if the cost of the sol_temp is better than the sol
        if ( ( sol_temp_cost < sol_cost ) or ( random.random() < annealing_func_val ) ):
            sol = sol_temp
        # decrease the temperature    
        temperature =temperature * cool
        
    return sol

# optimize function: Genetic, use the schedule_cost as the cost function
def genetic_optimize( domain, costf, pop_size=50, step=1, mut_prob=0.2, elite=0.2, max_iter=100 ):
    # function for mutation operation
    def mutate( vec ):
        # locate an element in domain
        i = random.randint( 0, len( domain) - 1 )
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            return vec[0:i] + [vec[i]-step] + vec[i+1:]
        elif vec[i] < domain[i][1]:
            return vec[0:i] + [vec[i]+step] + vec[i+1:]
        
    # function for cross-over operation
    def crossover( vec1, vec2 ):
        i = random.randint( 1, len(domain)-2 )
        return vec1[0:i] + vec2[i:]
    
    # build the initial population( the first random solution set )
    pop = []
    for i in range( pop_size ):
        sol = [ random.randint( domain[j][0], domain[j][1] ) for j in range( len(domain) ) ]
        pop.append( sol )
        
    # see how many winners from each generation
    top_elite = int( elite * pop_size )
    
    # main loop
    for i in range( max_iter ):
        pop_elem_costs = [ ( costf(j), j ) for j in pop ]
        pop_elem_costs.sort()
        ranked_pop = [ v for (s,v) in pop_elem_costs ]
        
        # start with the pure winners
        pop = ranked_pop[0:top_elite]
        
        # add mutated and crossovered elements to the original one to produce a new pop
        while len(pop) < pop_size:
            if random.random() < mut_prob:
                # mutate
                one_in_pop_elite = random.randint(0, top_elite )
                new_from_mutate = mutate( ranked_pop[one_in_pop_elite] )
                if new_from_mutate != None:
                    pop.append( new_from_mutate )
            else:
                # corss over
                one_in_pop_elite1 = random.randint(0, top_elite)
                while 1:
                    one_in_pop_elite2 = random.randint(0, top_elite)
                    if one_in_pop_elite1 != one_in_pop_elite2:
                        break
                new_from_cross = crossover( ranked_pop[one_in_pop_elite1], ranked_pop[one_in_pop_elite2] )
                if new_from_cross != None:
                    pop.append( new_from_cross )
                
        print pop_elem_costs[0][0], len(pop), pop
    
    return pop[0]
                        


#domain = [(0,9)] * ( len(people) * 2 )
#optimize_func = annealing_optimize
#result = optimize_func( domain, schedule_cost )       
#print 'Schedule cost:' + str(schedule_cost(result))
#print_schedule( result )
    