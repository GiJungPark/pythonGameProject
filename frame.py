import math
import os
import random
import pygame
##########################################################################
#초기화 pygame import시 반드시 필요
pygame.init() 

# 화면 크기 설정
screen_width = 1280 #가로 크기
screen_height = 800 #세로 크기
screen = pygame.display.set_mode((screen_width, screen_height))

# 화면 타이틀 설정
pygame.display.set_caption("AloneSurvive") #게임 이름

# FPS
clock = pygame.time.Clock()
##########################################################################
# 1. 사용자 게임 초기화 (배경 화면, 게임 이미지, 좌표, 속도, 폰트 등)
# 현재 파일의 위치 반환
current_path = os.path.dirname(__file__)
# images 폴더 위치 반환
image_path = os.path.join(current_path, "images") 

# 현재 파일의 위치 반환
current_path = os.path.dirname(__file__) 
# sounds 폴더 위치 반환
sounds_path = os.path.join(current_path, "sounds") 

#첫 화면 이미지 불러오기
start_background = pygame.image.load(os.path.join(image_path, "startBackGround.png"))
#배경 이미지 불러오기
background = pygame.image.load(os.path.join(image_path, "backGround.png"))

################################캐릭터#####################################
#캐릭터 좌표 만들기 및 이미지 불러오기
character = pygame.image.load(os.path.join(image_path, "character.png"))
character_size = character.get_rect().size
character_rect = character.get_rect()
character_width = character_size[0]
character_height = character_size[1]
character_x_pos = (screen_width / 2) - (character_width / 2)
character_y_pos = (screen_height / 2) + (character_height / 2)
#캐릭터 이동 방향
character_to_x = 0
character_to_y = 0
#캐릭터 이동 속도
character_speed = 1
#캐릭터 체력
character_hp = 100
#캐릭터 공격력
character_power = 2

################################무기클래스###################################
class Bullet(pygame.sprite.Sprite): 
  def __init__(self):
    super().__init__()
    #무기 이미지 불러오기
    self.bullet_image = pygame.image.load(os.path.join(image_path, "weapon.png"))
    #마우스 좌표
    mouse_x = pygame.mouse.get_pos()[0] 
    mouse_y = pygame.mouse.get_pos()[1]
    #공격 방향 (angle)
    self.angle = math.pi - math.atan2(mouse_x - int(character_x_pos), mouse_y - int(character_y_pos))
    self.image = pygame.transform.rotate(self.bullet_image, -(int(math.degrees(self.angle))))
    #무기 이동속도
    self.speed = 10
    #무기 좌표
    self.x = 0
    self.y = 0
    self.rect = self.image.get_rect()
    
  def update(self):
    #마우스 좌표 방향으로 이동
    self.x += self.speed * math.sin(self.angle)
    self.y -= self.speed * math.cos(self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = (int(character_x_pos + (character_width / 2)) + self.x, int(character_y_pos + (character_height / 2)) + self.y)
    
################################에임클래스###################################
class Crosshair(pygame.sprite.Sprite):
  def __init__(self):
      super().__init__()
      #에임 이미지 불러오기
      self.image = pygame.image.load(os.path.join(image_path, "crosshair.png"))
      self.rect = self.image.get_rect()

  def update(self):
      #마우스 위치로 좌표 변경
      self.rect.center = pygame.mouse.get_pos()

################################적클래스#################################### 
class Enemy(pygame.sprite.Sprite):
  def __init__(self):
    super().__init__()
    #적 이미지 불러오기
    self.image = pygame.image.load(os.path.join(image_path, "enemy.png"))
    self.rect = self.image.get_rect()
    #화면 내 랜덤하게 좌표 설정
    self.x = random.randrange(screen_width - self.rect.width)
    self.y = random.randrange(screen_height - self.rect.height)
    #적 이동속도
    self.speed = 3
    #적 이동방향
    self.direction = 1
    #적 체력
    self.hp = 10
    #적 공격력
    self.attack = 1

  def update(self):
    #x좌표가 스크린 끝부분에 도착하면 y좌표 변경 후 방향 전환
    self.x += self.speed * self.direction
    if self.hp > 0:
      if self.x <= 0:
        self.y += 20
        self.direction = 1
      if self.x + 40 >= screen_width:
        self.y += 20
        self.direction = -1
      self.rect = self.image.get_rect()
      self.rect.center = (int(self.x), int(self.y))

    #몬스터 사망시 객체 지움
    if self.hp <= 0:
      self.kill()
      self.rect.center = (-100, -100)
      

################################클래스 선언, sprit 그룹화#################
#무기 클래스
bullet = Bullet()
#무기 sprite 그룹화
bullet_list = pygame.sprite.Group() 
#에임 클래스
crosshair = Crosshair()
#에임 sprite 그룹화
crosshair_group = pygame.sprite.Group()
#적 클래스
enemy = Enemy()
#적 sprite 그룹화
enemy_list = pygame.sprite.Group()


################################변수######################################
#소리 변수
#메인 사운드 가져오기
main_sound = pygame.mixer.Sound((os.path.join(sounds_path, "bgm.mp3")))
#총 사운드 가져오기
shout_sound = pygame.mixer.Sound((os.path.join(sounds_path, "shoot.mp3")))
#장전 사운드 가져오기
reload_sound = pygame.mixer.Sound((os.path.join(sounds_path, "reload.wav")))
#쿨타임
last = pygame.time.get_ticks()  #마지막으로 공격한 시간을 얻는 값
cooldown = 300                  #공격 쿨타임 0.3초
reload = 2000                   #재장전 쿨타임 2초
#재장전
count = 6                       
#코인
coin = 0
#몹 업데이트 변수 (시작과 동시에 적 만들기 위해 -100000)
mob_last_update = -10000
#상태 변수(화면 전환)
Start = True
Play = False
#게임이 진행중인가를 파악하는 변수
running = True 

################################초기설정####################################
#마우스 포인터 보이게
pygame.mouse.set_visible(True)
#BGM 무한 반복
main_sound.play(-1)


################################이벤트루프####################################
while running:
  dt = clock.tick(60) #게임화면의 초당 프레임 수를 설정
################################시작 화면#####################################
  if Start :
    for event in pygame.event.get():  #어떤 이벤트가 발생
      if event.type == pygame.QUIT:   #창이 닫히는 이벤트가 발생
        running = False               #게임 종료

      #시작 화면 클릭으로 화면 전환 
      if event.type == pygame.MOUSEBUTTONDOWN: 
        #Start 좌표
        if (590 < pygame.mouse.get_pos()[0] < 690) and (480 < pygame.mouse.get_pos()[1] < 520):
          Start = False
          Play = True
          #게임 시작한 시간을 확인하는 변수 (제한 시간 타이머에 사용)
          play_now = int(pygame.time.get_ticks()/1000)
        #Quit 좌표
        if (590 < pygame.mouse.get_pos()[0] < 690) and (570 < pygame.mouse.get_pos()[1] < 620):
          running = False
    
    #시작 화면 그리기
    screen.blit(start_background, (0, 0))
    #화면 업데이트
    pygame.display.update()
  
################################게임 화면#####################################
  if Play :
    #제한시간 타이머 (200초 카운트, 200초 초과시 게임)
    timer = 200 + play_now - int(pygame.time.get_ticks()/1000)
    if timer == 0:
      running = False
    #마우스 포인터 가리기 
    pygame.mouse.set_visible(False)
    #현재 시간 변수
    now = pygame.time.get_ticks()
    
    for event in pygame.event.get():  #어떤 이벤트가 발생
      if event.type == pygame.QUIT:   #창이 닫히는 이벤트가 발생
        running = False               #게임 종료
#############################키보드를 입력할때############################
      if event.type == pygame.KEYDOWN:
        #캐릭터 방향키
        if event.key == pygame.K_a:   #왼쪽이동
          character_to_x -= character_speed
        elif event.key == pygame.K_d: #오른쪽이동
          character_to_x += character_speed
        elif event.key == pygame.K_w: #위이동
          character_to_y -= character_speed
        elif event.key == pygame.K_s: #아래이동
          character_to_y += character_speed
        elif event.key == pygame.K_r: #재장전
          if now - last >= reload:    #총을 사용한지 2초가 지나야 장전 가능
            last = now
            reload_sound.play()       #장전 사운드 출력
            count = 6
        #구매 키
        if event.key == pygame.K_z:   #공격력 증가
          if coin >= 2:               #coin이 2개 이상인 경우 구매 가능하며,
            coin -= 2                 #코인 2개로 구매가능
            character_power += 1
        elif event.key == pygame.K_x: #이동속도 증가
          if coin >= 2:               #coin이 2개 이상인 경우 구매 가능하며,
            coin -= 2                 #코인 2개로 구매가능
            character_speed += 1
        #메인 사운드 볼륨 조정 키
        if event.key == pygame.K_u:     #볼륨 증가
          main_volume = main_sound.get_volume()
          main_sound.set_volume(main_volume + 0.1)
        elif event.key == pygame.K_i:   #볼륨 감소
          main_volume = main_sound.get_volume()
          main_sound.set_volume(main_volume - 0.1)
        elif event.key == pygame.K_o:   #메인 사운드 일시중지
          main_sound.stop()
        elif event.key == pygame.K_p:   #메인 사운드 재시작
          main_sound.play(-1)
      
###########################키보드를 입력을 멈출때############################
      if event.type == pygame.KEYUP:
        #이동키를 땔 경우 멈춤
        if event.key == pygame.K_a or event.key == pygame.K_d:
          character_to_x = 0
        elif event.key == pygame.K_w or event.key == pygame.K_s:
          character_to_y = 0

#############################마우스를 클릭할때############################
      if event.type == pygame.MOUSEBUTTONDOWN:
        #총알이 1개 이상인 경우만 가능
        if count > 0:
          # 공격 쿨타임 0.3초
          if now - last >= cooldown:
            last = now
            #bullet_list 공격 클래스 객체 추가, 총 사운드 재생
            #총알 갯수 1개 차감
            bullet = Bullet()
            bullet_list.add(bullet)
            shout_sound.play()
            count -= 1
            
        #총알이 없는 경우
        elif now - last >= reload:
          #재장전 2초, 재장전 사운드 재생
          last = now
          reload_sound.play()
          count = 6

##########################캐릭터 위치 조정############################
    #이동한 좌표를 계속 업데이트
    character_x_pos += character_to_x
    character_y_pos += character_to_y
    #캐릭터 좌표 가져오기
    character_rect = character.get_rect()
    character_rect.left = character_x_pos
    character_rect.top = character_y_pos

    #스크린 밖으로 캐릭터가 나가지 못하도록 범위 설정
    if character_x_pos < 0:
      character_x_pos = 0
    elif character_x_pos > screen_width - character_width:
      character_x_pos = screen_width - character_width

    if character_y_pos < 0:
      character_y_pos = 0
    elif character_y_pos > screen_height - character_height:
      character_y_pos = screen_height - character_height

##########################몬스터 리스폰############################
    if now - mob_last_update > 10000:
      enemy = Enemy()
      mob_last_update = now
      enemy_list.add(enemy)

##########################화면에 그리기############################
    #배경 및 캐릭터 그리기
    screen.blit(background, (0, 0))
    screen.blit(character, (character_x_pos, character_y_pos))
    #총알 그리기
    bullet_list.update()
    bullet_list.draw(screen)
    #에임 그리기
    crosshair_group.add(crosshair)
    crosshair_group.update()
    crosshair_group.draw(screen)
    #적 그리기
    enemy_list.update()
    enemy_list.draw(screen)
      
################################충돌###############################
    #총알과 몬스터가 충돌할 경우
    hits = pygame.sprite.groupcollide(enemy_list, bullet_list, False, True)
    for hit in hits:
      enemy.hp -= character_power
      if enemy.hp <= 0:
        coin += 2
    #몬스터와 캐릭터가 충돌할 경우
    if character_rect.colliderect(enemy.rect):
      character_hp -= enemy.attack
      if character_hp < 0:
        running = False

#################################Text 설정#########################
    #폰트 설정
    nonFont = pygame.font.SysFont("arial", 25, True, False)
    timeFont = pygame.font.SysFont("arial", 50, True, False)
    aimFont = pygame.font.SysFont("arial", 20, True, False)
    BLACK = ( 0, 0, 0 )
    #객체에 Text 작성
    hp_Text = nonFont.render(f'HP : {str(character_hp)}', True, BLACK)
    coin_Text = nonFont.render(f'COIN : {str(coin)}', True, BLACK)
    damage_Text = nonFont.render(f'DAMEGE : {str(character_power)}', True, BLACK)
    speed_Text = nonFont.render(f'SPEED : {str(character_speed)}', True, BLACK)
    bullet_Text = nonFont.render(f'BULLET : {str(count)}', True, BLACK)
    timer_Text = timeFont.render(str(timer), True, BLACK)
    count_Text = aimFont.render(str(count), True, BLACK)
    reload_Text = aimFont.render('Reload!!!', True, BLACK)
    enemyHp_Text = aimFont.render(str(enemy.hp), True, BLACK)
    #Text 그리기
    screen.blit(hp_Text, [0, 0])
    screen.blit(coin_Text, [0, 25])
    screen.blit(damage_Text, [0, 50])
    screen.blit(speed_Text, [0, 75])
    screen.blit(bullet_Text, [0, 100])
    screen.blit(timer_Text, [600, 0])
    screen.blit(enemyHp_Text, [enemy.rect[0], enemy.rect[1]])
    if count > 0:
      screen.blit(count_Text, [pygame.mouse.get_pos()[0] + 10, pygame.mouse.get_pos()[1] + 10])
    else:
      screen.blit(reload_Text, [pygame.mouse.get_pos()[0] + 10, pygame.mouse.get_pos()[1] + 10])


    #화면 업데이트
    pygame.display.update()
# pygame 종료
pygame.quit()