from math import sqrt

# get recommendation for person by using a weighted average of every other 
# users` rankings

def getRecommendations( prefs, person, similarity ):
    totals = {}
    sim_sum = {}
    
    for other in prefs:
        
        # don`t compare with self
        if other == person: continue
        
        # calculate the similarity between you and others
        sim = similarity( prefs, person, other )
        
        # ignore scores that is zero or lower
        if sim <= 0: continue
        
        for item in prefs[other]:
            
            # only use the item you haven`t rated
            if item not in prefs[person] or prefs[other][item] == 0:
                
                # sum of the weighted average of the similarity of a item for 
                # every others
                totals.setdefault( item, 0 )
                totals[item] += prefs[other][item] * sim
                
                # sum of the similarity of a item for every others
                sim_sum.setdefault( item, 0 )
                sim_sum[item] += sim
                
    # create the item recommendation list
    rankings = [ ( total/sim_sum[item], item ) for item, total in totals.items()]
    
    # return the sorted recommendation list 
    rankings.sort(cmp=None, key=None, reverse=False)
    rankings.reverse()
    return rankings


# function of calculating the similarity of two person by using the distance
def simDistance( prefs, person1, person2 ):
    
    # get the list of shared_items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] += 1
            
    # if they haven`t both the same items, return 0
    if len( si ) == 0: return 0
    
    # add up the squares of all the differences
    sum_of_squares = sum( [pow( prefs[person1][item] - prefs[person2][item], 2 ) 
                           for item in prefs[person1] if item in prefs[person2]] )
    
    return 1 / ( 1 + sum_of_squares )


# function of calculating the similarity of two person by using the PERSON function
def simPerson( prefs, person1, person2 ):
    
    # get the list of mutually rated items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
            
    # if two person haven`t the same rated items, return 0
    if len( si ) == 0: return 0
    
    # record the numbers of the items which were rated by both person
    num = len( si )
    
    # sum of the ratings for the all rated items
    sum1 = sum( [prefs[person1][item] for item in si] )
    sum2 = sum( [prefs[person2][item] for item in si] )
    
    # sum of the squares of the ratings for all rated items 
    sum_square1 = sum( [pow( prefs[person1][item], 2 ) for item in si] )
    sum_square2 = sum( [pow( prefs[person2][item], 2 ) for item in si] )
    
    # sum of the products
    prod_sum = sum( [prefs[person1][item] * prefs[person2][item] for item in si] )
    
    # calculate person score
    n = prod_sum - ( sum1 * sum2 / float(num) )
    den = sqrt( ( sum_square1 - pow( sum1, 2) / float(num) ) *
                 ( sum_square2 - pow( sum2, 2 ) / float(num) ) )
    if den == 0: return 0
    
    r = n / float(den)
    
    return r 

def topMatches(prefs,person,n=5,similarity=simPerson):
    scores=[(similarity(prefs,person,other),other) 
                  for other in prefs if other!=person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

def transformPrefs(prefs):
    result={}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
      
            # Flip item and person
            result[item][person]=prefs[person][item]
    return result

def calculateSimilarItems(prefs,n=20):
    # Create a dictionary of items showing which other items they
    # are most similar to.
    result={}
    # Invert the preference matrix to be item-centric
    itemPrefs=transformPrefs(prefs)
    c=0
    for item in itemPrefs:
        # Status updates for large datasets
        c+=1    
        if c%100==0: print "%d / %d" % (c,len(itemPrefs))
        # Find the most similar items to this one
        scores=topMatches(itemPrefs,item,n=n,similarity=simPerson)
        result[item]=scores
    return result

def getRecommendedItems(prefs,itemMatch,user):
    userRatings=prefs[user]
    scores={}
    totalSim={}
    # Loop over items rated by this user
    for (item,rating) in userRatings.items( ):

        # Loop over items similar to this one
        for (similarity,item2) in itemMatch[item]:

            # Ignore if this user has already rated this item
            if item2 in userRatings: continue
            # Weighted sum of rating times similarity
            scores.setdefault(item2,0)
            scores[item2]+=similarity*rating
            # Sum of all the similarities
            totalSim.setdefault(item2,0)
            totalSim[item2]+=similarity

    # Divide each total score by total weighting to get an average
    #rankings=[(score/totalSim[item],item) for item,score in scores.items( )]
    rankings = []
    for item, score in scores.items():
        if totalSim[item] == 0:
            rankings.append((0,item))
        else:
            rankings.append((score/totalSim[item], item))

    # Return the rankings from highest to lowest
    rankings.sort( )
    rankings.reverse( )
    return rankings    