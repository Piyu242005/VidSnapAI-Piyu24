import os

folder = 'df88465a-a778-11f0-b431-f7d1de17ae9e'
base_dir = os.path.abspath('.')

files = ['Piyu_PICTURE_page-0001.jpg', 'Firefly_20250902205443.png']

with open(f'user_uploads/{folder}/input.txt', 'w') as f:
    for _ in range(3):
        for file in files:
            abs_path = os.path.join(base_dir, 'user_uploads', folder, file).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")
            f.write(f"duration 1\n")

print("Fixed input.txt with absolute paths")
