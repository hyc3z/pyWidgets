from PIL import ImageGrab, Image
import os
def main():
    img = Image.open("./logo_window.png")
    img = img.resize((64, 64), Image.ANTIALIAS)
    img.save("./logo_window.png")
    #Notice: You'll need multiple .png files to create a .ico file.
    #Check: http://www.winterdrache.de/freeware/png2ico/

if __name__ == '__main__':
    main()