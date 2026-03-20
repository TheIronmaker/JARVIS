import numpy as np
import pytest

from programs.Atom3D.shaders import VERTEX_SHADER, FRAGMENT_SHADER
from programs.Atom3D.main import Atom, config


def test_spherical_to_cartesian_known():
    atom = Atom(config)
    r = np.array([1.0])
    theta = np.array([np.pi / 2.0])
    phi = np.array([0.0])
    cart = atom.sphericalToCartesian(r, theta, phi)
    assert cart.shape == (1, 3)
    assert pytest.approx(cart[0, 0]) == 1.0  # x
    assert pytest.approx(cart[0, 1]) == 0.0  # y
    assert pytest.approx(cart[0, 2]) == 0.0  # z


def test_sample_functions_reproducible():
    atom1 = Atom({**config, 'orbital': {**config['orbital'], 'N': 50}})
    np.random.seed(42)
    r1 = atom1.sampleR().copy()
    theta1 = atom1.sampleTheta().copy()
    phi1 = atom1.samplePhi().copy()

    atom2 = Atom({**config, 'orbital': {**config['orbital'], 'N': 50}})
    np.random.seed(42)
    r2 = atom2.sampleR().copy()
    theta2 = atom2.sampleTheta().copy()
    phi2 = atom2.samplePhi().copy()

    assert np.allclose(r1, r2)
    assert np.allclose(theta1, theta2)
    assert np.allclose(phi1, phi2)


def test_inferno_and_generate_particles_shape_and_range():
    N = 100
    test_config = {**config, 'orbital': {**config['orbital'], 'N': N}, 'electron_r': 2.0}
    atom = Atom(test_config)

    np.random.seed(0)
    atom.generateParticles()

    assert len(atom.particles) == N

    for pos, col in atom.particles:
        # pos is length-3 vector
        assert pos.shape == (3,)
        # color is length-4 RGBA with values in [0,1]
        assert col.shape == (4,)
        assert np.all(col >= 0.0) and np.all(col <= 1.0)
        assert col[3] == pytest.approx(1.0)


def test_inferno_extremes():
    atom = Atom({**config, 'electron_r': 2.0, 'orbital': {**config['orbital'], 'N': 2}})
    r = np.array([0.0, atom.electron_r])
    theta = np.array([0.0, 1.0])
    phi = np.array([0.0, 1.0])
    colors = atom.inferno(r, theta, phi)
    assert colors.shape == (2, 4)
    assert np.all(colors >= 0.0) and np.all(colors <= 1.0)
    assert colors[0, 3] == pytest.approx(1.0)
    assert colors[1, 3] == pytest.approx(1.0)

def test_inferno():
    atom = Atom({**config, 'electron_r': 2.0, 'orbital': {**config['orbital'], 'N': 2}})

    r = np.array([0.5, 1.5])
    theta = np.array([0.5, 1.0])
    phi = np.array([0.5, 1.0])
    colors = atom.inferno(r, theta, phi)
    assert colors.shape == (2, 4)
    assert np.all(colors >= 0.0) and np.all(colors <= 1.0)
    assert colors[0, 3] == pytest.approx(1.0)
    assert colors[1, 3] == pytest.approx(1.0)



atom = Atom({**config, 'electron_r': 2.0, 'orbital': {**config['orbital'], 'N': 2}})


a0 = 1.0
def test_inferno_array(r, theta, phi, n, l, m):
    rho = 2 * r / (n * a0)
    


# Test data for inferno array test - for r, theta, phi, n, l, m
data = np.array([
    (1.2, 0.5, 0.5, 1, 0, 0),
    (1.0, 1.0, 1.0, 2, 0, 0),
    (3.0, 1.5, 1.2, 3, 0, 1)
])

#result = [atom.inferno(*data[i]) for i in range(len(data))]
#print(*result)

print("sampleTheta:", atom.samplePhi(10))