from rembg import remove
from PIL import Image
import os

def remove_background_ai(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.rsplit('.', 1)[0] + '.png')
            
            with open(input_path, 'rb') as i:
                with open(output_path, 'wb') as o:
                    input_data = i.read()
                    output_data = remove(input_data)  # AI 自動去背
                    o.write(output_data)
            print(f"處理完成: {filename}")

# 使用（需要先安裝：pip install rembg）
remove_background_ai("/home/waynelee0124/aoop_2025_group7_TBC/cat_folder/kp/walkingB", "/home/waynelee0124/aoop_2025_group7_TBC/cat_folder/kp/walking")