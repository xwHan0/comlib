
def render(file, template, content={}):
    """
    按照模板生成内容

    Argument:
    * file: {str} ---- 输出文件名
    * content: {template: content}  ---- 替换内容
      * template: {str} ---- 模板文件中的字符串。字符串前后允许有空格
      * content: {str | [str]}  ---- 替换内容。为[str]类型时，每个元素被替换为一行
    * template: {str} ---- 模板文件名

    Return: None
    """
    file_data = ""
    with open(template, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if content.has_key(line):
                if isinstance( content[line], list ):
                    new_line = ""
                    for l in content[line]:
                        new_line += l + "\n"
                else:
                    new_line = content[line]
            file_data += new_line
    with open(file,"w",encoding="utf-8") as f:
        f.write(file_data)


# def rect(width, height, text='', matrix=[1,0,0,1,0,0], id='', fill="#ffffff", stroke="#000000" stroke-width=1):
#     rst = []
#     rst.append( '<g id="{}" transform="matrix({},{},{},{},{},{})">'.format(id, *matrix) )
#     rst.append('    <rect x="0" y="0" width="{}" height="{}" fill="{}" stroke="{}" stroke-width="{}"/>'.format(
#         width, height, fill, stroke, stroke-width))
#     rst.append('    <text x="0" y="0">{}</text>'.format(text))
#     rst.append('</g>')

#     return []

