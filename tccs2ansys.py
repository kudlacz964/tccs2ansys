import argparse
import re
from PIL import Image
from PIL import ImageOps

threshold = 60
markColor = (255, 255, 255)

area = (1, 279, 505, 455)
pixelWidthRatio = 63.0
graphPixelHeight = 77

def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

def getValue(values, x):
    p = int(x * pixelWidthRatio)
    v = graphPixelHeight - values[p]
    return v / pixelHeightRatio

parser = argparse.ArgumentParser()

parser.add_argument("input", help="input image file")
parser.add_argument("-f", dest='output', help="output text file")
parser.add_argument('-o', dest='outputImage', help='output image file')
parser.add_argument('-b', dest='begin', help='begin of cycle')
parser.add_argument('-e', dest='end', help='end of cycle')
parser.add_argument('-s', dest='step', help='step')

results = parser.parse_args()

begin = 0.0
if results.begin is not None:
    begin = float(results.begin)
end = 8.0
if results.end is not None:
    end = float(results.end)
step = 0.02
if results.step is not None:
    step = float(results.step)

match = re.match(r'(.+)\.bmp', results.input)
if results.output is None:
    results.output = match.group(1) + '.txt'
if results.outputImage is None:
    results.outputImage = match.group(1) + '_out.bmp'

im = Image.open(results.input)
graph = im.crop(area)
pixels = graph.load()

values = {}

for x in range(0, graph.width):
    for y in range(0, graph.height):
        r, g, b = pixels[x, y]
        if (b > threshold):
            values[x] = y
            break

pixels = im.load()
for y in range(250, 355):
    r, g, b = pixels[507, y]
    if r > 200:
        last = y
pixelHeightRatio = float(356 - last)

pbegin = int(begin * pixelWidthRatio)
pend = int(end * pixelWidthRatio)
last = None
for x in range(pbegin, pend):
    y = values[x]
    pixels[area[0] + x, area[1] + y] = markColor
    if last is not None:
        if y < last:
            for i in range(y + 1, last):
                pixels[area[0] + x, area[1] + i] = markColor
        else:
            for i in range(last + 1, y):
                pixels[area[0] + x - 1, area[1] + i] = markColor
    last = y
im.save(results.outputImage)

with open(results.output, "w+") as f:
    count = 0
    for i in drange(begin, end, step):
        count += 1
    f.write("((inlet_velocity transient " + str(count) + " 1)\n(time")
    for i in range(0, count):
        f.write("\n")
        f.write(str(i * step))
    f.write(")\n(velo")
    for i in drange(begin, end, step):
        f.write("\n")
        f.write(str(round(getValue(values, i), 3)))
    f.write("))\n")
