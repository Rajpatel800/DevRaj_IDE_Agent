"""
Demo: Building a Calculator with the AI Agent System

This demonstrates what the system can build when you ask:
"@developer create a simple calculator CLI"
"""


class Calculator:
    """A simple calculator with basic operations"""
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers"""
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a"""
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers"""
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """Divide a by b"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    def power(self, a: float, b: float) -> float:
        """Raise a to the power of b"""
        return a ** b
    
    def sqrt(self, a: float) -> float:
        """Calculate square root of a"""
        if a < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return a ** 0.5


def main():
    """Main CLI interface"""
    calc = Calculator()
    
    print("=" * 50)
    print("Simple Calculator CLI")
    print("=" * 50)
    print("\nAvailable operations:")
    print("  1. Add")
    print("  2. Subtract")
    print("  3. Multiply")
    print("  4. Divide")
    print("  5. Power")
    print("  6. Square Root")
    print("  0. Exit")
    
    while True:
        print("\n" + "-" * 50)
        try:
            choice = input("Select operation (0-6): ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
            
            if choice == "6":
                # Square root only needs one number
                a = float(input("Enter number: "))
                result = calc.sqrt(a)
                print(f"√{a} = {result}")
            elif choice in ["1", "2", "3", "4", "5"]:
                a = float(input("Enter first number: "))
                b = float(input("Enter second number: "))
                
                if choice == "1":
                    result = calc.add(a, b)
                    print(f"{a} + {b} = {result}")
                elif choice == "2":
                    result = calc.subtract(a, b)
                    print(f"{a} - {b} = {result}")
                elif choice == "3":
                    result = calc.multiply(a, b)
                    print(f"{a} × {b} = {result}")
                elif choice == "4":
                    result = calc.divide(a, b)
                    print(f"{a} ÷ {b} = {result}")
                elif choice == "5":
                    result = calc.power(a, b)
                    print(f"{a} ^ {b} = {result}")
            else:
                print("Invalid choice. Please select 0-6.")
        
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
