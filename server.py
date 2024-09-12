import socket
import select
import pygame
import random
import pickle
import threading
import time
# 서버 설정
server_ip = '192.168.219.104'
server_port = 12345

# Pygame 초기화
pygame.init()

# 화면 설정
screen_width = 640
screen_height = 480

# 동그라미 클래스 정의
class Circle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = 20
        self.color = color
        self.active = False
        self.active_color = None

# 동그라미 생성 함수
def generate_circles():
    circles = []
    while len(circles) < 20:
        x = random.randint(50, screen_width - 50)
        y = random.randint(50, screen_height - 50)
        overlap = False
        for circle in circles:
            distance = ((x - circle.x) ** 2 + (y - circle.y) ** 2) ** 0.5
            if distance < circle.radius * 2:
                overlap = True
                break
        if not overlap:
            color = (255, 0, 0) if len(circles) < 10 else (0, 0, 255)
            circles.append(Circle(x, y, color))
    return circles

# 캐릭터 초기 위치 관리 (서버에서 관리)
characters = {
    # "player1": {"x": 100, "y": 100, "speed": 2, "direction": "down"},
    # "player2": {"x": 200, "y": 200, "speed": 2, "direction": "down"}
}

# 소켓 서버 설정
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(2)

print("서버가 시작되었습니다. 클라이언트 연결을 기다립니다...")

clients = []
circles = generate_circles()
timer_started = False
start_time = 0
total_time = 20
remaining_time = 0

# 클라이언트 핸들러 함수
def handle_client(client_socket):
    global circles, timer_started, start_time, characters, remaining_time
    client_socket.setblocking(0)
    try:
        while True:
            send_data = {}
            # select를 사용하여 데이터 수신 대기
            readable, _, _ = select.select([client_socket], [], [], 0)
            if readable:
                data = client_socket.recv(1024)
                if data:
                    message = pickle.loads(data)
                    client_id = message.get("id")  # 클라이언트 ID 수신
                    # 클라이언트가 게임 시작을 요청한 경우
                    if message.get("action") == "start_timer" and not timer_started:
                        print("타이머가 시작되었습니다.")
                        timer_started = True
                        start_time = pygame.time.get_ticks()
                        circles = generate_circles()
                        send_data['circles'] = circles

                    if message.get("action") == "move":
                        directions = message.get("move")  # 여러 방향 명령을 리스트로 받음
                        
                        # 리스트 내의 모든 방향을 처리
                        for direction in directions:
                            if direction == "up":
                                characters["player1"]["y"] -= characters["player1"]["speed"]
                                characters["player1"]["direction"] = "up"
                            if direction == "down":
                                characters["player1"]["y"] += characters["player1"]["speed"]
                                characters["player1"]["direction"] = "down"
                            if direction == "left":
                                characters["player1"]["x"] -= characters["player1"]["speed"]
                                characters["player1"]["direction"] = "left"
                            if direction == "right":
                                characters["player1"]["x"] += characters["player1"]["speed"]
                                characters["player1"]["direction"] = "right"

                    if message.get("action") == "character_info":
                        characters[message.get("id")] = message.get("info")
                        send_data["characters"] = characters

            # 타이머가 시작된 경우 남은 시간을 계산하여 클라이언트에 전송
            if timer_started:
                elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
                remaining_time = max(0, total_time - elapsed_time)
                
                # 남은 시간이 0이 되면 타이머 종료
                if remaining_time == 0:
                    timer_started = False
                    print("타이머가 종료되었습니다.")

                send_data['remaining_time'] = remaining_time
            send_data['timer_started'] = timer_started

            # 클라이언트에 데이터 전송
            client_socket.sendall(pickle.dumps(send_data))

            # 30hz로 제한
            time.sleep(1 / 100)

    except Exception as e:
        print(f"클라이언트 처리 중 오류: {e}")
    finally:
        if client_id in characters:
            del characters[client_id]
            print(f"클라이언트 {client_id}의 캐릭터 정보가 삭제되었습니다.")
        client_socket.close()
        print("클라이언트 연결이 종료되었습니다.")

# 서버 실행
try:
    while True:
        client_socket, _ = server_socket.accept()
        clients.append(client_socket)
        print("클라이언트가 연결되었습니다.")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

except KeyboardInterrupt:
    print("서버가 종료되었습니다.")
finally:
    for client in clients:
        client.close()
    server_socket.close()
    pygame.quit()
