import pygame
import time
import random
import math


pygame.font.init()



WIDTH,HEIGHT = 720,960
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("jpegfrog")

background = pygame.image.load("lexi.jpg")


grass = 508

tongue_active = False  # Is the tongue extending or not
tongue_length = 0  # Current length of the tongue
tongue_max_length = 200  # Maximum length the tongue can reach
tongue_speed = 10  # How fast the tongue grows
tongue_target_pos = (0, 0)  # Target position (mouse cursor)


#RAIN VARIABLES
RAINDROP_WIDTH = 10
RAINDROP_HEIGHT = 20
RAINDROP_VEL = 10

#PLAYER VARIABLES
PLAYER_WIDTH,PLAYER_HEIGHT = 96,140
PLAYER_VEL = 3

def mirror_images(images):
    return [pygame.transform.flip(image, True, False) for image in images]

class spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as message:
            exit("oops")
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)
    
idlesprites = spritesheet('FROGLET/PNG/froglet_frog_green_sheet_idle.png')
walksprites = spritesheet('FROGLET/PNG/froglet_frog_green_sheet_walk.png')

def scale_images(images, scale_factor):
    return [pygame.transform.scale(image, (int(image.get_width() * scale_factor), int(image.get_height() * scale_factor))) for image in images]

#LOAD IDLE FRAMES
idle_frames = idlesprites.images_at([(0, 0, 16, 20),(16, 0, 16, 20),(32, 0, 16, 20),(48, 0, 16, 20),(64, 0, 16, 20),(80, 0, 16, 20),(96, 0, 16, 20)], colorkey=(0,0,0))
scale_factor = 8
right_idle_frames = scale_images(idle_frames, scale_factor)
left_idle_frames = mirror_images(right_idle_frames)
#LOAD WALKING FRAMES
walk_frames = walksprites.images_at([(0, 0, 16, 20),(16, 0, 16, 20),(32, 0, 16, 20),(48, 0, 16, 20),(64, 0, 16, 20),(80, 0, 16, 20),(96, 0, 16, 20)], colorkey=(0,0,0))
scale_factor = 8
right_walk_frames = scale_images(walk_frames, scale_factor)
left_walk_frames = mirror_images(right_walk_frames)


def draw_tongue(player, tongue_length, tongue_target_pos):
    # Get the center of the player's mouth
    start_pos = (player.x + PLAYER_WIDTH // 2, player.y + PLAYER_HEIGHT // 2)

    # Calculate the direction vector to the mouse cursor
    dir_x, dir_y = tongue_target_pos[0] - start_pos[0], tongue_target_pos[1] - start_pos[1]
    distance = math.sqrt(dir_x**2 + dir_y**2)

    # Normalize direction vector
    if distance != 0:
        dir_x /= distance
        dir_y /= distance

    # Calculate the tongue's current end position
    end_pos = (start_pos[0] + dir_x * tongue_length, start_pos[1] + dir_y * tongue_length)

    pygame.draw.line(WIN, (255, 0, 0), start_pos, end_pos, 5)  # Draw a red line as the tongue




def draw(player,raindrops,current_frame):
    WIN.blit(background,(0,0))

    WIN.blit(current_frame,(player.x,player.y))

    for raindrop in raindrops:
        pygame.draw.rect(WIN,"blue",raindrop)
    
    if tongue_active:
        draw_tongue(player, tongue_length,tongue_target_pos)  # Draw the tongue

    pygame.display.update()



def main():
    global tongue_active, tongue_length, tongue_target_pos  # Ensure we modify these global variables
    run = True

    player = pygame.Rect(200,HEIGHT-PLAYER_HEIGHT,PLAYER_WIDTH,PLAYER_HEIGHT)

    clock = pygame.time.Clock()

    #rain variables
    raindrop_add_increment = 200
    raindrop_count = 0
    raindrops = []
    #player variables
    directionfacing = "right"
    walkstate = False
    hit = False
    #TONGUE VARIABLES
    tongue_active = False  # Is the tongue extending or not
    tongue_length = 0  # Current length of the tongue
    tongue_max_length = 200  # Maximum length the tongue can reach
    tongue_speed = 10  # How fast the tongue grows

    # Animation control
    frame_index = 0  # Current frame index for idle animation
    frame_delay = 100  # Time delay between frames (in milliseconds)
    last_frame_time = pygame.time.get_ticks()

    while run:
        raindrop_count += clock.tick(60)

        if raindrop_count > raindrop_add_increment:
            for _ in range(3):
                raindrop_x = random.randint(0,WIDTH-RAINDROP_WIDTH)
                raindrop = pygame.Rect(raindrop_x, -RAINDROP_HEIGHT,RAINDROP_WIDTH,RAINDROP_HEIGHT)
                raindrops.append(raindrop)

        raindrop_add_increment = max(200,raindrop_add_increment - 50)
        raindrop_count = 0



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                tongue_active = True
                tongue_length = 0  # Reset tongue length
                tongue_target_pos = pygame.mouse.get_pos()
                
        current_time = pygame.time.get_ticks()
        if current_time - last_frame_time > frame_delay:
            frame_index = (frame_index + 1) % len(idle_frames)  # Loop through frames
            last_frame_time = current_time
        
        # Tongue growth logic
        if tongue_active:
            tongue_length += tongue_speed
            if tongue_length >= tongue_max_length:
                tongue_length = tongue_max_length
                tongue_active = False  # Stop extending the tongue after reaching the max length
        
        #wasd movement code
        keys = pygame.key.get_pressed()
        walkstate = True
        if keys[pygame.K_a] and player.x - PLAYER_VEL >= 0: #left
            player.x -= PLAYER_VEL
            directionfacing = "left"
            if keys[pygame.K_s]: #left down
                player.y += PLAYER_VEL
            if keys[pygame.K_w] and player.y - PLAYER_VEL + PLAYER_HEIGHT > grass: #left down
                player.y -= PLAYER_VEL
        elif keys[pygame.K_d] and player.x + PLAYER_WIDTH + PLAYER_VEL <= WIDTH: #right
            player.x += PLAYER_VEL
            directionfacing = "right"
            if keys[pygame.K_s]: #down right
                player.y += PLAYER_VEL
            if keys[pygame.K_w] and player.y - PLAYER_VEL + PLAYER_HEIGHT > grass: #up right
                player.y -= PLAYER_VEL
        elif keys[pygame.K_w] and player.y - PLAYER_VEL + PLAYER_HEIGHT > grass: #up
            player.y -= PLAYER_VEL
        elif keys[pygame.K_s]: #down
            player.y += PLAYER_VEL
        else:
            walkstate = False
        for raindrop in raindrops[:]:
            raindrop.y += RAINDROP_VEL
            if raindrop.y > HEIGHT:
                raindrops.remove(raindrop)
            elif raindrop.y + raindrop.height >= player.y and raindrop.colliderect(player):
                raindrops.remove(raindrop)
                hit = True
                break
        
        current_time = pygame.time.get_ticks()
        if current_time - last_frame_time > frame_delay:
            frame_index = (frame_index + 1) % len(idle_frames)  # Loop through frames
            last_frame_time = current_time

        
        
        #ANIMATION SELECTOR
        #idling
        if walkstate == False:
            if directionfacing == "right":
                current_frame = right_idle_frames[frame_index]  # Get the current frame to display
            elif directionfacing == "left":
                current_frame = left_idle_frames[frame_index]  # Get the current frame to display
        elif walkstate == True:
            if directionfacing == "right":
                current_frame = right_walk_frames[frame_index]  # Get the current frame to display
            elif directionfacing == "left":
                current_frame = left_walk_frames[frame_index]  # Get the current frame to display
        draw(player,raindrops,current_frame)
    
    pygame.quit()



if __name__ == "__main__":
    main()