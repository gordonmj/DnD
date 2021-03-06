import json
import re
from collections import OrderedDict

# import spell


def read_meta(contents):
    finder = re.compile('-{3}.+-{3}', flags=re.DOTALL)
    head = finder.match(contents).group()
    lineparser = re.compile()


def read_list(s):
    tokens = s.replace('[', '').replace(']', '').split(sep=',')
    for i, t in enumerate(tokens):
        tokens[i] = cleanup(t)
    return tokens


def pair_off(s, ls=False):
    tokens = s.split(sep=':')
    if ls:
        return {tokens[0]: read_list(tokens[1])}
    else:
        return {tokens[0]: tokens[1]}


def cleanup(s):
    return s.replace('*', '').replace('"', '').strip()


def read_markdown(filename):
    ignores = ('---', 'layout:', 'date:', 'source:')
    with open(filename, 'r') as f:
        location = 0
        data = OrderedDict()
        effect = []
        for line in f:
            if(line.startswith(ignores)):
                location += 1
                continue
            if(line.isspace()):
                continue
            if(line.startswith('title')):
                data.update(pair_off(cleanup(line)))
                location += 1
                continue
            if(line.startswith('tags')):
                data.update(pair_off(line, True))
                location += 1
                continue

            if(location == 7):
                data.update({'type': cleanup(line)})
                location += 1
                continue
            if(8 <= location <= 11):
                data.update(pair_off(cleanup(line)))
                location += 1
                continue
            if(location > 11):
                effect.append(line)
                continue
        if (data['title'] == 'Sword Burst'):
            print('\n'.join(effect))
        data.update({'effect': '\n'.join(effect)})
    return data


def jsonify(filename):
    vals = read_markdown(filename)
    print(json.dumps(vals, indent=2))


if __name__ == '__main__':
    jsonify(r'C:\Users\Nicholas\Documents\GitHub\grimoire\_posts\2014-08-24-prestidigitation.markdown')
    jsonify(r'C:\Users\Nicholas\Documents\GitHub\grimoire\_posts\2015-01-12-teleport.markdown')
