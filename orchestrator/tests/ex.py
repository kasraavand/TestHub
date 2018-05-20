import doctest
import unittest
import factorial
import glob

"""
suite = unittest.TestLoader().discover('units')
# suite = unittest.TestLoader().loadTestsFromModule(testfile)
r = unittest.TextTestRunner().run(suite)

print(r.failures)
print(r.descriptions)

print(r.errors)
"""
doctest.testmod(factorial)
suite = unittest.TestSuite()
suite.addTest(doctest.DocTestSuite(factorial))
suite.addTest(doctest.DocFileSuite(*glob.glob('docs/*')))

runner = unittest.TextTestRunner(verbosity=2)
r = runner.run(suite)
print(r.failures)
print(r.descriptions)
print(r.errors)
