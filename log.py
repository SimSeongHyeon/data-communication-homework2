from datetime import datetime

class TimePrint:
    def __init__(self, message, timestamp=None):
        if timestamp is None:
            timestamp = self.get_current_time()
        self.timestamp = timestamp
        self.message = message

    def __str__(self):
        return f"[{self.timestamp}] {self.message}"

    def get_current_time(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

def log_event(message):
    time_print = TimePrint(message)
    print(str(time_print))  # 또는 로그 파일에 쓰도록 수정

def log_result(round_num, timestamp, result_matrix):
    time_print = TimePrint(f"Round {round_num} result: {result_matrix}", timestamp)
    print(str(time_print))  # 또는 로그 파일에 쓰도록 수정

class Log:
    def __init__(self, filename):
        self.filename = filename

    def write(self, message):
        with open(self.filename, 'a') as file:
            file.write(str(message) + '\n')

    def save(self):
        pass
