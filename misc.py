from datetime import datetime
from email.mime.text import MIMEText
import pandas as pd
import smtplib
import time


def timeit(func):
    def inner(*args):
        t = time.time_ns()
        result = func(*args)
        elapsed_time = (time.time_ns() - t) / (10 ** 9)
        print(f"{func.__name__} finished in {elapsed_time:.6f} secs.")
        return result

    return inner


def update_trade_history(symbol, operation, amount, price, file_name):
    with open(file_name, "a+") as log_file:
        current_time = str(pd.Timestamp("now"))
        log_file.write(f"{current_time},{operation},{amount},{symbol},{price:.2f}\n")


def send_email(subject, message, receiver_list, sender_username, sender_password):
    fromaddr = sender_username
    body = f"Dear trader:\n\n{datetime.now()}\n{message}\n\n- R from AuTBot"

    toaddr = receiver_list
    cc = []
    bcc = []

    msg = MIMEText(body, _charset="utf-8")
    msg["From"] = fromaddr
    msg["To"] = ", ".join(toaddr)
    msg["Cc"] = ", ".join(cc)
    msg["Bcc"] = ", ".join(bcc)
    msg["Subject"] = subject

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_username, sender_password)
        server.sendmail(fromaddr, (toaddr + cc + bcc), msg.as_bytes())
