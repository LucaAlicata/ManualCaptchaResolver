
import email.message
import smtplib, imaplib
from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes, time, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

class resolveCaptcha:
    def __init__(self, user, password, addressee, textElement, buttonElement):
        self.user = user
        self.password = password
        self.addressee = addressee
        self.textElement = textElement
        self.buttonElement = buttonElement
        self.browser = webdriver.Chrome()
        self.mailOn = True
        self.now = time.time()
        pass
    
    def readMail(self):
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(self.user, self.password)
        mail.list()
        mail.select('inbox')
        result, data = mail.uid('search', None, "UNSEEN")
        i = len(data[0].split())
        if i > 0:
            x = i-1
            latest_email_uid = data[0].split()[x]
            result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = email_data[0][1]
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)
            stringDate = email_message["Date"].split(" +")[0].split(", ")[1] if len(email_message["Date"].split(" +")) > 1 else email_message["Date"].split(" -")[0].split(", ")[1]
            mailTimestamp = datetime.datetime.strptime(stringDate, '%d %b %Y %H:%M:%S').timestamp()
            if mailTimestamp > self.now - 120000:
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True)
                        strbody = body.decode('utf-8')
                        print(strbody)
                        try:
                            capcha = strbody.split("-")[0].split("*")[1]
                            return capcha
                        except:
                            continue
                    else:
                        continue
        return "err"

    def insertCapcha(self, capcha, textElement, buttonElement):
        textElement.send_keys(capcha)
        buttonElement.click()


    def sendCapchaMail(self):
        if self.mailOn:
            msg = EmailMessage()
            msg['Subject'] = 'Capcha to risolve'
            msg['From'] = self.user
            msg['To'] = self.addressee
            msg.set_content('Capcha to risolve')
            image_cid = make_msgid()
            msg.add_alternative("""\
            <html>
                <body>
                    <img src="cid:{image_cid}">
                </body>
            </html>
            """.format(image_cid=image_cid[1:-1]), subtype='html')

            with open('captchaPage.png', 'rb') as img:

                # know the Content-Type of the image
                maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')

                # attach it
                msg.get_payload()[1].add_related(img.read(),
                                                    maintype=maintype,
                                                    subtype=subtype,
                                                    cid=image_cid)
            try:
                smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                smtp.login(self.user, self.password)
                smtp.sendmail(self.user, self.addressee, msg.as_string())
                smtp.quit()
            except:
                print("Error while sending the mail")
            finally:
                self.mailOn = False

    def fixCapcha(self):
        time.sleep(1)
        self.browser.get_screenshot_as_file('captchaPage.png')
        self.sendCapchaMail()
        time.sleep(10)
        i = 0
        textElement = self.browser.find_element(By.XPATH, self.textElement)
        buttonElement = self.browser.find_element(By.XPATH, self.buttonElement)
        while(i < 20):
            temp = self.readMail()
            if(temp != 'err'):
                self.insertCapcha(temp, textElement, buttonElement)
                i = 21
            else:
                time.sleep(5)
                i+=1

    def main(self):
        self.browser.get("https://captcha.com/demos/features/captcha-demo.aspx")
        self.fixCapcha()
        self.readMail()

bot = resolveCaptcha(
    user = "...",               # user mail
    password = "...",           # user password
    addressee = "...",          # adressee email
    textElement = "...",        # xpath of the textbox
    buttonElement = "..."       # xpath of the button
    )
bot.main()