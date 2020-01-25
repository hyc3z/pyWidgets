

def dumpDict2Py(_dict:dict, filename, dictname):
    str_dict = str(_dict)
    indent_level = 0
    indent_str = ' '*4
    beautified_str_dict = ""
    last_return_buffer = ""
    within_text = False
    for i in str_dict:
        return_buffer = ""
        indent = ""
        if i == "'":
            within_text = not within_text
        if i == '{':
            indent_level += 1
            return_buffer += "\n"
        if i == '}':
            indent_level -= 1
            return_buffer += "\n"
        if i == ',':
            if not within_text:
                return_buffer += "\n"
        if last_return_buffer != "":
            indent = indent_str*indent_level
        last_return_buffer = return_buffer
        beautified_str_dict += "{}{}{}".format(indent, i.strip() if i!=":" else ": ", return_buffer)
    with open(filename, "w", encoding="utf-8") as f:
        f.write("{}=".format(dictname))
        f.write(beautified_str_dict)
