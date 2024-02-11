import os
import subprocess
import queue

# the path to your source code
import threading

src_path = "feed_thing"

# a list of tasks to run
# "flake8","coverage"
# a list of tasks to run
tasks = ["isort", "pylint", "black", "pytest", "coverage"]

# a list of tasks that modify code
modifying_tasks = ["isort", "black"]


# the path to a file where the script will store the last modified time of the source code
timestamp_file = "last_modified.txt"

# get the last modified time of the source code
last_modified = os.path.getmtime(src_path)
print(last_modified)

# if the timestamp file exists, read the stored last modified time from the file
if os.path.exists(timestamp_file):
    with open(timestamp_file, "r") as f:
        stored_time = f.read()
else:
    # if the timestamp file does not exist, set the stored time to 0
    stored_time = 0

# a function to run a task and store its output in a queue
def run_task(task, src_path, output_queue):
    # run the task and capture its output
    output = subprocess.run([task, src_path], capture_output=True)

    # put the output in the queue
    output_queue.put(output.stdout)


# if the stored time is not the same as the current last modified time,
# run the tasks
if stored_time != last_modified:
    if stored_time != last_modified:
        # run the modifying tasks one at a time
        for task in modifying_tasks:
            subprocess.run([task, src_path])

            # create a queue to store the output from the non-modifying tasks
        output_queue = queue.Queue()

        # create a list of threads to run the non-modifying tasks in parallel
        threads = []
        for task in tasks:
            if task not in modifying_tasks:
                thread = threading.Thread(target=run_task, args=(task, src_path, output_queue))
                threads.append(thread)

        # start the threads
        for thread in threads:
            thread.start()

        # wait for the threads to finish
        for thread in threads:
            thread.join()

        # display the output from the queue one at a time
        while not output_queue.empty():
            print(output_queue.get().decode())

    # # create a list of threads to run the non-modifying tasks in parallel
        # threads = []
        # for task in tasks:
        #     if task not in modifying_tasks:
        #         thread = threading.Thread(target=subprocess.run, args=([task, src_path],))
        #         threads.append(thread)
        #
        # # start the threads
        # for thread in threads:
        #     thread.start()
        #
        # # wait for the threads to finish
        # for thread in threads:
        #     thread.join()

# update the stored last modified time in the timestamp file
with open(timestamp_file, "w") as f:
    f.write(str(last_modified))