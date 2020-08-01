from datetime import datetime
from email.mime.text import MIMEText
import pandas as pd
import smtplib


def update_trade_history(symbol, operation, amount, price, file_name):
    with open(file_name, 'a+') as hist_file:
        current_time = str(pd.Timestamp("now"))
        hist_file.write("{}: {} {} {} @ {}\n".format(current_time,
                                                    operation, amount, symbol, price))


def send_email(subject, message, receiver_list, sender_username, sender_password):
    fromaddr = 'superanels@gmail.com'
    body = "Dear trader:\n\n{}\n".format(
        datetime.now()) + message + " \n\n- R from TBot"

    toaddr = receiver_list
    cc = []
    bcc = []

    msg = MIMEText(body)
    msg['From'] = fromaddr
    msg['To'] = ', '.join(toaddr)
    msg['Cc'] = ', '.join(cc)
    msg['Bcc'] = ', '.join(bcc)
    msg['Subject'] = subject

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_username, sender_password)
        server.sendmail(fromaddr, (toaddr+cc+bcc), msg.as_string())
