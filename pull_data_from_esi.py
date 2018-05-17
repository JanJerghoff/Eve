import pymysql.cursors
import pymysql
import urllib.request, json


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
