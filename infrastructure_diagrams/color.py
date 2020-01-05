from colour import Color

# https://chase-seibert.github.io/blog/2011/07/29/python-calculate-lighterdarker-rgb-colors.html
def color_variant(hex_color, brightness_offset=1):
    """ takes a color like #87c95f and produces a lighter or darker variant """
    if len(hex_color) != 7:
        raise Exception(
            "Passed %s into color_variant(), needs to be in #87c95f format." % hex_color
        )
    rgb_hex = [hex_color[x : x + 2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [
        min([255, max([0, i])]) for i in new_rgb_int
    ]  # make sure new values are between 0 and 255
    # hex() produces "0x88", we want just "88"
    return "#%02x%02x%02x" % (new_rgb_int[0], new_rgb_int[1], new_rgb_int[2])


def darken_color(color_string, brightness_offset=-70):
    color = Color(color_string)
    return color_variant(color.hex, brightness_offset)


def lighten_color(color_string, brightness_offset=50):
    color = Color(color_string)
    return color_variant(color.hex, brightness_offset)
