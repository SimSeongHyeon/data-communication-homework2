import socket
from threading import Thread
from log import Log, TimePrint
from clock import Clock
from dict_convert import dict_to_str, str_to_dict, matrix_to_dict, dict_to_matrix
from datetime import datetime
import numpy as np
import json
import sys  
import time
from itertools import combinations

client_sockets = []
ROUND_LIMIT = 100
round_num = 0

# 서버 주소 및 포트 설정 (로컬에서 실행할 경우)
HOST = '127.0.0.1'  # 또는 'localhost'
PORT = 9999

# 시스템 클럭을 생성합니다.
clock = Clock()

# Log 클래스를 생성할 때 서버의 경우 client_id를 전달하지 않습니다.
log = Log("Server.txt")

# 행렬 연산 및 결과 저장에 필요한 전역 변수 선언
result_matrices = [np.zeros((10, 10)) for _ in range(6)]  # 6개의 10x10 행렬 생성
start_time = None  # 라운드 시작 시간을 저장할 변수
round_times = []  # 라운드 소요 시간을 저장할 리스트

def client_name(client_socket):
    return f"Client{client_sockets.index(client_socket) + 1}"


def threaded(client_socket, addr):
    name = client_name(client_socket)
    client_log = Log(f"Client{client_sockets.index(client_socket) + 1}.txt")  # 클라이언트별 파일 생성

    while True:
        try:
            data = client_socket.recv(1024)

            if not data:
                log.write(
                    TimePrint(
                        f"Disconnected by {addr[0]} ({name})",
                        clock.get(),
                    )
                )
                break

            log.write(
                TimePrint(
                    f"Received from {addr[0]} ({name}) >> {data.decode('utf-8')}",
                    clock.get(),
                )
            )

            received_data = data.decode("utf-8")

            client_log.write(TimePrint(f"Received from {addr[0]} ({name}) >> {data.decode('utf-8')}", clock.get()))

           # 라운드 시작 메시지 수신
            if received_data.startswith("Round"):
                global round_num
                round_num = int(received_data.split()[1])

                # 라운드가 종료되었을 때
                if round_num > ROUND_LIMIT:
                    log.write(TimePrint("All rounds completed. Server closing...", clock.get()))
                    close()
                    break

                log.write(TimePrint(f"Round {round_num} started.", clock.get()))

                # 클라이언트에게 현재 라운드 정보 전송
                send_data_to_clients({"result_matrix": result_matrix.tolist()})

                # 서버에서 연산을 수행하고 결과를 클라이언트에게 전송
                perform_matrix_operation()

                # 클라이언트에게 라운드 종료 메시지 전송
                send_data_to_clients("Round End")

        except ConnectionResetError as e:
            log.write(
                TimePrint(
                    f"Disconnected by {addr[0]} ({name})",
                    clock.get(),
                )
            )
            break
        except ConnectionAbortedError as e:
            break


def send_data_to_clients(data):
    for client in client_sockets:
        try:
            client.sendall(data)
        except Exception as e:
            log.write(TimePrint(f"Error sending data to client: {e}", clock.get()))


def decode_matrix_data(data):
    matrix_dict = json.loads(data)
    return dict_to_matrix(matrix_dict)


def perform_matrix_operation():
    global round_num
    global start_time
    global result_matrices
    
    # 라운드 시작 시간 기록
    if round_num == 1:
        start_time = time.time()

    # 연산 결과를 저장할 10x10 크기의 행렬 6개 생성
    result_matrices = [np.zeros((10, 10)) for _ in range(6)]
    
    # 모든 클라이언트 쌍에 대한 행렬 곱셈 연산
    client_pairs = list(combinations(range(1, 5), 2))
    for pair in client_pairs:
        client1, client2 = pair
        
        # 행렬 곱셈을 위해 서로 다른 두 클라이언트가 선택한 행렬 (예시로 랜덤 데이터 사용)
        matrix1 = np.random.rand(10, 10)
        matrix2 = np.random.rand(10, 10)
        
        # 나머지 두 클라이언트를 선택하여 공평하게 분배
        remaining_clients = [c for c in range(1, 5) if c not in pair]
        elements_to_calculate = np.prod(matrix1.shape) // 2  # 각 클라이언트에게 분배할 성분 수
        element_count = 0

        for client_id in remaining_clients:
            client_result = np.zeros((10, 10))  # 각 클라이언트의 결과 행렬 초기화
            for i in range(10):
                for j in range(10):
                    if element_count < elements_to_calculate:
                        # 곱셈 연산 수행 (랜덤 데이터를 사용하므로 예시로 곱셈 대신 덧셈 연산을 수행)
                        client_result[i][j] = matrix1[i][j] + matrix2[i][j]
                        element_count += 1
                    else:
                        break
            
            # 연산이 끝나고 각 라운드별 결과 행렬에 저장
            result_matrices[round_num % 6] += client_result

    # 라운드 종료 시간 측정 및 로그 기록
    if round_num == ROUND_LIMIT:  # ROUND_LIMIT = 100
        end_time = time.time()
        elapsed_time = end_time - start_time
        round_times.append(elapsed_time)

        # 결과 출력 및 로그 기록
        print(f"Round {round_num} completed in {elapsed_time} seconds")
        log.write(TimePrint(f"Round {round_num} completed in {elapsed_time} seconds", clock.get()))

        # 결과 행렬 출력
        for idx, matrix in enumerate(result_matrices):
            print(f"Result Matrix {idx + 1}:\n{matrix}")
            log.write(TimePrint(f"Result Matrix {idx + 1}:\n{matrix}", clock.get()))
            log.write(str(matrix))  # 행렬을 파일에 기록

        # Log에 round 별 연산 시간과 결과 행렬을 기록
        log.write(TimePrint(f"Round {round_num} took {elapsed_time} seconds", clock.get()))
        for idx, matrix in enumerate(result_matrices):
            log.write(f"Round {round_num} Result Matrix {idx + 1}:\n{matrix}")
    
    # 클라이언트에게 라운드 종료 메시지 전송
    send_data_to_clients("Round End")


def server():
    global clock, round_num
    clock.start()  # 시스템 클럭 시작

    log.write(TimePrint(f"Server start at {HOST}:{PORT}", clock.get()))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    log.write(TimePrint("Wait join client", clock.get()))

    try:
        while True:
            client_socket, addr = server_socket.accept()
            client_sockets.append(client_socket)
            client_thread = Thread(target=threaded, args=(client_socket, addr))
            client_thread.daemon = True
            client_thread.start()

            # 연결된 모든 클라이언트가 준비될 때까지 대기
            if len(client_sockets) == 4:
                for round_num in range(1, 101):
                    log_event(f"Round {round_num} started for all clients")
                    
                    # 클라이언트에게 현재 라운드 정보 전송
                    send_data_to_clients({"round_num": round_num})

                    # 서버에서 연산 수행 및 클라이언트에게 전송
                    perform_matrix_operation()

                    # 클라이언트에게 라운드 종료 메시지 전송
                    send_data_to_clients("Round End")
    except Exception as e:
        log.write(TimePrint(f"Error: {e}", clock.get()))

    # Gracefully Terminate
    close()


def close():
    for client_socket in client_sockets:
        client_socket.close()

    # 서버 로그에도 메시지를 기록합니다.
    log.write(TimePrint("Server stopping...", clock.get()))
    log.save()


if __name__ == "__main__":
    server()
    close()