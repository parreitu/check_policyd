#!/usr/bin/python
# -*- coding: utf-8 -*-

#################################################################################################

import sqlite3
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import requests


sqlitedb = '/opt/zimbra/data/cbpolicyd/db/cbpolicyd.sqlitedb' # DB path
alert_percent_limit = '75' #  Minimum percentage for alert sending
how_many_minutes_to_check = 10 # Alerts generated in the last few minutes are filtered based on this variable
sender = 'admin@mydomain.eus' # Email sender
receivers = ['user01@mydomain.eus', 'user02@mydomain.eus'] # Email receivers list
smtp_server = 'mailserver.mydomain.eus' # SMTP Server 
send_email = True

send_telegram = True
telegram_bottoken = "mytelegrambottoken"
telegram_chatid = "mychatid"



def send_alerts():

    body = " ALERTS SINCE: " + str(datetime.fromtimestamp(check_since))
    for key, value in alerts_dict.items():
        body = body + '\n\n' + '===============' + key   + '====================' + "\n"
        for item in value:
            body = body + str(item) + "\n"

    if send_email:

        msg = MIMEText(body,'plain','utf-8')
        msg['Subject'] = Header('PolicyD alerts !', 'utf-8')
        msg['From'] = sender
        msg['To'] = ", ".join(receivers)

        try:
            smtpObj = smtplib.SMTP(smtp_server)
            smtpObj.set_debuglevel(1)
            smtpObj.sendmail(sender, receivers, msg.as_string())
            # print ("Successfully sent email")
        #except :
            # print ("Error: unable to send email")
        finally:
            smtpObj.quit()

    if send_telegram:
        requests.get("https://api.telegram.org/bot"+telegram_bottoken+"/sendMessage?chat_id=" + telegram_chatid + "&text=" + body)



now = datetime.now() # current date and time
now_unixepoch = now.strftime('%s')
check_since = int(now_unixepoch) - ( how_many_minutes_to_check * 60 )

con = sqlite3.connect(sqlitedb)
cur = con.cursor()
cur.execute('SELECT QuotasLimitsID, TrackKey, LastUpdate, Counter from quotas_tracking WHERE counter >' + alert_percent_limit + ' and LastUpdate > ' + str(check_since))

quotas_tracking = []
for i in cur.fetchall():
#    print(i)
    email = i[1].split(":", 1)[1]
    quotas_tracking.append([i[0], email, str(datetime.fromtimestamp(i[2])), i[3]])

alerts_list = []
for i in quotas_tracking:
    cur.execute('SELECT Q.name FROM  quotas Q JOIN quotas_limits QL ON  Q.ID = QL.QuotasID  WHERE QL.ID = ' + str(i[0]))
    group_name = cur.fetchone()[0] # quota group name
    percent = "%"+str(round(i[3],2)) # quota limit percent
    alerts_list.append([ i[1], i[2], percent, group_name ] )

alerts_dict = {} 

for item in alerts_list:
    # print(item)
    user_email = str(item[0])
    if not user_email in alerts_dict:
        alerts_dict[user_email] = [] # add user email as dict key. It's value is a empty list

    previous_alerts  = alerts_dict[user_email] # Get user's previous alerts list
    previous_alerts.append(item) # append the new alert to user's alert list

#for key, value in alerts_dict.items():
#    print('===============' + key   + '====================')
#    for item in value:
#        print(item)

if alerts_dict: 
    send_alerts() # alerts_dict is not empty
