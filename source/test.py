from PIL import Image, ImageDraw

# Create a new ImageDraw object
im_draw = ImageDraw.Draw(Image.new('RGB', (100, 100)))

# Draw a line on the ImageDraw object
im_draw.line((0, 0, 99, 99), fill=(255, 255, 255))

# Convert the ImageDraw object to an Image object
im = Image.new('RGB', (100, 100))
im_draw = ImageDraw.Draw(im)
im_draw.line((0, 0, 99, 99), fill=(255, 255, 255))

# Display the image
im.show()

exit(0)

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

im1 = Image.open('volumio-pirate-audio/images/default.jpg')
im = ImageDraw.Draw(Image.new('RGB', im1.size))
font = ImageFont.truetype(os.path.join("volumio-pirate-audio", 'fonts/Roboto-Medium.ttf'), 24),


im.line((0, 0) + im1.size, fill=128)
im.line((0, im1.size[1], im1.size[0], 0), fill=128)

im1.paste(im)

# Display the image
im1.show()
