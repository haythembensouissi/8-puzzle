import pygame

def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb

pygame.mixer.init()

victory= pygame.mixer.Sound('./assets/Children Yay! Sound Effect.mp3')
moveself= pygame.mixer.Sound('./assets/move-self.mp3')




