# pyWidgets

个人在开发过程中用Py3造的一些轮子，供使用
### [utilities](utilities)<br>
* [pyinstaller tool](utilities/autobuild.py) 
Pyinstaller 打包工具.
* [camera QThreaded](utilities/camera_thread.py) 
 基于QThread和cv2的摄像头采集部分，配合[fetch_thread](utilities/fetch_thread.py)一起使用。由于性能原因已不使用，在必须使用cv2的场景可以参考
 。
* [camera QCamera](utilities/camera_arranger.py)
 基于QCamera的摄像头采集部分。经过测试在PyQt5环境下资源消耗比cv2方案小不少。支持自动根据摄像头数量进行扩展，可以用来做监控摄像头软件的组件使用。

* [progressbar](utilities/progressbar.py) 终端进度条.
* [clock display](utilities/time_thread.py) 时序线程，可以设定每隔一段时间定时执行任务。由于开销原因已不使用

* [circle detector](utilities/circle_detector.py) 图像中的圆检测，当初是用作参照物检测使用的，我们的设备中会放一个固定直径的圆用作参考。
### [ui](ui)<br>
Qt UI文件，供参考.

### [qtclasses](qtclasses)<br>
重写的Qt类
* [modifiedTableWidget](qtclasses/modifiedTableWidget.py) 支持整行选取的QTableWidget.
 
* [customedGraphicsView](qtclasses/customedGraphicsView.py) 重写QGraphicsView,对图像各种操作，如画点、画线，根据参照物测量距离，根据参照物测量面积、图片缩放、多边形绘制等.
