def my_function():
    try:
        # Code block where you suspect an exception might occur
        result = 10 / 0  # Example: Division by zero to trigger an exception
        # If an exception occurs before this line, the code inside the except block will execute
        # Otherwise, the code inside the try block will execute successfully
    except Exception:
        # Exception handling code
        # This block is executed if an exception occurs in the try block
        return False
    else:
        # This block is executed if no exception occurs in the try block
        return True


# Example usage
result = my_function()
print(result)  # Output: False
