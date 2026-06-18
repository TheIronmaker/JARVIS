# Modules
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# System Modules
from matricies import dh_matrix


def display_3D(pos, rot, colors=None):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_aspect('equal', adjustable='box')

    qs = [ax.quiver(
        *pos,
        *rot,
        length=1,
        normalize=True,
        color=colors[i],
        linewidth=2,
        pivot='tail')
        for i in range(3)]

    slider_axs = [plt.axes([0.2, 0.1*(i+1)/2, 0.6, 0.03]) for i in range(3)]

    sliders = [Slider(
        ax=slider_axs[i],
        label=f"Theta {i}",
        valmin=-2*3.14,
        valmax=2*3.14
    ) for i in range(3)]

    def update(val):
        for i, sym in enumerate([theta1, theta2, theta3]):
            angles[sym] = sliders[i].val
        
        x, y, z = get_position(T03, angles)
        for q in qs:
            q.set_offsets(np.column_stack((x, y, z)))

        fig.canvas.draw_idle()

    for slider in sliders:
        slider.on_changed(update)

    # Label axes and title
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    ax.set_title('3D Surface Plot')

    plt.show()


""" Working with DH principles, and not Screw Theory / PoE (Product of Exponentials) """

# The position (X, Y, Z) is in the top right corner of the matrix, and is a 3x1 vector
#foot_pos = [v.evalf(5) for v in list((T03[:3, 3].subs(angles)))]
def get_position(T03, angles):
    return [float(i) for i in [v.evalf(5)
        for v in list(
        (T03[:3, 3].subs(angles))
    )]]

def get_position_compact(T03, angles): return [float(i) for i in [v.evalf(5) for v in list((T03[:3, 3].subs(angles)))]]

# The rotation of the foot is in the top left 3x3 submatrix of T03
#foot_rot = T03[:3, :3]
def get_rot(T03, angles):
    pass

# Servo Angles
theta1, theta2, theta3 = sp.symbols('theta1 theta2 theta3')
angles = {theta1: 0, theta2: sp.pi/4, theta3: -sp.pi/4}

# Create DH Matrices (Chain Links) for Forward Kinematics
T01 = dh_matrix(a=2,  d=0, alpha=sp.pi/2, theta=theta1)
T12 = dh_matrix(a=10, d=0, alpha=0, theta=theta2)
T23 = dh_matrix(a=8,  d=0, alpha=0, theta=theta3)
T03 = T01 @ T12 @ T23 # Chain by multiplication

# Angles to Positions
foot_pos = get_position(T03, angles)
foot_rot = get_rot(T03, angles)

display_3D(foot_pos,
           np.eye(3), # Foot rot - future
           ['red', 'green', 'blue'])

