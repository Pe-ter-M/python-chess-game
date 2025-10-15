import os.path as path
from pygame import image

class Piece:

    '''Please enter a Doc String...'''
    def __init__(self,color,name,value):
        self.color=color
        self.name=name
        self.value=value
        self.image=None
        self.add_image()
        self.adjust_value()
    
    def adjust_value(self):
        if self.color == 'white':
            self.value *= 1
        else:
            self.value *= -1


    def add_image(self):
        self.full_path ='/home/phantom/coding/python-game/assets/imgs-80px'
        self.image=image.load(path.join(self.full_path,f'{self.color}_{self.name}.png'))
