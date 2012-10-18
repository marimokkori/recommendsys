from operator import add, neg
import MySQLdb as db
import random
import db_config as dbconf


# from a strategy name list, find the list of the winning value of the strategy
def gen_payoff_list( name_list ):
    winning_list = []
    # from the name list generate the payoff list use database
    con = dbconf.connect_db()
    
    # find the number of all users
    try:
        cursor = con.cursor()
        cursor.execute("""SELECT COUNT( DISTINCT user_id )
                            FROM base1""")
        con.commit()
    except db.Error:
        print 'ERROR: start to roll back'
        print db.Error
        try:
            con.rollback()
        except:
            pass    

    row = cursor.fetchone()
    all_usr_num = row[0]
    cursor.close()
    
    
    # find the expected rating and something evaluation of each item
    for j in range( len(name_list) ):
        name = name_list[j]
        name = db.escape_string(name)
        try:
            cursor = con.cursor()
            cursor.execute("""SELECT base1.rating 
                                FROM movies INNER JOIN base1 
                                ON movies.movie_id = base1.movie_id
                                WHERE movies.movie_name = '%s' """ % (name) )
            con.commit()
        except db.Error:
            print 'ERROR: start to roll back'
            print db.Error
            try:
                con.rollback()
            except:
                pass
            
        num_mov = int(cursor.rowcount)
        winning_score = 0.0
        score_list = {}
        
        for i in range( num_mov ):
            row = cursor.fetchone()
            row = str(row[0])
            score_list.setdefault(row, 0)
            score_list[row] += 1

        sum = 0.0
        div = 0.0
        for key,val in score_list.items():
            key = float(key)
            sum += key * val
            div += val
        # the expected rating
        expected_rating = float(sum) / float(div)
        # the popularity
        popularity = (float(div) / all_usr_num)*5.0
        
        # form the winning score
        winning_score = expected_rating + popularity 
            
        winning_list.append(winning_score)
    
    return winning_list        


# get the biggest payoff from the database use the name in the strategy list
# for the strategy from collaborative filter
def gen_payoff_coll_filt( result_coll_filt):
    name_from_result = []
    payoff_list = []
    # get name list of the result from collaborative filter
    for i in range( len(result_coll_filt) ):
        name_from_result.append(result_coll_filt[i][1])
        
    payoff_list = gen_payoff_list( name_from_result )
    
    #print payoff_list
    #print '\n'
    #print name_from_result        
    return payoff_list, name_from_result

# for the strategy from cluster, need pass in result from cluster include movie name
# array, and the name array generated from the gen_payoff_coll_filt() function.
def gen_payoff_cluster( result_cluster, movie_name_arr, name_arr_from_coll_filter, movie_had_seen ):
    # use a list to store the strategy name of the payoff
    name_from_result = []
    payoff_list = []
    # loop the name array return from collaborative filter to fetch the similar element
    # from the cluster to form a new name array list with the same length with the name
    # list from the collaborative filter
    for i in range( len(name_arr_from_coll_filter) ):
        name_coll = name_arr_from_coll_filter[i]
        # loop the cluster to find the similar element
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
                        name_from_result.append(movie_name_arr[location])
                        break
    
    payoff_list = gen_payoff_list( name_from_result )
    
    #print payoff_list
    #print '\n'
    #print name_from_result  
    return payoff_list, name_from_result

