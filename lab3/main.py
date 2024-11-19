import time
import board
import busio
import digitalio
import adafruit_vl53l0x
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# Initialize I2C bus and sensors.
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the VL53L0X distance sensor.
vl53 = adafruit_vl53l0x.VL53L0X(i2c)

# Initialize the OLED display.
oled_reset = digitalio.DigitalInOut(board.D4)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Clear the display.
oled.fill(0)
oled.show()

def display_distance(distance):
    """Display the distance on the OLED screen."""
    # Create a blank image for drawing.
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # Load default font.
    font = ImageFont.load_default()

    # Clear the image.
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

    # Define text position and draw the text.
    text = f"M23EEV006_Distance: {distance} mm"
    draw.text((0, 0), text, font=font, fill=255)

    # Display the image on the OLED.
    oled.image(image)
    oled.show()

try:
    while True:
        # Read the range from the VL53L0X sensor.
        distance = vl53.range
        display_distance(distance)  # Display the distance on the OLED.
        time.sleep(1)  # Update every second.
except KeyboardInterrupt:
    print("Exit")  # Exit on CTRL+C