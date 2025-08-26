import sys
import time
import os

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 mycode2.py <delay_ms> <message>")
        return

    try:
        delay = int(sys.argv[1])
        message = sys.argv[2]
    except ValueError:
        print("Error: Invalid delay input.")
        return

    time.sleep(delay / 1000.0)

    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)
    filename = os.path.join(log_dir, f"log_{delay}_{message}.txt")

    with open(filename, 'w') as f:
        f.write(f"Waited {delay}ms. Message: {message}\n")

    print(f"Output written to {filename}")

if __name__ == "__main__":
    main()
