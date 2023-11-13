from dict_convert import str_to_dict
from log import log_event
from dict_convert import matrix_to_dict, dict_to_matrix
import socket
import time
import numpy as np
import matrix
import log
import json  # 추가: JSON 데이터 전송을 위해 json 모듈 사용

def connect_to_server(server_address):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        return client_socket
    except Exception as e:
        print(f"Error connecting to the server: {e}")
        raise

def send_data(socket, data):
    # 데이터를 서버로 전송하는 함수
    data_copy = data.copy()  # 원본 데이터를 변경하지 않기 위해 복사
    data_copy["matrix1"] = data_copy["matrix1"].tolist()
    data_copy["matrix2"] = data_copy["matrix2"].tolist()

    data_json = json.dumps(data_copy, ensure_ascii=False)
    socket.sendall(data_json.encode())

def receive_data(socket):
    # 서버로부터 데이터를 받는 함수
    data = socket.recv(1024).decode()
    return str_to_dict(data)

def client_simulation(client_id, server_address):
    client_socket = connect_to_server(server_address)
    matrices = matrix.matrix_list()

    for round_num in range(1, 101):
        log.log_event(f"Round {round_num} started for Client {client_id}")

        for pair_client_id in range(1, 5):
            if pair_client_id != client_id:
                pair_client_socket = connect_to_server(server_address)

                log.log_event(f"Client {client_id} and Client {pair_client_id} performing matrix multiplication.")
                
                matrix1 = matrices[pair_client_id - 1]
                matrix2 = matrix.random_matrix()
                
                # 변경: 데이터를 딕셔너리로 구성하여 전송
                send_data(client_socket, {"client_id": client_id, "pair_client_id": pair_client_id, "matrix1": matrix1, "matrix2": matrix2})

                # 변경: 데이터를 딕셔너리로 받아와 처리
                result_data = receive_data(client_socket)
                
                # 수정: 결과 데이터의 구조에 따라 키 수정
                result_matrix = result_data.get("Matrix Result")
                matrices[client_id - 1] = result_matrix

                log.log_result(round_num, time.time(), result_matrix)
                
                pair_client_socket.close()

        log.log_event(f"Round {round_num} completed for Client {client_id}")

    client_socket.close()

if __name__ == "__main__":
    server_address = ('localhost', 9999)
    client_id = 1
    client_simulation(client_id, server_address)
