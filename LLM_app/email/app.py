import ssl
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders
import numpy as np
import smtplib

from selenium import webdriver
import time
from selenium.webdriver.common.by import By

import re
from bs4 import BeautifulSoup
import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless') # this is must
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


driver = webdriver.Chrome(options=chrome_options)

email_sender = 'aditshah06@gmail.com'
email_password = "qulneextawirnuja"
company_email = "@goclio.com"
no_people=20

position = "Data Scientist"
company = "Clio"
specific_position = "Data Scientist"


attachment_file_name = "/Users/aditshah/Desktop/resume/clio/Adit_Shah.pdf"
# csv  = "/Users/aditshah/Desktop/AMD_SCRAP.csv"
#page_html="https://www.linkedin.com/search/results/people/?keywords=darkvision&origin=FACETED_SEARCH&page={}&sid=*H)"
# page_html = "https://www.linkedin.com/search/results/people/?activelyHiringForJobTitles=%5B%22-100%22%5D&geoUrn=%5B%22104423466%22%2C%2290009553%22%5D&keywords=ea%20sports&origin=FACETED_SEARCH&page={}&sid=%40Si&spellCorrectionEnabled=false"
page_html="https://www.linkedin.com/search/results/people/?currentCompany=%5B%22385372%22%2C%2274769662%22%5D&keywords=clio&origin=FACETED_SEARCH&page={}&sid=ipZ"
formating="first.last"
# formating = "en"

def convert_name_format(name):
    temp = ";!*:,."
    
    # name=re.sub('A-Za-z0-9', '', name)
    name=name.lower()
    name = re.sub(rf'[{temp}]', '', name)
    return (name.split(" ")[0],name.split(" ")[1])


# def convert_name_format(name):
#     # Remove the surrounding brackets and quotes
#     clean_name = name.strip("[]'")

#     # Separate based on capital letters
#     parts = ['']
#     for char in clean_name:
#         if char.isupper() and parts[-1]:
#             parts.append(char.lower())
#         else:
#             parts[-1] += char.lower()
#     return (parts[0],parts[1])






def main():
    
    
    driver.get("https://www.linkedin.com/login")


    time.sleep(4)

    username = driver.find_element(by=By.XPATH, value="//input[@name='session_key']")
    password = driver.find_element(by=By.XPATH, value="//input[@name='session_password']")
    username.send_keys("aditshah06@gmail.com")
    password.send_keys("ADIT1112")
    time.sleep(4)
    submit = driver.find_element(by=By.XPATH, value="//button[@type='submit']").click()
    time.sleep(4)
    people_names = []
    for page in range(1, no_people//10+1, 1):
        page_url= page_html.format(page)
        driver.get(page_url)
        src = driver.page_source
        soup = BeautifulSoup(src, 'lxml')
        people_name_html = soup.find_all('div', {'class': 't-roman t-sans'})
        for name in people_name_html:
            people_names.append(name.text.strip().strip().split("View", 1)[0])
            
    
    subject = 'You will love this Profile, Adit Shah, ML Engineer, Concordia University Grad, Published 5+ Patents.'

    message =  """
    <html>
        <body>
            <p>Hello {},</p>
            <p>My Name is Adit Shah. I am currently holding 3+ years of work experience working on deploying LLM and computer vision based projects.</p>
            <p>I am interested in finding out more about positions related to {} at {}.</p>
            <p>As a motivated problem solver and diligent learner, I have developed proficiency in the areas of Machine Learning and MLOps while working at Robert Bosch and AIRY:3D, with a thorough understanding and keeping up with the state-of-the-art models and research in the evolving field of AI.</p>
            <p>Would love it if you could refer me for the position of {}.</p>
            <p>Thanks,<br>Adit Shah</p>
        </body>
    </html>
    """
    
    converted_names = np.vectorize(convert_name_format)(people_names)
    print(converted_names)

    # for i in range(len(converted_names[0])):
    #     print(converted_names[0][i]+"."+converted_names[1][i]+"@darkvision.com")
 
    # df =pd.read_csv(csv)
    # k = df.to_numpy()
    # for i in range(len(k)):
    #     k[i] = re.sub("[^A-Za-z]","", str(k[i]).split("\\")[0])

   

    # converted_names = np.vectorize(convert_name_format)(k)
    # converted_names=[["ashah9497", "15bec104"],["Ee","ww"]]

    for i in range(len(converted_names[0])):
        receiver_first_name = converted_names[0][i]
        receiver_surname = converted_names[1][i]
        if formating == "first":
            email_receiver = receiver_first_name+company_email
        elif formating == "first.last":
            email_receiver = receiver_first_name+"."+receiver_surname+company_email
        elif formating == "flast":
            email_receiver = receiver_first_name[0]+receiver_surname+company_email
        else:
            email_receiver = receiver_first_name+company_email
        print(email_receiver)
        body = message.format(receiver_first_name.capitalize(), position, company, specific_position)
        
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        
        em.set_content(body)

        em.add_alternative(body, subtype='html')

        with open(attachment_file_name, 'rb') as attachment_file:
            file_data = attachment_file.read()
            file_name = attachment_file.name.split("/")[-1]

        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(file_data)
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
        em.attach(attachment)

        # Add SSL (layer of security)
        context = ssl.create_default_context()

        # Log in and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
            
if __name__ == '__main__':
    main()