import re

shape = [
    'oooooo    oooooo',
    'oooooo    oooooo',
    'oooooo    oooooo',
    'ooooooo  ooooooo',
    '   oooo  oooo'
]

# Extract content
with open('keymap.c', 'r') as f:
    content = f.read()

match = re.search(r'(?<=const uint16_t PROGMEM keymaps\[]\[MATRIX_ROWS]\[MATRIX_COLS] = \{).*?(?=};)', content, re.S)
if match == None:
    print('Could not find layers')
    exit()
layers_group = match.group(0)

# Format
layers_group = re.sub('[ \n\t]*', '', layers_group)
layers_group = layers_group.replace('[', '\n    [')

layer_groups = list(re.finditer(r'(?<=LAYOUT\()[^\[]*(?=\))', layers_group))
layers = [match.group(0) for match in layer_groups]

shaped_keys = []
for l, layer in enumerate(layers):
    keys = layer.split(',')
    i = 0
    shaped_keys.append([[None for _ in range(max([len(i) for i in shape]))] for _ in range(len(shape))])

    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c != ' ':
                shaped_keys[l][y][x] = keys[i]
                i += 1

max_widths = [0]*max([len(i) for i in shape])
for w in range(len(max_widths)):
    m = 0
    for layer in shaped_keys:
        for row in layer:
            if len(row) <= w:
                break
            if row[w] == None:
                continue
            l = len(row[w])
            if l > m:
                m = l
    max_widths[w] = m

for i in range(len(layers)):
    keys = shaped_keys[i]
    layer = ''
    for row in keys:
        layer += '\n        '
        for j, key in enumerate(row):
            if key == None:
                if max_widths[j] > 0:
                    layer += ' ' * (max_widths[j] + 1)
                else:
                    layer += ' ' * 3
            else:
                layer += (key + ',').ljust(max_widths[j] + 1)
            layer += ' '
    layer += '\n        '
    layers[i] = layer



for i, layer in reversed(list(enumerate(layer_groups))):
    layers_group = layers_group[:layer.start()] + layers[i] + layers_group[layer.end():]

# Reinsert content
content = content[:match.start(0)] + layers_group + content[match.end(0):]

with open('keymap.c', 'w') as f:
    f.write(content)
