import datetime

def log(str_to_log):
    print(f"[SERVER] [{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}]: {str_to_log}")