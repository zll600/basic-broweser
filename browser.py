import tkinter
import tkinter.font
from constants import *
from url import URL
from html_parser import Text, Element, HTMLParser
from layout import BlockLayout, DocumentLayout

def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)


def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")

def lex(body):
    out = []
    buffer = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
            if buffer:
               out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Element(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out


def layout(tokens):
    weight = "normal"
    style = "roman"
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for token in tokens:
        if isinstance(token, Text):
            for word in token.text.split():
                font = tkinter.font.Font(
                            size=16,
                            weight=weight,
                            slant=style,
                        )
                w = font.measure(word)
                if cursor_x + w > WIDTH - HSTEP:
                    cursor_y += font.metrics("linespace") * 1.25
                    cursor_x = HSTEP
                display_list.append((cursor_x, cursor_y, word, font))
                cursor_x += w + font.measure(" ")
        elif token.tag == "i":
            style = "italic"
        elif token.tag == "/i":
            style = "roman"
        elif token.tag == "b":
            weight = "bold"
        elif token.tag == "/b":
            weight = "normal"

    return display_list

def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, 
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.display_list = []
    

    def scrolldown(self, e):
        max_y = max(self.document.height + 2*VSTEP - HEIGHT, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        self.draw()
    
    def draw(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll, self.canvas)

    def load(self, url):
        body = url.request()
        self.nodes = HTMLParser(body).parse()
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.draw()

if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
    # body = URL(sys.argv[1]).request()
    # nodes = HTMLParser(body).parse()
    # print_tree(nodes)