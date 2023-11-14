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

def log_event(message, filename):
    time_print = TimePrint(message)
    write_to_file(filename, str(time_print))

def log_result(round_num, timestamp, result_matrix, filename):
    time_print = TimePrint(f"Round {round_num} result: {result_matrix}", timestamp)
    write_to_file(filename, str(time_print))
    write_to_file(filename, str(result_matrix))

def write_to_file(filename, message):
    with open(filename, 'a') as file:
        file.write(message + '\n')
        
class Log:
    def __init__(self, filename, client_id=None):
        if client_id:
            self.filename = f"Client{client_id}.txt"
        else:
            self.filename = filename

    def write(self, message):
        write_to_file(self.filename, str(message))

    def save(self):
        # "save" 메서드를 호출하면 파일에 로그를 저장합니다.
        print(f"Saving log to {self.filename}")
        # 필요한 경우 여기에 추가적인 저장 로직을 구현할 수 있습니다.