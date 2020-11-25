import unittest
import sys
import py_compile
import krakenchecksumtest
import checksumtest
import checksumtest100

EXIT_SUCCESS=0
EXIT_FAILURE=1

# initialize the test suite
loader = unittest.TestLoader()
suite  = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(krakenchecksumtest))
suite.addTests(loader.loadTestsFromModule(checksumtest))
suite.addTests(loader.loadTestsFromModule(checksumtest100))

def compile():
    py_compile.compile('kraken_book.py')
    py_compile.compile('kraken.py')
    py_compile.compile('get_orders.py')
    py_compile.compile('get_token.py')
    py_compile.compile('kraken_orders.py')
    py_compile.compile('kraken_request.py')
    py_compile.compile('kraken_token.py')
    py_compile.compile('orders.py')
    py_compile.compile('pricelistener.py') 


def runtests():
    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)
    return result
    

if __name__ == "__main__":
    compile()
    result = runtests()
    print ("Finished Python Test")
    if result.wasSuccessful():
        sys.exit(EXIT_SUCCESS)
    sys.exit(EXIT_FAILURE)

