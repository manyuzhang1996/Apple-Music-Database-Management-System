import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from PyQt5.QtGui import QWindow
from updateDialog import updateDialog
from queryDialog import queryDialog


class AppWindow(QWindow):
    """
    The main application window.
    """

    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()

        self.ui = uic.loadUi('AppWindow.ui')
        self.ui.show();

        # Update dialog.
        self._update_dialog = updateDialog()
        self.ui.update_button.clicked.connect(self._show_update_dialog)

        # Query dialog.
        self._query_dialog = queryDialog()
        self.ui.query_button.clicked.connect(self._show_query_dialog)

    def _show_update_dialog(self):
        """
        Show the update dialog.
        """
        self._update_dialog.show_dialog()

    def _show_query_dialog(self):
        """
        Show the query dialog.
        """
        self._query_dialog.show_dialog()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = AppWindow()
    sys.exit(app.exec_())
#%%
