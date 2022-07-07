from difflib import unified_diff
from js import document
from os import listdir
from source_code_simplifier import source_code_simplifier
import io


def main():
    for input_file_name in sorted(listdir('.')):
        option = document.createElement('option')
        option.value = input_file_name
        option.innerHTML = input_file_name
        Element('inputSelect').element.appendChild(option)
    on_select_input(None)
    on_select_input_simplified_difference(None)


def on_click_simplify_button(_):
    input_ = Element('inputTextarea').element.value
    reader = io.BufferedReader(io.BytesIO(input_.encode('utf-8')))
    wrapper = io.TextIOWrapper(reader)
    try:
        simplified = source_code_simplifier(wrapper)
        difference_line_list = list(unified_diff(input_.splitlines(), simplified.splitlines(), n=1000))[3:]
        difference_styled_line_list = []
        for difference_line in difference_line_list:
            if difference_line.startswith('+'):
                difference_styled_line_list.append(f'<span style="color:green;">{difference_line}</span>')
            elif difference_line.startswith('-'):
                difference_styled_line_list.append(f'<span style="color:red;">{difference_line}</span>')
            else:
                difference_styled_line_list.append(difference_line)
        Element('differencePre').element.innerHTML = '\n'.join(difference_styled_line_list)
        Element('simplifiedPre').element.innerHTML = simplified
    except Exception as exception:
        Element('differencePre').element.innerHTML = exception


def on_select_input(_):
    with open(Element('inputSelect').element.value) as file:
        Element('inputTextarea').element.value = file.read()
    Element('differencePre').element.innerHTML = ''
    Element('simplifiedPre').element.innerHTML = ''
    on_click_simplify_button(None)
    Element('inputTextarea').element.onkeyup()


def on_select_input_simplified_difference(_):
    if Element('differenceSimplifiedSelect').element.value == 'difference':
        Element('differencePre').element.hidden = False
        Element('simplifiedPre').element.hidden = True
    elif Element('differenceSimplifiedSelect').element.value == 'simplified':
        Element('differencePre').element.hidden = True
        Element('simplifiedPre').element.hidden = False


if __name__ == '__main__':
    main()
