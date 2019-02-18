import pandas
import mail_client

"""
this program joins the grid.csv and players.csv files
to create a report of which players have not paid for all thier boxes at present date.

the comissioner (me) must update the amount_paid field for each user with player.csv
once payment is received.  From this updated file the program counts all the boxes
select for a specific user_id and cross-references that count with how much has been 
pasd versus the total cost.

an email is sent out to all that have not fully paid + the comissioner.
"""


PRICE_PER_BOX = 100



grid_df = pandas.read_csv('grid.csv')
players_df = pandas.read_csv('players.csv')

## count number of boxes each player holds
box_count = grid_df.groupby('user_id').count()
players_df = players_df.set_index('user_id')

## link player info with box coun
ledger = box_count.join(players_df,on='user_id')

## 'box_count' after the grouby holds the total boxes held by a given user_id
ledger['cost'] = ledger['box_number'] * PRICE_PER_BOX
ledger['amount_owed'] = ledger['cost'] - ledger['amount_paid']

ledger = ledger.reset_index()
cols = 'name user_id email box_number amount_paid amount_owed'.split()
ledger = ledger[cols]
ledger = ledger.rename(columns={'box_number':'boxes'})

ledger.to_csv('ledger.csv',index=False)

accounts = ledger[(ledger.amount_owed > 0) & (~ledger.user_id.isin(['nan','NaN','None','none']))]

row_template = """
<tr>
  <td width="300" height="30" style="font-family: Lucida Sans; font-size: 18px; color: #000000;">
      <strong>{name}</strong>
  </td>
  <td width="300" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
       {user_id}
  </td>
  <td width="500" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
       {email}
  </td>
  <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
       {boxes}
  </td>
  <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
       {amount_paid}
  </td>
  <td width="100" height="30" style="font-family:  Courier New; font-size: 16px; color: #000000;">
       {amount_owed}
  </td>
</tr>
"""

print(accounts)

rows = []
for _, item in accounts.iterrows():
	formats = dict(	name=item['name'],
					user_id=item['user_id'],
					email=item['email'],
					boxes=item['boxes'],
					amount_paid=item['amount_paid'],
					amount_owed=item['amount_owed'])

	rows.append(row_template.format(**formats))


subject = 'MegaBox March Madness Pool: Payments Outstanding' 
player_table = """
<html>
<head>
</head>
<body>
<br>
<span style="font-family: Lucida Sans; font-size:18px; color:#000000;"><strong>PAYMENTS OUTSTANDING</strong></span> 
<br> <br>
<table width="1300" border="1" cellpadding="6" cellspacing="0">
<tr>
  <td width="300" height="30" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
      <strong>Player</strong>
  </td>
  <td width="200" height="30" style="font-family:  Lucida Sans; font-size: 16px; color: #000000;">
       <strong>User_Id</strong>
  </td>
  <td width="500" height="30" style="font-family:  Lucida Sans; font-size: 16px; color: #000000;">
       <strong>Email</strong>
  </td>
  <td width="100" height="30" style="font-family:  Lucida Sans; font-size: 16px; color: #000000;">
       <strong>Boxes</strong>
  </td>
  <td width="100" height="30" style="font-family:  Lucida Sans; font-size: 16px; color: #000000;">
       <strong>Amt_Paid</strong>
  </td>
  <td width="100" height="30" style="font-family:  Lucida Sans; font-size: 16px; color: #000000;">
       <strong>Amt_Owed</strong>
  </td>
</tr>
"""
player_table += " ".join(rows) + """</table> </body> </html>"""

mailing_list = accounts['email'].tolist()
mailing_list.append('megaboxhoops@gmail.com')
#mailing_list = ['xjcarter@gmail.com','megaboxhoops@gmail.com']
for address in mailing_list:
	print('Sending to', address)
	mail_client.mail(address,subject,text='',html=player_table)




