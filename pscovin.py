"""
Simple Python code to send a telegram message to a group as soon as vaccine slot is available.


Usage:
For ease of use the code has be in one file. 
Step 1: Update user inputs:
Step 2: Run the code.  Note: its an infinite while loop. You have to kill the prog to stop it.
"""

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import json
import datetime
import os
import time
import telegram
from urllib.parse import quote

# ==============================
# ****  Start user input    ****
# ==============================
#
# Enter Telegram BOT token, chat id and self id.
# Below are dummy token and ids. 
#
my_token = '1234567890:asdfJKL;qweruiopKYHekw98339393'
chat_id=-1234567890
my_id=0987654321

# Enter the pin numbers you want to check 
# Eg. pin_lst=[ 560001, 560002]
#
pin_lst = [560001, 560002]

#
# Enter 1 for dose-1, 2 for dose-2 and 0 for both.
#
dose=1

#
#  Vaccine threshold number. Send a Telegram message 
#  when available vaccine is greater than threshold number
#  Recommendation is 5 - to reduce spamming.
#
threshold=5

#
#  Sleep time (s) after HTTP Exception. (Server error/server down).
#
sleepAfterError=180

#
#  Sleep time (s) after vaccine slots found. (Server error/server down).
#  
sleepAfterSuccess=600

#
# Recheck in seconds
# Recommended 30sec
#
recheckIn=30

#
#  Log file name...
#
fName="data.txt"
#
# ==============================
# ****   End  user input    ****
# ==============================

def sendTelegramMsg(message, chat_id, token=my_token):
    '''
    Send a telegram messsage.
    chat_id must be a number!
    '''
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=message)

#
def get_json(pin,ct):
    ''' Get data from url, strip and return a list of vaccine centers'''
    dtTag = ct.strftime("%d-%m-%Y")
    url_str = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode='+str(pin)+'&date='+dtTag
    try:
        req = Request(url_str, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        soup = BeautifulSoup(html,'html.parser')
        # Removed leading centers...
        site_json=json.loads(soup.text.replace('{\"centers\":','').rstrip('}'))
    except Exception:
        site_json=[]
        string_append_to_file(fName,listToString_withtimeTag(["Error fetching api from cowin"],ct),endLine=" "+str(pin)+" \n")
        sendTelegramMsg(listToString_withtimeTag(["Error fetching api from cowin"],ct),my_id)
        # 
        time.sleep(sleepAfterError)

    return site_json

#
def prt_str(i,j,chk_name,dose_no):
    ''' Formated print for screen display'''
    print(i['name'],"(",i['pincode'],"):  Date:  ",j['date'],"for age",j['min_age_limit'],"+",j['vaccine'],"=",j[chk_name]," (Dose "+str(dose_no)+ ")")

#
def ret_str(i,j,chk_name,dose_no):
    ''' Formated return for message'''
    return (i['name']+"("+str(i['pincode'])+"):  Date:  "+j['date']+"for age"+str(j['min_age_limit'])+"+"+j['vaccine']+"="+str(j[chk_name])+" (Dose "+str(dose_no)+ ")")

#
def listToString(s):    
    ''' Return the list as a string '''
    str1 = "\n" 
    return (str1.join(s))

#
def listToString_withtimeTag(s,timeTag=""):    
    ''' Return a list as a string with time tag '''
    if (len(s))==0:
        return timeTag.strftime("%Y-%m-%d %H:%M:%S")
    else:
        str1 = "\n" + timeTag.strftime("%Y-%m-%d %H:%M:%S")
        return (str1.join(s))

#
def get_free_center(cn_lst,dose_no):
    ''' Returns data of the center with free slots'''
    if dose_no==0:
        chk_name='available_capacity'
    elif dose_no==1:
        chk_name='available_capacity_dose1'
    elif dose_no==2:
        chk_name='available_capacity_dose2'
    #    
    ret_slot_found_flag=False
    ret_lst=[]
    #
    for i in cn_lst:
        for j in i['sessions']:
            if j[chk_name]>threshold:
              ret_lst.append(ret_str(i,j,chk_name,dose_no))
              ret_slot_found_flag=True
            else:
              prt_str(i,j,chk_name,dose_no)
    return ret_slot_found_flag,ret_lst           

#
def string_append_to_file(fname,tmp_str,endLine="",startLine=""):
    ''' Append string to file. 
        Use endLine="\n" for new line char at the end.   
    '''
    outload = open(fname, "a")
    outload.write(startLine+tmp_str+endLine)
    outload.close()

def main():
    """Start the bot"""
    sendTelegramMsg("Starting bot...",my_id)
    while True:
        """ Careful Infinite while loop """
        ct = datetime.datetime.now()
        os_name=os.name
        print("*** Checking  ***   :   ", ct, "*****************")
        master_flag=False
        for pin in pin_lst:
            site_json=get_json(pin,ct)
            slot_found_flag,avl_lst=get_free_center(site_json,dose)
            if slot_found_flag==True:
                master_flag=True                
                sendTelegramMsg(listToString(avl_lst),chat_id)
                string_append_to_file(fName,listToString_withtimeTag(avl_lst,ct),endLine="\n")

        print("*** Done checking ******************")
        if master_flag==True:
            print("Sleeping for ",sleepAfterSuccess," seconds.")
            time.sleep(sleepAfterSuccess)
        else:
            print("Sleeping for ",recheckIn," seconds.")
            time.sleep(recheckIn)

if __name__ == '__main__':
    # - Main code
    main()

