import Image
import os
import sys
import csv


folder = 'images/'
image_set = 'olympics'
size = (75, 75)
divisor = 8


def get_images(folder):
    images = []
    for filename in os.listdir(folder):
        images.append(folder + filename)
    return images


def get_average(filename):
    image = Image.open(filename)
    pixels = image.load()
    r = g = b = 0
    for x in xrange(0, image.size[0]):
        for y in xrange(0, image.size[1]):
            colour = pixels[x, y]
            r += colour[0]
            g += colour[1]
            b += colour[2]
    area = image.size[0] * image.size[1]
    r /= area
    g /= area
    b /= area
    return [(r, g, b), filename, image]


def get_difference(colour, colour1, x):
    return abs(colour[0][x] - colour1[0][x])


def closest(colour, colours):
    closest_image = [100000, None]
    for c in colours:
        r_diff = get_difference(colour, c, 0)
        g_diff = get_difference(colour, c, 1)
        b_diff = get_difference(colour, c, 2)
        c_diff = r_diff + g_diff + b_diff
        if c_diff < closest_image[0]:
            closest_image = [c_diff, c]
    return closest_image


def get_colours(images):
    colours = []
    for image in images:
        try:
            colours.append(get_average(image))
        except:
            continue
    return colours


def build_new_image(original_image_filename, colours, attributions_filename, image_set='olympics', use_attributions=True):
    attributions = {}
    if use_attributions:
        try:
            with open(attributions_filename, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    attributions[row[0]] = row[1]
        except:
            use_attributions = False
    original_image = Image.open(original_image_filename)
    blank_image = Image.new('RGB', (original_image.size[0] * size[0],
      original_image.size[1] * size[1]))
    pixels = original_image.load()
    x_blit = y_blit = 0
    x_map = y_map = 0
    image_map = ''
    area_text = '<area shape="rect" coords="{0}, {1}, {2}, {3}"' + \
          'href="http://127.0.0.1:8080/make?filename={4}&set={5}" title="{6}" />\n'
    for y in xrange(0, original_image.size[1]):
        for x in xrange(0, original_image.size[0]):
            closest_image = closest([pixels[x, y], None], colours)
            if closest_image[1][1] == None:
                continue
            img = closest_image[1][2]
            blank_image.paste(img, (x_blit, y_blit))
            author = ''
            if use_attributions:
                try:
                    author = attributions[closest_image[1][1]]
                except:
                    pass
            image_map += area_text.format(x_map, y_map,
              x_map + size[0] / divisor, y_map + size[1] / divisor,
              os.path.splitext(closest_image[1][1])[0], image_set, author)
            x_blit += size[0]
            x_map += size[0] / divisor
            # uncomment below to make each image unique
            # (needs many many many many many many many images for a good result)
            # colours.remove(closest_image[1])
        x_blit = 0
        y_blit += size[1]
        x_map = 0
        y_map += size[1] / divisor
    return blank_image, image_map


def main():
    global folder
    global image_set
    if len(sys.argv) < 2:
        print 'average_colour <image> <set>'
        return
    if len(sys.argv) > 2:
        image_set = sys.argv[2]
    image_set += '/'
    folder += image_set
    original_image_filename = sys.argv[1]
    images = get_images(folder)
    colours = get_colours(images)
    short_filename = os.path.splitext(os.path.basename(original_image_filename))[0]
    new_image, image_map = build_new_image(original_image_filename,
      colours, folder + 'attributions.csv', image_set[0:-1])
    new_image.save('static/{0}_done.jpg'.format(short_filename))
    f = open('templates/{0}_done.html'.format(short_filename), 'w')
    html = ('<img width={0} height={1} src="static/{2}_done.jpg" name="image"' + \
      'usemap="#image_map"/>').format(new_image.size[0] / divisor,
      new_image.size[1] / divisor, short_filename)
    html += '<map name="image_map">'
    html += image_map
    html += '</map><br /><a href="/imgur?filename={0}">Upload to imgur</a>'.format(
      short_filename)
    f.write(html)
    f.close()

if __name__ == '__main__':
    main()
