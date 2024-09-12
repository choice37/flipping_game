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

# 캐릭터 설정
player_size = 40
player_x = screen_width // 2 - player_size // 2
player_y = screen_height // 2 - player_size // 2
player_speed = 2  # 캐릭터 이동 속도를 2/3로 감소

# 배경 이미지 불러오기
background_image = pygame.image.load("background.png")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# 캐릭터 이미지 불러오기 (방향별 이미지)
character_up = pygame.image.load("character_up.png").convert_alpha()
character_down = pygame.image.load("character_down.png").convert_alpha()
character_left = pygame.image.load("character_left.png").convert_alpha()
character_right = pygame.image.load("character_right.png").convert_alpha()

# 연기 이미지 불러오기
smoke_image = pygame.image.load("smoke.png").convert_alpha()  # 연기 이미지
smoke_image = pygame.transform.scale(smoke_image, (player_size*1.2, player_size*1.2))  # 크기를 캐릭터 크기와 맞춤

# 이미지 크기 조정
character_up = pygame.transform.scale(character_up, (player_size, player_size))
character_down = pygame.transform.scale(character_down, (player_size, player_size))
character_left = pygame.transform.scale(character_left, (player_size, player_size))
character_right = pygame.transform.scale(character_right, (player_size, player_size))

# 초기 캐릭터 이미지는 아래쪽을 향하게 설정
current_character = character_down

# 복제 캐릭터 클래스
class Clone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice(["up", "down", "left", "right"])  # 랜덤한 방향 선택
        self.speed = 2  # 복제 캐릭터의 속도 설정
        self.start_time = pygame.time.get_ticks()  # 복제 캐릭터 생성 시간 저장
        self.last_direction_change = pygame.time.get_ticks()  # 마지막으로 방향이 바뀐 시간 저장

    def move(self):
        current_time = pygame.time.get_ticks()
        
        # 1초마다 랜덤한 방향 변경
        if current_time - self.last_direction_change > 500:
            self.direction = random.choice(["up", "down", "left", "right"])
            self.last_direction_change = current_time
        
        # 방향에 따라 캐릭터 이동
        if self.direction == "up":
            self.y -= self.speed
        elif self.direction == "down":
            self.y += self.speed
        elif self.direction == "left":
            self.x -= self.speed
        elif self.direction == "right":
            self.x += self.speed

    def get_image(self):
        # 방향에 따라 올바른 이미지를 반환
        if self.direction == "up":
            return character_up
        elif self.direction == "down":
            return character_down
        elif self.direction == "left":
            return character_left
        elif self.direction == "right":
            return character_right

    def is_expired(self):
        # 3초가 지나면 삭제
        return pygame.time.get_ticks() - self.start_time > 3000

# 연기 이펙트 클래스
class SmokeEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()  # 이펙트가 생성된 시간

    def is_expired(self):
        # 0.5초 후 이펙트가 사라짐
        return pygame.time.get_ticks() - self.start_time > 500

    def draw(self, screen):
        # 연기 이미지를 그리기
        screen.blit(smoke_image, (self.x, self.y))

# 복제 캐릭터 (하나만 유지)
clones = []
smoke_effect = None  # 연기 이펙트를 저장할 변수

# 게임 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 키 입력 처리
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

    # Z 키를 눌렀을 때 복제 캐릭터가 없으면 하나만 생성
    if keys[pygame.K_z] and smoke_effect is None:
        # 복제 캐릭터 생성
        clones.append(Clone(player_x, player_y))  # 새로운 복제 캐릭터를 리스트에 추가
        # 연기 이펙트 생성
        smoke_effect = SmokeEffect(player_x, player_y)

    # 화면 그리기
    screen.blit(background_image, (0, 0))  # 배경 이미지 그리기
    screen.blit(current_character, (player_x, player_y))  # 현재 방향에 맞는 캐릭터 이미지 그리기

    # 연기 이펙트가 있으면 그리기
    if smoke_effect:
        smoke_effect.draw(screen)
        # 연기 이펙트가 0.5초 후에 사라짐
        if smoke_effect.is_expired():
            smoke_effect = None

    # 복제 캐릭터가 있으면 이동 및 그리기
    for clone in clones:
        clone.move()
        clone_image = clone.get_image()  # 복제 캐릭터의 방향에 맞는 이미지 가져오기
        screen.blit(clone_image, (clone.x, clone.y))  # 복제 캐릭터 이미지 그리기


    # 3초가 지나면 복제 캐릭터 삭제
    clones = [clone for clone in clones if not clone.is_expired()]

    pygame.display.flip()  # 화면 업데이트
    clock.tick(60)  # FPS 60으로 설정

pygame.quit()
sys.exit()
