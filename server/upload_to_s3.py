import os
import s3fs
import datetime
import logging

local_path = "/data/logs/"
bucket = "stats.playfun.me"
def save_s3(bucket = bucket , path = local_path):
    try:
        s3 =  s3fs.S3FileSystem(anon=False)
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.split(".")[1] < datetime.datetime.now().strftime("%Y%m%d-%H"):
                    try:
                        filename = os.path.join(root, file)
                        appname, datetimestr = file.split(".")
                        datestr , hourstr = datetimestr.split("-")
                        s3.put(filename, "%s/%s/logs/%s/%s.log" % (bucket,appname, datestr, hourstr))
                        os.remove(filename)
                    except:
                        pass
    except Exception as e :
        logging.error(str(e))
if __name__ == "__main__":
    save_s3()
