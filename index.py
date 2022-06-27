from difflib import unified_diff
from js import document
from os import listdir
from source_code_normalizer import source_code_normalizer
import io


def main():
    for input_file_name in sorted(listdir('.')):
        option = document.createElement('option')
        option.value = input_file_name
        option.innerHTML = input_file_name
        Element('inputSelect').element.appendChild(option)
    on_select_input(None)
    on_select_input_normalized_difference(None)


def on_click_normalize_button(_):
    input_ = Element('inputTextarea').element.value
    reader = io.BufferedReader(io.BytesIO(input_.encode('utf-8')))
    wrapper = io.TextIOWrapper(reader)
    try:
        normalized = source_code_normalizer(wrapper)
        difference_line_list = list(unified_diff(input_.splitlines(), normalized.splitlines(), n=1000))[3:]
        difference_styled_line_list = []
        for difference_line in difference_line_list:
            if difference_line.startswith('+'):
                difference_styled_line_list.append(f'<span style="color:green;">{difference_line}</span>')
            elif difference_line.startswith('-'):
                difference_styled_line_list.append(f'<span style="color:red;">{difference_line}</span>')
            else:
                difference_styled_line_list.append(difference_line)
        Element('differencePre').element.innerHTML = '\n'.join(difference_styled_line_list)
        Element('normalizedPre').element.innerHTML = normalized
    except Exception as exception:
        Element('differencePre').element.innerHTML = exception


def on_select_input(_):
    with open(Element('inputSelect').element.value) as file:
        Element('inputTextarea').element.value = file.read()
    Element('differencePre').element.innerHTML = ''
    Element('normalizedPre').element.innerHTML = ''
    on_click_normalize_button(None)
    Element('inputTextarea').element.onkeyup()


def on_select_input_normalized_difference(_):
    if Element('differenceNormalizedSelect').element.value == 'difference':
        Element('differencePre').element.hidden = False
        Element('normalizedPre').element.hidden = True
    elif Element('differenceNormalizedSelect').element.value == 'normalized':
        Element('differencePre').element.hidden = True
        Element('normalizedPre').element.hidden = False


if __name__ == '__main__':
    main()
