import time
import sys
import s3fs

def main():
    datestr = sys.argv[1]
    fs = s3fs.S3FileSystem()
    for f in fs.glob("%s/%s/logs/%s/*.log" % ("stats.playfun.me", "sumikko",datestr)):
        data = ""
        try:
            s3 = s3fs.S3FileSystem(anon=False)
            data = s3.cat(f)
        except Exception as e :
            pass
        for line in data.split("\n"):
            print line
            sys.stdout.flush()
 
if __name__ == "__main__":
    main()
