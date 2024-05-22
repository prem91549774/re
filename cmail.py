import smtplib
from smtplib import SMTP
from email.message import EmailMessage
def sendmail(to,subject,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('buddipipremkumar@gmail.com','ppro qfzp dfmf lcql')
    msg=EmailMessage()
    msg['FROM']='buddipipremkumar@gmail.com'
    msg['SUBJECT']=subject
    msg['TO']=to
    msg.set_content(body)
    server.send_message(msg)
    server.quit()

