import sys
import warnings
from gui import *
warnings.filterwarnings('ignore')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    application = Application()
    sys.exit(app.exec_())