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
from datetime import date
import os
import time
import telegram
from urllib.parse import quote
import pandas as pd
df_previous=pd.DataFrame()

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
threshold=1

#
#  Sleep time (s) after HTTP Exception. (Server error/server down).
#
sleepAfterError=30

#
#  Sleep time (s) after vaccine slots found. (Server error/server down).
#  
sleepAfterSuccess=30

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
#
# Human sleep time / no disturbance time
#
on_time  = datetime.time(22,59)
off_time = datetime.time(6,59)
# ==============================
# ****   End  user input    ****
# ==============================

#
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
def ret_df(i,j,chk_name,dose_no,ct):
    ''' Formated return for message'''
    return pd.DataFrame({
                        "Name":[i['name']],
                        "Pin": [i['pincode']],
                        "Date":[j['date']],
                        "Age": [j['min_age_limit']],
                        "Vaccine":[j['vaccine']],
                        "Qnt":    [j[chk_name]],
                        "Dose":    dose_no,
                        "Msg Send Flg":    1,
                        "Time Tag": ct
                        })

#
def listToString(s):    
    ''' Return list as a string '''
    str1 = "\n" 
    return (str1.join(s))

#
def dfToString(df):    
    ''' Return df as a string '''
    str1=""
    for idx, row in df.iterrows():
        str1=str1+row['Name']+"("+str(row['Pin'])+"):  Date: "+row['Date']+ " for age "+ str(row['Age'])+"+ "+row['Vaccine']+"="+str(row['Qnt'])+" (Dose "+str(row['Dose'])      +")\n\n"
    return (str1)

#
def dfToStringPrt(df):    
    ''' Return df as a string '''
    str1=""
    for idx, row in df.iterrows():
        str1=str1+row['Name']+"("+str(row['Pin'])+"):  Date: "+row['Date']+ " for age "+ str(row['Age'])+"+ "+row['Vaccine']+"="+str(row['Qnt'])+" (Dose "+str(row['Dose'])      +")"
    return (str1)

#
def listToString_withtimeTag(lst,timeTag=""):    
    ''' Return a list as a string with time tag '''
    if (len(lst))==0:
        return timeTag.strftime("%Y-%m-%d %H:%M:%S")
    else:
        str1 = ""
        for i in lst:
            if str1=="": 
                str1=timeTag.strftime("%Y-%m-%d %H:%M:%S ")+i
            else:
                str1=str1+"\n"+timeTag.strftime("%Y-%m-%d %H:%M:%S ")+i
        return str1

def dfToString_withtimeTag(df,timeTag=""):    
    ''' Return a list as a string with time tag '''
    if (len(df))==0:
        return timeTag.strftime("%Y-%m-%d %H:%M:%S")
    else:
        str1 = ""
        for i in range(len(df)):
            if str1=="": 
                str1=timeTag.strftime("%Y-%m-%d %H:%M:%S ")+dfToStringPrt(df.iloc[i:i+1])
            else:
                str1=str1+"\n"+timeTag.strftime("%Y-%m-%d %H:%M:%S ")+dfToStringPrt(df.iloc[i:i+1])
        return str1

#
def get_free_center(cn_lst,dose_no,ct):
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
    for_df = pd.DataFrame()
    #
    for i in cn_lst:
        for j in i['sessions']:
            if j[chk_name]>threshold:
              ret_lst.append(ret_str(i,j,chk_name,dose_no))
              for_df = pd.concat([for_df, ret_df(i,j,chk_name,dose_no,ct)])
              ret_slot_found_flag=True
            else:
              pass
    return ret_slot_found_flag,ret_lst,for_df           

#
def string_append_to_file(fname,tmp_str,endLine="",startLine=""):
    ''' Append string to file. 
        Use endLine="\n" for new line char at the end.   
    '''
    outload = open(fname, "a")
    outload.write(startLine+tmp_str+endLine)
    outload.close()

#
def clean_old_entries_in_df():
    """ Clean the df for old entries (date) """
    global df_previous
    if df_previous.size!=0:
        indexNames = df_previous[df_previous['Time Tag'].dt.date<date.today()].index
        df_previous.drop(indexNames, inplace=True)
        df_previous.reset_index(drop=True, inplace=True)

#
def send_new_slots(df):
    """Check status with last printed status"""
    global df_previous
    # First time...
    if df_previous.size == 0:
        for i in range(len(df)):
            sendTelegramMsg(dfToString(df.iloc[i:i+1])+"Register:\nhttps://selfregistration.cowin.gov.in",chat_id)
            df.at[i,'Msg Send Flg']=0
        df_previous=df.copy()
    else:
        for i in range(len(df)):
            old_entry_flag=False
            for j in range(len(df_previous)):
                if (df_previous.at[j,'Name'] == df.at[i,'Name']) and \
                   (df_previous.at[j,'Pin'] == df.at[i,'Pin']) and \
                   (df_previous.at[j,'Vaccine'] == df.at[i,'Vaccine']) and \
                   (df_previous.at[j,'Dose'] == df.at[i,'Dose']) and \
                   (df_previous.at[j,'Age'] == df.at[i,'Age']) and \
                   (df_previous.at[j,'Date'] == df.at[i,'Date']) :
                    # Found a previous match 
                    old_entry_flag=True
            if old_entry_flag==False:
                sendTelegramMsg(dfToString(df.iloc[i:i+1])+"Register:\nhttps://selfregistration.cowin.gov.in",chat_id)
                df_previous=pd.concat([df_previous,df.iloc[i:i+1]]).reset_index(drop=True)
                df.at[i,'Msg Send Flg']=0
                
#
def main():
    """Start the bot."""
    sendTelegramMsg("Starting bot...",my_id)
    while True:
        ct = datetime.datetime.now()
        os_name=os.name
        df=pd.DataFrame()
        clean_old_entries_in_df()
        master_flag=False
        for pin in pin_lst:
            site_json=get_json(pin,ct)
            slot_found_flag,avl_lst,df_tmp=get_free_center(site_json,dose,ct)
            print("Pincode checking: ",pin)
            print(df_tmp)
            if df_tmp.size!=0 and slot_found_flag==True:
                df=pd.concat([df_tmp,df]).reset_index(drop=True)
                master_flag=True     

        if master_flag==True:
            send_new_slots(df)
            string_append_to_file(fName,dfToString_withtimeTag(df,ct),endLine="\n")
            print("Sleeping for ",sleepAfterSuccess," seconds.")
            time.sleep(sleepAfterSuccess)
        else:
            print("Sleeping for ",recheckIn," seconds.")
            time.sleep(recheckIn)

#
if __name__ == '__main__':
    main()

