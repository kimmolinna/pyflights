#from selenium.webdriver.chrome.service import Service as ChromeService
#from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import keyring

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

#service=ChromeService(ChromeDriverManager().install())

start = datetime.now()
end = start + relativedelta(days=1)
driver = webdriver.Chrome()
driver.get('https://gate.finnair.com/vpn/index.html')
driver.implicitly_wait(1.0)
driver.find_element(By.ID,'login').send_keys('AY29782')
driver.implicitly_wait(0.5)
driver.find_element(By.ID,'loginBtn').click()
driver.implicitly_wait(1.0)
driver.find_element(By.ID,'passwd').send_keys(keyring.get_password("finnair", "AY29782"))
driver.implicitly_wait(0.5)
driver.find_element(By.ID,'loginBtn').click()
input("Press any key to continue after authentication")
driver.get('https://gate.finnair.com/cvpn/http/skyway.finnair.fi/FinnairWDT')
driver.get('https://gate.finnair.com/cvpn/http/skyway.finnair.fi/FinnairWDT/StartApplication.aspx?group=appgroup-1&application=app-3')
Select(driver.find_element(By.NAME,'start_day')).select_by_index(start.day)
Select(driver.find_element(By.NAME,'start_month')).select_by_index(start.month)
Select(driver.find_element(By.NAME,'start_year')).select_by_value(str(start.year))
Select(driver.find_element(By.NAME,'end_day')).select_by_index(end.day)
Select(driver.find_element(By.NAME,'end_month')).select_by_index(end.month)
Select(driver.find_element(By.NAME,'end_year')).select_by_value(str(end.year))
driver.find_element(By.NAME,'departure').send_keys('HEL')
Select(driver.find_element(By.NAME,'aircraft')).select_by_value('350')
driver.find_element(By.XPATH,'//a[@href="JavaScript:form1.submit();"]').click()

count = 0; find = 0
flts = []; crew = []; pers = []

while count<12:
    try:
        table = driver.find_element(By.CLASS_NAME ,'main')
        success = True
        rows = table.find_elements(By.TAG_NAME, 'tr')
        for r in rows:
            flt = r.find_elements(By.CLASS_NAME,"row")
            if len(flt)==6:
                nbr=flt[0].text
                std=flt[1].text
                sta=flt[3].text
                std,sta = [("-".join(ts[:10].split(".")[::-1]))+' '+ts[11:16] for ts in [std,sta]]
                flts.append([std[:10].replace('-','')+nbr[2:],nbr[0:2],nbr[2:],std,flt[2].text,sta,flt[4].text,"","",flt[5].text.replace('Open positions: ','')])
                find+=1
        find = 0
        for f in flts:
            add="https://gate.finnair.com/cvpn/http/wpcrewap3.finnair.com:81/PAC/pairingflight.asp?departure=HEL"
            add+="&airliner="+f[1]
            add+="&flightnumber="+f[2]
            add+="&flightdate="+datetime.strptime(f[3],"%Y-%m-%d %H:%M").astimezone(timezone.utc).strftime("%Y%m%d")
            driver.get(add)
            info = driver.find_elements(By.CLASS_NAME,"default")
            if info:
                plane = info[len(info)-1].text.split(" ")
                reg = plane[1][1:6]
                flts[find][7]=plane[0]
                flts[find][8]=reg
                list = driver.find_element(By.TAG_NAME,"p")
                members = list.find_elements(By.TAG_NAME,"tr")
                for m in members:
                    c = m.find_elements(By.CLASS_NAME,"row")
                    if len(c)==6:
                        id=int(c[0].text)
                        crew.append([flts[find][1],id,c[3].text,c[4].text])
                        if id!=12345:
                            psen=0
                            if c[3].text=="PU":
                                sl=c[2].text.split("/")
                                sen=int(sl[0])
                                if len(sl)==2:
                                    psen=int(sl[1])
                            else:
                                sen=int(c[2].text)
                            pers.append([id,c[1].text,sen,psen,c[5].text])
            find+=1
    except:
        count += 1
        driver.implicitly_wait(0.5)
        if count > 10:
            break
driver.close()
pd.DataFrame(crew,columns=['company','id','tra','pos'])