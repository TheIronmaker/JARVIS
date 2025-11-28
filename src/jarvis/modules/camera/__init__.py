from .camera import Camera

import subprocess
import sys
import os

def start_instance():
    """Launch the standalone camera viewer as a separate Python process."""

    script_path = os.path.join(
        os.path.dirname(__file__),
        "camera_viewer.py"
    )

    return subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )