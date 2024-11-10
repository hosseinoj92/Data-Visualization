import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QGraphicsOpacityEffect, QFrame
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QFont

def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("SplashScreen")

        # Remove window borders and make it transparent
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set the size of the splash screen
        self.setFixedSize(600, 400)

        # Variables for animation
        self.counter = 0
        self.n = 100  # Total steps for the progress bar
        self.initUI()

        # Timer for progress bar updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.loading)
        self.timer.start(30)  # Adjust the speed of the progress bar

    def initUI(self):
        # Main layout centered
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.main_layout)

        # Central box with rounded corners and semi-transparent black background
        self.central_box = QFrame(self)
        self.central_box.setFixedSize(600, 350)  # Adjust size as needed
        self.central_box.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 200);  /* Transparent black background */
                border-radius: 20px;
            }
        """)
        self.main_layout.addWidget(self.central_box)

        # Overlay layout to position widgets
        self.overlay_layout = QVBoxLayout(self.central_box)
        self.overlay_layout.setContentsMargins(20, 20, 20, 20)
        self.overlay_layout.setSpacing(10)
        self.overlay_layout.setAlignment(Qt.AlignCenter)

        # Logo label (properly centered and scaled)
        self.logo_label = QLabel(self.central_box)
        self.logo_label.setAlignment(Qt.AlignCenter)
        icon_path = self.get_resource_path('icon.png')  # Use your logo file

        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        else:
            print(f"Icon file not found at {icon_path}")

        self.overlay_layout.addWidget(self.logo_label)

        # Frame to hold the text in a transparent black background
        self.text_background_frame = QFrame(self.central_box)
        self.text_background_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 150);  /* More transparent black background */
                border-radius: 15px;
            }
        """)
        self.text_background_layout = QVBoxLayout(self.text_background_frame)
        self.text_background_layout.setAlignment(Qt.AlignCenter)
        self.overlay_layout.addWidget(self.text_background_frame)

        # Main text label inside the transparent black box
        self.main_text_label = QLabel("Data Wiz Pro", self.text_background_frame)
        self.main_text_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.main_text_label.setStyleSheet("color: white;")
        self.main_text_label.setAlignment(Qt.AlignCenter)
        self.text_background_layout.addWidget(self.main_text_label)

        # Sub text label inside the transparent black box
        self.sub_text_label = QLabel("By Hossein Ostovar", self.text_background_frame)
        self.sub_text_label.setFont(QFont("Segoe UI", 14))
        self.sub_text_label.setStyleSheet("color: white;")
        self.sub_text_label.setAlignment(Qt.AlignCenter)
        self.text_background_layout.addWidget(self.sub_text_label)

        # Version label inside the transparent black box
        self.version_label = QLabel("Version 3.5.1", self.text_background_frame)
        self.version_label.setFont(QFont("Segoe UI", 12))
        self.version_label.setStyleSheet("color: white;")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.text_background_layout.addWidget(self.version_label)

        # Spacer
        self.overlay_layout.addStretch()

        # Custom progress bar
        self.progress_bar = QProgressBar(self.central_box)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(200, 200, 200, 0.3);
                color: #fff;
                border-style: none;
                border-radius: 10px;
                text-align: center;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background-color: qlineargradient(
                    spread:pad,
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(85, 170, 255, 255),
                    stop:1 rgba(0, 85, 255, 255)
                );
            }
        """)
        self.overlay_layout.addWidget(self.progress_bar)

        # Start animations
        self.start_animations()

    def start_animations(self):
        # Logo fade-in animation
        self.logo_opacity_effect = QGraphicsOpacityEffect()
        self.logo_label.setGraphicsEffect(self.logo_opacity_effect)
        self.logo_opacity_effect.setOpacity(0)
        self.logo_fade_animation = QPropertyAnimation(self.logo_opacity_effect, b"opacity")
        self.logo_fade_animation.setDuration(1000)
        self.logo_fade_animation.setStartValue(0)
        self.logo_fade_animation.setEndValue(1)
        self.logo_fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Start the animation
        self.logo_fade_animation.start()

    def loading(self):
        # Update progress bar
        self.progress_bar.setValue(self.counter)
        if self.counter >= self.n:
            self.timer.stop()
            self.close()  # Close the splash screen when done
        self.counter += 1

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def get_resource_path(self, filename):
        return resource_path(os.path.join('gui', 'resources', filename))
