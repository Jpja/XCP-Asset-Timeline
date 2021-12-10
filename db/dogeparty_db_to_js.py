#modifications from counterparty:
# db_file
# outpute file dp_history.js (near the end)

db_file = 'dogeparty.db' #latest Dogeparty DB

import os
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

import sqlite3
con = sqlite3.connect(db_file)
cur = con.cursor()


#Block timestamps  
ts = [None] * 8000000
for row in cur.execute('SELECT block_index, block_time FROM blocks;'):
  ts[row[0]] = row[1]
print('Block timestamps OK')


#Counterparty transaction are called messages.
#This script collects every message from tables issuances, destructions, broadcasts'.
#Messages are uniqely identified by tx_id & msg_id'
#These are incremental so it's easy to sort messages of various kinds.
# msg_id is implicitly 0 except for issuances it's specified in a table column. 
# And almost all issuances have msg_id=0, it's only in case of sweep the issuances are given incremental msg_id's.

msg = []
  #0 tx_id
  #1 msg_id
  #2 timestamp
  #3 msg type
    #0 = broadcast
    #1 = new asset (initial issuance)
	#2 = subsequent issuance
	#3 = subsequent issuance with lock
	#4 = destruction
  #4 source address (0 if irrelevant)
  #5 asset (0 if irrelevant)
  #6+ specifics for each msg type  

  
#Broadcasts
count = 0
for row in cur.execute('SELECT tx_index, block_index, source, text FROM broadcasts WHERE text IS NOT NULL AND text != \"\";'): 
#note: don't check if status='valid' bcs we care about texts, not betting related info
  msg.append([row[0], 0, ts[row[1]], 0, row[2], 0, row[3]])
  count += 1
print('Broadcasts: ' + str(count))


#Issuances
'''
The issuance table is difficult to work with.
Several issuances can happen in one transcation; therefore 2nd index 'msg_id'.
It is not specified if an issuance is the initial one. Crosschecking with assets table is not sufficient because table only shows block height.
Change of description is not specified either.
Only change to supply, transfer and lock are explicitly shown.
In some cases there is valid issuance but no change, i.e. can ignore. 
In a few cases both supply and description changed at once.

Lets make a list with changes only and leave 0 for unchanged values 
'''
issued = {}
descr = {}
div_status = {}
count_new = 0
count_empty = 0
count_subseq = 0
#for row in cur.execute('SELECT tx_index, block_index, asset, quantity, issuer, transfer, description, locked, divisible FROM issuances WHERE status = \"valid\";'):
for row in cur.execute('SELECT tx_index, msg_index, block_index, asset, quantity, divisible, source, issuer, transfer, description, locked, asset_longname  FROM issuances WHERE status = \"valid\";'):
  tx_index = row[0]
  msg_index = row[1]
  block_ts = ts[row[2]]
  asset = row[3]
  quantity = str(row[4])
  divisible = row[5]
  source = row[6]
  issuer = row[7]
  transfer = row[8]
  description = row[9]
  locked = row[10]
  asset_longname = row[11]

  if asset not in issued: #new asset
    msg.append([tx_index, msg_index, block_ts, 1, issuer, asset, quantity, divisible, description])
    count_new += 1
    issued[asset] = True
    descr[asset] = description
    div_status[asset] = divisible
	#sanity check; source and issuer must be the same?
    if source != issuer:
      print ("Sanity check failed!" + str(tx_index) + ' ' + asset + ' source != issuer')
	#sanity check; locked on issuance?
    if locked == 1:
      print ("Sanity check failed!" + str(tx_index) + ' ' + asset + ' locked on issuance')
    continue
	
  #sanity check; divisibility changed? (May happen in future upgrade)
  if divisible != div_status[asset]:
    print ("Sanity check failed!" + str(tx_index) + ' ' + asset + ' divisibility changed')

  type = 2	
  cond = 0
  quan = False #increase supply
  if quantity != '0':
    cond += 1
    quan = True
  else:
    quantity = 0
  
  if transfer == 1: #transfer
    cond += 1
  else:
    issuer = 0
   
  if description != descr[asset]: #change description
    cond += 1
    descr[asset] = description
  else:
    description = 0

  if locked == 1: #locking tx
    cond += 1
    type = 3

  if cond == 0:
    #print(str(tx_index) + ' ' + asset + ' empty issuance, ignore')
    count_empty += 1
    continue

  msg.append([tx_index, msg_index, block_ts, type, issuer, asset, quantity, divisible, description])
  count_subseq += 1
  
print('Issuances:       ' + str(count_new + count_empty + count_subseq))
print('  New assets:    ' + str(count_new))
print('  Subseq. issu.: ' + str(count_subseq))
print('  Empty, ignore: ' + str(count_empty))


#Destructions
count = 0
for row in cur.execute('SELECT tx_index, block_index, source, asset, quantity, tag FROM destructions WHERE status = \"valid\";'):
  tag = row[5].decode('UTF-8')
  msg.append([row[0], 0, ts[row[1]], 4, row[2], row[3], row[4], tag])
  count += 1
print('Destructions: ' + str(count))


#Replace numeric with subasset (asset_longname) where applicable
subassets = {}
for row in cur.execute('SELECT asset_name, asset_longname FROM assets WHERE asset_longname IS NOT NULL;'):
  subassets[row[0]] = row[1]
for i in range(len(msg)):
  if msg[i][3] == 0: #broadcast
    continue
  if msg[i][5] in subassets: #asset is a subasset
    msg[i][5] = subassets[msg[i][5]]
print('Subassets OK')


#Sort  	
msg.sort()  
print('Message list sorted')


#Remove msg_index to save space
for i in range(len(msg)):
  msg[i] = [x for j,x in enumerate(msg[i]) if j!=1]

  
#Write .js file containing entire msg history
out = "//Table with relevant info for Counterparty asset history search\n\nlet cp_history = " + str(msg) + ";"
file = open('dp_history.js', 'w', encoding="utf-8")
file.write(out)
file.close()
print('Output file written')

con.close()