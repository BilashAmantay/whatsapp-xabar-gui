from csv import reader
import os, time, csv
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('./logs/app.log')


# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)



WebDriverWaitTime = 10

def loadCSV2list(csv_filepath):
    contact_list =[]
    with open(csv_filepath,"r") as f:
        csv_reader = reader(f)
        for row in csv_reader:
            if row[0] not in contact_list:
                contact_list.append(row[0])
    return contact_list

def loadTxt2list(txt_filepath):
    contact_list =[]
    with open(txt_filepath,"r") as f:
        for line in f: 
            line = line.strip() 
            contact_list.append(line) 
    return contact_list



def construct_phone_number(contact_number):
    newname = '+'
    for n in range(len(contact_number)):
        if n==0:
            newname+=contact_number[0]
            newname+=' '
        elif n==4:
            newname+=' '+contact_number[n]
        elif n==7:
            newname+=' '+contact_number[n]
        else:
            newname+=contact_number[n]
    # print('New format', newname)
    return newname

def checkSentBefore(msg):
    return False #### <------------ уақытша 
    try:
        a = driver.find_elements_by_xpath("//*[contains(text(), '{}')]".format(msg))
        return len(a)>1
    except:
        logger.info("Didn't find msg had been send before")
        return False


def SendMessage(driver,PhoneNumber,msg):
    c=0
    Found_number = False
    c+=1
    logger.info('searching for {}, {}'.format(PhoneNumber,c))

    contact_url = "https://web.whatsapp.com/send?phone={}&text&source&data&app_absent".format(PhoneNumber)
    
    frindly_number=construct_phone_number(PhoneNumber)
    BeforeDriverGet = time.time()
    driver.get(contact_url)
    time.sleep(10)
    AfterDriverGet = time.time()

    try:
        BeforeWebDriverWait = time.time()
        WebDriverWait(driver, WebDriverWaitTime).until(EC.text_to_be_present_in_element((By.CLASS_PhoneNumber, "_2KQyF"), frindly_number))
        AfterWebDriverWait = time.time()
        logger.info('AfterWebDriverWait - BeforeWebDriverWait: {}'.format(AfterWebDriverWait - BeforeWebDriverWait))
        Found_number = True
        logger.info('Done WebDriverWait for: {}'.format(PhoneNumber))

    except:
        logger.info('Executed more than WebDriver default wait time: {}'.format(WebDriverWaitTime))
        print('Number not found, maybe in the contact')
        Found_number = True #<<<<<<<<<<--- temp solution 2021-05-15

    WebDriverWaitTrySection = time.time()
    logger.info('For Driver.get : {}'.format(AfterDriverGet - BeforeDriverGet))
    logger.info('WebDriverWaitTrySection - AfterDriverGet: {}'.format(WebDriverWaitTrySection - AfterDriverGet))

        # if Found_number: ## change to try to send regardless found or not found. 
        ## because in the number is saved in the contact, it will show name instead of number. 
    if Found_number:
        try:
            if checkSentBefore(msg):
                logger.info('Detected msg sent to {} before , skipping ............'.format(PhoneNumber))
            else:
                BeforeSendMsg = time.time()
                text_box = driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
                # time.sleep(5)
                text_box.send_keys(' ')
                text_box.send_keys(msg)
                button = driver.find_element_by_class_name('_1E0Oz')
                button.click()
                AfterSendMsg = time.time()
                logger.info('Time for sending msg: {}'.format(AfterSendMsg -BeforeSendMsg  ))

                ## check if massage been sent before 
                if checkSentBefore(msg):
                    logger.info('Send successuflly to {}'.format(PhoneNumber))
                    with open('./logs/suceed.csv', mode='a') as suceed_file:
                        suceed_writer = csv.writer(suceed_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        suceed_writer.writerow([PhoneNumber])
                else:
                    logger.info('Failed to send message to {}'.format(PhoneNumber))
                    with open('./logs/suceed.csv', mode='a') as failed_file:
                        failed_writer = csv.writer(failed_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        failed_writer.writerow([PhoneNumber])
                logger.info('Completed for the number: {}'.format(PhoneNumber ))
        except:
            logger.info('Number/name not found, or couldnt send out message to {}'.format(PhoneNumber))
            with open('./logs/not_found.csv', mode='a') as failed_file:
                not_found_writer = csv.writer(failed_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                not_found_writer.writerow([PhoneNumber])
    else:
        logger.info('Number not found: {}'.format(PhoneNumber))
        logger.info('Number/name not found, or couldnt send out message to {}'.format(PhoneNumber))
        with open('./logs/not_found.csv', mode='a') as failed_file:
            not_found_writer = csv.writer(failed_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            not_found_writer.writerow([PhoneNumber])
    time.sleep(3)
    return True