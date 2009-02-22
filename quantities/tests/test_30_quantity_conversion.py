﻿# -*- coding: utf-8 -*-

import unittest

from nose.tools import *
from numpy.testing import *
from numpy.testing.utils import *

import numpy as np
import quantities as q


def test_quantity_creation():
    assert_raises(LookupError, q.Quantity, 1, 'nonsense')
    assert_equal(str(q.Quantity(1, '')), '1 dimensionless')

class TestQuantities(unittest.TestCase):

    def numAssertEqual(self, a1, a2):
        """Test for equality of numarray fields a1 and a2.
        """
        self.assertEqual(a1.shape, a2.shape)
        self.assertEqual(a1.dtype, a2.dtype)
        self.assertTrue((a1 == a2).all())

    def numAssertAlmostEqual(self, a1, a2, prec = None):
        """Test for approximately equality of numarray fields a1 and a2.
        """
        self.assertEqual(a1.shape, a2.shape)
        self.assertEqual(a1.dtype, a2.dtype)

        if prec == None:
            if a1.dtype == 'Float64' or a1.dtype == 'Complex64':
                prec = 15
            else:
                prec = 7
        # the complex part of this does not function correctly and will throw
        # errors that need to be fixed if it is to be used
        if np.iscomplex(a1).all():
            af1, af2 = a1.flat.real, a2.flat.real
            for ind in xrange(af1.nelements()):
                self.assertAlmostEqual(af1[ind], af2[ind], prec)
            af1, af2 = a1.flat.imag, a2.flat.imag
            for ind in xrange(af1.nelements()):
                self.assertAlmostEqual(af1[ind], af2[ind], prec)
        else:
            af1, af2 = a1.flat, a2.flat
            for x1 , x2 in zip(af1, af2):
                self.assertAlmostEqual(x1, x2, prec)

    def test_simple(self):
        self.assertEqual(str(q.m), "1 m (meter)", str(q.m))
        self.assertEqual(str(q.J), "1 J (joule)", str(q.J))

    def test_creation(self):
        self.numAssertEqual(
            [100, -1.02, 30] * q.cm**2,
            q.Quantity(np.array([100, -1.02, 30]),
            q.cm**2)
        )
        self.assertEqual(
            str([100, -1.02, 30] * q.cm**2),
            str(q.Quantity(np.array([100, -1.02, 30]), q.cm**2))
        )

        self.assertEqual(
            -10.1 * q.ohm,
            q.Quantity(-10.1, q.ohm)
        )

        self.assertEqual(
            str(-10.1 * q.ohm),
            str(q.Quantity(-10.1, q.ohm))
        )

    def test_unit_aggregation(self):
        joule = q.kg*q.m**2/q.s**2
        pc_per_cc = q.CompoundUnit("pc/cm**3")
        area_per_volume = q.CompoundUnit("m**2/m**3")
        self.assertEqual(str(joule/q.m), "1.0 kg·m/s²", str(joule/q.m))
        self.assertEqual(str(joule*q.m), "1.0 kg·m³/s²", str(joule*q.m))
        self.assertEqual(
            str(q.J*pc_per_cc),
            "1.0 J·(pc/cm³)",
            str(q.J*pc_per_cc)
        )
        temp = pc_per_cc / area_per_volume
        self.assertEqual(
            str(temp.simplified),
            "3.08568025e+22 1/m",
            str(temp.simplified)
        )

    def test_ratios(self):
        self.assertAlmostEqual(
            q.m/q.ft.rescale(q.m),
            3.280839895,
            10,
            q.m/q.ft.rescale(q.m)
        )
        self.assertAlmostEqual(
            q.J/q.BTU.rescale(q.J),
            0.00094781712,
            10,
            q.J/q.BTU.rescale(q.J)
        )

    def test_compound_reduction(self):
        pc_per_cc = q.CompoundUnit("pc/cm**3")
        temp = pc_per_cc * q.CompoundUnit('m/m**3')
        self.assertEqual(str(temp), "1.0 (pc/cm³)·(m/m³)", str(temp))
        temp = temp.simplified
        temp = temp.rescale(q.pc**-4)
        self.assertEqual(str(temp), "2.79740021556e+88 1/pc⁴", str(temp))
        temp = temp.rescale(q.m**-4)
        self.assertEqual(str(temp), "3.08568025e+22 1/m⁴", str(temp))
        self.assertEqual(str(1/temp), "3.24077648681e-23 m⁴", str(1/temp))
        self.assertEqual(
            str(temp**-1),
            "3.24077648681e-23 m⁴",
            str(temp**-1)
        )

        # does this handle regular units correctly?
        temp1 = 3.14159 * q.m

        self.assertAlmostEqual(temp1, temp1.simplified)

        self.assertEqual(str(temp1), str(temp1.simplified))

    def test_equality(self):
        test1 = 1.5 * q.km
        test2 = 1.5 * q.km

        self.assertEqual(test1, test2)

        # test less than and greater than
        self.assertTrue(1.5 * q.km > 2.5 * q.cm)
        self.assertTrue(1.5 * q.km >= 2.5 * q.cm)
        self.assertTrue(not (1.5 * q.km < 2.5 * q.cm))
        self.assertTrue(not (1.5 * q.km <= 2.5 * q.cm))

        self.assertTrue(
            1.5 * q.km != 1.5 * q.cm,
            "unequal quantities are not-not-equal"
        )

    def test_getitem(self):
        tempArray1 = q.Quantity(np.array([1.5, 2.5 , 3, 5]), q.J)
        temp = 2.5 * q.J
        # check to see if quantities brought back from an array are good
        self.assertEqual(tempArray1[1], temp )
        # check the formatting
        self.assertEqual(str(tempArray1[1]), str(temp))

        def tempfunc(index):
            return tempArray1[index]

        # make sure indexing is correct
        self.assertRaises(IndexError, tempfunc, 10)

        # test get item using slicing
        tempArray2 = [100, .2, -1, -5, -6] * q.mA
        tempArray3 = [100, .2, -1, -5] * q.mA
        tempArray4 = [.2, -1 ] * q.mA

        self.numAssertEqual(tempArray2[:], tempArray2)

        self.numAssertEqual(tempArray2[:-1], tempArray3)
        self.numAssertEqual(tempArray2[1:3], tempArray4)

    def test_setitem (self):
        temp = q.Quantity([0,2,5,7.6], q.lb)

        # needs to check for incompatible units
        def test(value):
            temp[2] = value

        # make sure normal assignment works correctly
        test(2 *q.lb)

        self.assertRaises(ValueError, test, 60 * q.inch * q.J)
        # even in the case when the quantity has no units
        # (maybe this could go away)
        self.assertRaises(ValueError, test, 60)

        #test set item using slicing
        tempArray2 = [100, .2, -1, -5, -6] * q.mA
        tempArray3 = [100, .2, 0, 0, -6] * q.mA
        tempArray4 = [100,  1,  1,  1,  1] * q.mA

        tempArray4[1:] = [.2, -1, -5, -6] * q.mA
        self.numAssertEqual(tempArray4, tempArray2)

        tempArray3[2:4] = [-1, -5] * q.mA
        self.numAssertEqual(tempArray3, tempArray2)

        tempArray4[:] = [100, .2, -1, -5, -6] * q.mA
        self.numAssertEqual(tempArray4, tempArray2)

        # check and see that dimensionless numbers work correctly
        tempArray5 = q.Quantity([.2, -3, -5, -9,10])
        tempArray6 = q.Quantity([.2, -3, 0, 0,11])

        tempArray5[4] = 1 + tempArray5[4]
        tempArray5[2:4] = np.zeros(2)

        self.numAssertEqual(tempArray5, tempArray6)

        # needs to check for out of bounds
        def tempfunc(value):
            temp[10] = value

        self.assertRaises(IndexError, tempfunc, 5 * q.lb)

    def test_iterator(self):
        f = np.array([100, 200, 1, 60, -80])
        x = f * q.kPa

        # make sure the iterator objects have the correct units
        for i in x:
            # currently fails
            self.assertEqual(i.units, q.kPa.units)


if __name__ == "__main__":
    run_module_suite()