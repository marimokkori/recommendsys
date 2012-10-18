import random
import game_theory as gt


def merge_payoff_and_name(payoff_list, name_from_result):
    result = []
    for i in range( len(payoff_list) ):
        result.append((payoff_list[i], name_from_result[i]))
        
    return result    

def split_payoff_and_name( payoff_name ):
    payoff_list = []
    name_list = []
    for payoff, name in payoff_name:
        payoff_list.append(payoff)
        name_list.append(name)
        
    return payoff_list, name_list

# mutation for genetic, pass in a pop whose element is a list with some tuples in it
# see the output format in merge_payoff_and_name().        
def mutate_for_genetic( pop, result_cluster, movie_name_arr, movie_had_seen ):
    payoff_list = []
    name_list = []
    new_name_list = []
    new_payoff_list = []
    payoff_list, name_list = split_payoff_and_name( pop )
    new_pop = []
    mutate_location = random.randint( 0, len(name_list)-1 )

    name = name_list[mutate_location]
    for j in range( len(result_cluster) ):
        # use a flag variable to mark if there is a match
        flag = 0
        for k in result_cluster[j]:
            if name == movie_name_arr[k]:
                flag = 1
        if flag == 1:
            for i in range(10000):
                rand_loc = random.randint(0, len(result_cluster[j])-1 )
                location = result_cluster[j][rand_loc]
                if movie_name_arr[location] not in movie_had_seen.keys():
                    new_name_list = name_list[0:mutate_location] + [movie_name_arr[location]] + \
                            name_list[mutate_location+1:]
                    break
                
    new_payoff_list = gt.gen_payoff_list(new_name_list)
    new_pop = zip(new_payoff_list, new_name_list)
    
    return new_pop

# cross over for genetic
def cross_over_for_genetic(pop, result_cluster, movie_name_arr, movie_had_seen):
    payoff_list = []
    name_list = []
    new_name_list = []
    new_payoff_list = []
    list_for_cross_use = []
    payoff_list, name_list = split_payoff_and_name( pop )
    new_pop = []
    cross_over_location = random.randint(1,len(name_list)-2)
    
    for i in range( len(name_list) ):
        name_coll = name_list[i]
        for j in range( len(result_cluster) ):
            # use a flag variable to mark if there is a match
            flag = 0
            for k in result_cluster[j]:
                if name_coll == movie_name_arr[k]:
                    flag = 1
            if flag == 1:
                for i in range(10000):
                    rand_loc = random.randint(0, len(result_cluster[j])-1 )
                    location = result_cluster[j][rand_loc]
                    if movie_name_arr[location] not in movie_had_seen.keys():
                        list_for_cross_use.append(movie_name_arr[location])
                        break
    
    new_name_list = name_list[0:cross_over_location] + list_for_cross_use[cross_over_location:]
    new_payoff_list = gt.gen_payoff_list(new_name_list)
    new_pop = zip( new_payoff_list, new_name_list )
    
    return new_pop

# define the payoff function to compare the strategy for good or bad
# the payoff function like the cost function use in optimize but do the reverse work,
# it returns the result which is the bigger,the better.In contract, the cost function
# is the smaller, the better.
def payoff_func( pop ): 
    payoff_list, name_list = split_payoff_and_name( pop )
    sum_of_payoff = sum(payoff_list)
    
    return sum_of_payoff
    
# genetic optimize    
def genetic_opt(result_from_coll_filter, movie_had_seen, result_from_cluster, movie_name_arr):
    # generate the first pop and add to the pop list
    pop = []
    # pop_list is a list whose element is some lists like [(a,b),(c,d)]
    pop_list = []
    elite_rate = 0.2
    iteration = 100
    mutate_prob = 0.2
    payoff_list, name_list = gt.gen_payoff_coll_filt(result_from_coll_filter)
    pop = zip(payoff_list, name_list)
    pop_list.append(pop)
    # define pop size
    pop_size = 50
    
    while len(pop_list) < pop_size:
        payoff_list, name_list = gt.gen_payoff_cluster(result_from_cluster,
                                                        movie_name_arr, name_list, movie_had_seen)
        pop = zip(payoff_list, name_list)
        pop_list.append(pop)
    # define pop top elite number
    top_elite_num = int(elite_rate * pop_size)
    
    for i in range( iteration ):
        pop_element_costs = [(payoff_func(j),j) for j in pop_list]
        pop_element_costs.sort(cmp=None, key=None, reverse=False)
        pop_element_costs.reverse()
        ranked_pops = [ v for (s,v) in pop_element_costs]
        pop_list = ranked_pops[0:top_elite_num]
        
        while len(pop_list) < pop_size:
            if random.random() < mutate_prob:
                one_in_pop_elite = random.randint(0, top_elite_num)
                new_from_mutate = mutate_for_genetic( ranked_pops[one_in_pop_elite],
                                                      result_from_cluster, movie_name_arr,
                                                      movie_had_seen)
                if new_from_mutate != None:
                    pop_list.append(new_from_mutate)
            else:
                one_in_pop_elite = random.randint(0, top_elite_num)
                new_from_cross_over = cross_over_for_genetic( ranked_pops[one_in_pop_elite],
                                                              result_from_cluster, movie_name_arr,
                                                              movie_had_seen )
                if new_from_cross_over != None:
                    pop_list.append(new_from_cross_over)
    
    name_list_from_genetic, payoff_list_from_genetic = split_payoff_and_name( pop_list[0] )
    return name_list_from_genetic, pop_element_costs[0][0]

# genetic optimize, second edition, aims at higher speed.    
def genetic_opt_plus(result_from_coll_filter, movie_had_seen, result_from_cluster, movie_name_arr):
    # generate the first pop and add to the pop list
    pop = []
    elite_rate = 0.6
    iteration = 800
    mutate_prob = 0.2
    # create the first pop
    payoff_list, name_list = gt.gen_payoff_coll_filt(result_from_coll_filter)
    pop = zip(payoff_list, name_list)

    # define pop top elite number
    top_elite_num = int(elite_rate * len(pop))
    
    for i in range( iteration ):
        payoff_list, name_list = split_payoff_and_name(pop)
        current_payoff = sum(payoff_list)
        # sort the pop from best to worse about payoff
        pop.sort(cmp=None, key=None, reverse=False)
        pop.reverse()
        
        # mutation       
        if random.random() < mutate_prob:
            one_in_pop_elite = random.randint(0, top_elite_num)
            new_from_mutate = mutate_for_genetic_plus( pop, one_in_pop_elite, 
                                                       result_from_cluster, movie_name_arr,
                                                       movie_had_seen)
            new_from_mutate_payoff = sum([s for (s,n) in new_from_mutate])
            if new_from_mutate != None and new_from_mutate_payoff > current_payoff:
                pop = new_from_mutate
                current_payoff = new_from_mutate_payoff
        # cross over
        else:
            one_in_pop_elite = random.randint(0, top_elite_num)
            new_from_cross_over = cross_over_for_genetic_plus( pop, one_in_pop_elite,
                                                          result_from_cluster, movie_name_arr,
                                                          movie_had_seen )
            new_from_cross_over_payoff = sum([s for (s,n) in new_from_cross_over])
            if new_from_cross_over != None and new_from_cross_over_payoff > current_payoff:
                pop = new_from_cross_over
                current_payoff = new_from_cross_over_payoff
    # fetch the result
    payoff_list_from_genetic_plus, name_list_from_genetic_plus = split_payoff_and_name( pop )
    
    return name_list_from_genetic_plus, payoff_list_from_genetic_plus

# mutation for genetic_plus
def mutate_for_genetic_plus( pop, start_loc, result_cluster, movie_name_arr, movie_had_seen ):
    payoff_list = []
    name_list = []
    new_name_list = []
    new_payoff_list = []
    payoff_list, name_list = split_payoff_and_name( pop )
    new_pop = []
    mutate_location = random.randint( start_loc, len(name_list)-1 )

    name = name_list[mutate_location]
    for j in range( len(result_cluster) ):
        # use a flag variable to mark if there is a match
        flag = 0
        for k in result_cluster[j]:
            if name == movie_name_arr[k]:
                flag = 1
        if flag == 1:
            for i in range(10000):
                rand_loc = random.randint(0, len(result_cluster[j])-1 )
                location = result_cluster[j][rand_loc]
                if movie_name_arr[location] not in movie_had_seen.keys():
                    new_name_list = name_list[0:mutate_location] + [movie_name_arr[location]] + \
                                name_list[mutate_location+1:]
                    break
    new_payoff_list = gt.gen_payoff_list(new_name_list)
    new_pop = zip(new_payoff_list, new_name_list)
    
    return new_pop

# cross over for genetic_plus
def cross_over_for_genetic_plus(pop, start_loc, result_cluster, movie_name_arr, movie_had_seen):
    payoff_list = []
    name_list = []
    new_name_list = []
    new_payoff_list = []
    list_for_cross_use = []
    payoff_list, name_list = split_payoff_and_name( pop )
    new_pop = []
    cross_over_location = random.randint(start_loc+1, len(name_list)-2)
    
    for i in range( len(name_list) ):
        name_coll = name_list[i]
        for j in range( len(result_cluster) ):
            # use a flag variable to mark if there is a match
            flag = 0
            for k in result_cluster[j]:
                if name_coll == movie_name_arr[k]:
                    flag = 1
            if flag == 1:
                for round in range(10000):
                    rand_loc = random.randint(0, len(result_cluster[j])-1 )
                    location = result_cluster[j][rand_loc]
                    if movie_name_arr[location] not in movie_had_seen.keys():
                        list_for_cross_use.append(movie_name_arr[location])
                        break
                
    new_name_list = name_list[0:cross_over_location] + list_for_cross_use[cross_over_location:]
    new_payoff_list = gt.gen_payoff_list(new_name_list)
    new_pop = zip( new_payoff_list, new_name_list )
    
    return new_pop