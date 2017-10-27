import mosaic
import sys
from copy import deepcopy
RED = 0
GREEN = 1
BLUE = 2
WIDTH = 0
HEIGHT = 1
FIRST = 0


def compare_pixel(pixel1, pixel2):

    """
    :param pixel1:
    :param pixel2:
    :return: the sum of distances between pixels
    """
    distance_between_pixels = abs(pixel1[RED] - pixel2[RED]) + \
                             abs(pixel1[GREEN] - pixel2[GREEN]) + \
                             abs(pixel1[BLUE] - pixel2[BLUE])
    return distance_between_pixels


def compare(image1, image2):

    """
    :param image1:
    :param image2:
    :return: The function iterates over the pixels of both image and
    compares the images pixel by pixel by summing the distances between pixels
    """

    min_width = min(len(image1), len(image2))
    min_height = min(len(image1[WIDTH]), len(image2[WIDTH]))
    sum_pixel_distances = 0

    for i in range(min_width):
        for j in range(min_height):
            sum_pixel_distances += compare_pixel(image1[i][j], image2[i][j])
    return sum_pixel_distances


def get_piece(image, upper_left, size):

    """
    :param image: a list of lists of tuples
    :param upper_left: a tuple
    :param size: a tuple
    :return: The function slices the given image according to a given size and
    starting point
    """

    # extracting all parameters for the slicing
    image_row = len(image)
    image_column = len(image[WIDTH])
    upper_left_row = upper_left[WIDTH]
    upper_left_column = upper_left[HEIGHT]
    size_row = size[WIDTH]
    size_column = size[HEIGHT]

    # the the case where the slicing exceed the borders of the image
    if upper_left_row + size_row >= image_row:
        size_row = image_row - upper_left_row
    if upper_left_column + size_column >= image_column:
        size_column = image_column - upper_left_column

    # slicing the image
    sliced_image = list()
    for i in range(size_row):
        sliced_image.append(list())
        for j in range(size_column):
            sliced_image[i].append(image[upper_left_row + i][upper_left_column + j])
    return sliced_image


def set_piece(image, upper_left, piece):

    """
    :param image: a list of lists of tuples
    :param upper_left: a tuple representing the top left corner
    :param piece: a list of lists of tuples
    :return:
    """

    # extracting all the needed parameters for pasting
    image_row = len(image)
    image_column = len(image[WIDTH])
    upper_left_row = upper_left[WIDTH]
    upper_left_column = upper_left[HEIGHT]
    piece_row = len(piece)
    piece_column = len(piece[WIDTH])

    # handling the case when the pasting exceeds the borders of the image
    if upper_left_row + piece_row >= image_row:
        piece_row = image_row - upper_left_row
    if upper_left_column + piece_column >= image_column:
        piece_column = image_column - upper_left_column

    # pasting the piece on image
    for i in range(piece_row):
        for j in range(piece_column):
            image[upper_left_row + i][upper_left_column + j] = piece[i][j]


def average(image):

    """
    :param image: a list of lists of tuples
    :return: the average color of the image as a tuple (RED,GREEN,BLUE)
    """

    sum_red = 0
    sum_green = 0
    sum_blue = 0
    height = len(image)
    width = len(image[WIDTH])

    # iterating over the image and summing the values of RED, GREEN, and BLUE
    for i in range(len(image)):
        for j in range(len(image[i])):
            sum_red += image[i][j][RED]
            sum_green += image[i][j][GREEN]
            sum_blue += image[i][j][BLUE]

    # calculating the average
    avg_red = float(sum_red / (width * height))
    avg_green = float(sum_green / (width * height))
    avg_blue = float(sum_blue / (width * height))

    return avg_red, avg_green, avg_blue


def preprocess_tiles(tiles):

    """
    :param tiles: a list of images
    :return: a list of averages colors of each image in the list
    """

    average_colors = list()
    for i in range(len(tiles)):
        average_colors.append(average(tiles[i]))
    return average_colors


def get_best_tiles(objective, tiles, averages, num_candidates):
    """

    :param objective: the target image
    :param tiles: a list of images
    :param averages: a list of average colors of each tile in tiles
    :param num_candidates: the number of the returned tiles
    :return: a list of images, when each image has the closest average colors to
    the average color of the objective

    basic idea:
    The idea is to get the average color of the first tile, to compare it
    to the objective average color and determine it as the minimum distance.
    Next, to go over the rest of the tiles and find those whose whose
    average color is less than the determined average, in case it is,
    we append it to candidates list. we keep iterating until we get
    num_candidates tiles, in case after iterating over all the tiles
    and not finding num_candidates tiles, we extend the candidates list
    with one of its elements to get num_candidates tiles to return.
    """
    candidates = list()
    num_candidates_index = 0
    num_candidates = int(num_candidates)
    obj_average_color = average(objective)
    min_distance = compare_pixel(obj_average_color, averages[FIRST])
    candidates.append(tiles[FIRST])

    # iterating over the tiles
    for i in range(1, len(averages)):
        distance = compare_pixel(obj_average_color, averages[i])
        if min_distance > distance:
            candidates.append(tiles[i])
            min_distance = distance
            num_candidates_index += 1

        # in case we reached the needed number
        # od candidates, break out of the loop
        if num_candidates_index == num_candidates:
            break

    # in case we do not have enough candidates to return
    if len(candidates) < num_candidates:
        element = candidates[-1]  # in this case extending the last one
        comp_items = [element] * (num_candidates - len(candidates))
        candidates.extend(comp_items)

    return candidates


def choose_tile(piece, tiles):

    """
    :param piece: an image
    :param tiles: a list of candidates
    :return: the best fit tile

    The function goes over the list of candidates(images) and
    makes pixel-by-pixel comparison with the piece. The function return
    the tile is the closest fit to the piece
    """

    min_distance = compare(piece, tiles[FIRST])
    min_distance_index = 0

    for i in range(1, len(tiles)):
        sum_pixels = compare(piece, tiles[i])
        if min_distance > sum_pixels:
            min_distance = sum_pixels
            min_distance_index = i

    return tiles[min_distance_index]


def make_mosaic(image, tiles, num_candidates):

    """
    :param image:
    :param tiles: a list of images
    :param num_candidates:
    :return: The function creates a mosaic image out of an image
    """

    # extracting the needed parameters for the creation of the mosaic
    new_image = deepcopy(image)
    first_tile = tiles[FIRST]
    piece_height = len(first_tile[FIRST])
    piece_width = len(first_tile)
    piece_color_avg = preprocess_tiles(tiles)

    # creating the mosaic
    for i in range(0, len(image), piece_width):
        for j in range(0, len(image[i]), piece_height):
            piece = get_piece(image, (i, j), (piece_width, piece_height))
            candidates = get_best_tiles(piece, tiles, piece_color_avg, num_candidates)
            piece = choose_tile(piece, candidates)
            set_piece(new_image, (i, j), piece)

    return new_image


def main():

    # extracting the parameters of the mosaic
    image_source = sys.argv[1]
    images_dir = sys.argv[2]
    output_name = sys.argv[3]
    tile_height = sys.argv[4]
    num_candidates = sys.argv[5]

    # building the mosaic
    image = mosaic.load_image(image_source)
    tiles = mosaic.build_tile_base(images_dir, int(tile_height))
    mosaic_image = make_mosaic(image, tiles, num_candidates)
    mosaic.save(mosaic_image, output_name)


if __name__ == '__main__':
    main()

