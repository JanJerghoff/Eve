class mininore(object):
    def __init__(self, percentage):
        self.percentage = percentage
    def getpercentage(self):
        return self.percentage

lower_limit = dict()
lower_limit['Tritanium'] = mininore(50)
lower_limit['Pyerite'] = mininore(9)
lower_limit['Mexallon'] = mininore(40)
lower_limit['Isogen'] = mininore(10)
lower_limit['Nocxium'] = mininore(30)
lower_limit['Zydrine'] = mininore(15)
lower_limit['Megacyte'] = mininore(10)
lower_limit['Morphite'] = mininore(5)