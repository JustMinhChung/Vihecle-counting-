import os
import csv
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QFileDialog, QMessageBox, QLabel, QGroupBox, QFormLayout,
    QDoubleSpinBox, QPushButton, QSlider, QFrame
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QImage

from app import config
from app.ui.styles import DARK_THEME_STYLE
from app.ui.widgets.video_widget import VideoWidget
from app.ui.widgets.log_table import LogTable
from app.core.video_worker import VideoWorker
from app.core.video_clipper import ClipperThread

class MainWindow(QMainWindow):
    """
    Main Application Window orchestrating the GUI widgets and background worker threads.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Gate Vehicle Monitor & Tracker")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_THEME_STYLE)
        
        # Core State
        self.video_path = None
        self.worker = None
        self.active_clippers = []
        
        # Setup UI
        self.init_ui()

    def init_ui(self):
        # 1. Create Actions & Toolbar
        toolbar = self.addToolBar("Controls")
        toolbar.setMovable(False)
        
        self.act_open = QAction("📂 Open Video", self)
        self.act_open.triggered.connect(self.select_video)
        toolbar.addAction(self.act_open)
        
        toolbar.addSeparator()
        
        self.act_play = QAction("▶ Play", self)
        self.act_play.setEnabled(False)
        self.act_play.triggered.connect(self.play_video)
        toolbar.addAction(self.act_play)
        
        self.act_pause = QAction("⏸ Pause", self)
        self.act_pause.setEnabled(False)
        self.act_pause.triggered.connect(self.pause_video)
        toolbar.addAction(self.act_pause)
        
        self.act_stop = QAction("⏹ Stop", self)
        self.act_stop.setEnabled(False)
        self.act_stop.triggered.connect(self.stop_video)
        toolbar.addAction(self.act_stop)
        
        toolbar.addSeparator()
        
        self.act_draw = QAction("✏ Draw Gate", self)
        self.act_draw.setCheckable(True)
        self.act_draw.setEnabled(False)
        self.act_draw.triggered.connect(self.toggle_drawing_mode)
        toolbar.addAction(self.act_draw)
        
        # 2. Main Central Layout Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)
        
        # Left Panel: Video display & Timeline Slider
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        self.video_widget = VideoWidget()
        self.video_widget.line_drawn.connect(self.on_gate_line_drawn)
        left_layout.addWidget(self.video_widget, 1) # Video stretches to occupy space
        
        # Timeline slider
        slider_layout = QHBoxLayout()
        self.lbl_time_current = QLabel("00:00")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setEnabled(False)
        self.slider.sliderPressed.connect(self.on_slider_pressed)
        self.slider.sliderReleased.connect(self.on_slider_released)
        self.lbl_time_total = QLabel("00:00")
        
        slider_layout.addWidget(self.lbl_time_current)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.lbl_time_total)
        left_layout.addLayout(slider_layout)
        
        splitter.addWidget(left_widget)
        
        # Right Panel: Sidebar Controls and Stats
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        
        # Group Box 1: Live Stats Counter
        stats_group = QGroupBox("GATE STATISTICS")
        stats_layout = QHBoxLayout(stats_group)
        
        in_widget = QWidget()
        in_layout = QVBoxLayout(in_widget)
        self.lbl_val_in = QLabel("0")
        self.lbl_val_in.setObjectName("stat_val_in")
        self.lbl_val_in.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_lbl_in = QLabel("VEHICLES IN")
        lbl_lbl_in.setObjectName("stat_lbl")
        lbl_lbl_in.setAlignment(Qt.AlignmentFlag.AlignCenter)
        in_layout.addWidget(self.lbl_val_in)
        in_layout.addWidget(lbl_lbl_in)
        
        out_widget = QWidget()
        out_layout = QVBoxLayout(out_widget)
        self.lbl_val_out = QLabel("0")
        self.lbl_val_out.setObjectName("stat_val_out")
        self.lbl_val_out.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_lbl_out = QLabel("VEHICLES OUT")
        lbl_lbl_out.setObjectName("stat_lbl")
        lbl_lbl_out.setAlignment(Qt.AlignmentFlag.AlignCenter)
        out_layout.addWidget(self.lbl_val_out)
        out_layout.addWidget(lbl_lbl_out)
        
        stats_layout.addWidget(in_widget)
        stats_layout.addWidget(out_widget)
        sidebar_layout.addWidget(stats_group)
        
        # Group Box 1.5: Detection Settings
        settings_group = QGroupBox("DETECTOR SETTINGS")
        settings_layout = QFormLayout(settings_group)
        
        self.spin_conf = QDoubleSpinBox()
        self.spin_conf.setRange(0.1, 0.9)
        self.spin_conf.setValue(config.CONFIDENCE_THRESHOLD)
        self.spin_conf.setSingleStep(0.05)
        self.spin_conf.setDecimals(2)
        self.spin_conf.valueChanged.connect(self.on_confidence_changed)
        
        settings_layout.addRow("Min Confidence:", self.spin_conf)
        sidebar_layout.addWidget(settings_group)
        
        # Group Box 2: Activity Log Grid
        log_group = QGroupBox("ACTIVITY LOG & TIMESTAMPS")
        log_layout = QVBoxLayout(log_group)
        
        self.log_table = LogTable()
        self.log_table.clip_requested.connect(self.on_clip_requested)
        log_layout.addWidget(self.log_table)
        
        export_btn = QPushButton("Export Log to CSV")
        export_btn.setObjectName("secondary_btn")
        export_btn.clicked.connect(self.export_csv_log)
        log_layout.addWidget(export_btn)
        
        sidebar_layout.addWidget(log_group, 1) # Log takes up maximum vertical space in sidebar
        
        # Group Box 3: Custom Video Clipper
        clipper_group = QGroupBox("MANUAL VIDEO CLIPPER")
        clipper_layout = QFormLayout(clipper_group)
        
        self.spin_start = QDoubleSpinBox()
        self.spin_start.setRange(0.0, 9999.0)
        self.spin_start.setSuffix(" sec")
        
        self.spin_duration = QDoubleSpinBox()
        self.spin_duration.setRange(1.0, 60.0)
        self.spin_duration.setValue(5.0)
        self.spin_duration.setSuffix(" sec")
        
        self.btn_export_clip = QPushButton("Export Custom Clip")
        self.btn_export_clip.clicked.connect(self.on_manual_clip_clicked)
        self.btn_export_clip.setEnabled(False)
        
        clipper_layout.addRow("Start Time:", self.spin_start)
        clipper_layout.addRow("Duration:", self.spin_duration)
        clipper_layout.addRow(self.btn_export_clip)
        
        sidebar_layout.addWidget(clipper_group)
        
        splitter.addWidget(sidebar)
        
        # Set proportions: Left (75%), Right (25%)
        splitter.setSizes([900, 300])
        
        # 3. Status Bar
        self.statusBar().showMessage("Ready. Open a video to start monitoring.")

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Surveillance Video", "", "Video Files (*.mp4 *.avi *.mkv *.mov)"
        )
        if file_path:
            self.stop_video()
            self.video_path = file_path
            
            # Setup worker thread
            self.worker = VideoWorker(self.video_path)
            self.worker.set_confidence(self.spin_conf.value())
            self.worker.frame_ready.connect(self.on_frame_ready)
            self.worker.progress_changed.connect(self.on_progress_changed)
            self.worker.event_detected.connect(self.on_event_detected)
            self.worker.fps_updated.connect(self.on_fps_updated)
            self.worker.playback_finished.connect(self.on_playback_finished)
            
            # Set default line configurations
            self.worker.set_gate_line(config.DEFAULT_LINE[0], config.DEFAULT_LINE[1])
            self.video_widget.rel_pt1 = config.DEFAULT_LINE[0]
            self.video_widget.rel_pt2 = config.DEFAULT_LINE[1]
            
            # Update UI
            self.slider.setRange(0, self.worker.total_frames - 1)
            self.slider.setValue(0)
            self.slider.setEnabled(True)
            self.btn_export_clip.setEnabled(True)
            self.act_play.setEnabled(True)
            self.act_draw.setEnabled(True)
            
            mins = int((self.worker.total_frames / self.worker.fps) // 60)
            secs = int((self.worker.total_frames / self.worker.fps) % 60)
            self.lbl_time_total.setText(f"{mins:02d}:{secs:02d}")
            self.lbl_time_current.setText("00:00")
            
            self.log_table.clear_logs()
            self.lbl_val_in.setText("0")
            self.lbl_val_out.setText("0")
            
            # Show first frame
            self.worker.seek_to_frame(0)
            
            # Start worker in background
            self.worker.start()
            self.worker.pause()  # Start paused
            
            self.statusBar().showMessage(f"Loaded: {os.path.basename(file_path)} | Press Play to run tracking.")

    def play_video(self):
        if self.worker:
            self.worker.resume()
            self.act_play.setEnabled(False)
            self.act_pause.setEnabled(True)
            self.act_stop.setEnabled(True)
            self.statusBar().showMessage("Processing stream...")

    def pause_video(self):
        if self.worker:
            self.worker.pause()
            self.act_play.setEnabled(True)
            self.act_pause.setEnabled(False)
            self.statusBar().showMessage("Paused")

    def stop_video(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.worker = None
            
        self.act_play.setEnabled(False)
        self.act_pause.setEnabled(False)
        self.act_stop.setEnabled(False)
        self.act_draw.setEnabled(False)
        self.act_draw.setChecked(False)
        self.slider.setEnabled(False)
        self.btn_export_clip.setEnabled(False)
        self.video_widget.original_pixmap = None
        self.video_widget.update_display()
        self.statusBar().showMessage("Stopped.")

    def toggle_drawing_mode(self, checked):
        if checked:
            self.video_widget.set_drawing_mode(True)
            self.statusBar().showMessage("Draw Line: Click and drag on the video to place the counting gate.")
        else:
            self.video_widget.set_drawing_mode(False)
            self.statusBar().showMessage("Drawing mode cancelled.")

    @Slot(float)
    def on_confidence_changed(self, val):
        config.CONFIDENCE_THRESHOLD = val
        if self.worker:
            self.worker.set_confidence(val)
        self.statusBar().showMessage(f"Confidence threshold set to {val:.2f}")

    @Slot(tuple, tuple)
    def on_gate_line_drawn(self, pt1, pt2):
        if self.worker:
            self.worker.set_gate_line(pt1, pt2)
            self.act_draw.setChecked(False)
            self.statusBar().showMessage("Counting gate line updated successfully!")

    @Slot(QImage, int)
    def on_frame_ready(self, q_img, frame_idx):
        self.video_widget.set_frame(q_img)

    @Slot(int, int)
    def on_progress_changed(self, current_frame, total_frames):
        # Only update if the user is not dragging the slider
        if not self.slider.isSliderDown():
            self.slider.setValue(current_frame)
            if self.worker:
                time_sec = current_frame / self.worker.fps
                mins = int(time_sec // 60)
                secs = int(time_sec % 60)
                self.lbl_time_current.setText(f"{mins:02d}:{secs:02d}")

    def on_slider_pressed(self):
        if self.worker:
            self.worker.pause()

    def on_slider_released(self):
        if self.worker:
            seek_val = self.slider.value()
            self.worker.seek_to_frame(seek_val)
            self.worker.resume()
            self.act_play.setEnabled(False)
            self.act_pause.setEnabled(True)

    @Slot(dict)
    def on_event_detected(self, event_data):
        # Update logs grid
        self.log_table.add_log(event_data)
        
        # Update visual counters
        if self.worker:
            self.lbl_val_in.setText(str(self.worker.tracker.in_count))
            self.lbl_val_out.setText(str(self.worker.tracker.out_count))
            
            # Briefly flash the status bar
            self.statusBar().showMessage(f"ALERT: Vehicle #{event_data['id']} crossed gate ({event_data['direction']})")

    @Slot(float)
    def on_fps_updated(self, fps):
        self.statusBar().showMessage(f"Processing Speed: {fps:.1f} FPS")

    def on_playback_finished(self):
        self.pause_video()
        self.statusBar().showMessage("Video finished.")

    # Video clipping handlers
    @Slot(dict)
    def on_clip_requested(self, event_data):
        if not self.video_path:
            return
            
        # Calculate clip ranges
        event_time = event_data['timestamp']
        start_time = max(0.0, event_time - config.CLIP_MARGIN_SECONDS)
        duration = config.CLIP_MARGIN_SECONDS * 2.0
        
        # Generate safe file name
        timestamp_slug = event_data['timestamp_str'].replace(':', '-').replace('.', '_')
        output_name = f"clip_vehicle_{event_data['id']}_{event_data['class_name']}_{timestamp_slug}.mp4"
        
        self.start_clipping(start_time, duration, output_name)

    def on_manual_clip_clicked(self):
        if not self.video_path:
            return
            
        start_time = self.spin_start.value()
        duration = self.spin_duration.value()
        
        output_name = f"manual_clip_{int(start_time)}s_to_{int(start_time + duration)}s.mp4"
        self.start_clipping(start_time, duration, output_name)

    def start_clipping(self, start_time, duration, output_name):
        self.statusBar().showMessage("Exporting video clip...")
        
        # Start clipper in a separate background thread
        clipper = ClipperThread(self.video_path, start_time, duration, output_name)
        clipper.finished_signal.connect(self.on_clip_finished)
        clipper.failed_signal.connect(self.on_clip_failed)
        
        # Keep reference to prevent garbage collection
        self.active_clippers.append(clipper)
        clipper.start()

    @Slot(str)
    def on_clip_finished(self, output_path):
        # Find and remove clipper thread reference
        sender = self.sender()
        if sender in self.active_clippers:
            self.active_clippers.remove(sender)
            
        QMessageBox.information(
            self, "Success", 
            f"Video clip saved successfully to:\n{output_path}"
        )
        self.statusBar().showMessage("Clip saved successfully.")

    @Slot(str)
    def on_clip_failed(self, error_msg):
        sender = self.sender()
        if sender in self.active_clippers:
            self.active_clippers.remove(sender)
            
        QMessageBox.warning(
            self, "Export Error", 
            f"Could not export video clip:\n{error_msg}"
        )
        self.statusBar().showMessage("Clip export failed.")

    def export_csv_log(self):
        if not self.log_table.events:
            QMessageBox.warning(self, "No Data", "There are no logs to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Log CSV File", os.path.join(config.LOGS_DIR, "gate_logs.csv"), "CSV Files (*.csv)"
        )
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["No.", "Timestamp", "Class Type", "Vehicle ID", "Direction"])
                    for i, ev in enumerate(self.log_table.events):
                        writer.writerow([i + 1, ev['timestamp_str'], ev['class_name'], ev['id'], ev['direction']])
                QMessageBox.information(self, "Export Successful", f"Log successfully exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"An error occurred while saving the file:\n{str(e)}")

    def closeEvent(self, event):
        # Clean up worker before closing
        self.stop_video()
        event.accept()
