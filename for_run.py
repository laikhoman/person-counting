import sys
import pickle
from CoreRunner import CoreRunner
import os
from os import path

myList = sys.argv[1:]
print(myList)
core_obj = CoreRunner(myList[0], myList[1], myList[2], myList[3], myList[4], myList[5], myList[6])
core_obj_list = [core_obj]

# file for dumping object
file_path = path.relpath("app/main/abc" + core_obj.user_id + ".bin")
with open(file_path, "wb") as file_:
    print("succeed")
    pickle.dump(core_obj_list, file_, -1)
file_.close()

# file for save status line

if not os.path.exists("app/main/status_line/" + myList[1] + ".txt"):
    with open("app/main/status_line/" + myList[1] + ".txt", "w") as file:
       file.write("0")
    file.close()
