import pygame
import time
import myPongProtocol

pygame.init()

# Font that is used to render the text
font20 = pygame.font.Font('fonts/256_bytes.ttf', 90)
font21 = pygame.font.Font('fonts/256_bytes.ttf', 50)
font22 = pygame.font.Font('fonts/256_bytes.ttf', 30)
font23 = pygame.font.Font('fonts/256_bytes.ttf', 22)

# RGB values of standard colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Basic parameters of the screen
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TelePong Party - Waiting for players")

clock = pygame.time.Clock()
FPS = 30

# Striker class


class Striker:
        # Take the initial position, dimensions, speed and color of the object
    def __init__(self, posx, posy, width, height, speed, color, name):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.name = name
        # Rect that is used to control the position and collision of the object
        self.playerRect = pygame.Rect(posx, posy, width, height)
        # Object that is blit on the screen
        self.player = pygame.draw.rect(screen, self.color, self.playerRect)

    # Used to display the object on the screen
    def display(self):
        self.player = pygame.draw.rect(screen, self.color, self.playerRect)

    def update(self, yFac):
        self.posy = self.posy + self.speed*yFac

        # Restricting the striker to be below the top surface of the screen
        if self.posy <= 0:
            self.posy = 0
        # Restricting the striker to be above the bottom surface of the screen
        elif self.posy + self.height >= HEIGHT:
            self.posy = HEIGHT-self.height

        # Updating the rect with the new values
        self.playerRect = (self.posx, self.posy, self.width, self.height)

    def displayScore(self, score, x, y, color):
        text = font20.render(str(score), True, color)
        textRect = text.get_rect()
        textRect.center = (x, y)

        screen.blit(text, textRect)

    def displayNickname(self, nickname, x, y, color):
        text = font22.render(nickname, True, color)
        textRect = text.get_rect()
        textRect.center = (x, y)

        screen.blit(text, textRect)

    def getRect(self):
        return self.playerRect
    
    def reset(self):
        if self.name == "Player 1":
            self.posx = 20
            self.posy = (HEIGHT//2)-70
        elif self.name == "Player 2":
            self.posx = WIDTH-30
            self.posy = (HEIGHT//2)-70

# Ball class


class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.speed = speed
        self.color = color
        self.xFac = 1
        self.yFac = -1
        self.ball = pygame.draw.circle(
            screen, self.color, (self.posx, self.posy), self.radius)
        self.firstTime = 1

    def display(self):
        self.ball = pygame.draw.circle(
            screen, self.color, (self.posx, self.posy), self.radius)

    def update(self):
        self.posx += self.speed*self.xFac
        self.posy += self.speed*self.yFac

        # If the ball hits the top or bottom surfaces,
        # then the sign of yFac is changed and
        # it results in a reflection
        if self.posy <= 0 or self.posy >= HEIGHT:
            self.yFac *= -1

        if self.posx <= 0 and self.firstTime:
            self.firstTime = 0
            return 1
        elif self.posx >= WIDTH and self.firstTime:
            self.firstTime = 0
            return -1
        else:
            return 0

    def reset(self):
        self.posx = WIDTH//2
        self.posy = HEIGHT//2
        self.xFac *= -1
        self.firstTime = 1

    # Used to reflect the ball along the X-axis
    def hit(self):
        self.xFac *= -1

    def getRect(self):
        return self.ball

# Game Manager


def main():
    running = True
    show = True
    movements = []

    nickname = input()
    oppNickname = " "
    
    client_socket = myPongProtocol.createSocket()

    myPongProtocol.sendMsg("SERVER INIT_PLAYER", client_socket)

    # Se debe pedir por pantalla la IP y PORT del server para almacenarlos
    #  y poder después hacer el envío de mensajes.

    playerNumber, gameId = myPongProtocol.createPlayer(nickname, client_socket)
    while len(oppNickname) == 1:
        oppNickname = myPongProtocol.receiveOpponent(client_socket)
    
    # Defining the objects
    if playerNumber == 1:
        player1 = Striker(20, (HEIGHT//2)-70, 15, 110, 10, WHITE, nickname)
        player2 = Striker(WIDTH-30, (HEIGHT//2)-70, 15, 110, 10, WHITE, oppNickname)
    elif playerNumber == 2:
        player1 = Striker(20, (HEIGHT//2)-70, 15, 110, 10, WHITE, oppNickname)
        player2 = Striker(WIDTH-30, (HEIGHT//2)-70, 15, 110, 10, WHITE, nickname)
    
    pygame.display.set_caption("TelePong Party - "+player1.name+" vs "+player2.name)

    ball = Ball(WIDTH//2, HEIGHT//2, 9, 2, WHITE)

    listOfPlayers = [player1, player2]

    # Initial parameters of the players
    player1Score, player2Score = 0, 0
    player1YFac, player2YFac = 0, 0
    winner = Striker

    while running:
        screen.fill(BLACK)
        for i in range(0, HEIGHT, HEIGHT//10):
            pygame.draw.rect(screen, WHITE, (WIDTH//2 - 5, i, 6, HEIGHT//20))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    movements.append("UP")
                    #player2YFac = -1
                if event.key == pygame.K_DOWN:
                    movements.append("DOWN")
                    #player2YFac = 1
                # if event.key == pygame.K_w:
                # 	player1YFac = -1
                # if event.key == pygame.K_s:
                # 	player1YFac = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    movements.remove("UP")                            
                    #player2YFac = 0
                if event.key == pygame.K_DOWN:
                    movements.remove("DOWN")
                # if event.key == pygame.K_w or event.key == pygame.K_s:
                # 	player1YFac = 0
        
        if len(movements) <1:
            #player2YFac = 0
            movement = ""
        elif len(movements) > 1:
            #player2YFac = 0
            movement = ""
        elif movements[0] == "UP":
            #player2YFac = -1
            movement = "UP"
        elif movements[0] == "DOWN":
            #player2YFac = 1
            movement = "DOWN"
        
        '''pnumber, oponent = myPongProtocol.sendMovement(client_socket,movement)'''
        oponent = "NONE"
        print("oponent: "+str(oppNickname))
        print(len(oppNickname))
        if playerNumber == 1:
            if movement == "UP":
                player1YFac = -1
            elif movement == "DOWN":
                player1YFac = 1
            else:
                player1YFac = 0
                
            if oponent == "UP":
                player2YFac = -1
            elif oponent == "DOWN":
                player2YFac = 1
            else:
                player2YFac = 0
        else:
            if movement == "UP":
                player2YFac = -1
            elif movement == "DOWN":
                player2YFac = 1
            else:
                player2YFac = 0
                
            if oponent == "UP":
                player1YFac = -1
            elif oponent == "DOWN":
                player1YFac = 1
            else:
                player1YFac = 0


        # Collision detection
        for player in listOfPlayers:
            if pygame.Rect.colliderect(ball.getRect(), player.getRect()):
                ball.hit()

        # Updating the objects
        player1.update(player1YFac)
        player2.update(player2YFac)
        point = ball.update()

        # -1 -> Player_1 has scored
        # +1 -> Player_2 has scored
        # 0 -> None of them scored
        if point == -1:
            player1Score += 1
        elif point == 1:
            player2Score += 1
        
        if player1Score == 5:
            winner = player1
            break
        if player2Score == 5:
            winner = player2
            break
        
        ball.speed += 0.002
        #print(ball.speed)

        # Someone has scored a point and the ball is out of bounds.
        # So, we reset it's position
        if point:
            ball.reset()
            player1.reset()
            player2.reset()
            time.sleep(1)

        # Displaying the objects on the screen
        player1.display()
        player2.display()
        ball.display()

        # Displaying the scores of the players
        player1.displayScore(player1Score, 225, 55, WHITE)
        player1.displayNickname(player1.name, 225, 550, WHITE)
        player2.displayScore(player2Score, 675, 55, WHITE)
        player2.displayNickname(player2.name, 675, 550, WHITE)

        pygame.display.update()
        clock.tick(FPS)

    while show:
        msg = font21.render("Ha ganado el jugador "+winner.name, 0, WHITE)
        msg_rect = msg.get_rect(center=(WIDTH/2, HEIGHT/2))
        screen.fill('#274227')
        screen.blit(msg, msg_rect)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                show = False 

if __name__ == "__main__":
    main()
    pygame.quit()