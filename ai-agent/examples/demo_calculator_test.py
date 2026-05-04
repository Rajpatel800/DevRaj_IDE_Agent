"""
Demo: Tests for Calculator

This demonstrates what @tester would create when asked:
"@tester write tests for the calculator"
"""
import unittest
from demo_calculator import Calculator


class TestCalculator(unittest.TestCase):
    """Test cases for Calculator class"""
    
    def setUp(self):
        """Set up test fixture"""
        self.calc = Calculator()
    
    def test_add(self):
        """Test addition"""
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)
        self.assertEqual(self.calc.add(0, 0), 0)
        self.assertEqual(self.calc.add(1.5, 2.5), 4.0)
    
    def test_subtract(self):
        """Test subtraction"""
        self.assertEqual(self.calc.subtract(5, 3), 2)
        self.assertEqual(self.calc.subtract(0, 5), -5)
        self.assertEqual(self.calc.subtract(10, 10), 0)
        self.assertEqual(self.calc.subtract(5.5, 2.5), 3.0)
    
    def test_multiply(self):
        """Test multiplication"""
        self.assertEqual(self.calc.multiply(2, 3), 6)
        self.assertEqual(self.calc.multiply(-2, 3), -6)
        self.assertEqual(self.calc.multiply(0, 100), 0)
        self.assertEqual(self.calc.multiply(2.5, 2), 5.0)
    
    def test_divide(self):
        """Test division"""
        self.assertEqual(self.calc.divide(6, 2), 3)
        self.assertEqual(self.calc.divide(5, 2), 2.5)
        self.assertEqual(self.calc.divide(-10, 2), -5)
    
    def test_divide_by_zero(self):
        """Test division by zero raises error"""
        with self.assertRaises(ValueError) as context:
            self.calc.divide(5, 0)
        self.assertIn("Cannot divide by zero", str(context.exception))
    
    def test_power(self):
        """Test power operation"""
        self.assertEqual(self.calc.power(2, 3), 8)
        self.assertEqual(self.calc.power(5, 0), 1)
        self.assertEqual(self.calc.power(2, -1), 0.5)
        self.assertEqual(self.calc.power(4, 0.5), 2)
    
    def test_sqrt(self):
        """Test square root"""
        self.assertEqual(self.calc.sqrt(4), 2)
        self.assertEqual(self.calc.sqrt(9), 3)
        self.assertEqual(self.calc.sqrt(0), 0)
        self.assertAlmostEqual(self.calc.sqrt(2), 1.414, places=3)
    
    def test_sqrt_negative(self):
        """Test square root of negative number raises error"""
        with self.assertRaises(ValueError) as context:
            self.calc.sqrt(-1)
        self.assertIn("Cannot calculate square root of negative number", 
                     str(context.exception))
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Very large numbers
        self.assertEqual(self.calc.add(1e10, 1e10), 2e10)
        
        # Very small numbers
        self.assertAlmostEqual(self.calc.add(1e-10, 1e-10), 2e-10)
        
        # Mixed operations
        result = self.calc.multiply(self.calc.add(2, 3), 2)
        self.assertEqual(result, 10)


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCalculator)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()
