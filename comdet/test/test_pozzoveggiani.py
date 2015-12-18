from __future__ import absolute_import
import matplotlib.pyplot as plt
import numpy as np
import scipy.io
import comdet.test.test_3d as test_3d
import comdet.pme.plane as plane
import comdet.pme.sampling as sampling
import comdet.pme.acontrario.plane as ac_plane


def run(subsampling=1):
    inliers_threshold = 0.5
    sigma = 1
    epsilon = 0

    name = 'PozzoVeggiani'
    dirname = '../data/PozzoVeggiani/'
    mat = scipy.io.loadmat(dirname + 'Results.mat')
    data = mat['Points'].T
    proj_mat = mat['Pmat']
    visibility = mat['Visibility']

    # Removing far away points for display
    keep = reduce(np.logical_and, [data[:, 0] > -10, data[:, 0] < 20,
                                   data[:, 2] > 10, data[:, 2] < 45])
    data = data[keep, :]
    visibility = visibility[keep, :]
    # Re-order dimensions and invert vertical direction to get upright data
    data[:, 1] *= -1
    data = np.take(data, [0, 2, 1], axis=1)
    proj_mat[:, 1, :] *= -1
    proj_mat = np.take(proj_mat, [0, 2, 1, 3], axis=1)

    # subsample the input points
    points_considered = np.arange(0, data.shape[0], subsampling)
    data = data[points_considered, :]
    visibility = visibility[points_considered, :]

    n_samples = data.shape[0] * 2
    sampler = sampling.GaussianLocalSampler(sigma, n_samples)
    ac_tester = ac_plane.LocalNFA(data, epsilon, inliers_threshold)

    ransac_gen = sampling.ransac_generator(plane.Plane, data, sampler,
                                           inliers_threshold)

    projector = test_3d.Projector(data, visibility, proj_mat, dirname, None)

    seed = 0
    # seed = np.random.randint(0, np.iinfo(np.uint32).max)
    print 'seed:', seed
    np.random.seed(seed)

    output_prefix = name + '_n{0}'.format(data.shape[0])
    test_3d.test(plane.Plane, data, output_prefix, ransac_gen, ac_tester,
                 projector=projector)


if __name__ == '__main__':
    run(subsampling=10)
    run(subsampling=5)
    run(subsampling=2)
    run(subsampling=1)
    plt.show()