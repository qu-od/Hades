from typing import List, Tuple, Optional

from logs import TenzDataLogger


class WeightPoint():
    def __init__(self, time: float, weight: float):
        self.time: float = time #should be from a time.time() 
        self.weight: float = weight

    def __str__(self):
        return f"wp_time={self.time}, wp_weight={self.weight}"
    
    def __iter__(self): #NEED TESTING
        self.param_number = 1
        return self

    def __next__(self): #NEED TESTING
        if self.param_number > 2:
            raise StopIteration
        if self.param_number == 1: param_value = self.time
        if self.param_number == 2: param_value = self.weight
        self.param_number += 1
        #3rd param does not exist in triangle so iteration should be stopped
        return param_value

class WeightTimeline(list): #добавить метод для логирования (по 10 точек например не закрывая файл)
    def __init__(self):
        self.points_to_store: int = 300
        self.when_current_chunk_begun: Optional[float] = None
            #should be time.time() format
        # self.chunk_is_empty: bool = True #is True at start or during logging
        self.points_num_in_chunk: int = 0
        self.weight_timeline_logger = TenzDataLogger()

    def append_point(self, weight_point):
        self.append(weight_point)
        if self.points_num_in_chunk == 0: 
            #then remember time from a first weight point
            self.when_current_chunk_begun = weight_point.time
        self.points_num_in_chunk += 1
        if self.points_num_in_chunk >= self.points_to_store:
            #then log current chunk
            self._log_current_chunk() 
                #just log all weight points in self 
                # cuz they must be equivalent to current chunk #NEED TESTING
            self.points_num_in_chunk = 0
            self.when_current_chunk_begun = None
        if len(self) > self.points_to_store:
            # then delete oldest weight_point
            del self[0]

    def _log_current_chunk(self):
        self.weight_timeline_logger.log_weight_timeline_chunk(self)

    def get_lists_for_plot(self) -> Tuple[list, list]:
        if not self:
            times_list, weights_list = [], []
        else:
            times_list  =  [wp.time   for wp in self]
            weights_list = [wp.weight for wp in self]
        return times_list, weights_list

    def __del__(self):
        self.weight_timeline_logger.close_wtl_log()
