import MySQLdb as db

# connect to the database
def connect_db():
    try:
        con = db.connect('localhost', 'root', '19871109china', 'movie')
    except db.Error:
        print "fail to connect the database."
        print db.Error
        
    return con