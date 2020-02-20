import sys
import pickle
from CoreRunner import CoreRunner
from os import path

core_obj = CoreRunner("1", "2", "rtsp://guest:pmb12345@10.0.0.106:554/Streaming/Channels/1201", "10", "111", "21", "200")
core_obj_list = [core_obj]

file_path = path.relpath("app/main/abc" + "2" + ".bin")
with open(file_path, "wb") as file_:
    print("succeed")
    pickle.dump(core_obj_list, file_, -1)
file_.close()

with open("app/main/status_line/" + "2" + ".txt", "w") as file:
   file.write("0")
file.close()


# input multi items
file_path = path.relpath("app/main/abc" + "2" + ".bin")
with open(file_path, "rb") as f:
    core_runner_list = pickle.load(f)
f.close()
for i in range(len(core_runner_list)):
    if core_runner_list[i].line_id == "2":
        core_runner_list[i].start()