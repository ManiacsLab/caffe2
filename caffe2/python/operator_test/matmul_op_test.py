from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from hypothesis import given
import hypothesis.strategies as st

from caffe2.python import core
import caffe2.python.hypothesis_test_util as hu


class TestMatMul(hu.HypothesisTestCase):
    @given(M=st.integers(min_value=1, max_value=10),
           K=st.integers(min_value=1, max_value=10),
           N=st.integers(min_value=1, max_value=10),
           trans_a=st.booleans(),
           trans_b=st.booleans(),
           **hu.gcs)
    def test_matmul(self, M, K, N, trans_a, trans_b, gc, dc):
        X = np.random.randn(M, K).astype(np.float32)
        if trans_a:
            X = X.transpose()

        Y = np.random.randn(K, N).astype(np.float32)
        if trans_b:
            Y = Y.transpose()

        op = core.CreateOperator(
            'MatMul', ['X', 'Y'], 'out',
            trans_a=trans_a, trans_b=trans_b)

        def matmul_ref(X, Y, trans_a, trans_b):
            XX = X.transpose() if trans_a else X
            YY = Y.transpose() if trans_b else Y
            return (XX.dot(YY),)

        # Check against numpy reference
        self.assertReferenceChecks(gc, op, [X, Y, trans_a, trans_b],
                                   matmul_ref)
        # Check over multiple devices
        self.assertDeviceChecks(dc, op, [X, Y], [0])
        # Gradient check wrt X
        self.assertGradientChecks(gc, op, [X, Y], 0, [0])
        # Gradient check wrt Y
        self.assertGradientChecks(gc, op, [X, Y], 1, [0])
