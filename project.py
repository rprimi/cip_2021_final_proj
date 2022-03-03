"""
CAT: Numerical Reasoning
--------------------------------------------------
Final project CIP21. Simple Computerized Adaptive Test of Numerical Reasoning.
Ricardo Primi, Universidade São Francisco, Brazil (ricardo.primi@usf.edu.br)

Fun project to practice main concepts learned in CIP21
This uses data of a numerical reasoning test with item dificulties calibrated under Rasch model
(https://www.scielo.br/j/ptp/a/6rvvQsNBT9ZmgqQz7SyJ5TL/?lang=pt)

Problem Decomposition (milestones):

 - Function to create item data base (read_item_db())
    Reads a typical csv - dataframe - and transforms into a dictionary (key is the column name and element is a list
    of values of that variable.
    (found solution her https://www.geeksforgeeks.org/python-read-csv-columns-into-list/)

 - Function to select item via maximum information and keep track of items administered (next_item())
   # This works because lists within dictionnaires are mutables and are changed in place
   # I used a pop in a list inside a dictionnaire and it extracted one element from the list. Cool !
    # Thanks to this post:
    # https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value

 - Function to estimate ability (estimate_theta())
    * Rash model using formula rom: Baker, F. B., & Kim, S.-H. (2017). The Basics of Item Response Theory Using R.
     Springer International Publishing. https://doi.org/10.1007/978-3-319-54205-8

 - Main algorithm:
    * Intro: info and get name, present first item and get response and score
    * Test:  Estimate theta, check for stoping rule, stop or go to next item.
    * Print scores e standardized scores

"""

def main():
# Item database and initial lists and variables

    item_db = read_item_db('rn_db.csv') # item databas (dictionnaire)

    s = 0                               # scored response
    r = []                              # list of scored responses
    i = [item_db["coditem"][0]]         # code of item administered
    bs =[item_db["b"][0]]               # item difficulties

    sem_theta = .70
    max_items = 18
    resp = ""

# Instructions and first pass. Administer item RN01 as training
    print('Hello! I am RN_CAT a Computerized Adaptive Test of Numerical Reasoning!')
    print("I am a simple program created by padawan Ricardo who is learning the ways of the force with Python")
    print()
    name =  input("What is your name ? ")
    print("Hi " + name + ". Lets solve problems of numerical reasoning  ?")
    print()
    print("I will present number sequences and ask you to finish with the last numbers that logically follows the sequence")
    print("For instance: ")
    print()
    print(item_db["item"][0])
    print()
    resp = input("What is the two last numbers? (type one number, space and the next number): ")
    print()


# Fist pass
    s = score(resp, item_db["key"][0])
    r.append(s)

    if s == 1:
        print("Correct! Lets start the test")
    else:
        print("This sequence is aways increasing +3 so the correct answer is " + item_db["key"][0])
        print("Lets start the test")

# remove item 1 from the dictionnaire (these are removed in place)
    item_db['coditem'].remove(item_db['coditem'][0]),
    item_db['b'].remove(item_db['b'][0]),
    item_db['item'].remove( item_db['item'][0]),
    item_db['key'].remove(item_db['key'][0])

# calculate theta and next item from first pass
    theta = estimate_theta(r, bs, [-3])
    next_i = next_item(theta[0], item_db)

# Actual CAT (runs until sem is lower than sem_theta or when item reach max items
    while theta[1] >= sem_theta and len(r) <= max_items:

        print()
        resp = input(next_i["item"])
        print()

        s = score(resp, next_i["key"])

        if s == 1:
            yn = input("Correct! Type 'y' for the next item or 'n' to quit ")
        else:
            yn = input("Incorrect! The correct answer is " + next_i["key"] + " Type 'y' for the next item or 'n' to quit ")
        if yn == "n": break

        r.append(s)
        bs.append(next_i["b"])
        i.append(next_i["coditem"])

        theta = estimate_theta(r, bs, theta)
        next_i = next_item(theta[0], item_db)

    print()
    print("Congratulations! You finished the CAT RN test")
    print("You answered " + str(len(r)) + " items")
    print("You got " + str(sum(r)) + " correct")
    print("Your IRT theta scores was " + str(round(theta[0], 2)) + ", sem = " + str(round(theta[1], 2)))
    print("Your standardized score (M=100, DP=15 like in IQ tests) was " + str(round( ((theta[0] - 1.40)/1.50)*15) + 100  ))




def score(resp, key):

    resp = resp.split()
    key = key.split()

    if (resp[0] == key[0]) & (resp[1] == key[1]):
        s = 1
    else:
        s = 0
    return(s)

def next_item(theta, item_db):
    # Find index of item closest to theta
    # Pop this item from item_db
    # Returns a dictionnaire with the current item for administration

    i_nxt_itm = index_of_closest(item_db['b'], theta)

    next_item_db = {
        'coditem' : item_db['coditem'].pop(i_nxt_itm ),
        'b': item_db['b'].pop(i_nxt_itm ),
        'item' : item_db['item'].pop(i_nxt_itm ),
        'key' : item_db['key'].pop(i_nxt_itm )
    }

    return next_item_db



def index_of_closest(list, number):
    # Creates a list with bs (item difficulties) minus current theta.
    # The result item closest to zero is the item  with maximum information at current theta
    # Returns item index

    aux = []
    for valor in list:
        aux.append(abs(number-valor))
    return aux.index(min(aux))


import csv
def read_item_db(file):

    filename = open(file)

    file = csv.DictReader(filename)

    coditem = []
    b = []
    item = []
    key = []

    for col in file:
        coditem.append(col['coditem'])
        b.append(float(col['b']))
        item.append(col['item'])
        key.append(col['key'])

    item_db = {
        'coditem' : coditem,
        'b': b,
        'item' : item,
        'key' : key
     }
    return(item_db)



def estimate_theta(r, b, th):
    # r: response vector
    # b: item difficulty parameters

    import math
    conv = 0.001
    J = len(r)
    se = 10.0
    delta = conv + 1
    th = float(th[0])

    th_max = max(b) + .5
    th_min = min(b) - .5

    if sum(r) == J:
        th = th_max
    elif sum(r) == 0:
        th = th_min
    else:
        while abs(delta) > conv:
            sumnum = 0.0
            sumdem = 0.0
            for j in range(J):
                phat = 1 / (1.0 + math.exp(-1 * (th - b[j])))
                sumnum = sumnum + 1.0 * (r[j] - phat)
                sumdem = sumdem - 1.0 * phat * (1.0 - phat)
            delta = sumnum / sumdem
            th = th - delta
            se = 1 / math.sqrt(-sumdem)

    return [th, se]


if __name__ == '__main__':
    main()