import pymysql.cursors
import pymysql
from collections import defaultdict
import urllib.request, json
import math



#Pull Data from API (ESI), store in MYSQL
def esi_imp():
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             db='eve',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    response = urllib.request.urlopen('https://esi.tech.ccp.is/dev/markets/10000002/orders/?datasource=tranquility&order_type=all&page=1')
    response.getcode()
    pages = (response.getheader('X-Pages'))
    pages = int(pages)
    print (response.getheader('Expires'))
    toSQL = []
    for i in range(1,pages):
        url = "https://esi.tech.ccp.is/dev/markets/10000002/orders/?datasource=tranquility&order_type=all&page="
        url += str(i)
        with urllib.request.urlopen(url) as url:
            toSQL += json.loads(url.read().decode())
    
    cursor = connection.cursor()
    sql = 'TRUNCATE TABLE jita_prod'
    cursor.execute(sql)
    for row in toSQL:
        cursor.execute('INSERT INTO jita_prod(orderid, typeid, location, volume, price, buy) Values (%s, %s, %s, %s, %s, %s)', (row['order_id'], row['type_id'], row['location_id'], row['volume_remain'], row['price'], row['is_buy_order']))
    connection.commit()               
    connection.close


def ore_calc():
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             db='eve',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    sell_prices = "SELECT jita_prod.orderid, jita_prod.typeid, jita_prod.volume, jita_prod.price, typeid.typename FROM jita_prod,typeid \
    WHERE jita_prod.typeid = typeid.typeid AND jita_prod.buy = 1 AND (jita_prod.typeid = 11399 OR (jita_prod.typeid >= 28387 AND jita_prod.typeid <= 28432) \
    OR jita_prod.typeid = 28367 OR jita_prod.typeid = 28385 OR (jita_prod.typeid >= 46691 AND jita_prod.typeid <= 46705) OR (jita_prod.typeid >= 34 AND jita_prod.typeid <= 40))"
    cursor.execute(sell_prices)
    sell_prices = cursor.fetchall()
    oreminerals = "SELECT * from oremineral"
    cursor.execute(oreminerals)
    oreminerals = cursor.fetchall()
    connection.close()
    cursor.close()
    reprocessing = 0.8762148595
    buy_percentage = 1.03
    typeid = []
    for i in sell_prices:
        if i['typeid'] not in typeid:
            typeid.append(i['typeid'])
            
    min_price_list = []
    for i in typeid:
        ore = [item for item in sell_prices if item['typeid'] == i]
        min_ore = max(ore, key = lambda x:x['price'])
        min_price_list.append(min_ore)
        
    min_price_dic = {}
    for i in typeid:
        ore = [item for item in sell_prices if item['typeid'] == i]
        min_ore = max(ore, key = lambda x:x['price'])
        min_price_dic[min_ore['typename']] = min_ore
    
    minerals = {}
    for i in min_price_list:
        if i['typeid']>=34 and i['typeid']<=40:
            minerals[i['typename']] = i['price']
        elif i['typeid'] == 11399:
            minerals[i['typename']] = i['price']

    
    ores = []
    for i in min_price_list:
        if i['typeid'] >= 41 and i['typeid'] != 11399:
            ores.append(i)
            

    orevalue = defaultdict(int)
    for ore in oreminerals:
        for mineral in ore:
            if mineral != 'Ore' and mineral != 'typeid':
                orevalue[ore['Ore']] += ore[mineral]*reprocessing*minerals[mineral]
        if orevalue[ore['Ore']] > 0:
            orevalue[ore['Ore']] = 100/orevalue[ore['Ore']]*min_price_dic[ore['Ore']]['price']*buy_percentage/100
        for mineral in ore:
            if mineral != 'Ore' and mineral != 'typeid' and ore[mineral] > 0:
                ore[mineral] = minerals[mineral] * orevalue[ore['Ore']]

    oreminerals = [item for item in oreminerals if item['Ore'] != 'Compressed Platinoid Omber' and item['Ore'] != 'Compressed Glossy Scordite' and item['Ore'] != 'Compressed Sparkling Plagioclase']
    return oreminerals
    
    


        
def prod():
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             db='eve',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    blueprints = "SELECT industryactivitymaterials.typeid, industryactivitymaterials.materialtypeid, industryactivitymaterials.quantity, typeid.typename FROM industryactivitymaterials,typeid \
    WHERE typeid.typeid = industryactivitymaterials.materialtypeid AND industryactivitymaterials.activityid = 1"
    cursor.execute(blueprints)
    blueprints = cursor.fetchall()
    typeid = "SELECT * FROM typeid"
    cursor.execute(typeid)
    typeid = cursor.fetchall()
    oreminerals = "SELECT * FROM oremineral"
    cursor.execute(oreminerals)
    oreminerals = cursor.fetchall()
    connection.close()
    cursor.close()
    ME = 0.1
    Reprocessing = 0.8762148595
    
    

                
    production_dic = defaultdict(int)
    name = ""
    mats = 0
    production = dict()
    while name != 'no':
        name = input('What do you want to build? (type "no" to stop) ')
        if name == 'no':
            break
        blueprint_name = name + ' Blueprint'
        bp = [item for item in typeid if item['typename'] == blueprint_name]
        if not bp:
            print ('Sorry, my db doesnt know how to build this item')
        else:
            amount = 0
            amount = input('How many of them do you want to build? ')
            bp = bp[0]
            mats = [item for item in blueprints if bp['typeid'] == item['typeid']]
            try:
                int(amount)
            except ValueError:
                print ('This is not a valid number, please add a number of how many things you want to produce')
            amount = int(amount)
            for item in mats:
                production_dic[item['typename']] += amount * item['quantity']
    for item in production_dic:
        for blueprint in blueprints:
            if blueprint['typename'] == item:
                production[item] = blueprint
    
    oremineralsdict = dict()
    for ore in oreminerals:
        oremineralsdict[ore['Ore']] = ore
#    print (oremineralsdict)


    ore = ore_calc()

    
    mineraldict = {'Tritanium': 34, 'Pyerite': 35, 'Mexallon': 36, 'Isogen': 37, 'Nocxium': 38, 'Zydrine': 39, 'Megacyte': 40, 'Morphite': 11399}
    oredict = dict()
    for mineral in mineraldict:
        ores = []
        ores = [item for item in ore if item[mineral] > 0]
        ores = min(ores, key = lambda x:x[mineral])
        oredict[mineral] = ores

    goal = dict()
    for item in production:
        goal[item] = production[item]['quantity']  # Dictionary, Key = Mineral, Index = Amount of Mineral needed for jobs
        
    buydict = dict()
    
    for item in production:
        if production[item]['materialtypeid'] == mineraldict[item]:
            print (oremineralsdict[oredict[item]['Ore']])
            print (oremineralsdict[oredict[item]['Ore']][item])
            for i in goal:
                basicmineralinore = oremineralsdict[oredict[item]['Ore']][item]
                buydict[i] = dict()
                buydict[i]['Ore'] = oremineralsdict[oredict[i]['Ore']]['Ore']
                buydict[i]['Oreamount'] = int(math.ceil(production[i]['quantity']/(basicmineralinore * Reprocessing)))
                
                buydict[i]['Mineral'] = int()
                print (oremineralsdict[oredict[item]['Ore']][i])
                goal[i] -= int(math.ceil(production[item]['quantity']/(basicmineralinore * Reprocessing))) * Reprocessing * oremineralsdict[oredict[item]['Ore']][i]
                buydict[i]['Mineral'] += int(math.ceil(buydict[item]['Oreamount'] * oremineralsdict[oredict[item]['Ore']][i] * Reprocessing)) * oremineralsdict[oredict[item]['Ore']][i]
            buydict[item]['leftovers'] = buydict[item]['Mineral'] - production[item]['quantity']
    print (goal)
    print (buydict)
    print ('')
    
    count = 0
    while count < 1:
        for item in production:
            basicmineralinore = oremineralsdict[oredict[item]['Ore']][item]
            excess = buydict[item]['leftovers']
            if excess < basicmineralinore*Reprocessing*(-1):
                oreexcess = math.floor(excess * (-1))/(basicmineralinore * Reprocessing) 
                if oreexcess > buydict[item]['Oreamount']:
                    buydict[item]['Oreamount'] = 0
                    print (buydict[item]['Oreamount'])
                else:
                    buydict[item]['Oreamount'] -= oreexcess
                for i in goal:
                    goal[i] -= int(math.ceil(production[item]['quantity']/(basicmineralinore * Reprocessing))) * Reprocessing * oremineralsdict[oredict[item]['Ore']][i]
                    buydict[item]['Mineral'] += int(math.ceil(buydict[item]['Oreamount'] * oremineralsdict[oredict[item]['Ore']][i] * Reprocessing)) * oremineralsdict[oredict[item]['Ore']][i]
                buydict[item]['leftovers'] = buydict[item]['Mineral'] - production[item]['quantity']
        count += 1
    print (goal)
    print (buydict)
 #   print (goal)
    #        print (oremineralsdict[oredict[item]['Ore']]['Ore'])
   #         print(math.ceil(production[item]['quantity']/oremineralsdict[oredict[item]['Ore']][item]))
   
    
           #     for item in production:
          #          print(production[item]['quantity']/oremineralsdict[item]['])
                    
         #   return mineralset
        #    print (production[item]['materialtypeid'])

    
    #print (production_dic)
    #print (production)

    
prod()
