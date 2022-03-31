import os
import sys
from itertools import chain
import pandas as pd
import cv2
from datetime import datetime
import re
from PyQt5.QtCore import QUrl, QDateTime, QDir, QFileInfo
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QStyleFactory
from GUI import *


class myMainWindow(Ui_MainWindow, QMainWindow):
    cap_finish = pyqtSignal()  # 截图完成信号

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.fileName_save = None
        self.d_file = None
        self.fileList = None
        self.jg = None
        self.datafile_choose = None
        self.chicken_df = None
        self.j_df = None
        self.numList = None
        self.__duration = ""  # 文件总时间长度
        self.__curPos = ""  # 当前播放到位置
        self.vSld_pressed = False
        self.videoFullScreen = False  # 判断当前widget是否全屏
        self.videoFullScreenWidget = myVideoWidget()  # 创建一个全屏的widget
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        self.player.setVideoOutput(self.vPly)
        self.voBtn.clicked.connect(self.on_btnAdd_clicked)
        self.doBtn.clicked.connect(self.doBtn_clicked)
        self.svBtn.clicked.connect(self.svBtn_clicked)
        self.stBtn.clicked.connect(self.stBtn_clicked)
        self.puBtn.clicked.connect(self.puBtn_clicked)
        self.sdBtn.clicked.connect(self.sdBtn_clicked)
        self.zdBtn.clicked.connect(self.zdBtn_clicked)
        self.goBtn.clicked.connect(self.goBtn_clicked)
        self.bcBtn.clicked.connect(self.bcBtn_clicked)
        self.mtBtn.clicked.connect(self.mtBtn_clicked)
        self.qqBtn.clicked.connect(self.qqBtn_clicked)
        self.jnBtn.clicked.connect(self.jnBtn_clicked)
        self.teBtn.clicked.connect(self.teBtn_clicked)
        self.xsBtn.clicked.connect(self.xsBtn_clicked)
        self.j1Btn.clicked.connect(self.j1Btn_clicked)
        self.j2Btn.clicked.connect(self.j2Btn_clicked)
        self.j3Btn.clicked.connect(self.j3Btn_clicked)
        self.s1Btn.clicked.connect(self.s1Btn_clicked)
        self.s30Btn.clicked.connect(self.s30Btn_clicked)
        self.m1Btn.clicked.connect(self.m1Btn_clicked)
        self.sxBtn.clicked.connect(self.sxBtn_clicked)
        self.clBtn.clicked.connect(self.clBtn_clicked)
        self.player.positionChanged.connect(self.changeSlide)
        self.videoFullScreenWidget.doubleClickedItem.connect(self.videoDoubleClicked)  # 双击响应
        self.vPly.doubleClickedItem.connect(self.videoDoubleClicked)  # 双击响应
        self.vSld.setTracking(False)
        self.vSld.sliderReleased.connect(self.releaseSlider)
        self.vSld.sliderPressed.connect(self.pressSlider)
        self.vSld.sliderMoved.connect(self.moveSlider)
        self.vSld.ClickedValue.connect(self.clickedSlider)
        self.ySld.valueChanged.connect(self.volumeChange)
        self.vLst.setStyle(QStyleFactory.create('windows'))

    def openfolder(self):
        '''打开系统文件资源管理器的对应文件夹'''
        # import os
        folder = r'D:'
        # 方法1：通过start explorer
        # os.system("start explorer %s" % folder)
        # 方法2：通过startfile
        os.startfile(folder)
        # print("测试！")

    def sxBtn_clicked(self):
        if self.datafile_choose is None:
            print('我来！')
            rec_code = QMessageBox.information(self, '메시지 알림:',
                                               '데이터 파일이 열렸는지 확인해주세요!',
                                               QMessageBox.Yes)
            print(rec_code)
            if rec_code == 65536:
                print('我去！')
            else:
                print('我再去！')
                self.doBtn_clicked()
        elif self.chicken_df is None:
            QMessageBox.information(self, '메시지 알림:',
                                    '"jou1~jou2~jou3"의 데이터 변환이 완료되었는지 확인해주세요!',
                                    QMessageBox.Yes)
        else:
            self.j_df.set_index(['getTime'], inplace=True)
            # print(j01_df)

            zeroData = self.j_df.loc[:, 'w01':'w60'].isin([0.0])
            # print(zeroData)
            zeroIndex = zeroData[~zeroData]
            # print(zeroIndex)
            zeroReal = zeroIndex[zeroIndex.isnull().T.any()]
            # print(zeroReal)
            zeroList = zeroReal.index.tolist()
            print(zeroList)
            newList = []
            for num in zeroList:
                #     print(type(num))
                numTime = datetime.strptime(num[1:], '%Y-%m-%d %H:%M:%S')  # 他妈的命名'2021_10_23_00_27_30'这东西前面还有个空格！
                for n in range(60):  # 唉，这里也得提前一分钟啊！
                    newTime = numTime - 61 * pd.Timedelta(seconds=1) + n * pd.Timedelta(
                        seconds=1)  # 2021_10_23_00_27_30 ~ 2021_10_23_00_28_29
                    newList.append(newTime)
            self.numList = []
            for num in newList:
                self.numList.append('_'.join((re.findall(r"\d+\.?\d*", str(num)))))
            # print(self.numList)
            if self.numList:
                numStr = ' '.join(self.numList)
                newStr = numStr + '\n총 {}개의 문제 시점이 있습니다.\n'.format(len(self.numList))
                rec_code = ScrollMessageBox(QMessageBox.Critical, '0을 포함하는 시점은 다음과 같다:', newStr)
                print(rec_code)
                if rec_code == 65536:
                    print('我去！')
                else:
                    print('我再去！')
            else:
                print('没找到！')
                rec_code = QMessageBox.information(self, '메시지 알림:',
                                                   '0을 포함하는 시간 단계를 찾을 수 없습니다!',
                                                   QMessageBox.Yes)
                print(rec_code)

    def getFilepath(self, rootDir, filepathmsg, filetype):
        filepathresult = []
        for dirpath, dirNames, fileNames in os.walk(rootDir):
            for fileName in fileNames:
                apath = os.path.join(dirpath, fileName)
                apathname = os.path.splitext(apath)[0]
                apathtype = os.path.splitext(apath)[1]
                #             print(apath)
                #             print(apathname)
                #             print(apathtype)
                for i in filetype:
                    #                 print('走你!')
                    if i in apathtype:
                        #                     print('别急!')
                        for j in filepathmsg:
                            #                         print('快了!')
                            if j in apathname:
                                filepathresult.append(apath)
                                print('找到一只异常鸡鸡!')

        # for i in range(len(filepathresult)):
        #     print(filepathresult[i])
        if filepathresult:
            fileStr = '\n'.join(filepathresult)
            newfileStr = fileStr + '\n지금까지 총 {}개의 문제 사진이 있습니다.\n'.format(len(filepathresult))
            rec_code = ScrollMessageBox(QMessageBox.Critical, '잘못된 데이터가 포함된 사진는 다음과 같다:', newfileStr)
            print(rec_code)
            if rec_code == 65536:
                print('我去！')
            else:
                print('我再去！')
                rec_code1 = QMessageBox().question(None, "확인하십시오.", "문제가 있는 사진을 확실히 정리하시겠습니까?",
                                                   QMessageBox.Yes | QMessageBox.No)
                print(rec_code1)
                if rec_code1 == 65536:
                    print('我去！')
                else:
                    qliList = []
                    mi = 1
                    for wimgPath in filepathresult:
                        os.remove(wimgPath)
                        qliList.append(os.path.exists(wimgPath))
                    for element in qliList:
                        if not element:
                            mi = 2
                        else:
                            mi = 1
                    if mi == 1:
                        rec_code = QMessageBox.information(self, '메시지 알림:',
                                                           '문제 사진이 지워지지 않으니 수동으로 확인해주세요!',
                                                           QMessageBox.Yes)

                        print(rec_code)
                    elif mi == 2:

                        rec_code = QMessageBox.information(self, '메시지 알림:',
                                                           '문제가 있는 사진 {}장을 모두 삭제되었습니다!'.format(len(filepathresult)),
                                                           QMessageBox.Yes)

                        print(rec_code)
                    else:
                        print('救mi啊！')


        else:
            print('没找到！')
            rec_code = QMessageBox.information(self, '메시지 알림:',
                                               '잘못된 데이터가 포함된 사진을 찾을 수 없습니다!',
                                               QMessageBox.Yes)
            print(rec_code)

    def clBtn_clicked(self):
        # print(self.fileName_save)
        if self.numList is None:
            print('我来！')
            rec_code = QMessageBox.information(self, '메시지 알림:',
                                               '먼저 데이터에 0이 포함되어 있는지 여부를 필터링하십시오!\n(위의 빨간 버튼을 눌러주십시오.)',
                                               QMessageBox.Yes)
            print(rec_code)
            if rec_code == 65536:
                print('我去！')
            else:
                print('我再去！')
        elif self.fileName_save is None:
            print('我来！')
            rec_code = QMessageBox.information(self, '메시지 알림:',
                                               '문제 사진의 검색 디렉토리를 확인하십시오!)',
                                               QMessageBox.Yes)
            print(rec_code)
            if rec_code == 65536:
                print('我去！')
            else:
                self.svBtn_clicked()

        else:
            rfileName_save = self.fileName_save + '//'
            root_path = r'%s' % rfileName_save  # +r 神器!
            print('开始在{}目录下检索不能用的图片...'.format(root_path))
            filetype = ['.png']
            self.getFilepath(root_path, self.numList, filetype)

    def s1Btn_clicked(self):

        self.jg = 1
        print('1秒1张')

    def s30Btn_clicked(self):

        self.jg = 30
        print('30秒1张')

    def m1Btn_clicked(self):

        self.jg = 60
        print('1分钟1张')

    def qqBtn_clicked(self):
        self.playlist.clear()  # 清空播放列表
        self.vLst.clear()
        self.player.stop()

    def xsBtn_clicked(self):
        pos = self.vLst.currentRow()
        item = self.vLst.takeItem(pos)  # python会自动删除

        if (self.playlist.currentIndex() == pos):  # 是当前播放的曲目
            nextPos = 0
            if pos >= 1:
                nextPos = pos - 1
                self.playlist.removeMedia(pos)  # 从播放列表里移除
                if self.vLst.count() > 0:  # 剩余个数
                    self.playlist.setCurrentIndex(nextPos)
                    self.do_currentChanged(nextPos)  # 当前曲目变化
                else:
                    self.player.stop()
                    self.vLst.LabCurMedia.setText("无曲目")
            else:
                self.playlist.removeMedia(pos)

    ##   @pyqtSlot()    ##双击时切换播放文件

    def on_listWidget_doubleClicked(self, index):
        rowNo = index.row()  # 行号
        self.playlist.setCurrentIndex(rowNo)
        self.player.play()

    def jnBtn_clicked(self):
        print("on_btnPrevious_clicked")
        self.playlist.previous()

    ##下一曲目
    def teBtn_clicked(self):
        print("on_btnNext_clicked")
        self.playlist.next()

    def closeEvent(self, event):
        if (self.player.state() == QMediaPlayer.PlayingState):
            self.player.stop()

    def volumeChange(self, position):
        volume = round(position / self.ySld.maximum() * 100)
        print("vlume %f" % volume)
        self.player.setVolume(volume)
        self.ysLab.setText("현재 볼륨:" + str(volume) + "%")

    def clickedSlider(self, position):
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            self.vsLab.setText("현재 진행률:" + "%.2f%%" % position)
        else:
            self.vSld.setValue(0)

    def moveSlider(self, position):
        self.vSld_pressed = True
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            self.vsLab.setText("현재 진행률:" + "%.2f%%" % position)

    def pressSlider(self):
        self.vSld_pressed = True
        print("pressed")

    def releaseSlider(self):
        self.vSld_pressed = False

    def changeSlide(self, position):
        if not self.vSld_pressed:  # 进度条被鼠标点击时不更新
            self.vidoeLength = self.player.duration() + 0.1
            self.vSld.setValue(round((position / self.vidoeLength) * 100))
            self.vsLab.setText("현재 진행률:" + "%.2f%%" % ((position / self.vidoeLength) * 100))

    def SetPlaybackRate(self, val):
        if self.player.duration() > 0:
            self.player.pause()
            self.player.setPlaybackRate(val)
            self.player.play()
            self.bsLab.setText('x' + str(val) + '배속')

    def goBtn_clicked(self):
        # self.vidoeLength = self.player.duration() + 0.1
        val = self.player.playbackRate() + 1
        print(val)
        val1 = val * 0.5
        print(val1)
        self.SetPlaybackRate(val1)

    def bcBtn_clicked(self):
        # self.vidoeLength = self.player.duration() - 0.1
        val = self.player.playbackRate() + 1
        val2 = val * 2
        self.SetPlaybackRate(val2)

    def mtBtn_clicked(self):
        self.player.setVolume(0)
        # self.player.isMuted()

    # def voBtn_clicked(self):
    #     # QtWidgets.QMessageBox.information(self.voBtn, "标题", "这是一个打开视频文件的按钮！")
    #     # absolute_path is a QString object
    #     # cwd = os.getcwd()  # 获取当前程序文件位置
    #     videofile_choose, videotype_choose = QFileDialog.getOpenFileName(self,
    #                                                             '비디오 파일 선택',
    #                                                             './',  # 起始路径
    #                                                             'All Video Files (*);;*.mp4;;*.avi;;*.mov;;*.mkv')  # 设置文件扩展名过滤,用双分号间隔
    #     if videofile_choose == "":
    #         print("\n取消选择")
    #         return
    #     print("\n你选择的文件为:")
    #     print(videofile_choose)
    #     print("文件筛选器类型: ", videotype_choose)
    #     self.player.setMedia(QMediaContent(QUrl(videofile_choose)))
    #     print(self.player.availableMetaData())

    def on_btnAdd_clicked(self):
        ##      curPath=os.getcwd()     #获取系统当前目录
        ##      curPath=QDir.homePath()

        cur_path = os.path.abspath(__file__)
        dlgTitle = "비디오 파일 선택"
        filt = "*.mp4;;*.avi;;*.mov;;*.mkv;;All Video Files (*)"
        # path=".../"
        # file_name='...cvs'
        # path + file_name
        self.fileList, flt = QFileDialog.getOpenFileNames(self, dlgTitle, cur_path, filt)
        print('拿到视频文件：{}个！'.format(len(self.fileList)))
        count = len(self.fileList)
        if count < 1:
            return

        filename = self.fileList[0]
        fileInfo = QFileInfo(filename)  # 文件信息
        QDir.setCurrent(fileInfo.absolutePath())  # 重设当前路径

        for i in range(count):
            filename = self.fileList[i]
            fileInfo.setFile(filename)
            video = QMediaContent(QUrl.fromLocalFile(filename))
            self.playlist.addMedia(video)  # 添加播放媒体
            ##         basename=os.path.basename(filename)    #文件名和后缀
            basename = fileInfo.baseName()
            self.vLst.addItem(basename)  # 添加到界面文件列表

        if (self.player.state() != QMediaPlayer.PlayingState):
            self.playlist.setCurrentIndex(0)
            self.player.play()
            self.zLab.setText('Playing')

    def doBtn_clicked(self):

        # QtWidgets.QMessageBox.information(self.voBtn, "标题", "这是一个打开数据文件的按钮！")
        cur_path = os.path.abspath(__file__)
        self.datafile_choose, datatype_choose = QFileDialog.getOpenFileName(self,
                                                                            '데이터 파일 선택', cur_path,
                                                                            '*.csv;;*.txt;;*.xlsx;;*.json;;All TxT Files (*)')
        if datatype_choose:
            print('当前数据文件：\n', self.datafile_choose)
            datafile = open(self.datafile_choose, 'r', encoding='utf-8')
            with datafile:
                file_contents = datafile.read()
                self.dPly.clear()
                self.dPly.append(file_contents)
                self.dPly.scrollToAnchor('_id')
            datafile.close()

    def jouST(self, jID):

        if self.datafile_choose is None:
            print('我来！')
            rec_code = QMessageBox.information(self, '메시지 알림:',
                                               '데이터 파일이 열렸는지 확인해주세요!',
                                               QMessageBox.Yes | QMessageBox.No)
            print(rec_code)
            if rec_code == 65536:
                print('我去！')
            else:
                print('我再去！')
                self.doBtn_clicked()
        else:
            print('jeoul{}'.format(jID))
            print('拿到数据文件：\n', self.datafile_choose)
            self.chicken_df = pd.read_csv(self.datafile_choose, encoding='utf-8', sep=',')
            # print('chicken 변수 type:', type(self.chicken_df))
            col_names = self.chicken_df.columns.values
            # print(col_names)
            for index, value in enumerate(col_names):
                col_names[index] = value.replace(" ", "")
            self.chicken_df.drop(["_id", "farmID", "dongID", "temp", "humi", "co", "nh"], axis=1, inplace=True)
            chicken_single = self.chicken_df.groupby(['jeoulID'])
            self.j_df = chicken_single.get_group(jID)
            print(self.j_df.shape)
            j_time = pd.to_datetime(self.j_df.iloc[0].at['getTime'])
            j_star = j_time - 61 * pd.Timedelta(seconds=1)  # 修正数据一分钟延迟问题
            j_w = self.j_df.loc[:, 'w01':'w60']
            j_l2 = j_w.values.tolist()
            j_l1 = list(chain.from_iterable(j_l2))
            # print(len(j01_l1))
            # print(j01_l1)
            j_t = []
            for i in range(len(j_l1)):
                j_t.append(j_star + i * pd.Timedelta(seconds=1))
            # print(len(j01_t))
            # print(j01_t)
            j_s = list(map(str, j_t))
            # print(j01_s)
            j_d = {'getTime': j_s, 'j0{}'.format(jID): j_l1}
            # print(j01_d)
            j = pd.DataFrame(j_d).reset_index(drop=True)
            # print(j)
            j.set_index('getTime', inplace=True)
            self.dPly.clear()
            self.dPly.setText(j.to_string())
            self.dPly.scrollToAnchor('j0' + str(jID))
            self.d_file = j
            # print(self.d_file)
            # print(col_names)

    def j1Btn_clicked(self):
        # print(len(self.dPly.toPlainText()))
        self.jouST(jID=1)

    def j2Btn_clicked(self):

        self.jouST(jID=2)

    def j3Btn_clicked(self):

        self.jouST(jID=3)

    def stBtn_clicked(self):
        if self.player.state() == 1:
            self.player.pause()
            self.zLab.setText(' Pause')
        else:
            self.player.play()
            if self.player.duration() > 0:
                self.zLab.setText('Playing')

    def puBtn_clicked(self):
        self.player.stop()
        self.zLab.setText('End')

    def svBtn_clicked(self):

        # QtWidgets.QMessageBox.information(self.voBtn, "标题", "这是一个存储文件的按钮！")
        cur_path = os.path.abspath(__file__)
        self.fileName_save = QFileDialog.getExistingDirectory(self, '저장 폴더 선택', cur_path)
        if self.fileName_save == "":
            print("\n取消选择")
            return

        print("\n你选择的文件夹为:")
        print(self.fileName_save)
        # print(type(self.fileName_save))
        # print('self.fileName_save' in locals().keys())

    def sdBtn_clicked(self):

        if self.player.duration() == 0:
            rec_code = QMessageBox.information(self, '메시지 알림:',
                                               '비디오 파일이 열렸는지 확인해주세요!',
                                               QMessageBox.Yes | QMessageBox.No)
            if rec_code == 65536:
                print('我去！')
            else:
                self.on_btnAdd_clicked()
            # print(self.fileName_save)
        elif self.fileName_save is None:
            print('我来！')
            rec_code = QMessageBox.information(self, '메시지 알림:',
                                               '저장 폴더가 선택되었는지 확인하십시오!',
                                               QMessageBox.Yes | QMessageBox.No)
            print(rec_code)
            if rec_code == 65536:
                print('我去！')
            else:
                self.svBtn_clicked()
        else:
            screen = QGuiApplication.primaryScreen()
            cast_png = self.fileName_save + QDateTime.currentDateTime().toString("yyyy-MM-dd hh-mm-ss-zzz") + '.png'
            screen.grabWindow(self.vPly.winId()).save(cast_png)

    def zdBtn_clicked(self):

        # 将视频文件按照每秒一张图进行抓取图片
        global x_file
        if self.player.duration() == 0:
            rec_code = QMessageBox.information(self, '메시지 알림:',
                                               '비디오 파일이 열렸는지 확인해주세요!',
                                               QMessageBox.Yes | QMessageBox.No)
            if rec_code == 65536:
                print('我去！')
            else:
                self.on_btnAdd_clicked()
        elif self.datafile_choose is None:
            rec_code = QMessageBox.information(self, '메시지 알림:',
                                               '데이터 파일이 열렸는지 확인해주세요!',
                                               QMessageBox.Yes | QMessageBox.No)
            print(rec_code)
            if rec_code == 65536:
                print('我去！')
            else:
                self.doBtn_clicked()

        elif self.chicken_df is None:
            QMessageBox.information(self, '메시지 알림:',
                                    '"jou1~jou2~jou3"의 데이터 변환이 완료되었는지 확인해주세요!',
                                    QMessageBox.Yes | QMessageBox.No)

        elif self.jg is None:
            print('我来！')
            QMessageBox.information(self, '메시지 알림:',
                                    '스크린샷 간격(1초~30초~1분)이 선택되었는지 확인하십시오!',
                                    QMessageBox.Yes | QMessageBox.No)

        elif self.fileName_save is None:

            print('我来！')
            rec_code = QMessageBox.information(self, '메시지 알림:',
                                               '저장 폴더가 선택되었는지 확인하십시오!',
                                               QMessageBox.Yes | QMessageBox.No)
            print(rec_code)
            if rec_code == 65536:
                print('我去！')

            else:
                self.svBtn_clicked()
        else:
            # print(self.d_file)
            filepathes = self.fileList
            e_path = self.fileName_save + '//'
            self.d_file.index = pd.DatetimeIndex(self.d_file.index)
            # print(self.d_file.axes)
            # print(self.d_file)
            # 初始化一个VideoCapture对象
            # starttime = datetime.now()
            cap = cv2.VideoCapture()
            for filepath in filepathes:
                vopen = cap.open(filepath)
                if not vopen:
                    print("打开第{}个视频失败！".format(filepathes.index(filepath) + 1))
                # v_file = cv2.VideoCapture(v_path)  # 读入视频文件
                fps = round(cap.get(cv2.CAP_PROP_FPS))  # 视频帧计数间隔频率
                jfps = fps * self.jg
                print('当前截图帧率：', jfps)
                # size = (round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                #         round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                # print('Size:', size)
                # print(size[0] // 10)
                # print(size[1] // 10)
                # 新 resize
                # cap.set(cv2.CAP_PROP_FRAME_WIDTH, size[0] // 10)
                # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1] // 10)

                frames = round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                time = int(frames / fps)
                # filename = os.path.splitext(os.path.basename(filepath))[0]
                #     print("{}video fps:{}".format(filename, fps))
                #     print("{}video size:{}".format(filename, size))
                #     print("{}total time:{}s".format(filename, time))
                #     视频处理
                v_name = os.path.basename(filepath)
                #     vy_name = v_name.strip('.mp4')
                # t_name = v_name.split("_")[-1].strip('.mp4')
                t_name = os.path.splitext(v_name.split("_")[-1])[0]  # 全新安稳消除后缀法
                z_name = t_name[0:4] + '-' + t_name[4:6] + '-' + t_name[6:8] + ' ' + t_name[8:10] + ':' + t_name[
                                                                                                          10:12] + ':' + t_name[
                                                                                                                         12:14]
                t_time = datetime.strptime(z_name, "%Y-%m-%d %H:%M:%S")
                #     建立一个新的文件夹，名称为原文件夹名称后加上_frames
                frame_path = '{}{}_frames'.format(e_path, t_name)
                #     print(frame_path)
                if not os.path.exists(frame_path):
                    os.mkdir(frame_path)

                ds_time = list(self.d_file.index)[0]
                de_time = list(self.d_file.index)[-1]
                #     print(ds_time)
                e_time = t_time + time * pd.Timedelta(seconds=1)
                frametoStart = 1 * fps  # 不要自作聪明
                #     动态调整起始时间
                if e_time < ds_time:
                    print('视频时间在数据时间之外！err1')
                elif e_time < de_time:
                    if t_time >= ds_time:
                        x_file = self.d_file.loc[str(t_time):str(e_time)]  # 得到对应视频时间长度的重量数据
                        print('截图起始位置：', frametoStart)
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frametoStart)
                        # print('태그를 지정 할 수 있는 실제 동영상 길이:{}', str(e_time - t_time))
                    elif t_time <= ds_time:
                        x_file = self.d_file.loc[str(ds_time):str(e_time)]
                        # 设置起始帧
                        frametoStart = (ds_time - t_time).seconds * fps
                        print('截图起始位置：', frametoStart)
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frametoStart)
                        # print('현재 스크린샷의 시작 프레임:{}',frametoStart)
                        # print('태그를 지정할 수 있는 실제 동영상 길이:{}', str(e_time - ds_time))
                    # print(x_file)
                elif t_time > ds_time:
                    print('视频时间在数据时间之外！err2')
                sx_file = x_file.reset_index()  # 时间再现
                sx_file.index = sx_file.index + 1  # 从1开始！
                #     print(range(sx_file.index[0], sx_file.index[-1]))
                #     print(sx_file)
                v_success = cap.isOpened()
                d_success = not self.d_file.empty

                if v_success and d_success:  # 判断是否正常打开 vc.isOpened()
                    count = 0
                    ecount = 0
                    while True:

                        if cap.grab():
                            count = count + 1

                            if count % jfps == 1:
                                flag, image = cap.retrieve()
                                #         print(v_success), print(d_success)
                                #                 print(ecount)
                                if not flag:

                                    print('吁~吁~~~')
                                    continue

                                elif image is None:  # exist broken frame
                                    print("没拆到图~~~~~")
                                    continue

                                else:

                                    imagename = re.findall(r"\d+\.?\d*", str(sx_file.iloc[ecount * self.jg].tolist()))
                                    imagepath = frame_path + '//' + '_'.join(imagename) + '.png'
                                    # print(imagepath)

                                    look = cv2.imwrite(imagepath, image)  # 把路径改成全部为英文数字的、没有空格、没有中文的路径才可以保存图片！！！
                                    # endtime = datetime.now()
                                    # if look:
                                    #     print("Time:{}s".format((endtime - starttime).seconds))
                                    if not look:
                                        QMessageBox.information(self, '메시지 알림:',
                                                                '쓰기 오류입니다!',
                                                                QMessageBox.Yes | QMessageBox.No)
                                        continue
                                    ecount = ecount + 1
                                    if ecount > sx_file.index[-1] // self.jg:
                                        print("吁~~~~~")
                                        break
                                        #           cv2.waitKey(1)

                            # count = count + 1

                else:
                    if not v_success:
                        print('视频打开失败！')
                    elif not d_success:
                        print('数据打开失败！')
                    else:
                        print('未知错误2！')
                cap.release()
            QMessageBox.information(self, '메시지 알림:',
                                    '동영상 변환이 완료되었습니다!',
                                    QMessageBox.Yes | QMessageBox.No)

    def videoDoubleClicked(self, text):

        if self.player.duration() > 0:  # 开始播放后才允许进行全屏操作
            if self.videoFullScreen:
                self.player.setVideoOutput(self.vPly)
                self.videoFullScreenWidget.hide()
                self.videoFullScreen = False
            else:
                self.videoFullScreenWidget.show()
                self.player.setVideoOutput(self.videoFullScreenWidget)
                self.videoFullScreenWidget.setFullScreen(True)
                self.videoFullScreen = True


if __name__ == '__main__':
    print('cv2_dir:\n', cv2.__file__)
    app = QApplication(sys.argv)
    mainWindows = myMainWindow()
    mainWindows.show()
    sys.exit(app.exec_())
