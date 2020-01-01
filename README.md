# pyWidgets

### [utilities](utilities)<br>
* [pyinstaller tool](utilities/autobuild.py) Tool for auto-building .exe applications via pyinstaller.
* [camera QThreaded](utilities/camera_thread.py) Use along with [fetch_thread](utilities/fetch_thread.py) to capture webcams.
* [convertpng](utilities/convert_png.py) Convert .png to windows standard size.
* [progressbar](utilities/progressbar.py) Terminal progressbar.
* [clock display](utilities/time_thread.py) Create a thread that signals current time every second. Can be used to display time on a gui application.

### [ui](ui)<br>
User interface templates for Qt applications.

### [qtclasses](qtclasses)<br>
Reimplemented Qt Classes.
* [customedGraphicsView](qtclasses/customedGraphicsView.py) Based on QGraphicsView, but implemented cursor-focused zoom-in and zoom-out capabilities with cursor changes, drawing lines and dots on the image.
* [modifiedTableWidget](qtclasses/modifiedTableWidget.py)  Based on QTableWidget, but can change the color of entire row when mouse is hovering on.
 
