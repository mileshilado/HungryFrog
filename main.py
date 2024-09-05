import pygame
import time
import random



pygame.font.init()



WIDTH,HEIGHT = 720,960
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("jpegfrog")

background = pygame.image.load("lexi.jpg")


PLAYER_VEL = 3

grass = 508

RAINDROP_WIDTH = 10
RAINDROP_HEIGHT = 20
RAINDROP_VEL = 10

PLAYER_WIDTH,PLAYER_HEIGHT = 96,140

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

def draw(player,raindrops,current_frame):
    WIN.blit(background,(0,0))

    WIN.blit(current_frame,(player.x,player.y))

    for raindrop in raindrops:
        pygame.draw.rect(WIN,"blue",raindrop)
    

    pygame.display.update()

def main():
    run = True

    player = pygame.Rect(200,HEIGHT-PLAYER_HEIGHT,PLAYER_WIDTH,PLAYER_HEIGHT)

    clock = pygame.time.Clock()

    raindrop_add_increment = 200
    raindrop_count = 0
    
    directionfacing = "right"
    walkstate = False

    raindrops = []
    hit = False

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

        current_time = pygame.time.get_ticks()
        if current_time - last_frame_time > frame_delay:
            frame_index = (frame_index + 1) % len(idle_frames)  # Loop through frames
            last_frame_time = current_time
        
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