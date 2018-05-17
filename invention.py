import pymysql.cursors
import pymysql
from collections import defaultdict
import urllib.request, json
from class_ship_invention import invention
import math


# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             db='eve',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


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

# Sucht für eine Anzahl (count) an benötigten Decryptoren die günstigsten heraus
def InvPreis(count):
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             db='eve',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()

    result = "SELECT * FROM jita_prod WHERE typeid >= 34201 AND typeid <= 34208 AND buy = 0 AND location = 60003760"
    cursor.execute(result)
    result = cursor.fetchall()

    connection.close()
    count2 = count
    cost = 0
    bla = []
    while count > 0:
        minPrice = min(result, key = lambda x:x['price'])
        result[:] = [d for d in result if d.get('orderid') != minPrice['orderid']]
        count -= minPrice["volume"]
        cost += minPrice["volume"] * minPrice["price"]
        bla.append(minPrice)
    else:
        cost += minPrice['price'] * count
    avg = cost/count2
    print ("Der Durchschnittspreis für %s Decryptor ist %s ISK." % (count2, avg))

# single invention for calculating prices with outsourced jobs
def invention():
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             db='eve',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    result = "SELECT jita_prod.orderid, jita_prod.typeid, jita_prod.volume, jita_prod.price, typeid.typename FROM jita_prod,typeid \
    WHERE jita_prod.typeid = typeid.typeid AND jita_prod.buy = 0 AND jita_prod.location = 60003760 AND ((jita_prod.typeid >= 34201 AND jita_prod.typeid <= 34208) \
    OR jita_prod.typeid = 20117 OR jita_prod.typeid = 25887 OR jita_prod.typeid = 27025 OR jita_prod.typeid = 27059 OR jita_prod.typeid = 28843 OR jita_prod.typeid = 20171 \
    OR jita_prod.typeid = 20172 OR (jita_prod.typeid >= 20410 AND jita_prod.typeid <= 20425))"
    cursor.execute(result)
    result = cursor.fetchall()
    material = "SELECT * FROM datacore"
    cursor.execute(material)
    material = cursor.fetchall()
    connection.close()
    dummy = 0
    ship = 0
    ship_input = ""
     
    while dummy == 0:
        ship_input = input("What ship do you want to invent? ")
        ship = [item for item in material if item.get('Ship') == ship_input]
        ship = ship[0]
        if not ship:
            print ("Your Input is not valid, please write the name of a existing t2 Frigate, Destroyer, Cruiser, Battlecruiser or Battleship (e.g. Claw)")
        else:
            break

    datacore1 = [item for item in result if item.get('typeid') == ship['Datacore1']]
    datacore1 = min(datacore1, key = lambda x:x['price'])


    datacore2 = [item for item in result if item.get('typeid') == ship['Datacore2']]
    datacore2 = min(datacore2, key = lambda x:x['price'])

    
    Accelerant = [item for item in result if item.get('typeid') == 34201]
    Accelerant = min(Accelerant, key = lambda x:x['price'])
    Attainment = [item for item in result if item.get('typeid') == 34202]
    Attainment = min(Attainment, key = lambda x:x['price'])
    Augmentation = [item for item in result if item.get('typeid') == 34203]
    Augmentation = min(Augmentation, key = lambda x:x['price'])
    Opt_Attainment = [item for item in result if item.get('typeid') == 34207]
    Opt_Attainment = min(Opt_Attainment, key = lambda x:x['price'])
    Opt_Augmentation = [item for item in result if item.get('typeid') == 34208]
    Opt_Augmentation = min(Opt_Augmentation, key = lambda x:x['price'])
    Parity = [item for item in result if item.get('typeid') == 34204]
    Parity = min(Parity, key = lambda x:x['price'])
    Process = [item for item in result if item.get('typeid') == 34205]
    Process = min(Process, key = lambda x:x['price'])
    Symmetry = [item for item in result if item.get('typeid') == 34206]
    Symmetry = min(Symmetry, key = lambda x:x['price'])
    Accelerant['Chance'] = 20
    Attainment['Chance'] = 80
    Augmentation['Chance'] = -40
    Opt_Attainment['Chance'] = 90
    Opt_Augmentation['Chance'] = -10
    Parity['Chance'] = 50
    Process['Chance'] = 10
    Symmetry['Chance'] = 0
    # Hier später Runs = Runs + Basic, sobald man Basic Runs als input hat
    Accelerant['Runs'] = 2
    Attainment['Runs'] = 5
    Augmentation['Runs'] = 10
    Opt_Attainment['Runs'] = 3
    Opt_Augmentation['Runs'] = 8
    Parity['Runs'] = 4
    Process['Runs'] = 1
    Symmetry['Runs'] = 3
    Accelerant['ME'] = 4
    Attainment['ME'] = 3
    Augmentation['ME'] = 0
    Opt_Attainment['ME'] = 3
    Opt_Augmentation['ME'] = 4
    Parity['ME'] = 3
    Process['ME'] = 5
    Symmetry['ME'] = 3
    Decryptor = [Accelerant, Attainment, Augmentation, Opt_Attainment, Opt_Augmentation, Parity, Process, Symmetry]
    cost = None
    name = 'bla'
    success = 0
    G_inv = 0
    while True:
        G_inv = input("How much profit should the inventor get per slot per day? ")
        try:
            int(G_inv)
            break
        except ValueError:
            try:
                float(G_inv)
                break
            except ValueError:
                print("This is not a valid number")
    G_inv = int(G_inv)
    ME = 0
    # sobald skills verfügbar muss die 41 bei frigs, xx bei cruisern etc ausgetauscht werden gegen einen mit skills errechneten wert
    # AUCH die ME reduktion (250000 bei frigs) muss später getauscht werden gegen individuell errechnete beträge
    for i in Decryptor:
        tries = 24/7.433
        rate = inv[ship_input].getpercent()+11
        success = tries/100*(rate/100*(100+i['Chance']))
        i_COST = ((i['price'] + inv[ship_input].getdatacore()*datacore1['price'] + inv[ship_input].getdatacore()*datacore2['price'])/(rate/100*(100+i['Chance']))*100)+G_inv/success
        i_cost = (i_COST/i['Runs'])-i['ME']*inv[ship_input].getcost()
        if cost == None:
            cost = i_cost
            name = i['typename']
            runs = i['Runs']
            ME = i['ME']*inv[ship_input].getcost()
        elif cost > i_cost:
            cost = i_cost
            name = i['typename']
            runs = i['Runs']
            ME = i['ME']*inv[ship_input].getcost()

    print ("to get %s ISK profit per day, the inventor has to get %s ISK per blueprint" % (G_inv, i_COST))
    print ('the prefered Decryptor is the %s, your costs per run are at %s, your saving per run trough the ME are %s' % (name, i_COST/runs, ME))
    print (inv[ship_input].getdatacore())








def mass_invention():
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             db='eve',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    result = "SELECT jita_prod.orderid, jita_prod.typeid, jita_prod.volume, jita_prod.price, typeid.typename FROM jita_prod,typeid \
    WHERE jita_prod.typeid = typeid.typeid AND jita_prod.buy = 0 AND jita_prod.location = 60003760 AND ((jita_prod.typeid >= 34201 AND jita_prod.typeid <= 34208) \
    OR jita_prod.typeid = 20117 OR jita_prod.typeid = 25887 OR jita_prod.typeid = 27025 OR jita_prod.typeid = 27059 OR jita_prod.typeid = 28843 OR jita_prod.typeid = 20171 \
    OR jita_prod.typeid = 20172 OR (jita_prod.typeid >= 20410 AND jita_prod.typeid <= 20425))"
    cursor.execute(result)
    result = cursor.fetchall()
    material = "SELECT * FROM datacore"
    cursor.execute(material)
    material = cursor.fetchall()
    connection.close()
    ship = 0
    production_dic = defaultdict(int)
    ship_name = ""
    
    while ship_name != "no":
        ship_name = input("What ship do you want to invent? (type 'no' to stop) ")
        ship_amount = 0
        if ship_name == 'no':
            break
        if ship == 0:
            ship = [item for item in material if item.get('Ship') == ship_name]
            if not ship:
                print ("Your Input is not valid, please write the name of a existing t2 Frigate, Destroyer, Cruiser, Battlecruiser or Battleship (e.g. Claw)")
            else:
                while True:
                    ship_amount = input("how many of them do you want to invent? ")
                    try:
                        int(ship_amount)
                        break
                    except ValueError:
                        print("This is not a valid number, please add just a number of ship bpcs you want to invent")
                ship_amount = int(ship_amount)
                production_dic[ship_name] = ship_amount
        else:
            prove = [item for item in material if item.get('Ship') == ship_name]
            if not prove:
                print ("Your Input is not valid, please write the name of a existing t2 Frigate, Destroyer, Cruiser, Battlecruiser or Battleship (e.g. Claw)")
            else:
                while True:
                    ship_amount = input("how many of them do you want to invent? ")
                    try:
                        int(ship_amount)
                        break
                    except ValueError:
                        print ("This is not a valid number, please add just a number of ship bpcs you want to invent")
                ship_amount = int(ship_amount)
                production_dic[ship_name] = ship_amount
                prove = prove[0]
                ship.append(prove)

    print (ship)
    Datacore1 = []
    Datacore2 = []
    count = 0
    for item in ship:
        datacore1 = [item for item in result if item.get('typeid') == ship[count]['Datacore1']]
        datacore1 = min(datacore1, key = lambda x:x['price'])
        Datacore1.append(datacore1)
        datacore2 = [item for item in result if item.get('typeid') == ship[count]['Datacore2']]
        datacore2 = min(datacore2, key = lambda x:x['price'])
        Datacore2.append(datacore2)
        count += 1
        
    Accelerant = [item for item in result if item.get('typeid') == 34201]
    Accelerant = min(Accelerant, key = lambda x:x['price'])
    Attainment = [item for item in result if item.get('typeid') == 34202]
    Attainment = min(Attainment, key = lambda x:x['price'])
    Augmentation = [item for item in result if item.get('typeid') == 34203]
    Augmentation = min(Augmentation, key = lambda x:x['price'])
    Opt_Attainment = [item for item in result if item.get('typeid') == 34207]
    Opt_Attainment = min(Opt_Attainment, key = lambda x:x['price'])
    Opt_Augmentation = [item for item in result if item.get('typeid') == 34208]
    Opt_Augmentation = min(Opt_Augmentation, key = lambda x:x['price'])
    Parity = [item for item in result if item.get('typeid') == 34204]
    Parity = min(Parity, key = lambda x:x['price'])
    Process = [item for item in result if item.get('typeid') == 34205]
    Process = min(Process, key = lambda x:x['price'])
    Symmetry = [item for item in result if item.get('typeid') == 34206]
    Symmetry = min(Symmetry, key = lambda x:x['price'])
    decryptor_dic ={'Accelerant Decryptor' : {'Chance': 20, 'Runs': 2, 'ME': 4}, 'Attainment Decryptor' : {'Chance': 80, 'Runs': 5, 'ME': 3} ,'Augmentation Decryptor' :{'Chance': -40, 'Runs': 10, 'ME': 0},\
                     'Optimized Attainment Decryptor' : {'Chance': 90, 'Runs': 3, 'ME': 3}, 'Optimized Augmentation Decryptor' : {'Chance': -10, 'Runs': 8, 'ME': 4}, 'Parity Decryptor' : {'Chance': 50, 'Runs': 4, 'ME': 3},\
                     'Process Decryptor' : {'Chance': 10, 'Runs': 1, 'ME': 5}, 'Symmetry Decryptor' : {'Chance': 0, 'Runs': 3, 'ME': 3}}

    Decryptor = [Accelerant, Attainment, Augmentation, Opt_Attainment, Opt_Augmentation, Parity, Process, Symmetry]
    name = 'bla'
    success = 0
    G_inv = 0
    outsourcing = input("do you want your invention job done by someone else? ")
    outsourcing.lower()
    if outsourcing == "yes" or outsourcing == "y":
        while True:
            G_inv = input("How much profit should the inventor get per slot per day? ")
            try:
                int(G_inv)
                break
            except ValueError:
                try:
                    float(G_inv)
                    break
                except ValueError:
                    print("This is not a valid number")
    G_inv = int(G_inv)
    ME = 0
    count = 0
    buy = 0
    datacore_dic = defaultdict(int)
    ship_decryptor_dic = {}
    cost = None
    Cost = None
    Success = None
    Cost_dic = {}
    Success_dic = {}
    Runs_dic = {}
    for x in ship:
        for i in Decryptor:
            tries = 24/7.433
            rate = inv[x['Ship']].getpercent()+11
            success = tries/100*(rate/100*(100+decryptor_dic[i['typename']]['Chance']))
            i_COST = ((i['price'] + inv[x['Ship']].getdatacore()*datacore1['price'] + inv[x['Ship']].getdatacore()*datacore2['price'])/(rate/100*(100+decryptor_dic[i['typename']]['Chance']))*100)+(G_inv/success)
            i_cost = (i_COST/decryptor_dic[i['typename']]['Runs'])-decryptor_dic[i['typename']]['ME']*inv[x['Ship']].getcost()
            if cost == None:
                Success = success
                Cost = i_COST
                cost = i_cost
                name = i['typename']
                runs = decryptor_dic[i['typename']]['Runs']
                ME = decryptor_dic[i['typename']]['ME']*inv[x['Ship']].getcost()
                buy = inv[x['Ship']].getdatacore()
                buy = int(buy)
            elif cost > i_cost:
                Success = success
                Cost = i_COST
                cost = i_cost
                name = i['typename']
                runs = decryptor_dic[i['typename']]['Runs']
                ME = decryptor_dic[i['typename']]['ME']*inv[x['Ship']].getcost()
                buy = inv[x['Ship']].getdatacore()
                buy = int(buy)
        Cost_dic[x['Ship']] = Cost
        Success_dic[x['Ship']] = Success/100
        Runs_dic[x['Ship']] = runs
        datacore_dic[Datacore1[count]['typename']] += buy * production_dic[x['Ship']]
        datacore_dic[Datacore2[count]['typename']] += buy * production_dic[x['Ship']]
        datacore_dic[name] += production_dic[x['Ship']]
        ship_decryptor_dic[x['Ship']] = name 
        count += 1
        

    for x in datacore_dic:
        print('%s %s' % (datacore_dic[x], x))
    for x in ship_decryptor_dic:
        print('for invention of %s please use %s' % (x, ship_decryptor_dic[x]))
    for C in Cost_dic:
        print ('invention cost per %s BPC: %s' % (C, Cost_dic[C]))
        print ('invention cost per %s run: %s' % (C, Cost_dic[C]/Runs_dic[C]))