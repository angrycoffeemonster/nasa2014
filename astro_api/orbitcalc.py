import numpy as np
import json
import math
import gzip
##
#Globals
asteroids = []
jed_apr142014=2456760.5
jed_cur = jed_apr142014
earth = { 'L': 100.46457166, 'P': 365.256, 'a': 1.00000261, 'e': 0.01671123, 'epoch': 2451545, 'full_name': "Earth", 'i': 0.00001531, 'ma': -2.4731102699999923, 'om': 0, 'w': 102.93768193, 'w_bar': 102.93768193, 'n': 0.0 }


##

#Load asteroid data
rootdir='./'#'/home/jeff/Work/NASA2014/nasa2014/'
files=['asteroids_neo.json.gz']
fs = []
for name in files:
    fs.append( gzip.open(rootdir + name) )

for f in fs:
    asteroids = asteroids + json.load(f)

##
def AsteroidPositionVector(ast,jed=jed_cur):
    return KeplerToHeliocentric(jed,ast['i'],ast['om'],ast['w'],ast['ma'],ast['n'],ast['epoch'],ast['e'],ast['a'],-1.0)

def EarthPositionVector(jed=jed_cur):
    return KeplerToHeliocentric(jed, earth['i'], earth['om'], earth['w'], earth['ma'], earth['n'],earth['epoch'],earth['e'],earth['a'],earth['P'])
    
def KeplerToHeliocentric(jed,i,om,w,ma,n,epoch,e,a,P):
    """
    Given kepler dynamics and date, calculates the X, Y, and Z in Heliocentric coordinates, unit of AU.
    i: inclination
    om: longitude/right ascention of ascending node ("om" in json)
    w: perigee of ascending node
    ma: mean anomaly
    n: mean deg/day
    jed: Current julian day, float
    epoch: jed of orbital data (Should be ~2.4 million)
    e: eccentricity
    a: Semi-major axis
    """

    pi = math.pi
    
    i_rad = (i) * pi/180.0#
    o_rad = (om) * pi/180.0# // longitude of ascending node
    p_rad = (w) * pi/180.0# // LONGITUDE of perihelion
    ma_rad = ma * pi/180.0
    n_rad=0.0
    if P > 0.:
        n_rad = 2.0 * pi / P
    else:
        n_rad = n * pi/180.0# // mean motion
    

    d = jed - epoch
    M = ma_rad + n_rad * d

    E0 = M
    E1 = M + e * math.sin(E0)
    lastdiff = abs(E1-E0)
    E0 = E1
    for ii in range(25):
        E1 = M + e * math.sin(E0)
        lastdiff = abs(E1-E0)
        E0 = E1
        if lastdiff > 0.0000001:
            break
            
    E = E0

    v = 2.0 * math.atan(math.sqrt((1.0+e)/(1.0-e)) * math.tan(E/2.0))

    #// radius vector, in AU
    r = a * (1.0 - e*e) / (1.0 + e * math.cos(v))

    #// heliocentric coords
    X = r * (math.cos(o_rad) * math.cos(v + p_rad - o_rad) - math.sin(o_rad) * math.sin(v + p_rad - o_rad) * math.cos(i_rad))
    Y = r * (math.sin(o_rad) * math.cos(v + p_rad - o_rad) + math.cos(o_rad) * math.sin(v + p_rad - o_rad) * math.cos(i_rad))
    Z = r * (math.sin(v + p_rad - o_rad) * math.sin(i_rad))
    return np.array([X, Y, Z])
##



def GetClosestAsteroids(limit,day):
    day = day + jed_apr142014
    jed_cur = day
    
    earth_pos_vec = EarthPositionVector(day)
    for i,a in enumerate(asteroids):
        asteroids[i]['pos_vec']=AsteroidPositionVector(a,day)
        asteroids[i]['pos_vec_earth'] = a['pos_vec']-earth_pos_vec
        asteroids[i]['earth_dist'] = math.sqrt( np.dot(asteroids[i]['pos_vec_earth'] , asteroids[i]['pos_vec_earth'] ) )
    
    ast_sort = sorted(asteroids,key= lambda x: x['earth_dist'])
    ast = ast_sort[:limit]
    
    earth_pos_vec_2 = EarthPositionVector(day + 1)
    for i,a in enumerate(ast):
        ast[i]['pos_vec_2']=AsteroidPositionVector(a,day+1)
        ast[i]['pos_vec_earth_2'] = a['pos_vec_2']-earth_pos_vec_2
        ast[i]['earth_dist_2'] = math.sqrt( np.dot(ast[i]['pos_vec_earth_2'] , ast[i]['pos_vec_earth_2'] ) )
        ast[i]['earth_dv'] = (ast[i]['earth_dist_2'] - ast[i]['earth_dist']) * 149597871.0 / 86400.0
        
        ast[i]['pos_vec']=0
        ast[i]['pos_vec_2']=0
        ast[i]['pos_vec_earth']=0
        ast[i]['pos_vec_earth_2']=0
    return ast
    
    
    
##



def LoadFullAsteroidData():
    rootdir='/home/jeff/Work/NASA2014/nasa2014/'
    files=['asteroids1.json.gz','asteroids2.json.gz','asteroids3.json.gz']
    fs = []
    for name in files:
        fs.append( gzip.open(rootdir + name) )

    asteroids = []
    for f in fs:
        for line in f:
            asteroids.append( json.loads(line) )
            
    ast_neo = filter(lambda x: x['neo']=='Y', asteroids)
    print len(asteroids), len(ast_neo)
    
    f = open(rootdir + 'asteroids_neo.json','w')
    json.dump(ast_neo,f)
    f.close()

#LoadFullAsteroidData()


##

#print len(asteroids)