import sys, cv2, os, time, csv
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QFileDialog,
                               QSlider, QTableWidget, QTableWidgetItem, QHeaderView,
                               QFrame, QTextEdit, QProgressBar)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QImage, QPixmap
from ultralytics import YOLO

STYLE_V30 = """
QMainWindow { background-color: #FDFBF6; }
QWidget { font-family: 'Microsoft YaHei'; font-weight: bold; }
#LeftPanel { background-color: #333333; border-radius: 20px; }
#PanelTitle { color: white; font-size: 16px; }
#LeftPanel QPushButton { background-color: #9CAF88; color: #333333; border-radius: 10px; padding: 12px; border: none; text-align: left; }
#MidPanel { background-color: #EFEFEF; border-radius: 20px; border: 1px solid #DDD; }
#MonitorBar { background-color: #222222; border-radius: 15px; color: #9CAF88; font-family: 'Consolas'; }
#MidTitle { color: #98A9BD; font-size: 15px; }
#RightPanel { background-color: #D4B0B5; border-radius: 20px; color: black; }
#RightSectionTitle { color: #000000; font-size: 16px; border-left: 5px solid #000000; padding-left: 10px; margin-bottom: 5px; }
#BigNum { font-size: 55px; color: #000; }
#DataCard { background-color: rgba(255,255,255,0.7); border-radius: 15px; border: none; }
QProgressBar { border: none; background: rgba(0,0,0,0.1); height: 12px; border-radius: 6px; }
QProgressBar::chunk { background-color: #9CAF88; border-radius: 6px; }
"""


class YoloHistoryWorkstation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO目标检测模型")
        self.resize(1700, 950)
        self.setStyleSheet(STYLE_V30)
        self.model = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_engine)
        self.source_path = None
        self.detection_results = []
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)

        # --- 左侧面板 ---
        lp = QFrame();
        lp.setObjectName("LeftPanel");
        lp.setFixedWidth(300)
        lp_lay = QVBoxLayout(lp)
        lp_lay.addWidget(QLabel("📂 资产管理", objectName="PanelTitle"))
        self.btn_model = QPushButton("📥 载入权重模型 (.pt)");
        self.btn_model.clicked.connect(self.load_model)
        lp_lay.addWidget(self.btn_model)
        for n, t in [("🖼️ 图片分析", 'img'), ("🎞️ 视频检测", 'vid'), ("📁 目录扫描", 'dir')]:
            btn = QPushButton(n);
            btn.clicked.connect(lambda chk=False, s=t: self.set_source(s))
            lp_lay.addWidget(btn)
        self.btn_export = QPushButton("📊 导出全部历史 (CSV)")
        self.btn_export.setStyleSheet("background-color: #D4B0B5; color: black;");
        self.btn_export.clicked.connect(self.export_csv)
        lp_lay.addWidget(self.btn_export)
        lp_lay.addSpacing(20);
        lp_lay.addWidget(QLabel("⚙️ 引擎参数", objectName="PanelTitle"))
        self.s_conf = self.add_slider(lp_lay, "置信度阈值")
        self.s_iou = self.add_slider(lp_lay, "重叠度(IoU)")
        lp_lay.addStretch()
        self.btn_run = QPushButton("▶ 启动分析引擎")
        self.btn_run.setStyleSheet("background-color: #9CAF88; font-size: 18px; height: 50px;");
        self.btn_run.clicked.connect(self.toggle_engine)
        lp_lay.addWidget(self.btn_run)
        main_lay.addWidget(lp, 2)

        # --- 中间面板 ---
        mid_lay = QVBoxLayout()
        vp = QFrame();
        vp.setObjectName("MidPanel")
        v_lay = QVBoxLayout(vp)
        v_lay.addWidget(QLabel("🎥 实时分析预览", objectName="MidTitle"))
        self.display = QLabel("等待数据...");
        self.display.setAlignment(Qt.AlignCenter);
        self.display.setMinimumSize(800, 600)
        v_lay.addWidget(self.display)
        mon = QFrame();
        mon.setObjectName("MonitorBar");
        mon.setFixedHeight(60)
        m_lay = QHBoxLayout(mon)
        self.lbl_fps = QLabel("FPS: --");
        self.lbl_res = QLabel("RES: --");
        self.lbl_ms = QLabel("MS: --")
        for l in [self.lbl_fps, self.lbl_res, self.lbl_ms]: m_lay.addWidget(l)
        mid_lay.addWidget(vp, 9);
        mid_lay.addWidget(mon, 1)
        main_lay.addLayout(mid_lay, 6)

        # --- 右侧面板 ---
        rp_lay = QVBoxLayout()
        stat = QFrame();
        stat.setObjectName("RightPanel");
        stat.setFixedHeight(230)
        s_lay = QVBoxLayout(stat)
        s_lay.addWidget(QLabel("📊 当前帧目标数", objectName="RightSectionTitle"))
        self.v_num = QLabel("0");
        self.v_num.setObjectName("BigNum");
        s_lay.addWidget(self.v_num)
        self.p_conf = QProgressBar();
        s_lay.addWidget(self.p_conf)

        tc = QFrame();
        tc.setObjectName("DataCard")
        t_lay = QVBoxLayout(tc)
        t_lay.addWidget(QLabel("📜 历史检测清单 (累计)", objectName="RightSectionTitle"))
        self.table = QTableWidget(0, 3)  # 改为3列
        self.table.setHorizontalHeaderLabels(["来源文件", "类别", "置信度"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t_lay.addWidget(self.table)

        lc = QFrame();
        lc.setObjectName("DataCard");
        lc.setFixedHeight(180)
        l_lay = QVBoxLayout(lc)
        l_lay.addWidget(QLabel("📟 系统日志", objectName="RightSectionTitle"))
        self.log_box = QTextEdit();
        self.log_box.setReadOnly(True);
        self.log_box.setStyleSheet("background: #222; color: #9CAF88;")
        l_lay.addWidget(self.log_box)

        rp_lay.addWidget(stat);
        rp_lay.addWidget(tc);
        rp_lay.addWidget(lc)
        main_lay.addLayout(rp_lay, 2)

    def process(self, frame, filename="Live"):
        if frame is None: return
        t1 = time.time()
        res = self.model(frame, conf=self.s_conf.value() / 100, iou=self.s_iou.value() / 100, verbose=False)[0]
        t2 = time.time()

        # 更新监控数据
        self.lbl_fps.setText(f"FPS: {1 / (t2 - t1 + 0.0001):.1f}")
        self.lbl_res.setText(f"RES: {frame.shape[1]}x{frame.shape[0]}")
        self.v_num.setText(str(len(res.boxes)))

        # 插入检测结果到历史
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")
        for b in res.boxes:
            cls = res.names[int(b.cls[0])]
            conf = f"{float(b.conf[0]):.2f}"
            self.detection_results.append([timestamp, filename, cls, conf])

            self.table.insertRow(0)  # 始终插入到第一行
            self.table.setItem(0, 0, QTableWidgetItem(filename))
            self.table.setItem(0, 1, QTableWidgetItem(cls))
            self.table.setItem(0, 2, QTableWidgetItem(conf))

        # 渲染图片
        ann = res.plot();
        rgb = cv2.cvtColor(ann, cv2.COLOR_BGR2RGB)
        qi = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.shape[1] * 3, QImage.Format_RGB888)
        self.display.setPixmap(
            QPixmap.fromImage(qi).scaled(self.display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def update_engine(self):
        if self.source_type == 'vid':
            r, f = self.cap.read()
            if r:
                self.process(f, "Video")
            else:
                self.timer.stop()
        elif self.source_type == 'dir':
            if self.idx < len(self.files):
                fpath = self.files[self.idx]
                fname = os.path.basename(fpath)
                self.process(cv2.imread(fpath), fname)
                self.idx += 1
            else:
                self.timer.stop();
                self.log("✅ 批量扫描完成")

    # --- 其余基础功能保持不变 ---
    def add_slider(self, lay, name):
        lay.addWidget(QLabel(name, styleSheet="color: #AAA; font-size: 11px;"))
        s = QSlider(Qt.Horizontal);
        s.setRange(0, 100);
        s.setValue(25);
        lay.addWidget(s);
        return s

    def log(self, m):
        self.log_box.append(f"[{QDateTime.currentDateTime().toString('HH:mm:ss')}] {m}")

    def load_model(self):
        p, _ = QFileDialog.getOpenFileName(self, "权重", "", "*.pt")
        if p: self.model = YOLO(p); self.btn_model.setText(f"✅ {os.path.basename(p)}")

    def set_source(self, t):
        self.source_type = t
        if t == 'img':
            self.source_path, _ = QFileDialog.getOpenFileName(self)
        elif t == 'vid':
            self.source_path, _ = QFileDialog.getOpenFileName(self)
        elif t == 'dir':
            self.source_path = QFileDialog.getExistingDirectory(self)

    def toggle_engine(self):
        if not self.model or not self.source_path: return
        if self.source_type == 'dir':
            self.files = [os.path.join(self.source_path, f) for f in os.listdir(self.source_path) if
                          f.lower().endswith(('.jpg', '.png'))]
            self.idx = 0;
            self.timer.start(100)
        elif self.source_type == 'vid':
            self.cap = cv2.VideoCapture(self.source_path);
            self.timer.start(30)
        else:
            self.process(cv2.imread(self.source_path), os.path.basename(self.source_path))

    def export_csv(self):
        if not self.detection_results: return
        p, _ = QFileDialog.getSaveFileName(self, "保存", "History.csv", "*.csv")
        if p:
            with open(p, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(["时间", "文件名", "类别", "置信度"])
                csv.writer(f).writerows(self.detection_results)
            self.log("✅ CSV已导出")


if __name__ == "__main__":
    app = QApplication(sys.argv);
    w = YoloHistoryWorkstation();
    w.show();
    sys.exit(app.exec())