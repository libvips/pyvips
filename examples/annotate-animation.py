#!/usr/bin/python3

import sys
import pyvips

if len(sys.argv) != 4:
    print(f"usage: {sys.argv[0]} input-animation output-animation text")
    sys.exit(1)

text = pyvips.Image.text(sys.argv[3], dpi=300, rgba=True)


# draw an overlay on a page ... this could do anything
def process_page(page, i):
    return page.composite(text, "over",
                          x=(i * 4) % page.width,
                          y=(i * 4) % page.height)


# load the animation, chop into pages, rejoin, save
animation = pyvips.Image.new_from_file(sys.argv[1], n=-1, access="sequential")
pages = animation.pagesplit()
pages = [process_page(page, i) for page, i in zip(pages, range(len(pages)))]
animation = pages[0].pagejoin(pages[1:])
animation.write_to_file(sys.argv[2])
