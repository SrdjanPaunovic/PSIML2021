import numpy as np
import os
from PIL import Image


def find_board(image_file):
    image = np.array(image_file)
    width, height = image_file.size

    for y in range(width):
        for x in range(height):
            pixel = image[x, y]
            if pixel[0] != 0:
                return x, y


def get_board(image_file, x_offset, y_offset):
    image = np.array(image_file)
    width, height = image_file.size

    board_size = 0
    for x1 in range(height - x_offset):
        pixel = image[x1 + x_offset, y_offset]
        if pixel[0] == 0:
            board_size = x1
            break

    return image_file.crop((y_offset, x_offset, y_offset + board_size, x_offset + board_size))


def get_tiles(board):
    tile_size = board.size[0] / 8

    tiles = []
    for i in range(8):
        for j in range(8):
            tile = board.crop((j * tile_size, i * tile_size, (j + 1) * tile_size, (i + 1) * tile_size))
            tiles.append(tile)

    return tiles


def remove_tile_color(tile):
    tile = tile.convert("L")
    tile_data = tile.load()
    img = np.array(tile)
    img[img > 230] = 255
    img[img <= 100] = 0

    return Image.fromarray(img.astype('uint8'), 'L')


def remove_tiles_color(tiles):
    new_tiles = []
    for tile in tiles:
        new_tile = remove_tile_color(tile)
        new_tiles.append(new_tile)
    return new_tiles


def compare_image(img1, img2):
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    cmp = (arr1 == 0) & (arr2 == 0)
    cmp1 = (arr1 == 255) & (arr2 == 255)
    return np.sum(cmp) + np.sum(cmp1)


def remove_transparent(piece):
    piece = piece.convert("RGBA")
    image = Image.new("RGBA", piece.size, "WHITE")
    image.paste(piece, (0, 0), piece)

    return image.convert("RGB")


def load_pieces(black_pieces_path):
    pieces = {}
    for path, _, files in os.walk(black_pieces_path):
        for name in files:
            piece = Image.open(os.path.join(path, name))
            piece = remove_transparent(piece)
            piece = piece.convert("L")
            pieces[os.path.splitext(name)[0]] = piece

    return pieces


def find_figure(black_pieces, white_pieces, tile):
    # empty field
    if np.sum(np.array(tile) == 0) == 0:
        return "empty"

    all_figure = [["b_" + k, compare_image(v, tile)] for k, v in black_pieces.items()]
    all_figure.extend([["w_" + k, compare_image(v, tile)] for k, v in white_pieces.items()])

    all_figure.sort(key=lambda item: item[1], reverse=True)
    return all_figure[0][0]


def get_letter(figure_name):
    name_maper = {
        'b_bishop': 'b',
        'b_king': 'k',
        'b_knight': 'n',
        'b_pawn': 'p',
        'b_queen': 'q',
        'b_rook': 'r',
        'w_bishop': 'B',
        'w_king': 'K',
        'w_knight': 'N',
        'w_pawn': 'P',
        'w_queen': 'Q',
        'w_rook': 'R'
    }
    return name_maper.get(figure_name, '#')


def print_row(fig_arr):
    i = 0
    row_text = ""
    for fig in fig_arr:
        l = get_letter(fig)
        if l == '#':
            i += 1
        elif i > 0:
            row_text += str(i) + l
            i = 0
        else:
            row_text += l
    if i > 0:
        row_text += str(i)
    return row_text


directions = {
    "Q": [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)],
    "q": [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)],
    "R": [(-1, 0), (0, 1), (1, 0), (0, -1)],
    "r": [(-1, 0), (0, 1), (1, 0), (0, -1)],
    "P": [(-1, -1), (-1, 1)],
    "p": [(1, -1), (1, 1)],
    "B": [(-1, -1), (-1, 1), (1, 1), (1, -1)],
    "b": [(-1, -1), (-1, 1), (1, 1), (1, -1)],
    "K": [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)],
    "k": [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)],
    "N": [(-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2)],
    "n": [(-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2)]
}

moves = {
    "Q": range(1, 8),
    "q": range(1, 8),
    "R": range(1, 8),
    "r": range(1, 8),
    "P": range(1, 2),
    "p": range(1, 2),
    "B": range(1, 8),
    "b": range(1, 8),
    "K": range(1, 2),
    "k": range(1, 2),
    "N": range(1, 2),
    "n": range(1, 2)
}


def _move_figure(row, col, board_matrix, blockset, directions, step):
    return_matrix = np.zeros((8, 8), dtype=np.uint8)

    for row_dir, col_dir in directions:
        for i in step:
            r = row + i * row_dir
            c = col + i * col_dir
            if (0 > r or r >= 8) or (0 > c or c >= 8):
                break

            if board_matrix[r][c] in blockset:
                break

            return_matrix[r][c] = 1
            if board_matrix[r][c] != '#':
                break

    return return_matrix


def move_figure(row, col, board_matrix, fig, defensive=False):
    if fig[0].isupper():
        blockset = {'Q', 'R', 'N', 'P', 'K', 'B'}
    else:
        blockset = {'q', 'r', 'n', 'p', 'k', 'b'}

    direction = directions[fig]
    step = moves[fig]

    if defensive and fig == 'p':
        direction = [(1, 0)]
    elif defensive and fig == 'P':
        direction = [(-1, 0)]

    return _move_figure(row, col, board_matrix, blockset, direction, step)


def find_check(board_matrix):
    white_king_matrix = np.zeros((8, 8))
    white_king_matrix[board_matrix == "K"] = 1
    black_king_matrix = np.zeros((8, 8))
    black_king_matrix[board_matrix == "k"] = 1
    white_board_matrix = np.zeros((8, 8))
    black_board_matrix = np.zeros((8, 8))
    for i, fig in enumerate(board_matrix.flatten()):
        col = i % 8
        row = i // 8
        if fig == '#':
            continue

        if fig.isupper():
            white_board_matrix += move_figure(row, col, board_matrix, fig)
        else:
            black_board_matrix += move_figure(row, col, board_matrix, fig)

    # black_board_matrix[black_board_matrix > 1] = 1
    # white_board_matrix[white_board_matrix > 1] = 1

    result = {'B': False, 'W': False}

    if np.sum(black_board_matrix * white_king_matrix) > 0:
        result['B'] = True

    if np.sum(white_board_matrix * black_king_matrix) > 0:
        result['W'] = True

    return result


def is_checkmate(board_matrix, ex_result, attacker):

    new_result = ex_result
    if attacker == "W":
        king = 'k'
    else:
        king = "K"

    for i, fig in enumerate(board_matrix.flatten()):
        col = i % 8
        row = i // 8

        if fig == '#':
            continue

        if fig.islower() == king.islower():
            fig_possible_moves = move_figure(row, col, board_matrix, fig, defensive=True)

            # if fig == king:
            for x in np.argwhere(fig_possible_moves == 1):
                new_board = board_matrix.copy()
                new_board[row][col] = '#'
                new_board[x[0]][x[1]] = fig
                new_result = find_check(new_board)
                if new_result[attacker] != ex_result[attacker]:
                    return False

            # else:
            #     new_board[new_board == fig] = '#'
            #     new_board[fig_possible_moves > 0] = fig
            #     new_result = find_check(new_board)
            #     if new_result[attacker] != ex_result[attacker]:
            #         return False
    return True


if __name__ == "__main__":
    # root_path = input()
    root_path = r"C:\Users\srdja\Downloads\checkmate_public (2)\public\set\19"
    test_name = os.path.basename(root_path)
    # tiles_path = root_path + r"\tiles"
    image_path = r"%s\%s.png" % (root_path, test_name)
    black_pieces_path = root_path + r"\pieces\black"
    white_pieces_path = root_path + r"\pieces\white"

    # save_path = r"C:\Users\srdja\Downloads\checkmate_public (1)\public\test"

    image_file = Image.open(image_path)

    x, y = find_board(image_file)
    print(str(x) + "," + str(y))

    board = get_board(image_file, x, y)
    new_size = int(board.size[0] * 8)
    new_size = (new_size, new_size)
    board = board.resize(new_size)

    tiles = get_tiles(board)
    tiles = remove_tiles_color(tiles)

    black_pieces = load_pieces(black_pieces_path)
    white_pieces = load_pieces(white_pieces_path)

    figure_array = [find_figure(black_pieces, white_pieces, tile) for tile in tiles]
    figure_arrays = np.array_split(figure_array, 8)
    rows_for_print = (print_row(fig_arr) for fig_arr in figure_arrays)
    print('/'.join(rows_for_print))

    board_matrix = np.array([[get_letter(field) for field in row] for row in figure_arrays])

    result = find_check(board_matrix)

    attacked_king = "#"
    if result["B"] and result["W"]:
        print('-')
    elif result["B"]:
        attacked_king = "B"
        print("B")
    elif result["W"]:
        attacked_king = 'W'
        print("W")
    else:
        print('-')

    if attacked_king == "#":
        print()
    else:
        is_mate = is_checkmate(board_matrix, result, attacked_king)
        if is_mate:
            print('1')
        else:
            print('0')

    # i = 0
    # for tile in tiles:
    #     i += 1
    #     tile.save(save_path + "\\tiles\\" + str(i) + ".jpg")
    #
    # for b_p in black_pieces:
    #     black_pieces[b_p].save(save_path + "\\" + b_p + ".jpg")
    #
    # for w_p in white_pieces:
    #     white_pieces[w_p].save(save_path + "\\w_" + w_p + ".jpg")
