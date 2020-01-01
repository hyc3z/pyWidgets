import shutil
import os
import datetime


def main():
    cur_dir = "."
    entrance_file = "main.py"
    work_dir = "./build"
    dist_dir = "./dist"
    icon_file = "icon.ico"
    copy_dir = ["./dark", "./light"]
    copy_file = ["./light.qss", "./dark.qss", "logo_login.png", "logo_yxy_square.png", "logo_window.png", "logo_zjdxyxy.png", "database.db", "icon.ico"]
    options = "-w --icon={} ".format(icon_file)
    if os.path.exists(work_dir):
        if os.path.isdir(work_dir):
            shutil.rmtree(work_dir)
    if os.path.exists(dist_dir):
        if os.path.isdir(dist_dir):
            shutil.rmtree(dist_dir)
    os.mkdir(work_dir)
    os.mkdir(dist_dir)
    os.system("""pyinstaller "{}" --windowed --clean  --distpath="{}" -i {}  """.format(
            os.path.join(cur_dir, entrance_file),
            os.path.join(cur_dir, dist_dir),
            os.path.join(cur_dir, icon_file),
        )
    )
    dist_subdir = os.listdir(dist_dir)
    if(len(dist_subdir)) != 1:
        return 2
    exe_dir = os.path.join(dist_dir,dist_subdir[0])
    for i in copy_dir:
        target_dir = os.path.join(exe_dir,i)
        if os.path.exists(target_dir):
            if os.path.isdir(target_dir):
                shutil.rmtree(target_dir)
        shutil.copytree(i, os.path.join(exe_dir,i))
    for i in copy_file:
        target_dir = os.path.join(exe_dir, i)
        if os.path.exists(target_dir):
            if os.path.isfile(target_dir):
                os.remove(target_dir)
        shutil.copyfile(i, os.path.join(exe_dir, i))
    now = datetime.datetime.now()
    date = now.date()
    timeobj = now.time()
    timestr = "{0:02d}{1:02d}{2:02d}".format(timeobj.hour, timeobj.minute, timeobj.second)
    shutil.make_archive("{}-{}-{}".format(dist_subdir[0],date,timestr), "zip", exe_dir)


if __name__ == '__main__':
    main()
    # print()