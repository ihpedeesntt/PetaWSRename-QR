import shutil
import cv2
import pyzbar.pyzbar as pyzbar
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QDesktopWidget, QPushButton, QMessageBox, QLineEdit, \
    QLabel, QFileDialog, QProgressBar
from pathlib import Path
import sys
from glob import glob
import os
import pandas as pd

path_input = ''
path_output = ''


class PetaWSRename(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('PyQt File Dialog')
        self.setGeometry(100, 400, 600, 100)

        layout = QGridLayout()
        self.setLayout(layout)

        # Input
        dir_btn_input = QPushButton('Browse')
        dir_btn_input.clicked.connect(self.open_dir_input_dialog)
        self.dir_input_name = QLineEdit()
        self.dir_input_name.setReadOnly(True)

        # Output
        dir_btn_output = QPushButton('Browse')
        dir_btn_output.clicked.connect(self.open_dir_output_dialog)
        self.dir_output_name = QLineEdit()
        self.dir_output_name.setReadOnly(True)

        # Button Process
        self.proses_btn = QPushButton('Proses')
        self.proses_btn.clicked.connect(self.proses)

        # Progres Bar
        self.progressBar = QProgressBar()
        self.progressBar.setProperty("value", 0)

        # Proses
        self.prosesSekarang = QLabel()
        self.prosesSekarang.setText("Belum ada proses")

        # Layout
        layout.addWidget(QLabel('Folder Input'), 1, 0, 1, 1)
        layout.addWidget(self.dir_input_name, 1, 1, 1, 1)
        layout.addWidget(dir_btn_input, 1, 2, 1, 1)

        layout.addWidget(QLabel('Folder Output'), 2, 0, 1, 1)
        layout.addWidget(self.dir_output_name, 2, 1, 1, 1)
        layout.addWidget(dir_btn_output, 2, 2, 1, 1)

        layout.addWidget(QLabel('Proses'), 3, 0, 1, 1)
        layout.addWidget(self.prosesSekarang, 3, 1, 1, 2)

        layout.addWidget(QLabel('Progress'), 4, 0, 1, 1)
        layout.addWidget(self.progressBar, 4, 1, 1, 2)

        layout.addWidget(self.proses_btn, 5, 2, 1, 1)

        self.setWindowTitle('PetaWS-QRCodeReader')
        self.center()
        self.show()

    def open_dir_input_dialog(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select a Directory")
        if dir_name:
            global path_input
            path = Path(dir_name)
            path_input = str(path)
            self.dir_input_name.setText(path_input)
            print(path_input)

    def open_dir_output_dialog(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select a Directory")
        if dir_name:
            global path_output
            path = Path(dir_name)
            path_output = str(path)
            self.dir_output_name.setText(path_output)
            print(path_output)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Keluar', 'Apakah Anda yakin ingin keluar?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    @staticmethod
    def is_folder_empty(folder_path):
        if not os.path.exists(folder_path):
            return True

        if not os.listdir(folder_path):
            return True
        return False

    def create_folder_if_not_exists(self, folder_path):
        if os.path.exists(folder_path):
            return True
        try:
            os.makedirs(folder_path)
            return True
        except OSError as e:
            print(e)
            return False

    def copy_and_rename_file(self, source_file_path, destination_file_path):
        if not os.path.exists(source_file_path):
            return False
        try:
            shutil.copy(source_file_path, destination_file_path)
            os.rename(destination_file_path, destination_file_path)
            return True
        except Exception as e:
            print(e)
            return False

    def get_file_extension(self, file_path):
        if not os.path.exists(file_path):
            return ""

        file_name, file_extension = os.path.splitext(file_path)
        return file_name, file_extension

    def detect_qr_code(self, image_path):
        image = cv2.imread(image_path)
        qr_codes = pyzbar.decode(image)
        return qr_codes

    def proses(self):
        if path_input == '' or path_output == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Folder Input/Output")
            msg.setInformativeText('Harap memilih folder output dan input terlebih dahulu')
            msg.setWindowTitle("Galat")
            msg.exec_()
            return

        import os
        if not self.is_folder_empty(path_output):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Folder Output")
            msg.setInformativeText('Untuk folder output harap dibuat kosong!')
            msg.setWindowTitle("Galat")
            msg.exec_()
            return

        types = ('*.jpg', '*.JPEG', '*.jpeg', '*.JPG')
        list_images = []
        for files in types:
            list_images.extend(glob(path_input + os.path.sep + files))

        if len(list_images) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Folder Input")
            msg.setInformativeText('Untuk folder input yang Anda pilih tidak terdapat file gambar!')
            msg.setWindowTitle("Galat")
            msg.exec_()
            return

        list_log = []
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(len(list_images))
        counter = 0
        for i in sorted(list_images):
            counter = counter + 1
            file_name, file_extension = self.get_file_extension(i)
            file_name = file_name.split('/')[-1]

            self.prosesSekarang.setText(file_name)
            self.progressBar.setValue(counter)

            qr_codes = self.detect_qr_code(i)

            if len(qr_codes) == 0:
                list_log.append([file_name, "Gagal", "Tidak ada QR ditemukan!"])
            else:
                for qr_code in qr_codes:
                    idsls = qr_code.data.decode()

                    idkab = idsls[:4]
                    kdkec = idsls[4:7]
                    kddesa = idsls[7:10]

                    path_folder_destination = path_output + os.path.sep + idkab + os.path.sep + kdkec + os.path.sep + \
                                              kddesa
                    path_file_destination = path_folder_destination + os.path.sep + idsls + file_extension
                    self.create_folder_if_not_exists(path_folder_destination)
                    self.copy_and_rename_file(source_file_path=i, destination_file_path=path_file_destination)
                    list_log.append([file_name, "Berhasil", ""])

        df_result = pd.DataFrame(list_log, columns=[
            "Nama File",
            "Status",
            "Info"
        ])

        df_result.to_excel(path_output + os.path.sep + "Hasil.xlsx", index=False)
        self.prosesSekarang.setText("Proses telah selesai harap cek folder output!")
        self.proses_btn.setDisabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = PetaWSRename()
    win.show()
    sys.exit(app.exec_())
