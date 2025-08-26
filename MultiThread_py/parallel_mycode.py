import subprocess
from concurrent.futures import ProcessPoolExecutor, wait
from datetime import datetime
import time
import os
import sys
from threading import Lock
from queue import Queue

# ---- Editable section ----

script_name = "mycode2.py"  # Script to run
args = [
    (1000, "Alpha"),
    (2000, "Beta"),
    (500, "Gamma"),
    (3000, "Delta"),
    (1000, "Epsilon"),
    (400, "Zeta"),
]

# script_name = "mycode.py"  # Script to run
# args = [
#     (1000,),
#     (2000,),
#     (500,),
#     (3000,),
#     (1000,),
#     (400,),
# ]

M = 3  # Number of concurrent workers
# --------------------------

process_log = []
lock = Lock()

def run_mycode(arg_tuple):
    """
    Run the specified script with given arguments (as tuple).
    Returns: (args, success: bool, error_message or None)
    """
    try:
        str_args = list(map(str, arg_tuple))  # Convert all to strings
        subprocess.run(['python3', script_name, *str_args], check=True)
        return (arg_tuple, True, None)
    except subprocess.CalledProcessError as e:
        return (arg_tuple, False, str(e))

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_table(process_log):
    clear_terminal()
    print(f"   {'Worker':<10} {'Args':<30} {'Start Time':<15} {'Finish Time':<15} {'Delta(s)':<10} {'Status':<10}")
    print('-' * 99)

    with lock:
        sorted_log = sorted(process_log, key=lambda x: (x['worker_id'], x['start_order']))
        previous_worker_id = None

        for entry in sorted_log:
            if previous_worker_id is not None and entry['worker_id'] != previous_worker_id:
                print('- ' * 50)

            start = entry['start_time'].strftime("%H:%M:%S") if entry['start_time'] else ""
            finish = entry['finish_time'].strftime("%H:%M:%S") if entry['finish_time'] else ""
            delta = entry.get('delta_time', "")
            arg_str = str(entry['args'])

            print(f"   {entry['worker_id']:<10} {arg_str:<30} {start:<15} {finish:<15} {delta:<10} {entry['status']:<10}")
            previous_worker_id = entry['worker_id']

    print('-' * 99)
    sys.stdout.flush()

def main():
    task_queue = Queue()
    for arg in args:
        task_queue.put(arg)

    with ProcessPoolExecutor(max_workers=M) as executor:
        future_to_worker = {}
        start_counter = 0

        # Launch initial tasks
        for worker_id in range(M):
            if not task_queue.empty():
                arg = task_queue.get()
                start_time = datetime.now()

                with lock:
                    process_log.append({
                        "worker_id": worker_id,
                        "args": arg,
                        "start_time": start_time,
                        "finish_time": "",
                        "delta_time": "",
                        "status": "Running",
                        "start_order": start_counter
                    })
                    start_counter += 1

                future = executor.submit(run_mycode, arg)
                future_to_worker[future] = worker_id

        # Monitor completion and refill workers
        while future_to_worker:
            done, _ = wait(future_to_worker.keys(), timeout=0.5)

            with lock:
                for future in done:
                    worker_id = future_to_worker[future]
                    arg, success, error = future.result()
                    finish_time = datetime.now()

                    for entry in reversed(process_log):
                        if entry["worker_id"] == worker_id and entry["status"] == "Running":
                            entry["finish_time"] = finish_time
                            delta = (finish_time - entry["start_time"]).total_seconds()
                            entry["delta_time"] = f"{delta:.2f}"
                            entry["status"] = "Done" if success else "Failed"
                            break

                    del future_to_worker[future]

                    if not task_queue.empty():
                        new_arg = task_queue.get()
                        new_start = datetime.now()

                        process_log.append({
                            "worker_id": worker_id,
                            "args": new_arg,
                            "start_time": new_start,
                            "finish_time": "",
                            "delta_time": "",
                            "status": "Running",
                            "start_order": start_counter
                        })
                        start_counter += 1

                        new_future = executor.submit(run_mycode, new_arg)
                        future_to_worker[new_future] = worker_id

            print_table(process_log)
            time.sleep(0.5)

        print_table(process_log)

if __name__ == "__main__":
    main()
