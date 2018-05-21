import pymysql.cursors
import pymysql
from collections import defaultdict
import urllib.request, json
import math
from mininore import mininore


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


    mineral_in_ore_value = dict()
    for ore in oreminerals:
        mineral_in_ore_value[ore['Ore']] = 0
        for mineral in ore:
            if mineral != 'Ore' and mineral != 'typeid':
                mineral_in_ore_value[ore['Ore']] += ore[mineral]*reprocessing*minerals[mineral]
                
    ore_percentage_price_mineral = dict()
    for ore in oreminerals:
        ore_percentage_price_mineral[ore['Ore']] = dict()
        for mineral in ore:
            if mineral != 'Ore' and mineral != 'typeid' and ore[mineral] > 0:
                ore_percentage_price_mineral[ore['Ore']][mineral] = 100/mineral_in_ore_value[ore['Ore']] * (ore[mineral] * minerals[mineral]*reprocessing)

    
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
    
    returnlist = [oreminerals, ore_percentage_price_mineral]
    return returnlist
    

    


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
    
    

                
    material_needed_total = defaultdict(int)
    name = ""
    mats = list()
    production = dict()
    ships = dict()
    while name != 'no':
        name = input('What do you want to build? (type "no" to stop) ')
        if name == 'no':
            break
        blueprint_name = name + ' Blueprint'
        bp = [item for item in typeid if item['typename'] == blueprint_name]
        if not bp:
            print ('Sorry, my db doesnt know how to build this item')
        else:
            ships[bp[0]['typename']] = defaultdict(int)
            ships[bp[0]['typename']]['typeid'] = bp[0]['typeid']
            amount = 0
            amount = input('How many of them do you want to build? ')
            bp = bp[0]
            mats += [item for item in blueprints if bp['typeid'] == item['typeid']]
            try:
                int(amount)
            except ValueError:
                print ('This is not a valid number, please add a number of how many things you want to produce')
            amount = int(amount)
            ships[bp['typename']]['amount'] = amount
    if not ships:
        print ('you havent selected any ship at all')
        return
    
    for item in mats:
        for ship in ships:
            if ships[ship]['typeid'] == item['typeid']:
                material_needed_total[item['typename']] += ships[ship]['amount'] * item['quantity']

    for blueprint in blueprints:
        for ship in ships:
            if ships[ship]['typeid'] == blueprint['typeid']:
                production[blueprint['typename']] = dict()
                production[blueprint['typename']]['materialtypeid'] = blueprint['materialtypeid']
                production[blueprint['typename']]['quantity'] = 0


    for item in mats:
        for ship in ships:
            if ships[ship]['typeid'] == item['typeid']:
                production[item['typename']]['quantity'] += ships[ship]['amount'] * item['quantity']


    oremineralsdict = dict()
    for ore in oreminerals:
        oremineralsdict[ore['Ore']] = ore
    
    oredef = ore_calc()
    ore = oredef[0]
    ore_percentage_mineralprice = oredef[1]
    #print (ore_percentage_mineralprice)
    
    mineraldict = {'Tritanium': 34, 'Pyerite': 35, 'Mexallon': 36, 'Isogen': 37, 'Nocxium': 38, 'Zydrine': 39, 'Megacyte': 40, 'Morphite': 11399}
    

    oredict = dict()
    for mineral in mineraldict:
        ores = []
        ores = [item for item in ore if item[mineral] > 0 and ore_percentage_mineralprice[item['Ore']][mineral] > lower_limit[mineral].getpercentage()]
        ores = min(ores, key = lambda x:x[mineral])
        oredict[mineral] = ores
                                                            
                    
    buydict = dict()
    #print ('PRODUCTION \n %s' % production)
    #print ('material_needed_total \n %s' % material_needed_total)
  #  print ('OREMINERALSDICT \n %s' % oremineralsdict)
   # print ('OREDICT \n %s' % oredict)

    for i in material_needed_total:
        buydict[i] = dict()
        buydict[i]['Mineral'] = int() 
    for item in production:
        if production[item]['materialtypeid'] == mineraldict[item]:
            for i in material_needed_total:
                basicmineralinore = oremineralsdict[oredict[i]['Ore']][i]
                buydict[i]['Ore'] = oremineralsdict[oredict[i]['Ore']]['Ore']
                buydict[i]['Oreamount'] = math.ceil(production[i]['quantity']/(basicmineralinore * Reprocessing))
                material_needed_total[i] -= math.floor(buydict[item]['Oreamount'] * Reprocessing * oremineralsdict[oredict[item]['Ore']][i])                        
                buydict[i]['Mineral'] += math.ceil(buydict[item]['Oreamount'] * oremineralsdict[oredict[item]['Ore']][i] * Reprocessing)
    for item in production:
        buydict[item]['leftovers'] = buydict[item]['Mineral'] - production[item]['quantity']
    #print (material_needed_total)
    #print (buydict)
  
    count = 0
    while count < 10:
        for item in production:
            basicmineralinore = oremineralsdict[oredict[item]['Ore']][item]
            excess = buydict[item]['leftovers']
            if excess > basicmineralinore*Reprocessing or excess < 0:
                oreexcess = math.floor(excess/(basicmineralinore * Reprocessing)) 
                if oreexcess > buydict[item]['Oreamount']:
                    oreexcess = buydict[item]['Oreamount']
                    buydict[item]['Oreamount'] = 0
                else:
                    buydict[item]['Oreamount'] -= oreexcess
                for i in material_needed_total:
                    material_needed_total[i] += oreexcess * oremineralsdict[oredict[item]['Ore']][i]*Reprocessing
                    buydict[i]['Mineral'] -= oreexcess * oremineralsdict[oredict[item]['Ore']][i]*Reprocessing
        for item in production:
            buydict[item]['leftovers'] = buydict[item]['Mineral'] - production[item]['quantity']
        count += 1     
    #    print ('material_needed_total \n %s' % material_needed_total)
    #print ('BUYDICT \n %s' % buydict)
    #print ('PRODUCTION \n %s' % production)
    for item in production:
        if buydict[item]['Oreamount'] > 0:
            print ('%s %s' % (buydict[item]['Ore'], buydict[item]['Oreamount']))


prod()

