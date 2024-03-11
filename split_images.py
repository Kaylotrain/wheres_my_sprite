from PIL import Image
import os
from joblib import Parallel, delayed
import numpy as np
def cut_spritesheet(spritesheet_path, sprite_width, sprite_height, offset_x=0, offset_y=0):
    sheet_name = os.path.splitext(os.path.basename(spritesheet_path))[0]
    output_dir = f"animations_god/"
    os.makedirs(output_dir, exist_ok=True)
    
    sheet = Image.open(spritesheet_path)
    cols = (sheet.width - offset_x) // sprite_width
    rows = (sheet.height - offset_y) // sprite_height
    print(f"Cutting {rows}x{cols} sprites from {sheet_name}")
    sprites = []
    
    for row in range(rows):
        for col in range(cols):
            left = col * sprite_width + offset_x
            top = row * sprite_height + offset_y
            right = left + sprite_width
            bottom = top + sprite_height
            
            sprite = sheet.crop((left, top, right, bottom))
            sprites.append(sprite)
    
    animation_types = {
        'idle': [0],
        'crouch': [1],
        'jump': [2, 3],
        'run': list(range(4, 12)),
        'block': [12],
        'receive_standing_damage': [13],
        'receive_crouching_damage': [14]
    }
    
    for anim_type, indexes in animation_types.items():
        anim_dir = os.path.join(output_dir, anim_type)
        os.makedirs(anim_dir, exist_ok=True)
        
        for i, index in enumerate(indexes, start=1):
            sprite = sprites[index]
            sprite_filename = f"{anim_type}{i}_{sheet_name}.png"
            sprite = sprite.convert("RGB")
            sprite = sprite.resize((299, 299))
            image_array = np.array(sprite) / 255.0
            
            sprite.save(os.path.join(anim_dir, sprite_filename))
            print(f"Saved {sprite_filename} to {anim_dir}")

def process_spritesheet(spritesheet_path, sprite_width, sprite_height, offset_x, offset_y):
    cut_spritesheet(spritesheet_path, sprite_width, sprite_height, offset_x, offset_y)

def process_spritesheets_parallel(folder_path, sprite_width, sprite_height, offset_x=0, offset_y=0):
    spritesheet_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".png")]
    Parallel(n_jobs=-1)(delayed(process_spritesheet)(path, sprite_width, sprite_height, offset_x, offset_y) for path in spritesheet_paths)

# Example usage
process_spritesheets_parallel('god_images/', 300, 290, 40, 20)
