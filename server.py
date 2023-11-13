import socket
from threading import Thread
from log import Log, TimePrint
from clock import Clock
from dict_convert import dict_to_str, str_to_dict, matrix_to_dict, dict_to_matrix
import numpy as np
import json
import sys

client_sockets = []
ROUND_LIMIT = 100
round_num = 0

# 서버 주소 및 포트 설정 (로컬에서 실행할 경우)
HOST = '127.0.0.1'  # 또는 'localhost'
PORT = 9999

clock = Clock()
log = Log("Server.txt")


def client_name(client_socket):
    return f"Client{client_sockets.index(client_socket) + 1}"


def threaded(client_socket, addr):
    name = client_name(client_socket)
    dic = {"name": name}
    client_socket.send(dict_to_str(dic).encode())

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
            client.sendall(data.encode())
        except Exception as e:
            log.write(TimePrint(f"Error sending data to client: {e}", clock.get()))


def decode_matrix_data(data):
    matrix_dict = json.loads(data)
    return dict_to_matrix(matrix_dict)


def perform_matrix_operation():
    # 라운드마다 수행할 행렬 연산 로직 추가
    global round_num
    log.write(TimePrint(f"Performing matrix operation for Round {round_num}...", clock.get()))

    # 예시로 두 행렬을 더하는 연산을 수행
    matrix_a = np.random.randint(0, 10, size=(10, 10))
    matrix_b = np.random.randint(0, 10, size=(10, 10))
    result_matrix = matrix_a + matrix_b

    # 결과 행렬을 클라이언트에게 전송
    result_matrix_str = dict_to_str({"result_matrix": result_matrix.tolist()})
    send_data_to_clients(f"Matrix Result {result_matrix_str}")

    log.write(TimePrint(f"Matrix operation for Round {round_num} completed.", clock.get()))


def server():
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

    except Exception as e:
        log.write(TimePrint(f"Error: {e}", clock.get()))


def close():
    for client in client_sockets:
        client.close()
    log.write(TimePrint("Server stopping...", clock.get()))
    log.save()


if __name__ == "__main__":
    server()
    close()
