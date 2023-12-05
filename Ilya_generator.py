import arcade
import numpy as np # можешь установить, полезная штука

SCALE_VALUE = 4
PLAYER_MOVEMENT_SPEED = 5
PLAYER_JUMP_SPEED = 20
PLAYER_SPRITE = 'Mine_/blocks/mud.png'
BLOCK_SPRITES_URL = 'Mine_/blocks/'

WIDTH, HEIGHT = 500, 500

class Block(arcade.Sprite):
    def __init__(self, image, scale: int, pos: tuple, strength):
        super().__init__(image, scale)
        self.strength = strength
        self.position = pos
    def update(self): 
        if self.strength <= 0: self.kill()

class Player(arcade.Sprite):
    def __init__(self, game):
        super().__init__(PLAYER_SPRITE, 4)
        
        self.game = game
        self.position = 250, 400

    def camera_to_player(self):
        screen_center_x = self.center_x - (self.game.camera.viewport_width / 2)
        screen_center_y = self.center_y - (self.game.camera.viewport_height / 2)

        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.game.camera.move_to(player_centered)

class BlockManager:
    def __init__(self, game):
        # self.block_types_list = os.listdir('Mine_/blocks')
        self.block_size = 16 * SCALE_VALUE
        self.block_sprite_list = arcade.SpriteList()
        self.game = game
    def setup_block(self, pos, is_grass: bool):
        block_image = 'grass_side' if is_grass else 'dirt'
        block = Block(f'{BLOCK_SPRITES_URL}{block_image}.png', SCALE_VALUE, pos, 10) #  + self.block_types_list[0]
        self.block_sprite_list.append(block)
        self.game.scene.add_sprite('Blocks', block)

class Generate_Terrain:
    def __init__(self, game, matrix_size: int = 10):
        self.matrix_size = matrix_size
        self.peak_height = int(matrix_size // 2)
        self.peak_position = int(matrix_size // 2)
        self.game = game
        self.block_manager = BlockManager(self.game)

        self.terrain_matrix = self.generate_terrain_matrix()
        self.generate_terrain()
        # self.show_matrix()
    
    def show_matrix(self):
        for i, k in enumerate(self.terrain_matrix):
            print(i, k)

    def generate_terrain_matrix(self):
        terrain = np.zeros((self.matrix_size, self.matrix_size))
        # print(terrain)
        for x in range(self.matrix_size):
            height = int(self.peak_height * np.exp(-(x - self.peak_position)**2 / (2 * self.peak_height**2)))
            terrain[:height, x] = 1
        return terrain
    
    def generate_terrain(self):
        for y in range(self.matrix_size):
            for x in range(self.matrix_size):
                if self.terrain_matrix[y][x] == 1:
                    
                    is_grass = False
                    if self.terrain_matrix[y + 1][x] == 0: is_grass = True

                    self.block_manager.setup_block(
                        (
                        self.block_manager.block_size / 2 + self.block_manager.block_size * x, 
                        self.block_manager.block_size / 2 + self.block_manager.block_size * y
                        ),
                        is_grass
                    )
            # break

class Game(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT)

        self.physics_engine = None
        self.scene = None
        self.camera = None
        self.player = None
        self.terrain_generator = None

        self.setup()

    def setup(self):
        self.scene = arcade.Scene()
        self.terrain_generator = Generate_Terrain(self)
        self.camera = arcade.Camera(self.width, self.height)

        self.player = Player(self)
        self.scene.add_sprite('Player', self.player)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=1, walls=self.scene['Blocks']
        )

    def on_draw(self):
        self.clear(arcade.color.AERO_BLUE)

        self.camera.use()
        self.scene.draw()

    def update(self, delta_time):
        self.physics_engine.update()
        self.player.camera_to_player()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W: 
            if self.physics_engine.can_jump(): self.player.change_y = PLAYER_JUMP_SPEED

        elif key == arcade.key.A: self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.D: self.player.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key == arcade.key.A: self.player.change_x = 0
        elif key == arcade.key.D: self.player.change_x = 0

game = Game()
game.run()
