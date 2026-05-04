from pathlib import Path
from typing import Literal
import json
import argparse

with open(Path(__file__).parent / "config.json", "r") as c:
    COLORS = json.load(c)

def hex_to_bytes(h:str) -> bytes:
    hex_val = h.lstrip('#')
    rgb = tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))
    return bytes(rgb)

class DepthFiller:
    def __init__(self, depth, depth_to_go:int) -> None:
        if depth_to_go <= 0:
            self.children = []
        else:
            self.children = [DepthFiller(depth, depth_to_go-1)]
        self.get_color = lambda n: b"\x00\x00\x00"
        self.calc_maxdepth = lambda n: None
        self.size = 1
        self.maxdepth = -1
    
    def update_children(self, dummy):
        return

class MapObj:
    def __init__(self, obj:Path, depth=0):
        self.obj = obj
        self.name = obj.name
        self.depth = depth
        self.children:list[MapObj|DepthFiller] = [MapObj(child, depth+1) for child in obj.glob("*")]
    
    def calc_maxdepth(self, imagemode):
        for child in self.children:
            child.calc_maxdepth(imagemode)
        if imagemode == "m":
            self.size = 1
            for child in self.children:
                self.size += child.size
            if len(self.children) == 0:
                self.maxdepth = 0
            else:
                self.maxdepth = 1 + max([child.maxdepth for child in self.children])
            self.update_children()
        else:
            self.size = 1
        
    def update_children(self, md=0):
        for child in self.children:
            child.update_children(self.maxdepth-1)
        if (len(self.children) == 0):
            self.children.append(DepthFiller(self.depth+1, md-1))
        
    def get_color(self, pixelmode:Literal["e", "b", "n", "ba", "na"]) -> bytes:
        if pixelmode == "e":
            if self.obj.is_file():
                mapping = COLORS.get("ext")
                ext = self.obj.suffix
                color_hex = mapping.get(ext, mapping.get(""))
                color_bytes = hex_to_bytes(color_hex)
            else:
                color_bytes = b"\xff\xff\xff"
        
        else:
            if "n" in pixelmode:
                mapping = COLORS.get("ch")
                color_bytes_list = []
                for char in self.name:
                    color_hex_part = mapping.get(char, mapping.get(""))
                    color_bytes_part = hex_to_bytes(color_hex_part)
                    color_bytes_list.append(color_bytes_part)

            else:
                if self.obj.is_file():
                    with open(self.obj, "rb") as f:
                        data = f.read()
                    color_bytes_list = []
                    for i in range(int(len(data)/3)):
                        color_bytes_list.append(data[i*3:i*3+3])
                else:
                    return b""

            if "a" in pixelmode:
                count = len(color_bytes_list)
                color_bytes = bytes(tuple(sum(channel) // count for channel in zip(*color_bytes_list)))
            else:
                color_bytes = b"".join(color_bytes_list)
            
        return color_bytes

def generate_colormap_tree(pobj:Path, imagemode:Literal["l", "s", "m"], pixelmode:Literal["e", "b", "n", "ba", "na"]) -> bytes:
    obj = MapObj(pobj)
    
    obj.calc_maxdepth(imagemode)

    if imagemode == "m": #now it errors with 'image height of zero?'
        width:int = obj.size
        height:int = obj.maxdepth

    cmap = b""
    objlist = [obj]
    while objlist != []:
        objlist_new = []
        for obj in objlist:
            for _ in range(obj.size):
                cmap += obj.get_color(pixelmode)
            objlist_new.extend(obj.children)
        objlist = objlist_new.copy()

    if imagemode != "m":
        twidth = len(cmap) // 3
        if imagemode == "s":
            avg = int(twidth**0.5) + 1
            delta_pix = avg**2 - twidth
            for _ in range(delta_pix):
                cmap += b"\x00\x00\x00"
            width = avg
            height = avg
        else:
            width = twidth
            height = 1

    header = f"P6\n{width} {height}\n255\n".encode('ascii')

    return header + cmap

def create_raw_image(in_:Path, outfile:Path, imagemode:Literal["l", "s", "m"], pixelmode:Literal["e", "b", "n", "ba", "na"]):
    """imagemode: l = line, r = rectangle, m = map; pixelmode [combine]: b = bytes, n = name, a = average, e = extention"""
    colormap = generate_colormap_tree(in_, imagemode, pixelmode)
    with open(f"{outfile}.ppm", "wb") as o:
        o.write(colormap)

def info():
    print("\nINFO\n" \
    "   IMAGEMODE\n" \
    "       The format of the output file\n" \
    "       Choices:\n" \
    "           'l' = A one pixel high, long line\n" \
    "           's' = A square with filler pixels in the bottom-right\n" \
    "           'm' = A 'map' of the input, check it out to understand ;)\n" \
    "           ! 'm' cannot be used on single files !" \
    "   PIXELMODE\n" \
    "       The way the colors of the pixels are determined\n" \
    "       Choices:\n" \
    "           'e' = 'extention': The file extention determines the color. Only affects files. Don't use with colormode 'm'\n" \
    "           'b' = 'bytes': The bytes from the file determine the colors. Only affects files. Don't use with colormode 'm'\n" \
    "           'ba' = Same as 'b', but the color is averaged\n" \
    "           ! IT IS NOT ADVISED TO RUN 'b' OR 'ba' ON LARGE DIRECTORIES !\n" \
    "           'n' = 'name': The name determines the color\n" \
    "           'na' = Same as 'n', but the color is averaged\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--info",
        help="Display helpful info about arguments",
        action="store_true"
    )

    parser.add_argument(
        "--in",
        dest="fof",
        help="The folder or file to create an image from"
    )

    parser.add_argument(
        "--out",
        help="The name of the image file"
    )

    parser.add_argument(
        "-i", "--imagemode",
        default="r",
        choices=["l", "s", "m"],
        help="The imagemode (see --info). Default: s"
    )

    parser.add_argument(
        "-p", "--pixelmode",
        default="na",
        choices=["e", "b", "ba", "n", "na"],
        help="The pixelmode (see --info). Default: na"
    )

    args = parser.parse_args()

    if args.info:
        info()
    
    else:
        if not (args.fof and args.out):
            print("--in and --out are required")
            exit()
        in_ = Path(args.fof)
        out = Path(args.out)
        imagemode = args.imagemode
        pixelmode = args.pixelmode
        create_raw_image(in_, out, imagemode, pixelmode)

if __name__ == "__main__":
    main()
