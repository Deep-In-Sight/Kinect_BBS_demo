import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QFileDialog

class FileOpener(QWidget):
    def __init__(self):
        super().__init__()

        # Create a vertical layout
        layout = QVBoxLayout()

        # Create a button and add it to the layout
        self.openButton = QPushButton('Open', self)
        self.openButton.clicked.connect(self.openFileNameDialog)
        layout.addWidget(self.openButton)

        # Create a text edit to display the file content
        self.textEdit = QTextEdit(self)
        layout.addWidget(self.textEdit)

        # Set the layout on the application's window
        self.setLayout(layout)

    def openFileNameDialog(self):
        # Open file dialog and get the selected file path
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            # Read the file and set its content to the text edit
            with open(fileName, 'r') as file:
                self.textEdit.setText(file.read())

def main():
    app = QApplication(sys.argv)
    ex = FileOpener()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()  