import pygame
import sys
import random
import asyncio
import socket
import json
import uuid
import os
import copy
import json

# Pygame 초기화
pygame.init()

# 화면 설정
screen_width = 1080
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("2D RPG")

# 소켓 설정
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_socket.connect(('192.168.219.104', 12345))

# FPS 설정
clock = pygame.time.Clock()

# 색상 정의
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 폰트 설정
font = pygame.font.SysFont(None, 40)

# 캐릭터 설정
player_color = None
direction = "down"
client_id = str(uuid.uuid4())
player_size = 40
player_x = screen_width // 2 - player_size // 2
player_y = screen_height // 2 - player_size // 2
player_speed = 300
clock = pygame.time.Clock()

# 두 번째 캐릭터 설정
other_player_color = None
player2_x = screen_width // 3 - player_size // 2
player2_y = screen_height // 3 - player_size // 2
player2_speed = 2


def resource_path(relative_path):
    """ 리소스 파일의 절대 경로를 반환합니다. """
    try:
        # PyInstaller는 임시 폴더에서 파일을 실행할 때 '_MEIPASS' 폴더를 사용합니다.
        base_path = sys._MEIPASS
    except Exception:
        # 실행 파일이 아닐 때는 현재 파일의 위치를 사용합니다.
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 캐릭터 이미지 불러오기
character_up = pygame.image.load(resource_path("character_up.png")).convert_alpha()
character_down = pygame.image.load(resource_path("character_down.png")).convert_alpha()
character_left = pygame.image.load(resource_path("character_left.png")).convert_alpha()
character_right = pygame.image.load(resource_path("character_right.png")).convert_alpha()
character2_up = pygame.image.load(resource_path("character2_up.png")).convert_alpha()
character2_down = pygame.image.load(resource_path("character2_down.png")).convert_alpha()
character2_left = pygame.image.load(resource_path("character2_left.png")).convert_alpha()
character2_right = pygame.image.load(resource_path("character2_right.png")).convert_alpha()

# 이미지 크기 조정
character_up = pygame.transform.scale(character_up, (player_size, player_size))
character_down = pygame.transform.scale(character_down, (player_size, player_size))
character_left = pygame.transform.scale(character_left, (player_size, player_size))
character_right = pygame.transform.scale(character_right, (player_size, player_size))
character2_up = pygame.transform.scale(character2_up, (player_size, player_size))
character2_down = pygame.transform.scale(character2_down, (player_size, player_size))
character2_left = pygame.transform.scale(character2_left, (player_size, player_size))
character2_right = pygame.transform.scale(character2_right, (player_size, player_size))

# 초기 캐릭터 이미지 설정
current_character = character_down
current_character2 = character2_down

# 동그라미 클래스
class Circle:
    def __init__(self, x, y, color, id, is_gray=False, radius=20, active=False, active_color=None):
        self.id = id
        self.x = x
        self.y = y
        self.is_gray = is_gray  # 회색 상태 추가
        self.radius = 20
        self.color = color
        self.active = active
        self.active_color = active_color
        

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "color": list(self.color),
            "id": self.id,
            "active": self.active,
            "active_color": list(self.active_color) if self.active_color else None,
            "is_gray": self.is_gray
        }
    
    @staticmethod
    def from_dict(data):            
        return Circle(
            x=data['x'],
            y=data['y'],
            color=tuple(data['color']),  # 리스트를 tuple로 변환
            id=data['id'],
            active=data.get('active', False),
            active_color=tuple(data['active_color']) if data.get('active_color') else None,  # 리스트를 tuple로 변환 (None 체크)
            is_gray=data.get('is_gray', False)
        )

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        if self.active:
            pygame.draw.circle(screen, self.active_color, (self.x, self.y), self.radius + 5, 2)

    def flip_color(self):
        if self.active and self.active_color:
            self.color = self.active_color

    def set_gray(self):
        self.is_gray = True
        self.color = (128, 128, 128)

    def reset_color(self, color):
        self.is_gray = False
        self.color = color  # 원래 색상으로 복원

# 동그라미 생성 함수
def generate_circles():
    circles = []
    circle_length = 50
    circle_id = 0  # ID 생성용 초기값
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
            color = (255, 0, 0) if len(circles) < circle_length / 2 else (0, 0, 255)  # RED 또는 BLUE
            circles.append(Circle(x, y, color, circle_id))  # 고유 ID 부여
            circle_id += 1  # 다음 동그라미를 위해 ID 증가
    return circles

# 충돌 체크 함수
def check_collision(player_x, player_y, circle):
    player_center_x = player_x + player_size // 2
    player_center_y = player_y + player_size // 2
    distance = ((player_center_x - circle.x) ** 2 + (player_center_y - circle.y) ** 2) ** 0.5
    return distance < player_size // 2 + circle.radius

# 타이머 변수 초기화
remaining_time = 20
timer_started = False
start_time = 0
total_time = 20
circles = generate_circles()
characters = {}

async def receive_data(reader):
    try:
        # 데이터 길이(4바이트)를 비동기적으로 읽음
        data_length_bytes = await reader.readexactly(4)
        if not data_length_bytes:
            return None
        
        # 데이터 길이를 정수로 변환
        data_length = int.from_bytes(data_length_bytes, 'big')

        # 데이터 길이만큼 수신
        data = await reader.readexactly(data_length)

        # 받은 데이터를 JSON으로 디코딩
        try:
            game_info = json.loads(data.decode('utf-8'))
            return game_info
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류: {e}")
            return None

    except asyncio.IncompleteReadError as e:
        print(f"데이터 수신 중 오류: {e}")
        return None
    except Exception as e:
        print(f"소켓 오류: {e}")
        return None

async def handle_network(reader):
    global remaining_time, timer_started, characters, circles, player_color, other_player_color
    while True:
        game_info = await receive_data(reader)
        if game_info:
            if 'remaining_time' in game_info:
                remaining_time = game_info['remaining_time']
                # print(f"서버로부터 받은 remaining_time: {remaining_time}")
            if 'timer_started' in game_info:
                timer_started = game_info['timer_started']
                # print(f"서버로부터 받은 timer_started: {timer_started}")
            if 'characters' in game_info:
                characters = game_info['characters']
            if 'circles' in game_info:
                circles_data = game_info['circles']
                circles = [Circle.from_dict(circle_data) for circle_data in circles_data]
            if 'player_color' in game_info:
                color = game_info['player_color']  # 서버에서 받은 색상 설정
                player_color = (255, 0, 0) if color == 'RED' else (0, 0, 255)
                other_player_color = (0, 0, 255) if color == 'RED' else (255, 0, 0)
                print(f"서버로부터 받은 색상: {color}")

# 비동기 네트워크 전송 함수
async def send_data(writer, data):
    try:
        # sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # 데이터를 JSON으로 직렬화하고 UTF-8로 인코딩
        json_data = json.dumps(data).encode('utf-8')

        # 데이터 길이를 먼저 4바이트로 전송
        writer.write(len(json_data).to_bytes(4, 'big'))

        # 데이터 전송
        writer.write(json_data)
        await writer.drain()  # 데이터를 모두 보낼 때까지 대기
    except Exception as e:
        print(f"데이터 전송 중 오류: {e}")

def interpolate(start_pos, end_pos, alpha):
    return start_pos + (end_pos - start_pos) * alpha

# 캐릭터 정보 전송 함수
async def send_character_info(writer, x, y, direction):
    character_info_message = {
        "action": "character_info",
        "id": client_id,  # 고유 ID 추가
        "info": {"x": x, "y": y, "direction": direction}
    }
    await send_data(writer, character_info_message)
    # client_socket.sendall(json.dumps(character_info_message).encode('utf-8'))

# circles 정보 전송 함수 (여러 개 전송)
async def send_circles_status(writer, circles_status_list):
    circles_status_message = {
        "action": "circle_info_batch",
        "id": client_id,
        "circles": circles_status_list
    }
    await send_data(writer, circles_status_message)
    # client_socket.sendall(json.dumps(circles_status_message).encode('utf-8'))

async def request_color(writer):
    color_request = {"action": "request_color", "id": client_id}
    await send_data(writer, color_request)
    # client_socket.sendall(json.dumps(color_request).encode('utf-8'))
    
async def main():
    global circles, timer_started, start_time, characters, direction, player_color, other_player_color
    global player_x, player_y, player2_x, player2_y, current_character, current_character2

    # 마지막으로 쉬프트 키를 사용한 시간과 쿨타임 설정
    last_shift_time = -1000  # 초기값 설정
    shift_cooldown = 500  # 2초 (2000밀리초)
    CTRL_KEY = False

    # 비동기적으로 서버에 연결
    reader, writer = await asyncio.open_connection('192.168.219.104', 12345)

    # 네트워크 통신을 처리하는 task 생성
    network_task = asyncio.create_task(handle_network(reader))

    # 색상 요청
    await request_color(writer)
    # request_color()
    while player_color is None:
        print("색상을 받을 때까지 대기 중...")
        await asyncio.sleep(0.1)  # 짧은 대기 시간

    lock = asyncio.Lock()

    while True:
        df = clock.tick(50) / 1000.0  # 프레임 차이를 초 단위로 변환
        async with lock:  # 락을 사용하여 상태 보호
            local_circles = copy.deepcopy(circles)
            # 회색 있는지 검사
            for circle in local_circles:
                if circle.is_gray:
                    print(f"회색 동그라미 ID: {circle.id}")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    writer.close()
                    await writer.wait_closed()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and not timer_started:
                    # 서버에 게임 시작 신호 보내기
                    timer_started = True
                    start_message = {"action": "start_timer", "id": client_id}
                    # send_data(client_socket, start_message)
                    await send_data(writer, start_message)
                    # client_socket.send(json.dumps(start_message).encode('utf-8'))

            # 화면 업데이트 처리
            screen.fill(WHITE)
            # 플레이어 이동 처리
            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()  # 현재 시간

            player2_exist = False

            # 다른 캐릭터 위치 화면에 그리기
            for player_id, char in characters.items():
                if player_id != client_id:
                    # 캐릭터 방향에 따라 이미지를 선택
                    if char["direction"] == "up":
                        current_character2 = character2_up
                    elif char["direction"] == "down":
                        current_character2 = character2_down
                    elif char["direction"] == "left":
                        current_character2 = character2_left
                    elif char["direction"] == "right":
                        current_character2 = character2_right

                    # 캐릭터 위치를 보간하여 부드럽게 이동
                    player2_x = interpolate(player2_x, char["x"], 0.7)
                    player2_y = interpolate(player2_y, char["y"], 0.7)

                    # player2_x, player2_y = char["x"], char["y"]
                    player2_exist = True

            # 충돌 처리
            for index, circle in enumerate(local_circles):
                player1_collision = check_collision(player_x, player_y, circle)
                player2_collision = check_collision(player2_x, player2_y, circle) if player2_exist else False

                if player1_collision and player2_collision:
                    continue
                elif player1_collision:
                    circle.active = True
                    circle.active_color = player_color
                elif player2_collision:
                    circle.active = True
                    circle.active_color = other_player_color
                else:
                    circle.active = False

            prev_player_x, prev_player_y = player_x, player_y

            # 회색으로 바뀐 동그라미의 인덱스를 저장할 리스트
            gray_circles = []

            # 컨트롤 키가 눌린 상태에서 동그라미를 회색으로 변경
            if keys[pygame.K_LCTRL]:
                CTRL_KEY = True
                for index, circle in enumerate(local_circles):
                    if circle.active == True and circle.active_color == player_color:
                        circle.set_gray()
                        # 회색으로 변경된 동그라미의 인덱스를 기록
                        if circle.id not in gray_circles:
                            gray_circles.append(circle.id)  # 고유 ID로 관리

            if keys[pygame.K_LSHIFT] and current_time - last_shift_time >= shift_cooldown:
                if direction == "left":
                    player_x -= player_speed * 10 * df
                    # for index in gray_circles:
                    #     local_circles[index].x -= player_speed * 10 * df
                elif direction == "right":
                    player_x += player_speed * 10 * df
                    # for index in gray_circles:
                    #     local_circles[index].x += player_speed * 10 * df
                elif direction == "up":
                    player_y -= player_speed * 10 * df
                    # for index in gray_circles:
                    #     local_circles[index].y -= player_speed * 10 * df
                elif direction == "down":
                    player_y += player_speed * 10 * df
                    # for index in gray_circles:
                    #     local_circles[index].y += player_speed * 10 * df
                last_shift_time = current_time

            if keys[pygame.K_LEFT]:
                player_x -= player_speed * df
                current_character = character_left
                direction = "left"
                # for index in gray_circles:
                #     local_circles[index].x -= player_speed * df
            if keys[pygame.K_RIGHT]:
                player_x += player_speed * df
                current_character = character_right
                direction = "right"
                # for index in gray_circles:
                #     local_circles[index].x += player_speed * df
            if keys[pygame.K_UP]:
                player_y -= player_speed * df
                current_character = character_up
                direction = "up"
                # for index in gray_circles:
                #     local_circles[index].y -= player_speed * df
            if keys[pygame.K_DOWN]:
                player_y += player_speed * df
                current_character = character_down
                direction = "down"
                # for index in gray_circles:
                #     local_circles[index].y += player_speed * df

            if (keys[pygame.K_RETURN] or keys[pygame.K_SPACE]) and timer_started:
                for index, circle in enumerate(local_circles):
                    if circle.active and circle.active_color == player_color:
                        circle.flip_color()

            # 컨트롤 키를 뗐을 때 동그라미를 원래 색상으로 고정
            if not keys[pygame.K_LCTRL] :
                for circle in local_circles:
                    if circle.is_gray:
                        circle.reset_color(player_color)
                CTRL_KEY = False

            player_x = max(0, min(player_x, screen_width - player_size))
            player_y = max(0, min(player_y, screen_height - player_size))

            await send_character_info(writer, player_x, player_y, direction)

            # 서버로부터 남은 시간 받아서 화면에 표시
            if timer_started:
                timer_text = font.render(f"Timer: {remaining_time}s", True, BLACK)
                screen.blit(timer_text, (screen_width // 2 - 60, 10))
            else:
                start_text = font.render("Click to Start", True, BLACK)
                screen.blit(start_text, (screen_width // 2 - 100, 10))

            blue_count = sum(1 for circle in local_circles if circle.color == BLUE)
            red_count = sum(1 for circle in local_circles if circle.color == RED)

            blue_count_text = font.render(f"Blue: {blue_count}", True, BLUE)
            red_count_text = font.render(f"Red: {red_count}", True, RED)

            screen.blit(blue_count_text, (10, 10))
            screen.blit(red_count_text, (screen_width - 150, 10))

            # 변경된 상태를 저장할 리스트
            changed_circles = []

            server_circles_state = copy.deepcopy(circles)

            # 이동 차이 계산
            delta_x = player_x - prev_player_x
            delta_y = player_y - prev_player_y

            # 모든 local_circles 동그라미의 상태를 업데이트
            for index, circle in enumerate(local_circles):
                changed_circle = {}
                changed_circle["id"] = circle.id
                # 회색 동그라미 일 경우만 이동
                changed_circle["x"] = circle.x + delta_x if circle.is_gray else circle.x
                changed_circle["y"] = circle.y + delta_y if circle.is_gray else circle.y
                changed_circle["radius"] = circle.radius
                changed_circle["color"] = list(circle.color)
                changed_circle["active"] = circle.active
                changed_circle["active_color"] = list(circle.active_color) if circle.active_color else None
                changed_circle["is_gray"] = circle.is_gray
                changed_circles.append(changed_circle)
            



            # # 게임 루프 끝에서 변경된 부분을 비교
            # for index, (server_circle, local_circle) in enumerate(zip(server_circles_state, local_circles)):
            #     changed_circle = {}
            #     if server_circle.active != local_circle.active:
            #         changed_circle["active"] = local_circle.active
            #     if server_circle.active_color != local_circle.active_color:
            #         changed_circle["active_color"] = local_circle.active_color
            #     if server_circle.color != local_circle.color:
            #         changed_circle["color"] = local_circle.color
            #     if server_circle.x != local_circle.x:
            #         changed_circle["x"] = local_circle.x
            #     if server_circle.y != local_circle.y:
            #         changed_circle["y"] = local_circle.y
            #     if changed_circle:
            #         changed_circle["id"] = local_circle.id  # 고유 ID로 관리
            #         changed_circles.append(changed_circle)

            if changed_circles:
                # send_circles_status(changed_circles)
                await send_circles_status(writer, changed_circles)

            # 동기화 문제를 해결하기 위해 캐릭터가 이동한 만큼 동그라미도 이동
            for circle in local_circles:
                if circle.is_gray:  # 회색 동그라미만 이동 처리
                    circle.x += delta_x  # 캐릭터가 이동한 만큼 X좌표 변경
                    circle.y += delta_y  # 캐릭터가 이동한 만큼 Y좌표 변경

            for circle in circles:
                circle.draw(screen)

            if player2_exist:
                screen.blit(current_character2, (player2_x, player2_y))
            screen.blit(current_character, (player_x, player_y))       
            
            pygame.display.flip()
            

        # 비동기 작업들이 실행될 시간을 양보
        await asyncio.sleep(1/70) 
        

if __name__ == "__main__":
    asyncio.run(main())
