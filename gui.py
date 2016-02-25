import sys, logger, signal
import global_const, scrape
from PyQt4 import QtGui, QtCore

signal.signal(signal.SIGINT, signal.SIG_DFL)

class ShadowGUI(QtGui.QWidget):
    def __init__(self):
        super(ShadowGUI, self).__init__()
        self.initUI()

    def initUI(self):
        #Define scrape button properties
        self.scrape_btn = QtGui.QPushButton('Scrape')
        self.scrape_btn.clicked.connect(self.begin_scraping)
        # scrape_btn.resize(scrape_btn.sizeHint())
        # scrape_btn.move(200, 200)

        #Define cancel button properties
        cancel_btn = QtGui.QPushButton('Cancel', self)
        cancel_btn.clicked.connect(self.closeEvent)
        # cancel_btn.resize(cancel_btn.sizeHint())
        # cancel_btn.move(300, 200)

        name = QtGui.QLabel('Enter location title:')
        link = QtGui.QLabel('Enter shadow url:')
        folder = QtGui.QPushButton('Select folder', self)
        folder.clicked.connect(self.showDialog)

        self.folderEdit = QtGui.QLineEdit()
        self.folderEdit.setPlaceholderText('Results will be saved in the selected folder')

        linkEdit = QtGui.QLineEdit()
        linkEdit.setPlaceholderText('https://humboldt.craigslist.org/search/apa')
        linkEdit.textChanged[str].connect(self.text_changed)

        nameEdit = QtGui.QComboBox(self)
        nameEdit.setEditable(True)
        nameEdit.setDuplicatesEnabled(False)
        nameEdit.setInsertPolicy(QtGui.QComboBox.InsertAtTop)
        names_list = sorted(global_const.shadow_db.collection_names())
        nameEdit.addItems(names_list)
        nameEdit.activated[str].connect(self.combo_chosen)
        nameEdit.editTextChanged[str].connect(self.combo_chosen)

        #Create file dialog
        # self.textEdit = QtGui.QTextEdit()
        # self.setCentralWidget(self.textEdit)
        # openFolder = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
        # openFolder.setShortcut('Ctrl+O')
        # openFolder.setStatusTip('Open new folder')
        # openFolder.triggered.connect(self.showDialog)

        #Set layout for buttons
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.scrape_btn)
        hbox.addWidget(cancel_btn)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(name, 1, 0)
        grid.addWidget(nameEdit, 1, 1)
        grid.addWidget(link, 2, 0)
        grid.addWidget(linkEdit, 2, 1, 1, 2)
        grid.addWidget(folder, 3, 0)
        grid.addWidget(self.folderEdit, 3, 1, 1, 2)
        grid.addLayout(vbox, 4, 2)

        # self.setLayout(vbox)
        self.setLayout(grid)

        #self.statusBar().showMessage("Ready for scraping!")
        self.resize(200, 200)
        self.center()
        self.setWindowTitle('Shadow Market Scraper')
        self.show()

    #Handle text change in combo box to update global city name
    def combo_chosen(self, text):
        global_const.city_name = str(text)
        print global_const.city_name

    def text_changed(self, text):
        global_const.city_url = str(text)
        print global_const.city_url


    #Create message box to respond to cancel action
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
        'Are you sure you want to cancel scraping',
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            # event.accept()
            QtCore.QCoreApplication.instance().quit()
        else:
            event.ignore()

    #Center screen on monitor
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def begin_scraping(self):
        if global_const.city_name == "":
            QtGui.QMessageBox.warning(self, 'No location title!',
            'Enter a location title',
            QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)
        elif global_const.city_url == "":
            QtGui.QMessageBox.warning(self, 'No location url!',
            'Enter a url corresponding to the location',
            QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)
        elif global_const.csv_directory == "":
            QtGui.QMessageBox.warning(self, 'No results folder selected!',
            'Select a folder to save the scraping results',
            QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)
        else:
            #add final check
            #ensure link in http format and folder in correct form
            reply = QtGui.QMessageBox.warning(self, 'Check values!',
            'Scraping link: ' + global_const.city_url +
            '\nLocation title: ' + global_const.city_name +
            '\nResults folder: ' + global_const.csv_directory + '\nIs this correct?',
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No, QtGui.QMessageBox.NoButton)
            if reply == QtGui.QMessageBox.Yes:
                self.scrape_btn.setEnabled(False)
                scrape.main()
                QtCore.QCoreApplication.instance().quit()

    def showDialog(self):
        fname = QtGui.QFileDialog.getExistingDirectory(self, "Open folder",
        "/home", QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks)
        if fname:
            self.folderEdit.setText(fname)
            global_const.csv_directory = str(fname)
            print global_const.csv_directory
        else:
            self.folderEdit.setText("No folder selected. Please select a folder to save scraping results.")

def main():
    try:
        scrape.set_up()
        app = QtGui.QApplication(sys.argv)
        view = ShadowGUI()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        QtCore.QCoreApplication.instance().quit()
    except Exception as e:
        print "Error: {}".format(e)
        print "Well something went wrong, so I will crash not so gracefully"
        QtCore.QCoreApplication.instance().quit()
    finally:
        QtCore.QCoreApplication.instance().quit()

if __name__ == '__main__':
    main()
