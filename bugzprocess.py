import shelve
import datetime

bugz = shelve.open('bugzdb.pydb')

for entry in bugz['1155']['Comment'].keys():
    print bugz['1155']['Comment'][entry]['who']
    
for bugkey in bugz.keys():
    if bugkey != 'lastupdated':
        for entry in bugz[bugkey]['Comment'].keys():
            if bugz[bugkey]['Comment'][entry]['who'] == 'tim.browning@renishaw.com':
                print bugz[bugkey]['Comment'][entry]['thetext']