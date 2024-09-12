import pygame
import sys
import random

# Pygame 초기화
pygame.init()

# 화면 설정
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("2D RPG")

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
player_size = 40
player_x = screen_width // 2 - player_size // 2
player_y = screen_height // 2 - player_size // 2
player_speed = 2

# 두번째 캐릭터 설정
player2_x = screen_width // 3 - player_size // 2
player2_y = screen_height // 3 - player_size // 2
player2_speed = 2

# 캐릭터 이미지 불러오기 (첫 번째 캐릭터)
character_up = pygame.image.load("character_up.png").convert_alpha()
character_down = pygame.image.load("character_down.png").convert_alpha()
character_left = pygame.image.load("character_left.png").convert_alpha()
character_right = pygame.image.load("character_right.png").convert_alpha()

# 캐릭터 이미지 불러오기 (두 번째 캐릭터)
character2_up = pygame.image.load("character2_up.png").convert_alpha()
character2_down = pygame.image.load("character2_down.png").convert_alpha()
character2_left = pygame.image.load("character2_left.png").convert_alpha()
character2_right = pygame.image.load("character2_right.png").convert_alpha()

# 이미지 크기 조정 (첫 번째 캐릭터)
character_up = pygame.transform.scale(character_up, (player_size, player_size))
character_down = pygame.transform.scale(character_down, (player_size, player_size))
character_left = pygame.transform.scale(character_left, (player_size, player_size))
character_right = pygame.transform.scale(character_right, (player_size, player_size))

# 이미지 크기 조정 (두 번째 캐릭터)
character2_up = pygame.transform.scale(character2_up, (player_size, player_size))
character2_down = pygame.transform.scale(character2_down, (player_size, player_size))
character2_left = pygame.transform.scale(character2_left, (player_size, player_size))
character2_right = pygame.transform.scale(character2_right, (player_size, player_size))

# 초기 캐릭터 이미지 설정
current_character = character_down
current_character2 = character2_down  # 두 번째 캐릭터 초기 이미지

# 동그라미 클래스
class Circle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = 20
        self.color = color
        self.active = False  # 선이 활성화되었는지 여부
        self.active_color = None  # 활성화된 선의 색상 (빨강 or 파랑)

    def draw(self, screen):
        # 동그라미 그리기
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # 선이 활성화되었으면 그리기
        if self.active:
            pygame.draw.circle(screen, self.active_color, (self.x, self.y), self.radius + 5, 2)

    def flip_color(self):
        # 활성화된 선의 색상으로 동그라미 색을 바꿈
        if self.active and self.active_color:
            self.color = self.active_color

# 동그라미 생성 함수 (새롭게 동그라미를 흩뿌림)
def generate_circles():
    circles = []
    while len(circles) < 20:
        x = random.randint(50, screen_width - 50)
        y = random.randint(50, screen_height - 50)
        # 동그라미가 겹치지 않게 확인
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
    # 캐릭터의 중심 좌표 계산
    player_center_x = player_x + player_size // 2
    player_center_y = player_y + player_size // 2

    # 캐릭터의 중심과 동그라미의 중심 간의 거리 계산
    distance = ((player_center_x - circle.x) ** 2 + (player_center_y - circle.y) ** 2) ** 0.5
    return distance < player_size // 2 + circle.radius

# 타이머 및 시작 버튼 상태
timer_started = False
start_time = 0
total_time = 20  # 20초 타이머
circles = generate_circles()  # 처음 시작할 때 동그라미 생성

# 게임 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not timer_started:
            # 마우스 클릭으로 타이머 시작
            timer_started = True
            start_time = pygame.time.get_ticks()
            circles = generate_circles()  # 타이머 시작 시 동그라미 다시 생성

    # 키 입력 처리 (첫 번째 캐릭터 방향키로 이동)
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
        current_character = character_left  # 왼쪽으로 이동할 때 이미지 변경
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
        current_character = character_right  # 오른쪽으로 이동할 때 이미지 변경
    if keys[pygame.K_UP]:
        player_y -= player_speed
        current_character = character_up  # 위로 이동할 때 이미지 변경
    if keys[pygame.K_DOWN]:
        player_y += player_speed
        current_character = character_down  # 아래로 이동할 때 이미지 변경

    # 첫 번째 캐릭터가 화면을 벗어나지 않도록 제한
    player_x = max(0, min(player_x, screen_width - player_size))
    player_y = max(0, min(player_y, screen_height - player_size))

    # 키 입력 처리 (두 번째 캐릭터 AWSD로 이동)
    if keys[pygame.K_a]:
        player2_x -= player2_speed
        current_character2 = character2_left  # 왼쪽으로 이동할 때 이미지 변경
    if keys[pygame.K_d]:
        player2_x += player2_speed
        current_character2 = character2_right  # 오른쪽으로 이동할 때 이미지 변경
    if keys[pygame.K_w]:
        player2_y -= player2_speed
        current_character2 = character2_up  # 위로 이동할 때 이미지 변경
    if keys[pygame.K_s]:
        player2_y += player2_speed
        current_character2 = character2_down  # 아래로 이동할 때 이미지 변경

    # 두 번째 캐릭터가 화면을 벗어나지 않도록 제한
    player2_x = max(0, min(player2_x, screen_width - player_size))
    player2_y = max(0, min(player2_y, screen_height - player_size))

    # 화면 그리기
    screen.fill(WHITE)  # 배경을 흰색으로 채움

    # 동그라미 그리기
    for circle in circles:
        circle.draw(screen)

    # 캐릭터 그리기 (첫 번째 캐릭터)
    screen.blit(current_character, (player_x, player_y))
    # 캐릭터 그리기 (두 번째 캐릭터)
    screen.blit(current_character2, (player2_x, player2_y))

    # 첫 번째 캐릭터와 두 번째 캐릭터의 충돌 체크
    for circle in circles:
        player1_collision = check_collision(player_x, player_y, circle)
        player2_collision = check_collision(player2_x, player2_y, circle)

        if player1_collision and player2_collision:
            # 두 캐릭터가 모두 충돌할 경우 기존 상태 유지
            continue
        elif player1_collision:
            # 첫 번째 캐릭터만 충돌한 경우 빨간색으로 활성화
            circle.active = True
            circle.active_color = RED
        elif player2_collision:
            # 두 번째 캐릭터만 충돌한 경우 파란색으로 활성화
            circle.active = True
            circle.active_color = BLUE
        else:
            # 두 캐릭터 모두 충돌하지 않으면 비활성화
            circle.active = False

    # 타이머 표시
    if timer_started:
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        remaining_time = max(0, total_time - elapsed_time)
        timer_text = font.render(f"Timer: {remaining_time}s", True, BLACK)
        screen.blit(timer_text, (screen_width // 2 - 60, 10))

        # 타이머가 0이면 뒤집기 기능 비활성화
        if remaining_time == 0:
            timer_started = False  # 타이머 종료
    else:
        start_text = font.render("Click to Start", True, BLACK)
        screen.blit(start_text, (screen_width // 2 - 100, 10))

    # 파란색 및 빨간색 동그라미 개수 세기
    blue_count = sum(1 for circle in circles if circle.color == BLUE)
    red_count = sum(1 for circle in circles if circle.color == RED)

    blue_count_text = font.render(f"Blue: {blue_count}", True, BLUE)
    red_count_text = font.render(f"Red: {red_count}", True, RED)

    screen.blit(blue_count_text, (10, 10))  # 파란색 동그라미 개수 왼쪽에 표시
    screen.blit(red_count_text, (screen_width - 150, 10))  # 빨간색 동그라미 개수 오른쪽에 표시

    # 첫 번째 캐릭터의 뒤집기 키 (엔터키), 타이머가 작동 중일 때만 가능
    if keys[pygame.K_RETURN] and timer_started:
        for circle in circles:
            if circle.active and circle.active_color == RED:
                circle.flip_color()  # 빨간색으로 뒤집기

    # 두 번째 캐릭터의 뒤집기 키 (스페이스바), 타이머가 작동 중일 때만 가능
    if keys[pygame.K_SPACE] and timer_started:
        for circle in circles:
            if circle.active and circle.active_color == BLUE:
                circle.flip_color()  # 파란색으로 뒤집기

    pygame.display.flip()  # 화면 업데이트
    clock.tick(60)  # FPS 60으로 설정

pygame.quit()
sys.exit()
