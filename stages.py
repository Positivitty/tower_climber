STAGE_1 = [
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B...P............E.E....B',
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
]



STAGE_2 = [
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B............E..........B',
    'B........BBBBBBB........B',
    'B..P................E...B',
    'BBBBBBB...........BBBBBBB',
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
]

STAGE_3 = [
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B..P.............E..E...B',
    'BBBBBBBBB.......BBBBBBBBB',
    'B.......................B',
    'B......BBBBBBBBBBB......B',
    'BHHHHHHHHHHHHHHHHHHHHHHHB',
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
]



# This will be changed after a few testing, I just wanted to make one exist first. B = Block (Implement collisions) R = Ranged Enemy, M = Melee Enemy, P =  Player, H = Hazard (Implement Collisions)

# Here is how I implement Blocks (Numbers are copy pasted from another project and most likely need to be changed)
#class Block(pygame.sprite.Sprite):
    #def __init__(self, game, x, y):
        #self.game = game
        #self._layer = BLOCK_LAYER
        #self.groups = self.game.all_sprites, self.game.blocks
        #pygame.sprite.Sprite.__init__(self, self.groups)

        #self.x = x * TILE_SIZE
        #self.y = y * TILE_SIZE
        #self.width = TILE_SIZE
        #self.height = TILE_SIZE

        #self.image = self.game.character_spritesheet.get_sprite(960, 448, 32, 32)

        #self.rect = self.image.get_rect()
        #self.rect.x = self.x
        #self.rect.y = self.y


        #Functions to add in main.py
        #def create_map(self):
        #for i, row in enumerate(TILE_MAP):
            #for j, tile in enumerate(row):
                #if tile == "B":
                    #Block(self, j, i)
                
                #elif tile == "P":
                    #self.player = Player(self, j, i)
                #else:
                    #Ground(self, j, i)


        #Additional Note I haven't checked your methods of implementing things these are just copy paste methods from another project I (Moses) was working on.
        #Changes Will Be Necessary after I have time to review the code thoroughly.
