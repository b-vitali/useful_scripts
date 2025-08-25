import sys
import time
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 mycode.py <number>")
        return

    try:
        n = int(sys.argv[1])
        if n < 0:
            raise ValueError("Negative delay not allowed.")
    except ValueError:
        print("Error: Please provide a valid non-negative integer.")
        return

    # Create 'log' folder if it doesn't exist
    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)

    filename = os.path.join(log_dir, f"log_{n}.txt")

    # Convert milliseconds to seconds and wait
    delay_seconds = n / 1000.0
    time.sleep(delay_seconds)

    with open(filename, 'w') as f:
        f.write(f"Waited for {n} milliseconds.\n")

    print(f"Output written to {filename}")

if __name__ == "__main__":
    main()
