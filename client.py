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
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.219.104', 12345))

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
player_speed = 2
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
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = 20
        self.color = color
        self.active = False
        self.active_color = None

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        if self.active:
            pygame.draw.circle(screen, self.active_color, (self.x, self.y), self.radius + 5, 2)

    def flip_color(self):
        if self.active and self.active_color:
            self.color = self.active_color

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
            color = RED if len(circles) < 10 else BLUE
            circles.append(Circle(x, y, color))
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

# 비동기 네트워크 처리
async def receive_data(sock):
    while True:
        try:
            data = await asyncio.get_event_loop().run_in_executor(None, sock.recv, 4096)
            if not data:
                break
            game_info = json.loads(data.decode('utf-8'))
            return game_info
        except Exception as e:
            print(f"소켓 오류: {e}")
            break

async def handle_network(client_socket):
    global remaining_time, timer_started, characters, circles, player_color, other_player_color
    while True:
        game_info = await receive_data(client_socket)
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
                circles = game_info['circles']
            if 'player_color' in game_info:
                color = game_info['player_color']  # 서버에서 받은 색상 설정
                player_color = (255, 0, 0) if color == 'RED' else (0, 0, 255)
                other_player_color = (0, 0, 255) if color == 'RED' else (255, 0, 0)
                print(f"서버로부터 받은 색상: {color}")

def interpolate(start_pos, end_pos, alpha):
    return start_pos + (end_pos - start_pos) * alpha

# 캐릭터 정보 전송 함수
def send_character_info(x, y, direction):
    character_info_message = {
        "action": "character_info",
        "id": client_id,  # 고유 ID 추가
        "info": { "x": x, "y": y, "direction": direction }
    }
    client_socket.sendall(json.dumps(character_info_message).encode('utf-8'))

# circles 정보 전송 함수 (여러 개 전송)
def send_circles_status(circles_status_list):
    circles_status_message = {
        "action": "circle_info_batch",
        "id": client_id,
        "circles": circles_status_list
    }
    client_socket.sendall(json.dumps(circles_status_message).encode('utf-8'))

def request_color():
    color_request = {"action": "request_color", "id": client_id}
    client_socket.sendall(json.dumps(color_request).encode('utf-8'))
    
async def main():
    global circles, timer_started, start_time, characters, direction, player_color, other_player_color
    global player_x, player_y, player2_x, player2_y, current_character, current_character2

    # 마지막으로 쉬프트 키를 사용한 시간과 쿨타임 설정
    last_shift_time = -1000  # 초기값 설정
    shift_cooldown = 500  # 2초 (2000밀리초)
    CTRL_KEY = False

    # 네트워크 통신 태스크 시작
    network_task = asyncio.create_task(handle_network(client_socket))
    request_color()
    while player_color is None:
        print("색상을 받을 때까지 대기 중...")
        await asyncio.sleep(0.1)  # 짧은 대기 시간

    # 이전 상태를 저장할 변수
    previous_circles_state = copy.deepcopy(circles)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client_socket.close()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not timer_started:
                # 서버에 게임 시작 신호 보내기
                timer_started = True
                start_message = {"action": "start_timer", "id": client_id}
                client_socket.send(json.dumps(start_message).encode('utf-8'))

        # 화면 업데이트 처리
        screen.fill(WHITE)
        
        # 플레이어 이동 처리
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()  # 현재 시간

        for index, circle in enumerate(circles):
            # index 이전 상태를 저장할 변수
            prev_active = circle.active
            prev_active_color = circle.active_color


        # 회색으로 바뀐 동그라미의 인덱스를 저장할 리스트
        gray_circles = []

        # 컨트롤 키가 눌린 상태에서 동그라미를 회색으로 변경
        if keys[pygame.K_LCTRL]:
            CTRL_KEY = True
            for index, circle in enumerate(circles):
                if circle.active == True and circle.active_color == player_color:
                    circle.color = (128, 128, 128)  # 동그라미를 회색으로 변경
                    # 회색으로 변경된 동그라미의 인덱스를 기록
                    if index not in gray_circles:
                        gray_circles.append(index)

        # 쉬프트 키를 눌렀을 때 빠른 속도 적용
        if keys[pygame.K_LSHIFT] and current_time - last_shift_time >= shift_cooldown:
            # 현재 방향으로 이동
            if direction == "left":
                player_x -= player_speed * 10
                for index in gray_circles:
                    circles[index].x -= player_speed * 10
            elif direction == "right":
                player_x += player_speed * 10
                for index in gray_circles:
                    circles[index].x += player_speed * 10
            elif direction == "up":
                player_y -= player_speed * 10
                for index in gray_circles:
                    circles[index].y -= player_speed * 10
            elif direction == "down":
                player_y += player_speed * 10
                for index in gray_circles:
                    circles[index].y += player_speed * 10
            last_shift_time = current_time  # 마지막으로 쉬프트를 사용한 시간 업데이트

        if keys[pygame.K_LEFT]:
            player_x -= player_speed 
            current_character = character_left
            direction = "left"
            for index in gray_circles:
                circles[index].x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed 
            current_character = character_right
            direction = "right"
            for index in gray_circles:
                circles[index].x += player_speed
        if keys[pygame.K_UP]:
            player_y -= player_speed 
            current_character = character_up
            direction = "up"
            for index in gray_circles:
                circles[index].y -= player_speed
        if keys[pygame.K_DOWN]:
            player_y += player_speed
            current_character = character_down
            direction = "down"
            for index in gray_circles:
                circles[index].y += player_speed

        # 컨트롤 키를 뗐을 때 동그라미를 원래 색상으로 고정
        if CTRL_KEY and not keys[pygame.K_LCTRL] :
            for circle in circles:
                if circle.active and circle.active_color == player_color and circle.color == (128, 128, 128):
                    circle.color = player_color
            CTRL_KEY = False
        
        send_character_info(player_x, player_y, direction)

        player_x = max(0, min(player_x, screen_width - player_size))
        player_y = max(0, min(player_y, screen_height - player_size))

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
        
        # 변경된 상태를 저장할 리스트
        changed_circles = []

        # for index in gray_circles:
        #     changed_circles.append({
        #         "id": index,
        #         "color": circles[index].color,
        #         "x" : circles[index].x,
        #         "y" : circles[index].y
        #     })

        # 충돌 처리
        for index, circle in enumerate(circles):
            player1_collision = check_collision(player_x, player_y, circle)
            player2_collision = check_collision(player2_x, player2_y, circle) if player2_exist else False

            # 변경 여부를 추적하기 위해 이전 상태를 저장
            # prev_active = circle.active
            # prev_active_color = circle.active_color

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

            # # 상태가 변경되었을 경우에만 리스트에 추가
            # if circle.active != prev_active or circle.active_color != prev_active_color:
            #     changed_circles.append({
            #         "id": index,  # 고유 식별자, ID 사용
            #         "active": circle.active,
            #         "active_color": circle.active_color
            #     })

        # 서버로부터 남은 시간 받아서 화면에 표시
        if timer_started:
            timer_text = font.render(f"Timer: {remaining_time}s", True, BLACK)
            screen.blit(timer_text, (screen_width // 2 - 60, 10))
        else:
            start_text = font.render("Click to Start", True, BLACK)
            screen.blit(start_text, (screen_width // 2 - 100, 10))

        blue_count = sum(1 for circle in circles if circle.color == BLUE)
        red_count = sum(1 for circle in circles if circle.color == RED)

        blue_count_text = font.render(f"Blue: {blue_count}", True, BLUE)
        red_count_text = font.render(f"Red: {red_count}", True, RED)

        screen.blit(blue_count_text, (10, 10))
        screen.blit(red_count_text, (screen_width - 150, 10))

        if (keys[pygame.K_RETURN] or keys[pygame.K_SPACE]) and timer_started:
            for index, circle in enumerate(circles):
                if circle.active and circle.active_color == player_color:
                    circle.flip_color()
                    # changed_circles.append({
                    #     "id": index,
                    #     "color": circle.color
                    # })

        # 게임 루프 끝에서 변경된 부분을 비교
        for index, (prev_circle, curr_circle) in enumerate(zip(previous_circles_state, circles)):
            changed_circle = {}
            if prev_circle.active != curr_circle.active:
                changed_circle["active"] = curr_circle.active
            if prev_circle.active_color != curr_circle.active_color:
                changed_circle["active_color"] = curr_circle.active_color
            if prev_circle.color != curr_circle.color:
                changed_circle["color"] = curr_circle.color
            if prev_circle.x != curr_circle.x:
                changed_circle["x"] = curr_circle.x
            if prev_circle.y != curr_circle.y:
                changed_circle["y"] = curr_circle.y
            if changed_circle:
                changed_circle["id"] = index
                changed_circles.append(changed_circle)

        if changed_circles:
            send_circles_status(changed_circles)

        # 루프 끝에서 이전 상태를 업데이트
        previous_circles_state = copy.deepcopy(circles)

        for circle in circles:
            circle.draw(screen)

        if player2_exist:
            screen.blit(current_character2, (player2_x, player2_y))
        screen.blit(current_character, (player_x, player_y))        
        
        pygame.display.flip()
        clock.tick(70)

        # 비동기 작업들이 실행될 시간을 양보
        await asyncio.sleep(0) 

if __name__ == "__main__":
    asyncio.run(main())
