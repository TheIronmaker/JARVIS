import moderngl

from PySide6 import QtGui, QtOpenGLWidgets
from PySide6.QtCore import Qt
from PySide6 import QtGui

from jarvis_app.tools.simple_app import SimpleApp
from jarvis_core.utils.services.path_resolver import PathResolver, FileManager
from jarvis_core.databus.subscriber import Subscriber

class ModernGLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Changes color? Investigate.
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop)
        self.ctx = None

    def initializeGL(self):
        self.ctx = moderngl.create_context()

        # Transparent Window - None of these were required... Maybe while rendering?
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
        self.ctx.clear(red=0.5, green=0.7, blue=1.0, alpha=1.0)
        self.ctx.disable(moderngl.GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        if self.ctx:
            self.ctx.viewport = (0, 0, w, h)

    def paintGL(self):
        if not self.ctx:
            return

        self.ctx.screen.use()
        self.ctx.clear(0.035, 0.118, 0.149, 0.2)

        # --- ModernGL rendering code goes here - e.g. vao---

def win_format():
    # Setup surface format for ModernGL compatibility - Required
    fmt = QtGui.QSurfaceFormat()
    fmt.setVersion(3, 3) # Minimum OpenGL version for ModernGL
    fmt.setProfile(QtGui.QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    fmt.setAlphaBufferSize(8) # Recommended, not needed
    QtGui.QSurfaceFormat.setDefaultFormat(fmt)

resolver = PathResolver()
print(resolver.resolve_path("config", "YAML", "config"))

if __name__ == "__main__":
    win_format()
    app = SimpleApp()
    app.launch({
        "title": "Test App for ModernGL",
        "central_widget": ModernGLWidget()
    })