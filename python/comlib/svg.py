

class Render:
    def __init__(self, template):
        self.cnxt = []
        with open(template, "r", encoding="utf-8") as f:
            for line in f:
                self.cnxt.append(line)

    def render_block( self, content={} ):
        cnxt = []
        for line in self.cnxt:
            line1 = line.strip()
            if line1 in content:
                if isinstance( content[line1], list ):
                    cnxt += [l+'\n' for l in content[line1]]
                else:
                    cnxt.append( content[line1] + '\n' )
            else:
                cnxt.append( line )

        self.cnxt = cnxt

    def render_to_file(self, file):
        with open(file,"w",encoding="utf-8") as f:
            f.writelines(self.cnxt)


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


def rect(width, height, text='', cls='', matrix=[1,0,0,1,0,0], id=''):
     rst = []
     rst.append( '<g id="{}" transform="matrix({},{},{},{},{},{})" class="{}">'.format(id, *matrix, cls) )
     rst.append('    <rect x="0" y="0" width="{}" height="{}"/>'.format(width, height))
     rst.append('    <text x="{}" y="{}">{}</text>'.format(width/2, height/2, text))
     rst.append('</g>')

     return rst

