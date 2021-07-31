import math
import time
class Verbose:
    def __init__(self, start_with="", max_lines=25, time_mode="average", average_length=10, round_to=2, show_time=True, line_char="=", space_char="-", arrow_head=">"):
        self.start_with = start_with
        self.max_lines = max_lines
        self.process_time = 0
        self.previous_time = 0
        self.time_mode = time_mode
        self.average_length = average_length
        self.time_steps = [0] * average_length
        self.average_counter = 0
        self.show_time=show_time
        self.round_to = round_to
        self.line_char = line_char
        self.space_char = space_char
        self.arrow_head = arrow_head
    
    def calc_last_time(self):
        current_time = time.time()
        if self.time_mode == "per_step":
            self.process_time = round(current_time - self.previous_time, self.round_to)
        else:
            average = sum(self.time_steps)/self.average_length
            actual_time = round(current_time - self.previous_time, self.round_to)
            self.process_time = round(average, self.round_to)
            self.time_steps[self.average_counter] = actual_time if not actual_time > 100000 else 0.00
            self.average_counter += 1
            if self.average_counter == self.average_length:
                self.average_counter = 0
        self.previous_time = current_time

    def reset_time(self):
        self.process_time = 0

    def make_verbose(self, done, total, start_with=""):
        if start_with == "":
            start_with = self.start_with

        num_lines = int((done/total)*self.max_lines)
        lines = self.line_char*num_lines
        spaces = self.space_char*(self.max_lines-num_lines)

        if self.show_time:
            self.calc_last_time()
            remaining_steps = total - done
            remaining_time = ""
            remaining_time = round(self.process_time * remaining_steps, self.round_to)
            print(f"\r{start_with}  [{lines}{self.arrow_head}{spaces}]  {done}/{total} ETA: {remaining_time} sec for {self.process_time} sec/steps", end="", sep=" ", flush=True)
            if remaining_steps == 0: 
                self.reset_time()
        else:
            print(f"\r{start_with}  [{lines}{self.arrow_head}{spaces}]  {done}/{total}", end="", sep=" ", flush=True)

def divide_chunks(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]