import random
import math
import game_theory as gt

# optimize function: Annealing, use schedule_cost as the cost function
def annealing_optimize( result_from_coll_filter, movie_had_seen, result_from_cluster, movie_name_arr ):
    temperature = 5000.0
    cool = 0.96

    # generate the first pop and add to the pop list
    sol = []
    sol_tmp = []
    # create the first pop
    payoff_list_coll, name_list_coll = gt.gen_payoff_coll_filt(result_from_coll_filter)
    sol = zip(payoff_list_coll, name_list_coll)

    # mian loop
    while temperature > 0.1:
        payoff_list_tmp, name_list_tmp = gt.gen_payoff_cluster(result_from_cluster,
                                                        movie_name_arr, name_list_coll,
                                                        movie_had_seen)
        
        sol_tmp = zip(payoff_list_tmp, name_list_tmp)
        
        sol = annealing_choice( sol, sol_tmp, temperature)

        # decrease the temperature    
        temperature =temperature * cool
    
    sol.sort()
    sol.reverse()
    payoff_list_from_annealing, name_list_from_annealing = split_payoff_and_name( sol )
    
    return name_list_from_annealing, payoff_list_from_annealing

def annealing_choice( sol, sol_tmp, temperature ):
    result_pop = []
    result_payoff = 0
    # calculate the current cost and the new cost
    sol_cost = payoff_func( sol )
    
    sol_tmp_cost = payoff_func( sol_tmp )
    
    # important!!! if sol_cost > sol_tmp_cost, so we set (sol_cost-sol_tmp_cost).
    # if sol_cost < sol_tmp_cost, we set (sol_tmp_cost-sol_cost).
    annealing_func_val = pow( math.e, -(sol_cost-sol_tmp_cost) / temperature )
        
    # see if the cost of the pop2 is better than the pop1, be careful, the bigger, the better 
    if ( ( sol_tmp_cost > sol_cost ) or ( random.random() < annealing_func_val ) ):
        result_pop = sol_tmp
        result_payoff = sol_tmp_cost
    else:
        result_pop = sol
        result_payoff = sol_cost
   
    return result_pop

def payoff_func( sol ): 
    payoff_list, name_list = split_payoff_and_name( sol )
    sum_of_payoff = sum(payoff_list)

    return sum_of_payoff



def split_payoff_and_name( payoff_name ):
    payoff_list = []
    name_list = []

    for i in range( len(payoff_name) ):
        payoff_list.append(payoff_name[i][0])
        name_list.append(payoff_name[i][1])
   
    return payoff_list, name_list
