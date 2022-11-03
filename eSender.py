import os
import datetime as dt
from ini_res import Ini

INI = Ini()
NOW = dt.datetime.now()
INI_NAME = 'eSender.ini'
LOG_NAME = 'eSender.log'


def stream():

    """ Прием файла и конвертация в сообщение для отправки  / Receive and convert file to msg for sending """

    path = INI.get(log=LOG_NAME, ini=INI_NAME, section='STREAM', param='path')
    files_list = []
    for root, dirs, files in os.walk(path):
        for f in files:
            files_list.append(f)
    # print(files_list) # ['BAR.PRN', 'KUH.PRN']
    # cp = INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='codepage')
    orders = []
    codepage = INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='codepage')
    for name in files_list:
        with open(f'{path}/{name}', "r", encoding=codepage) as data:
            orders.extend(data.readlines())
    for_send = ''.join(orders)
    for_send2 = for_send.encode("cp1251").decode('cp1251')

    del files_list
    del orders
    return for_send2

# ---------------------- EMAIL ------------------ #


def email():

    """ Отправка на почту / Send to email """

    from email.mime.multipart import MIMEMultipart
    from email.mime.image import MIMEImage
    from email.mime.text import MIMEText
    import smtplib

    # create message object instance
    msg = MIMEMultipart()

    # set the parameters of the message

    try:

        if INI.get(log=LOG_NAME, ini=INI_NAME, section='EMAIL', param='from_app_psw') != "" and INI.get(log=LOG_NAME, ini=INI_NAME, section='EMAIL', param='from_address') != "":
            password = INI.get(log=LOG_NAME, ini=INI_NAME, section='EMAIL', param='from_app_psw')
            msg['From'] = INI.get(log=LOG_NAME, ini=INI_NAME, section='EMAIL', param='from_address')
        else:
            print('Error! Check ini[EMAIL]params')

        msg['To'] = INI.get(log=LOG_NAME, ini=INI_NAME, section='EMAIL', param='to_address')
        msg['Subject'] = INI.get(log=LOG_NAME, ini=INI_NAME, section='EMAIL', param='subject')
    except Exception as Argument:
        with open(LOG_NAME, "a") as log_file:
            log_file.write(f"{NOW} : EMAIL ERROR: {str(Argument)}")
    else:
        # attach image to message body
        msg.attach(MIMEText(stream()))

        try:
            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(msg['From'], password)
                connection.sendmail(msg['From'], msg['To'], msg.as_string())
            connection.close()
        except Exception as Argument:
            with open(LOG_NAME, "a") as log_file:
                log_file.write(f"{NOW} : EMAIL ERROR: {str(Argument)}")
        else:
            try:
                dir = INI.get(log=LOG_NAME, ini=INI_NAME, section='STREAM', param='path')
                for f in os.listdir(dir):
                    os.remove(os.path.join(dir, f))

            except FileNotFoundError:
                pass


# ---------------------- GUI & RUN --------------- #


def running():

    import threading

    tmeout = int(INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='timeout'))
    threading.Timer(tmeout, running).start()
    data_for_send = stream()
    count = int(INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='counter'))
    if data_for_send != '':
        INI.set(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='counter', data=str(count+1))
        clear = lambda: os.system('cls')
        clear()
        print(f'Completed tasks: {count+1}')
        email()
    else:
        pass


def start():

    """ Задачи перед стартом основной рабочей петли """

    INI.set(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='counter', data='0')
    with open(LOG_NAME, "a") as log_file:
        log_file.write(f"{NOW} : eSender started.")
    running()


start()
