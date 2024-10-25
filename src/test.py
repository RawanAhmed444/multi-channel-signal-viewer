import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from PyQt5.QtWidgets import QGraphicsEllipseItem

plot = pg.plot()
plot.setAspectLocked()

# Add polar grid lines
plot.addLine(x=0, pen=0.2)
plot.addLine(y=0, pen=0.2)
for r in range(2, 20, 2):
    circle = QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
    circle.setPen(pg.mkPen(0.2))
    plot.addItem(circle)

# make polar data
theta = np.linspace(0, 2 * np.pi, 100)
radius = np.random.normal(loc=10, size=100)

# Transform to cartesian and plot
x = radius * np.cos(theta)
y = radius * np.sin(theta)
plot.plot(x, y)

if __name__ == "__main__":
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
        QtGui.QGuiApplication.instance().exec_()
