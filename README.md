# pscovin
Python code to find a free vaccine slots @ the given Pincodes based on cowin APIs. 

## **Assumption:** 
python 3* installed, internet connection

## **Required packages**
beutifulsoup4, json, python-telegram-bot, telegram 

## **Step 1:**  Set up Telegram APIs and BOT

- Install the required packages in python (pip install ...)
- Get yourself a telegram account. 
- Get a telegram API_Token
- Set up the first bot in telegram. (This bot will actually post the vaccine update in the group)
- Create a group in telegram. (Eg Vaccine @Pincode). Get this group id (Negative number)
- Get your telegram id. (Positive number)
- When done: Input your above data and **run** the testTelegram.py. If the test message is send you are ready.
> For all the above steps you have to google around. Some how not straight forward.

## **Step 2**:  Run the pscovin code

Now update all User Inputs in the pscovin.py.

my_token, my_id, chat_id, pin_lst, dose (read the comments in the code for details.

## **Step 3:**  Run the code...   

Feel free to drop me a question! Though i assure google will provide a better answer!

I had lot of fun but the documentation was the most boring...  

## Update:

Updated the code with following changes:

- 1 message per day per center. (Reduce spaming)
- Cowin link in the message to directly go to register
- Log updates for data analytics
- Possibility to have night time sleep
