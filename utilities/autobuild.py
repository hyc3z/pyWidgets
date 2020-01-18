import shutil
import os
import datetime
import time
import tarfile


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
    return timestr


def main():
    start_time = time.time()
    cur_dir = "."
    entrance_file = "main.py"
    work_dir = "./build"
    dist_dir = "./dist"
    icon_file = "icon.ico"
    src_dir = "./src"
    copy_dir = [
        "./dark",
        "./light",
        "./font",
        "./pic",
    ]
    copy_file = [
        "./light.qss",
        "./dark.qss",
        "logo_login.png",
        "logo_login_cropped.png",
        "logo_yxy_square.png",
        "logo_window.png",
        "logo_zjdxyxy.png",
        "database.db",
        "icon.ico"
    ]
    src_file = [
        "camera.py",
        "camera_thread.py",
        "customedGraphicsView.py",
        "dark.qss",
        "database_controller.py",
        "database_macros.py",
        "dialog_exit.py",
        "dict2py.py",
        "fetch_thread.py",
        "helptable_data.py",
        "levelfour_macros.py",
        "icon.ico",
        "login.py",
        "logo_login.png",
        "logo_login_cropped.png",
        "logo_window.png",
        "logo_yxy_square.png",
        "logo_zjdxyxy.png",
        "main.py",
        "mainwindow.py",
        "modifiedTableWidget.py",
        "pwd_util.py",
        "time_thread.py",
        "tree_dict.py",
        "tree_dict_to_qtreewidgetitems.py",
        "ui_login.py",
        "ui_mainwindow_4.py",
        "ui_popup_noicon.py",
    ]
    if os.path.exists(work_dir):
        if os.path.isdir(work_dir):
            shutil.rmtree(work_dir)
    if os.path.exists(dist_dir):
        if os.path.isdir(dist_dir):
            shutil.rmtree(dist_dir)
    if os.path.exists(src_dir):
        if os.path.isdir(src_dir):
            shutil.rmtree(src_dir)
    os.mkdir(work_dir)
    os.mkdir(dist_dir)
    os.mkdir(src_dir)
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
    timestr = get_datetime_string_now()
    for i in src_file:
        target_dir = src_dir
        shutil.copyfile(i, os.path.join(target_dir, i))
    for i in copy_dir:
        target_dir = src_dir
        shutil.copytree(i, os.path.join(target_dir, i))
    # shutil.make_archive("{}-{}-{}".format(dist_subdir[0],date,timestr), "zip", exe_dir)
    now = datetime.datetime.now()
    date = now.date()
    generate_finish = time.time()
    print_time_diff(finish=generate_finish, start=start_time, taskstr="Generating")
    print("Making release tar.xz archive...")
    print("WARNING: It's going to take a long time.")
    make_tarxz("{}-{}-{}.{}".format(dist_subdir[0], date, timestr, "tar.xz"), exe_dir)
    finish_time = time.time()
    print_time_diff(finish=finish_time, start=generate_finish, taskstr="Compressing release")
    print("Making source tar.xz archive...")
    print("WARNING: It's going to take a long time.")
    make_tarxz("{}-{}-{}.{}".format("source", date, timestr, "tar.xz"), src_dir)
    finish_time_2 = time.time()
    print_time_diff(finish=finish_time_2, start=finish_time, taskstr="Compressing source")


if __name__ == '__main__':
    main()
