import clusters
import MySQLdb as db
import db_config as dbconf

# fetch the data for cluster from database
def get_data_from_db():
    # get data from database
    con = dbconf.connect_db()
    prefs = {}
    pref = {}
    movies = {}

    try:
        cursor = con.cursor()
        cursor.execute("""SELECT  movies.movie_id, movies.movie_name, base1.user_id, base1.rating 
                        FROM movies INNER JOIN base1 
                        ON movies.movie_id = base1.movie_id""")
        con.commit()
    except db.Error, e:
        print 'ERROR: start to roll back'
        print db.Error
        try:
            con.rollback()
        except:
            pass

    num_mov = int(cursor.rowcount)

    for i in range(num_mov):
        row = cursor.fetchone()
        movie_id = str(row[0])
        movie_name = str(row[1])
        user_id = str(row[2])
        rating = float(row[3])
    
        movies.setdefault(movie_id, "")
        movies[movie_id] = movie_name

        prefs.setdefault(user_id, {})
        prefs[user_id][movies[movie_id]] = rating 


    cursor.close()
    con.close()
    return prefs

# reverse the dictionary fetched from database, use movie id as keys
def transformPrefs(prefs):
    result={}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
      
            # Flip item and person
            result[item][person]=prefs[person][item]
    return result

# change the dictionary to arrays
def dic_to_arr_cluster( rev_prefs, user_id_arr ):
    movie_name_arr = []
    rating_arrs = []
    for movie_name, usr_rating in rev_prefs.items():
        rating_arr = []
        movie_name_arr.append(movie_name)
        for i in range( len(user_id_arr) ):
            flag = 0
            for user_id, rating in usr_rating.items():
                if i == int(user_id): 
                    rating_arr.append(rating)
                    flag = 1
            if flag == 0:
                rating_arr.append(0)
        #print len( rating_arr )
        rating_arrs.append(rating_arr)
    return movie_name_arr, user_id_arr, rating_arrs

# store the name array for cluster, one can use the result from the cluster element 
# to locate the name in the name array 
def store_name_arr_for_cluster(movie_name_arr):
    con = dbconf.connect_db()
                  
    try:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS `cluster_mov_id_arr_cache1` (
                        `clus_movie_id` int(10) unsigned NOT NULL,
                        `movie_name` varchar(170) NOT NULL,
                        PRIMARY KEY (`clus_movie_id`)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 """)
        con.commit()
        cur.close()
    except db.Error:
        pass
                
    for i in range( len(movie_name_arr) ):
        movie_name = movie_name_arr[i]
        movie_name = db.escape_string(movie_name)
        clus_movie_id = i 
        try:
            cur = con.cursor()
            cur.execute("""REPLACE cluster_mov_id_arr_cache1( movie_name, clus_movie_id )
                            VALUES( '%s', %d )""" % ( movie_name,clus_movie_id))
            con.commit()
            cur.close()
        except db.Error:
            print 'error'
            print db.Error
            try:
                con.rollback()
                #cur = con.cursor()
                #cur.execute("""INSERT INTO cluster_mov_id_arr_cache( clus_movie_id, movie_name )
                #                VALUES( %d, '%s' )""" % (clus_movie_id, movie_name))
                #con.commit()
                #cur.close()
            except db.Error:
                print db.Error
    
    con.close()
    print 'store cluster name array finished.'

# fetch the name array from database for the cluster result to locate the name
# of the result    
def fetch_clust_name_arr_from_db():
    name_arr = []
    con = dbconf.connect_db()
    
    try:
        cur = con.cursor()
        cur.execute("""SELECT movie_name
                        FROM cluster_mov_id_arr_cache1""")
        con.commit()
    except db.Error:
        print 'select error.'
        print db.Error
        try:
            con.rollback()
        except db.Error:
            print db.Error
    
    row_num = int(cur.rowcount)
    
    for i in range( row_num ):
        row = cur.fetchone()
        name = row[0]
        name_arr.append(name)
        
    cur.close()
    con.close()
    print 'fetch cluster name array success.'
    return name_arr
        

# store the result in the database, the parameter is from the kcluster() output which is a list
def store_cluster_result(cluster_result):
    con = dbconf.connect_db()
               
    try:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS `cluster_result_cache1` (
                        `cluster_id` int(10) unsigned NOT NULL,
                        `clus_movie_id` int(10) unsigned NOT NULL,
                        PRIMARY KEY (`cluster_id`,`clus_movie_id`),
                        KEY `clus_movie_id` (`clus_movie_id`)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8""")
        con.commit()
        cur.close()
    except db.Error:
        pass
           
    # clear the database table for a new cluster procedure
    #try:
    #    cur = con.cursor()
     #   cur.execute("""DELETE FROM cluster_result_cache""")
      #  con.commit()
       # cur.close()
    #except db.Error:
     #   print 'delete failed.'
      #  print db.Error
       # try:
        #    con.rollback()
       # except db.Error:
        #    print db.Error
    
    # store the cluster result in the database    
    for i in range( len(cluster_result) ):
        one_cluster = cluster_result[i]
        cluster_id = i
        for clus_movie_id in one_cluster:
            try:
                cur = con.cursor()
                cur.execute("""REPLACE cluster_result_cache1( cluster_id, clus_movie_id )
                                VALUES( %d, %d )""" % (cluster_id, clus_movie_id))
                con.commit()
                cur.close()
            except db.Error:
                print 'error'
                print db.Error
                try:
                    con.rollback()
                    #cur = con.cursor()
                    #cur.execute("""INSERT INTO cluster_result_cache( cluster_id, clus_movie_id )
                    #           VALUES( %d, %d )""" % (cluster_id, clus_movie_id))
                    #con.commit()
                    #cur.close()
                except db.Error:
                    print db.Error
            
    con.close()
    print 'store cluster result finished.'
    
# fetch the cluster result in the database, output the result list whose element are some list 
# which store the movie id in that cluster.
def fetch_cluster_result_from_db():
    con = dbconf.connect_db()
    # create the variable to store the result
    result = []
    # select the cluster id, no need to confirm the sequence
    try:
        cur = con.cursor()
        cur.execute("""SELECT DISTINCT(cluster_id)
                        FROM cluster_result_cache1""")
        con.commit()
    except db.Error:
        print 'select error.'
        print db.Error
        try:
            con.rollback()
        except db.Error:
            print db.Error
    
    row_num = int(cur.rowcount)
    cur.close()
    cluster_id_arr = range(row_num)
    
    # from the cluster id to find its element to complete the cluster which is a list
    for cluster_id in cluster_id_arr:
        one_cluster = []
        try:
            cur = con.cursor()
            cur.execute("""SELECT  clus_movie_id
                            FROM cluster_result_cache1
                            WHERE cluster_id=%d""" % (cluster_id))
            con.commit()
        except db.Error:
            print 'select error'
            print db.Error
            try:
                con.rollback()
            except db.Error:
                print db.Error
        # append the element into the cluster list
        rownum = int(cur.rowcount)
        for i in range(rownum):
            row = cur.fetchone()
            clus_movie_id = int(row[0])
            one_cluster.append(clus_movie_id)
            
        cur.close()
        # append the cluster into the result list
        result.append(one_cluster)
        
    con.close()
    print 'fetch cluster result success.'
    return result
        
def initialize_cluster():
    prefs = get_data_from_db()
    user_id_arr = prefs.keys()
    rev_prefs = transformPrefs( prefs )

    (movie_name_arr, user_id_arr, rating_arrs) = dic_to_arr_cluster( rev_prefs, user_id_arr )


    #result_from_cluster = clusters.kcluster( rating_arrs )
    kcluster_result = clusters.kcluster(rating_arrs)
    store_name_arr_for_cluster(movie_name_arr)
    store_cluster_result(kcluster_result)

def run_cluster():
    movie_name_arr = fetch_clust_name_arr_from_db()
    result_from_cluster = fetch_cluster_result_from_db()
    
    return result_from_cluster, movie_name_arr
