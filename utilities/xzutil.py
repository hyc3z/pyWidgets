import datetime
import tarfile
import os

def make_tarxz(output_filename, source_dir):
    with tarfile.open(output_filename, "w:xz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def print_time_diff(taskstr, start, finish):
    minutes = int((finish - start) / 60)
    seconds = int((finish - start) - 60 * minutes)
    string = "{} Spent: {} min {} secs.".format(taskstr, minutes, seconds)
    print(string)
    return string

def get_datetime_string_now():
    now = datetime.datetime.now()
    date = now.date()
    timeobj = now.time()
    timestr = "{0:02d}{1:02d}{2:02d}".format(timeobj.hour, timeobj.minute, timeobj.second)
    return "{}-{}".format(date, timestr)

def main():
    make_tarxz("main.tar.xz", "./dist")




if __name__ == '__main__':
    main()