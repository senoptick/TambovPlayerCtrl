import gpiod

chip = gpiod.Chip('gpiochip0')
line = chip.get_line(6)

line.request(consumer="test", type=gpiod.LINE_REQ_DIR_IN)

print("value:", line.get_value())
