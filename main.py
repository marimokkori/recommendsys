import run_collaborative_filtering as coll
import run_cluster as clus
import game_theory as gt
import genetic_optimize as gene
import annealing_optimize as ann
import statistics as stat
import MySQLdb as db
import random
import time
import math
import db_config as dbconf



# initialize the experiment for first use
def initialize():
    coll.initialize_collaborative_filter()
    clus.initialize_cluster()

# analysis the collaborative filter method, see if game theory method is effective
def origin_coll_filter_analysis(user_id):
    result_from_coll_filter, movie_had_seen = coll.run_collaborative_filter(user_id)
    payoff_list, name_from_coll_result = gt.gen_payoff_coll_filt(result_from_coll_filter)

    print 'collaborative filter analysis finished.'
    return name_from_coll_result, payoff_list

def genetic_plus_opt_analysis(user_id):
    result_from_coll_filter, movie_had_seen = coll.run_collaborative_filter(user_id)
    result_from_cluster, movie_name_arr = clus.run_cluster()
    
    time_start = record_runtime()
    
    name_list_from_genetic, payoff_list_from_genetic = gene.genetic_opt_plus(result_from_coll_filter,
                                                                             movie_had_seen, 
                                                                             result_from_cluster,
                                                                              movie_name_arr)
    
    time_end = record_runtime()
    time_pass = time_end - time_start
    
    print 'genetic_plus optimize analysis finished.'
    return name_list_from_genetic, payoff_list_from_genetic, time_pass

# analysis the annealing optimize method, see if game theory method is effective
def annealing_opt_analysis(user_id):
    result_from_coll_filter, movie_had_seen = coll.run_collaborative_filter(user_id)
    result_from_cluster, movie_name_arr = clus.run_cluster()
    
    time_start = record_runtime()
    
    name_list_from_annealing, payoff_list_from_annealing = ann.annealing_optimize(
                                                    result_from_coll_filter, movie_had_seen, 
                                                    result_from_cluster, movie_name_arr)
    
    time_end = record_runtime()
    time_pass = time_end - time_start
    
    print 'annealing optimize analysis finished.'
    return name_list_from_annealing, payoff_list_from_annealing, time_pass

def format_result_output(result_list_name, result_list_payoff, time_pass=0):
    print '\n'
    print(result_list_name)
    print '\n'
    print(result_list_payoff)
    print '\n'
    print(time_pass)
    print '\n'

def gen_rand_usr( num_of_usr ):
    # fetch the database to get the numbers of the users
    con = dbconf.connect_db()
    cur = con.cursor()
    cur.execute( """SELECT COUNT( DISTINCT( user_id ) )
                    FROM test1 """)
    usr_sum = cur.fetchone()[0]
    
    rand_usr_list = []
    for i in range( num_of_usr ):
        usr = random.randint( 1, usr_sum )
        rand_usr_list.append(str(usr))
    
    return rand_usr_list

def record_runtime():
    time_spot = time.time()
    
    return time_spot

# built the dictionary from the analysis result
def create_analysis_dict():
    # initial a dictionary to cache the analysis result to draw picture
    method_list = ('game theory', 'genetic optimize', 'annealing optimize', 'collaborative filter')
    attribute_list = ('recommend numbers', 'run time', 'average payoff', 'standard deviation', 
                      'recommend list')
    
    analysis_result = {}
    for method in method_list:
        analysis_result.setdefault(method, {})
        for attribute in attribute_list:
            analysis_result[method].setdefault(attribute, [])
    
    print analysis_result, '\n'
    return analysis_result

# insert the analysis result into a dictionary
def built_analysis_dict( analysis_result_dict, method, name_list, payoff_list, rtime=0 ):
    reco_num = len(name_list)
    run_time = rtime
    average_rating = sum(payoff_list)/reco_num
    # calculate the standard deviation
    std_dev = calculate_std_dev(payoff_list)
    recommend_list = zip( payoff_list, name_list )
    
    for attribute in analysis_result_dict[method].keys():
        if attribute == 'recommend numbers':
            analysis_result_dict[method][attribute].append(reco_num)
        elif attribute == 'run time':
            analysis_result_dict[method][attribute].append(run_time)
        elif attribute == 'average payoff':
            analysis_result_dict[method][attribute].append(average_rating)
        elif attribute == 'standard deviation':
            analysis_result_dict[method][attribute].append(std_dev)
        elif attribute == 'recommend list':
            analysis_result_dict[method][attribute].append(recommend_list)
    
    print analysis_result_dict, '\n'        
    return analysis_result_dict
            
# calculate the standard deviation    
def calculate_std_dev(val_list):
    val_num = len(val_list)
    square_sum = 0.0
    avg = float(sum(val_list))/float(val_num)
    for val in val_list:
        square_sum += pow((val - avg), 2)
        
    result = math.sqrt(square_sum / float(val_num))
    
    return result

# fetch the data from the dictionary for later use
def fetch_analysis_dict_for_plot( analysis_dict, attr ):
    x_vec = {}
    y_vec = {}
    x_label = 'random member'
    y_label = ''
    for method, attribute_dict in analysis_dict.items():
        x_vec.setdefault(method, [])
        y_vec.setdefault(method, [])
        for attribute, attribute_list in attribute_dict.items():
            if attr == attribute:
                y_label = attribute
                for i in range( len(attribute_list) ):
                    x_vec[method].append(i)
                    y_vec[method].append(attribute_list[i])
    
    print x_vec, y_vec                
    return x_vec, y_vec, x_label, y_label

def fetch_rec_pre_dict_for_plot( analysis_dict, method_list, usr_list, attr ):
    analysis_dict_rec_pre = {}
    
    for method in method_list:
        print 'method:', method
        analysis_dict_rec_pre.setdefault(method, {})
        recall_dict, precision_dict = stat.calc_recall_prec(usr_list, 
                                                       analysis_dict[method]['recommend list'])
        analysis_dict_rec_pre[method].setdefault('recall', [])
        analysis_dict_rec_pre[method].setdefault('precision', [])
        for user_id, val in recall_dict.items():
            analysis_dict_rec_pre[method]['recall'].append(val)
        for user_id, val in precision_dict.items():
            analysis_dict_rec_pre[method]['precision'].append(val)
    
    print 'analysis_dict_rec_pre:', analysis_dict_rec_pre, '\n'
    x_vec, y_vec, x_label, y_label = fetch_analysis_dict_for_plot( analysis_dict_rec_pre,
                                                                   attr )
    y_label += '*100'
    return x_vec, y_vec, x_label, y_label

def run_all_analysis():
    # assign a user id to run
    num_of_usr = 2
    usr_list = gen_rand_usr(num_of_usr)
    print usr_list
    analysis_result = {}
    analysis_result = create_analysis_dict()
    method_list = ('genetic optimize', 'annealing optimize', 'collaborative filter')
    attribute_list = ('recommend numbers', 'run time', 'average payoff', 'standard deviation',
                      'recommend list')
    extra_attribute_list = ('recall', 'precision')
    
    for i in range(len(usr_list)):
        user_id = usr_list[i]

        name_from_coll_result, payoff_from_coll = origin_coll_filter_analysis(user_id)
        analysis_result = built_analysis_dict( analysis_result, method_list[2],
                                                name_from_coll_result, payoff_from_coll
                                                )
        
        name_from_genetic, payoff_from_genetic, time_gene = genetic_plus_opt_analysis(user_id)
        analysis_result = built_analysis_dict( analysis_result, method_list[0], 
                                               name_from_genetic, payoff_from_genetic, 
                                               time_gene )
        name_from_annealing, payoff_from_annealing, time_anna = annealing_opt_analysis(user_id)
        analysis_result = built_analysis_dict( analysis_result, method_list[1], 
                                               name_from_annealing, payoff_from_annealing, 
                                               time_anna )
    
        format_result_output( name_from_coll_result, payoff_from_coll )
        format_result_output( name_from_genetic, payoff_from_genetic, time_gene )
        format_result_output( name_from_annealing, payoff_from_annealing, time_anna )
    
    for j in range(len(attribute_list)-1):
        x_vec, y_vec, x_label, y_label = fetch_analysis_dict_for_plot( analysis_result,
                                                                        attribute_list[j])     
        stat.draw_pic(x_vec, y_vec, x_label, y_label, attribute_list[j])
    
    for k in range( len(extra_attribute_list) ):    
        x_vec, y_vec, x_label, y_label = fetch_rec_pre_dict_for_plot( analysis_result,
                                                                   method_list, usr_list,
                                                                   extra_attribute_list[k] )
        stat.draw_pic(x_vec, y_vec, x_label, y_label, extra_attribute_list[k])

run_all_analysis()