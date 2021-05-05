from typing import List, Tuple, Optional

import time
# import datetime
import pathlib



class TenzDataLogger():
    def __init__(self):
        self.filename_template: str = "expansion.log"
        time_str = time.strftime("%d.%m.%y %H-%M", time.localtime())
        # wtl is an alias for weight_timeline
        dir_path_str = pathlib.Path(__file__).parent.absolute()
        self.wtl_log_name = f"{dir_path_str}\logs\{time_str}_weights_{self.filename_template}"
        #\logs\ NEED TESTING
        self.wtl_log = open(self.wtl_log_name, 'w')

    def log_weight_timeline_chunk(self, weight_timeline):
        if self.wtl_log.closed: 
            self.wtl_log = \
                open(self.wtl_log_name, 'w') #NEED TESTING
        F = self.wtl_log
        F.write("\n-------------NEW CHUNK-------------\n")
        for i, w_point in enumerate(weight_timeline):
            line = f"wp{i}, {w_point.time}, {w_point.weight}"
            F.write(line + '\n')
        

    def log_all_weight_timeline_data_chunks(self, *weight_timeline):
        pass

    def close_wtl_log(self):
        self.wtl_log.close()
        print("weight_timeline_log closed")

    '''def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.wtl_log.close()
        #close all other files'''

