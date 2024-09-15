import asyncio
import pygame
import random
import pickle
import time
import json

# 서버 설정
server_ip = '192.168.219.104'
server_port = 12345

# Pygame 초기화
pygame.init()

# 화면 설정
screen_width = 1080
screen_height = 720

# 동그라미 클래스 정의
class Circle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = 20
        self.color = color
        self.active = False
        self.active_color = None

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "color": self.color
        }
    
    @staticmethod
    def from_dict(data):
        return Circle(
            x=data['x'],
            y=data['y'],
            radius=data['radius'],
            color=data['color'],
            active=data.get('active', False),
            active_color=data.get('active_color', None)
        )

# 동그라미 생성 함수
def generate_circles():
    circles = []
    circle_length = 50
    while len(circles) < circle_length:
        x = random.randint(50, screen_width - 50)
        y = random.randint(50, screen_height - 50)
        overlap = False
        for circle in circles:
            distance = ((x - circle.x) ** 2 + (y - circle.y) ** 2) ** 0.5
            if distance < circle.radius * 2:
                overlap = True
                break
        if not overlap:
            color = (255, 0, 0) if len(circles) < circle_length / 2 else (0, 0, 255)
            circles.append(Circle(x, y, color))
    return circles

# 캐릭터 초기 위치 관리 (서버에서 관리)
characters = {}

circles = generate_circles()
timer_started = False
start_time = 0
total_time = 20
remaining_time = 0

async def handle_client(reader, writer):
    global circles, timer_started, start_time, characters, remaining_time
    client_id = None
    try:
        last_time = time.time()
        while True:
            send_data = {}

            # 비동기적으로 클라이언트에서 데이터 읽기
            data = await reader.read(1024)
            if not data:
                break

            message = json.loads(data.decode('utf-8'))
            client_id = message.get("id")  # 클라이언트 ID 수신
            if message.get("action") == "request_color":
                print('색상 요청이 왔습니다.')
                send_data["player_color"] = "RED" if len(characters) == 0 else "BLUE"

            # 클라이언트가 게임 시작을 요청한 경우
            if message.get("action") == "start_timer" and not timer_started:
                print("타이머가 시작되었습니다.")
                timer_started = True
                start_time = pygame.time.get_ticks()
                circles = generate_circles()

            if message.get("action") == "character_info":
                characters[message.get("id")] = message.get("info")
                send_data["characters"] = characters

            if message.get("action") == "circle_info_batch":
                # 여러 개의 변경된 circle 상태를 처리
                for circle_data in message.get("circles"):
                    circle_id = circle_data["id"]  # circle_id는 리스트의 인덱스

                    # 서버에서 해당 circle 상태 업데이트 (리스트 인덱스 사용)
                    if 0 <= circle_id < len(circles):
                        circle = circles[circle_id]
                        # circle_data에 해당 값이 있을 때만 업데이트
                        if "color" in circle_data:
                            circle.color = circle_data["color"]
                        if "active" in circle_data:
                            circle.active = circle_data["active"]
                        if "active_color" in circle_data:
                            circle.active_color = circle_data["active_color"]
                        if "x" in circle_data:
                            circle.x = circle_data["x"]
                        if "y" in circle_data:
                            circle.y = circle_data["y"]

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
            circle_dict_list = [circle.to_dict() for circle in circles]
            send_data['circles'] = circle_dict_list

            # 클라이언트에 데이터 비동기 전송
            writer.write(json.dumps(send_data).encode('utf-8'))
            await writer.drain()

            # 60hz로 제한
            # await asyncio.sleep(1 / 60)
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
        
        # 여기서 delta_time을 사용하여 타이머 및 게임 업데이트
        await asyncio.sleep(max(1/70 - delta_time, 0))  # 70Hz를 유지하면서도 부드럽게 처리

    except Exception as e:
        print(f"클라이언트 처리 중 오류: {e}")
    finally:
        if client_id in characters:
            del characters[client_id]
            print(f"클라이언트 {client_id}의 캐릭터 정보가 삭제되었습니다.")
        writer.close()
        await writer.wait_closed()
        print("클라이언트 연결이 종료되었습니다.")

async def main():
    server = await asyncio.start_server(handle_client, server_ip, server_port)
    print(f"서버가 {server_ip}:{server_port}에서 시작되었습니다.")

    async with server:
        await server.serve_forever()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("서버가 종료되었습니다.")
finally:
    pygame.quit()
