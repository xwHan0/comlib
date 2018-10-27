
"""

一个图标由以下结构：

<----------  WIGHT  ------------>
---------------------------------
|                               |
|                               |
|                               |
|                ————————————————
|                |              |
|                |       |      |
|----------------| ——————|————— |
|                |       |      |
|                |              |
------------------———————————————

"""


flag = ['expand', 'contract']
pre = [True, False]

SVG_WIDTH = 20
SVG_HEIGHT = 30

SVG_HEADER = [
    '<?xml version="1.0" encoding="utf-8"?>\n',
    '<svg version="1.1" id="progress" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" ',
    '    width="{0}" height="{1}">\n'.format( SVG_WIDTH, SVG_HEIGHT ),

]
    
SVG_FOOT = ['</svg>\n']

SVG_ROOT = ""

box_size = SVG_WIDTH // 2
x_vertical = box_size + box_size // 2
y_vectical_st = SVG_HEIGHT - box_size
y_vectical_ed = SVG_HEIGHT

for fg in flag:
    for p in pre:
        name = "{0}flag_{1}_{2}.svg".format(SVG_ROOT, fg, ('sub' if p else 'root'))
        f = open(name, 'w')
        
        f.writelines(SVG_HEADER)

        content = [
            '<rect x="{0}" y="{1}" width="{0}" height="{0}" stroke="black" fill="none" />\n'.format(box_size, y_vectical_st),
            '<line x1="{0}" y1="{1}" x2="{2}" y2="{1}" stroke="black" />\n'.format( box_size+2, SVG_HEIGHT-box_size//2, SVG_WIDTH-2 ),
            
            '<line x1="{0}" y1="{1}" x2="{0}" y2="{2}" stroke="black" />\n'.format( x_vertical, y_vectical_st+2, y_vectical_ed-2 ) if fg == "expand" else "",
            '<line x1="0" y1="{0}" x2="{1}" y2="{0}" stroke="black" stroke-dasharray="4,1" />\n'.format( SVG_HEIGHT-box_size//2, SVG_WIDTH//2 ) if p else "",
        ]
        f.writelines(content)
        f.writelines(SVG_FOOT)
        f.close()


other = ['vectical', 'leaf', 'empty']

for file in other:
    name = "{0}flag_{1}.svg".format(SVG_ROOT, file)
    f = open(name, 'w')
    
    f.writelines(SVG_HEADER)

    if file == "vectical":
        content = [
            '<line x1="{0}" y1="0" x2="{0}" y2="{1}" stroke="black" stroke-dasharray="4,1" />\n'.format( box_size+box_size//2, SVG_HEIGHT ),
        ]
    elif file == "leaf":
        content = [
            '<line x1="0" y1="{0}" x2="{1}" y2="{0}" stroke="black" stroke-dasharray="4,1" />\n'.format( SVG_HEIGHT-box_size//2, SVG_WIDTH ),
        ]
    else:
        content = []
            
    f.writelines(content)
    f.writelines(SVG_FOOT)
    f.close()
     










