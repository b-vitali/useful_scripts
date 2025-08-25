import subprocess
from concurrent.futures import ProcessPoolExecutor, wait
from datetime import datetime
import time
import os
import sys
from threading import Lock
from queue import Queue

# ---- Editable section ----
n_values = [1, 2000, 10000, 200, 2000, 4400]  # Inputs for the subprocess
M = 3  # Number of concurrent workers
# --------------------------

# Shared list to log process info
process_log = []
lock = Lock()  # Protects access to process_log for thread safety

def run_mycode(n):
    """
    Run 'mycode.py' as a subprocess with argument 'n'.
    Returns tuple: (n, success: bool, error_message or None)
    """
    try:
        subprocess.run(['python3', 'mycode.py', str(n)], check=True)
        return (n, True, None)
    except subprocess.CalledProcessError as e:
        return (n, False, str(e))

def clear_terminal():
    """Clears the terminal screen (cross-platform)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_table(process_log):
    """
    Prints the table of task statuses (running, done, failed),
    including time metrics. Adds a horizontal line between different workers.
    """
    clear_terminal()
    print(f"{'Worker':<10} {'N':<10} {'Start Time':<20} {'Finish Time':<20} {'Delta(s)':<10} {'Status':<10}")
    print('-' * 90)

    with lock:
        # Sort log first by worker, then by task start order
        sorted_log = sorted(process_log, key=lambda x: (x['worker_id'], x['start_order']))
        previous_worker_id = None

        for entry in sorted_log:
            # Print separator if we're moving to a new worker
            if previous_worker_id is not None and entry['worker_id'] != previous_worker_id:
                print('- ' * 45)


            start = entry['start_time'].strftime("%H:%M:%S") if entry['start_time'] else ""
            finish = entry['finish_time'].strftime("%H:%M:%S") if entry['finish_time'] else ""
            delta = entry.get('delta_time', "")

            print(f"{entry['worker_id']:<10} {entry['n']:<10} {start:<20} {finish:<20} {delta:<10} {entry['status']:<10}")
            previous_worker_id = entry['worker_id']

    print('-' * 90)
    sys.stdout.flush()


def main():
    # Queue of tasks to run
    task_queue = Queue()
    for n in n_values:
        task_queue.put(n)

    with ProcessPoolExecutor(max_workers=M) as executor:
        future_to_worker = {}  # Map future -> worker ID
        start_counter = 0      # For maintaining execution order

        # Launch initial tasks (up to M workers)
        for worker_id in range(M):
            if not task_queue.empty():
                n = task_queue.get()
                start_time = datetime.now()

                with lock:
                    process_log.append({
                        "worker_id": worker_id,
                        "n": n,
                        "start_time": start_time,
                        "finish_time": "",
                        "delta_time": "",
                        "status": "Running",
                        "start_order": start_counter
                    })
                    start_counter += 1

                future = executor.submit(run_mycode, n)
                future_to_worker[future] = worker_id

        # Monitor task completion and refill workers with next task
        while future_to_worker:
            done, _ = wait(future_to_worker.keys(), timeout=0.5)

            with lock:
                for future in done:
                    worker_id = future_to_worker[future]
                    n, success, error = future.result()

                    finish_time = datetime.now()

                    # Find and update the corresponding running task
                    for entry in reversed(process_log):
                        if entry["worker_id"] == worker_id and entry["status"] == "Running":
                            entry["finish_time"] = finish_time
                            delta = (finish_time - entry["start_time"]).total_seconds()
                            entry["delta_time"] = f"{delta:.2f}"
                            entry["status"] = "Done" if success else "Failed"
                            break

                    # Remove completed future
                    del future_to_worker[future]

                    # Assign new task to this worker, if available
                    if not task_queue.empty():
                        new_n = task_queue.get()
                        new_start = datetime.now()

                        process_log.append({
                            "worker_id": worker_id,
                            "n": new_n,
                            "start_time": new_start,
                            "finish_time": "",
                            "delta_time": "",
                            "status": "Running",
                            "start_order": start_counter
                        })
                        start_counter += 1

                        new_future = executor.submit(run_mycode, new_n)
                        future_to_worker[new_future] = worker_id

            # Update the status table every loop
            print_table(process_log)
            time.sleep(0.5)

        # Final update after all tasks are done
        print_table(process_log)

if __name__ == "__main__":
    main()
