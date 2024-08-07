# Import necessary modules from Kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle

# Import necessary modules from Pygame
import pygame
import numpy as np

class PygameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize Pygame
        pygame.init()
        
        # Pygame surface dimensions
        self.width, self.height = 300, 200
        
        # Pygame surface
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((255, 255, 255))  # White background
        
        # Call Pygame initialization method
        self.initialize_pygame()
        
        # Schedule update method to be called every frame
        Clock.schedule_interval(self.update, 1.0 / 60.0)
    
    def initialize_pygame(self):
        # Pygame font
        self.font = pygame.font.SysFont("Arial", 24)
        
        # Pygame clock
        self.clock = pygame.time.Clock()
    
    def update(self, dt):
        # Clear the surface
        self.surface.fill((255, 255, 255))  # White background
        
        # Draw a rotating rectangle
        pygame.draw.rect(self.surface, (255, 0, 0), (self.width // 2 - 50, self.height // 2 - 50, 100, 100))
        
        # Render text
        text_surface = self.font.render("Pygame in Kivy", True, (0, 0, 0))
        self.surface.blit(text_surface, (self.width // 2 - text_surface.get_width() // 2, 20))
        
        # Rotate the rectangle
        self.surface = pygame.transform.rotate(self.surface, 1)
        
        # Convert surface to texture
        pixel_array = pygame.surfarray.array3d(self.surface)
        np_surface = np.swapaxes(pixel_array, 0, 1)
        np_surface = np.flip(np_surface, 0)
        self.texture = Texture.create(size=self.surface.get_size())
        self.texture.blit_buffer(np_surface.tostring(), bufferfmt="ubyte", colorfmt="rgb")
        
        # Update Kivy canvas
        self.canvas.clear()
        self.canvas.ask_update()
        self.canvas.add(Rectangle(texture=self.texture, pos=self.pos, size=self.size))
    
class PygameKivyApp(App):
    def build(self):
        return PygameWidget()

if __name__ == "__main__":
    PygameKivyApp().run()
