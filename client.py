import pygame
import sys
import random
import asyncio
import socket
import pickle
import uuid

# Pygame 초기화
pygame.init()

# 화면 설정
screen_width = 640
screen_height = 480
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
direction = "down"
client_id = str(uuid.uuid4())
player_size = 40
player_x = screen_width // 2 - player_size // 2
player_y = screen_height // 2 - player_size // 2
player_speed = 2

# 두 번째 캐릭터 설정
player2_x = screen_width // 3 - player_size // 2
player2_y = screen_height // 3 - player_size // 2
player2_speed = 2

# 캐릭터 이미지 불러오기
character_up = pygame.image.load("character_up.png").convert_alpha()
character_down = pygame.image.load("character_down.png").convert_alpha()
character_left = pygame.image.load("character_left.png").convert_alpha()
character_right = pygame.image.load("character_right.png").convert_alpha()
character2_up = pygame.image.load("character2_up.png").convert_alpha()
character2_down = pygame.image.load("character2_down.png").convert_alpha()
character2_left = pygame.image.load("character2_left.png").convert_alpha()
character2_right = pygame.image.load("character2_right.png").convert_alpha()

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
            game_info = pickle.loads(data)
            return game_info
        except Exception as e:
            print(f"소켓 오류: {e}")
            break

async def handle_network(client_socket):
    global remaining_time, timer_started, characters
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
                print(f"서버로부터 받은 characters: {game_info['characters']}")
                characters = game_info['characters']
            pass

def interpolate(start_pos, end_pos, alpha):
    return start_pos + (end_pos - start_pos) * alpha

# 캐릭터 이동 요청 함수
def send_move_request(directions):
    move_message = {"action": "move", "move": directions}
    client_socket.sendall(pickle.dumps(move_message))

# 캐릭터 정보 전송 함수
def send_character_info(x, y, direction):
    character_info_message = {
        "action": "character_info",
        "id": client_id,  # 고유 ID 추가
        "x": x,
        "y": y,
        "direction": direction
    }
    print(f"캐릭터 정보 전송: {character_info_message}")
    client_socket.sendall(pickle.dumps(character_info_message))

async def main():
    global circles, timer_started, start_time, characters, direction
    global player_x, player_y, player2_x, player2_y, current_character, current_character2

    # 네트워크 통신 태스크 시작
    network_task = asyncio.create_task(handle_network(client_socket))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client_socket.close()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not timer_started:
                # 서버에 게임 시작 신호 보내기
                timer_started = True
                start_message = {"action": "start_timer"}
                client_socket.send(pickle.dumps(start_message))

        # 플레이어 이동 처리
        keys = pygame.key.get_pressed()
        # directions = []

        # if keys[pygame.K_LEFT]:
        #     directions.append("left")
        # if keys[pygame.K_RIGHT]:
        #     directions.append("right")
        # if keys[pygame.K_UP]:
        #     directions.append("up")
        # if keys[pygame.K_DOWN]:
        #     directions.append("down")

        # if directions:
        #     send_move_request(directions)

        if keys[pygame.K_LEFT]:
            player_x -= player_speed
            current_character = character_left
            direction = "left"
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
            current_character = character_right
            direction = "right"
        if keys[pygame.K_UP]:
            player_y -= player_speed
            current_character = character_up
            direction = "up"
        if keys[pygame.K_DOWN]:
            player_y += player_speed
            current_character = character_down
            direction = "down"
        
        send_character_info(player_x, player_y, direction)

        player_x = max(0, min(player_x, screen_width - player_size))
        player_y = max(0, min(player_y, screen_height - player_size))

        # if keys[pygame.K_a]:
        #     player2_x -= player2_speed
        #     current_character2 = character2_left
        # if keys[pygame.K_d]:
        #     player2_x += player2_speed
        #     current_character2 = character2_right
        # if keys[pygame.K_w]:
        #     player2_y -= player2_speed
        #     current_character2 = character2_up
        # if keys[pygame.K_s]:
        #     player2_y += player2_speed
        #     current_character2 = character2_down

        # player2_x = max(0, min(player2_x, screen_width - player_size))
        # player2_y = max(0, min(player2_y, screen_height - player_size))

        # 다른 캐릭터 위치 화면에 그리기
        for player_id, char in characters.items():
            if player_id != "client_id":
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
                # player_x = interpolate(player_x, char["x"], 0.5)
                # player_y = interpolate(player_y, char["y"], 0.5)

                player2_x, player2_y = char["x"], char["y"]

        # 화면 업데이트 처리
        screen.fill(WHITE)
        for circle in circles:
            circle.draw(screen)

        screen.blit(current_character, (player_x, player_y))
        screen.blit(current_character2, (player2_x, player2_y))

        # 충돌 처리
        for circle in circles:
            player1_collision = check_collision(player_x, player_y, circle)
            player2_collision = check_collision(player2_x, player2_y, circle)

            if player1_collision and player2_collision:
                continue
            elif player1_collision:
                circle.active = True
                circle.active_color = RED
            elif player2_collision:
                circle.active = True
                circle.active_color = BLUE
            else:
                circle.active = False

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

        if keys[pygame.K_RETURN] and timer_started:
            for circle in circles:
                if circle.active and circle.active_color == RED:
                    circle.flip_color()

        if keys[pygame.K_SPACE] and timer_started:
            for circle in circles:
                if circle.active and circle.active_color == BLUE:
                    circle.flip_color()

        pygame.display.flip()
        clock.tick(60)

        # 비동기 작업들이 실행될 시간을 양보
        await asyncio.sleep(0) 

if __name__ == "__main__":
    asyncio.run(main())
