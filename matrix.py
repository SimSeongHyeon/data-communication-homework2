import numpy as np
import socket
import time
import log

# 서버 주소 및 포트 설정
SERVER_ADDRESS = 'localhost'  # 서버 주소
SERVER_PORT = 9999  # 서버 포트

# 클라이언트 번호 (1부터 4까지 설정)
CLIENT_NUMBER = 1

def connect_to_server():
    # 서버에 연결하는 함수
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_ADDRESS, SERVER_PORT))
    return client_socket

def send_data(socket, data):
    # 데이터를 서버로 전송하는 함수
    socket.sendall(data.encode())

def receive_data(socket):
    # 서버로부터 데이터를 받는 함수
    data = socket.recv(1024).decode()
    return data

def main():
    # 서버와 연결 설정
    server_socket = connect_to_server()

    # 서버에 클라이언트 번호 전송
    send_data(server_socket, f'Client {CLIENT_NUMBER}')

    # 연산을 진행할 행렬 생성
    matrix_list = matrix_list()
    my_matrix = random_matrix()

    round_num = 1

    while round_num <= 100:
        log.log_event(f'Round {round_num}')
        for i in range(2, 5):
            if i == CLIENT_NUMBER:
                continue  # 본인 클라이언트는 스킵
            selected_clients = [CLIENT_NUMBER, i]
            request = f'Selected Clients: {selected_clients}\n'
            send_data(server_socket, request)

            # 서버로 행렬 전송
            my_matrix_str = arr_to_str(my_matrix)
            send_data(server_socket, my_matrix_str)

            # 다른 클라이언트로부터 행렬 수신
            other_matrix_str = receive_data(server_socket)
            other_matrix = str_to_arr(other_matrix_str)
            
            # 행렬 곱셈 연산 수행
            result_matrix = np.dot(my_matrix, other_matrix)

            # 서버로 결과 전송
            result_matrix_str = arr_to_str(result_matrix)
            send_data(server_socket, result_matrix_str)

            # 서버로부터 라운드 종료 메시지 수신
            receive_data(server_socket)

            # 결과 행렬 업데이트
            matrix_list[round_num % 6] = result_matrix
        round_num += 1

    # 클라이언트 종료 메시지 전송
    send_data(server_socket, 'Client Done')

    # 서버로부터 종료 메시지 수신
    receive_data(server_socket)

    # 소켓 연결 종료
    server_socket.close()

def matrix_list():
    """
    연산 결과를 저장할 10x10 크기의 행렬 6개 생성
    """
    matrixList = []
    for i in range(6):
        matrixList.append(np.empty((10, 10)))
    return matrixList

def random_matrix(rangeMin=0, rangeMax=100, row=10, col=10):
    """
    무작위 정수기반(0~100사이) 행렬을 생성
    """
    matrix = np.random.randint(rangeMin, rangeMax + 1, size=(row, col))
    return matrix

def arr_to_str(array):
    """
    1차원 배열을 문자열로 변환
    """
    return " ".join(map(str, array))

def str_to_arr(s):
    """
    문자열을 1차원 배열로 변환
    """
    return np.array(list(map(int, s.split())))

def matrix_to_dict(matrix):
    return matrix.tolist()  # NumPy 배열을 리스트로 변환하여 반환

def dict_to_matrix(matrix_dict):
    return np.array(matrix_dict)  # 리스트를 NumPy 배열로 변환하여 반환

if __name__ == "__main__":
    main()
