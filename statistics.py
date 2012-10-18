import matplotlib.pyplot as plt
import random
import MySQLdb as db
import db_config as dbconf

  
# method_list = ('game theory', 'genetic optimize', 'annealing optimize')
def draw_pic(x_vec, y_vec, x_label='', y_label='', title=''):
    i = random.randint(0,1000)
    file_name = 'attribute0' + str(i) + '.png'
    plt.plot(
             x_vec['genetic optimize'], y_vec['genetic optimize'], 'r-s',
             x_vec['annealing optimize'], y_vec['annealing optimize'], 'g-^',
             x_vec['collaborative filter'], y_vec['collaborative filter'], 'b--')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.savefig(file_name)
    plt.close()
    
# calculate the recall and precision, pass in the user list and the recommend .
# this function can just used for one method one time . 
def calc_recall_prec(usr_rec_for, rec_list):
    # construct a dictionary to store the user and his recommend, its element has the form
    # {'user name':[(rating, item),...,(rating, item)], ....}
    user_rec_dict = {}
    for i in range( len(usr_rec_for) ):
        user_rec_dict.setdefault(usr_rec_for[i], [])
        for j in range( len(rec_list) ):
            user_rec_dict[usr_rec_for[i]] = rec_list[j]
    # fetch the test data 
    test_prefs = get_test_prefs()
    # form the test data dictionary, it has the form:{'user': [(rating,item),...,(rating,item)]
    test_rec_dict = {}
    for i in range( len(usr_rec_for) ):
        test_rec_dict.setdefault(usr_rec_for[i], [])
        for key, val in test_prefs[usr_rec_for[i]].items():
            test_rec_dict[usr_rec_for[i]].append((val, key))
    
    # pass in the dictionary above and the user list, calculate the recall dictionary and 
    # the precision dictionary.they all have the form:{'user':rate,...,'user':rate}
    recall_dict , precision_dict = compute_rec_pre( user_rec_dict, test_prefs, usr_rec_for )
    #return the two dictionary
    return recall_dict, precision_dict

# compute the recall and the precision
def compute_rec_pre( user_rec_dict, test_prefs, usr_rec_for ):
    recall_dict = {}
    precision_dict = {}
    # loop the user in the passed in list, calculate each recall and precision.
    for user in usr_rec_for:
        tp = 0.0
        fn = 0.0
        fp = 0.0
        recall_dict.setdefault(user, 0.0)
        precision_dict.setdefault(user, 0.0)
        # fetch the user`s rating list, it has the form:[(rating,item name),...,(rating,item name)]
        rec_list = user_rec_dict[user]
        # loop the list,find the match item between the recommend list and the test list
        for i in range( len(rec_list) ):
            for movie in test_prefs[user]:
                if movie == rec_list[i][1]:
                    tp += 1.0
                    break
        
        fn = len(rec_list) - tp
        fp = len(test_prefs[user].keys()) - tp
        # calculate the recall and precision from each user, multiply 100 in order to 
        # draw the graph.
        recall = tp / (tp + fn)
        recall_dict[user] = recall*100
        
        precision = tp / (tp + fp)
        precision_dict[user] = precision*100
    
    return recall_dict, precision_dict

def get_test_prefs():
    # get data from database
    con = dbconf.connect_db()
    test_prefs = {}
    movies = {}

    try:
        cursor = con.cursor()
        cursor.execute("""SELECT  movies.movie_id, movies.movie_name, test1.user_id, test1.rating 
                        FROM movies INNER JOIN test1 
                        ON movies.movie_id = test1.movie_id""")
        con.commit()
    except db.Error:
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

        test_prefs.setdefault(user_id, {})
        test_prefs[user_id][movies[movie_id]] = rating 


    cursor.close()
    con.close()

    return test_prefs


            