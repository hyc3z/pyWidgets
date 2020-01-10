import tarfile
import os

def make_tarxz(output_filename, source_dir):
    with tarfile.open(output_filename, "w:xz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def main():
    make_tarxz("main.tar.xz", "./dist")




if __name__ == '__main__':
    main()