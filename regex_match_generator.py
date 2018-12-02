import re
import regex
from itertools import product


def is_valid_regex(input):
    try:
        re.compile(input)
        return True
    except re.error:
        return False


bs = r'(?<!\\)\\'
no_bs = rf'(?<!{bs})'


def replace_metas(input):
    range_regex = r'(?<!\\)\{(\d+,?\d*|,\d+)(?<!\\)\}'
    input = regex.sub(rf'{no_bs}\.', '\\w', input)
    input = regex.sub(rf'{no_bs}\\w', '[A-Za-z0-9_]', input)
    input = regex.sub(rf'{no_bs}\\W', '[^A-Za-z0-9_]', input)
    input = regex.sub(rf'{no_bs}\\d', '[0-9]', input)
    input = regex.sub(rf'{no_bs}\\D', '[^0-9]', input)
    input = regex.sub(rf'{no_bs}\\s', r'[\\f\\n\\r\\t\\v]', input)
    input = regex.sub(rf'{no_bs}\\S', r'[^\\f\\n\\r\\t\\v]', input)
    input = regex.sub(rf'{no_bs}\\f', '\f', input)
    input = regex.sub(rf'{no_bs}\\n', '\n', input)
    input = regex.sub(rf'{no_bs}\\r', '\r', input)
    input = regex.sub(rf'{no_bs}\\t', '\t', input)
    input = regex.sub(rf'{no_bs}\\v', '\v', input)
    input = regex.sub(rf'{no_bs}\\a', '\a', input)

    input = regex.sub(rf'{no_bs}\*', '{0,}', input)
    input = regex.sub(rf'{no_bs}\+', '{1,}', input)
    input = regex.sub(rf'(?<!{bs}|{range_regex})\?(?=\?)', '{0,1}', input)
    input = regex.sub(rf'(?<!{bs}|{range_regex})\?', '{0,1}', input)

    input = regex.sub(r'\\([^\(\)\[\]\{\}])', lambda x: x.group(1), input)

    return input


def find_paren_pairs(s):
    bs = '\\c' [0]
    pairs = []
    start_index = 0
    level = 0
    for i, c in enumerate(s):
        if c in '()':
            a = False if i == 0 else s[i - 1] == bs
            b = False if i <= 1 else s[i - 2] == bs
            if a or not b:
                if c == '(':
                    level += 1
                    if level == 1:
                        start_index = i
                else:
                    level -= 1
                    if level == 0:
                        pairs += [(start_index, i + 1)]
    return pairs


# repeat = r'(?:\{\d+,\d*\}|\{\d*,\d+\}|\{\d+\})'
# repeat = rf'(?:{no_bs}\{{\d+,\d*(?:{no_bs}\}})|(?:{no_bs}\{{)\d*,\d+(?:{no_bs}\}})|(?:{no_bs}\{{)\d+(?:{no_bs}\}}))'
repeat = rf'(?:{no_bs}\{{\d+,\d*\}}|\{{\d*,\d+\}}|\{{\d+\}})'
# parens = r'\((?:[^|]+\|)*[^|()]+\)'
# parens = rf'{no_bs}\((?:[^|]+(?:{no_bs}\|))*[^|()]+(?:{no_bs}\))'
# parens = rf'(?:{no_bs}\(|^)(?:[^|]+(?:{no_bs}\|))*[^|()]+(?:{no_bs}\)|$)'
inside_parens = rf'(?:[^|]+(?:{no_bs}\|))*[^|()]+'
parens = rf'{no_bs}\({inside_parens}(?:{no_bs}\))'
inside_parens_full_str = rf'^{inside_parens}$'
# char_range = r'\[[^\[\]]+\]'
# char_range = rf'(?:{no_bs}\[)(?:{no_bs}[^\[\]])+(?:{no_bs}\])'
char_range = rf'(?:{no_bs}\[)[^\[\]]+(?:{no_bs}\])'


def parse(s):
    # s = regex.sub(inside_parens_full_str, lambda m: f'({m.group(0)})', s)

    # paren_pairs = find_paren_pairs(s)
    # marks = sum(paren_pairs, tuple())
    # if len(marks) > 0 and marks[0] != 0:
    #     marks = (0,) + marks
    # if len(marks) > 0 and marks[-1] != len(s):
    #     marks = marks + (len(s),)
    # sections = [s[start:stop] for start, stop in zip(marks, marks[1:])]
    # # print(sections)
    # # print([re.match(parens, section) for section in sections])
    # if len(sections) > 1:
    #     sections = [section if not re.match(parens, section) else possibilities(parse(section[1:-1])) for section in sections]
    #     print(sections)
    #     sections = [section if type(section) is not list else '(' + '|'.join(section) + ')' for section in sections]
    #     s = ''.join(sections)
    #     # print(sections)

    pattern = fr'{parens}{repeat}?|{char_range}{repeat}?|.{repeat}?|[^()\[\]]+'
    return re.findall(pattern, s)


def replace_char_range(char_range):
    pattern = rf'{no_bs}[\[|\]]|[^-]-[^-\]]|.'
    sub_tokens = re.findall(pattern, char_range)
    for i, sub_token in enumerate(sub_tokens):
        if len(sub_token) == 3:
            min_num = ord(sub_token[0])
            max_num = ord(sub_token[2])
            all_chars = ''.join(map(chr, range(min_num, max_num + 1)))
            sub_tokens[i] = all_chars
    return ''.join(sub_tokens)


def replace_char_ranges(tokens):
    for i, token in enumerate(tokens):
        if re.match(char_range, token):
            tokens[i] = replace_char_range(token)
    return tokens


def parens_product(s):
    s = re.findall(parens + '|' + repeat, s)
    content = re.split('[|()]', s[0])[1:-1]
    s[0] = content
    repeat_range = re.split('[,{}]', s[1])[1:-1]
    if repeat_range[0] == '':
        repeat_range[0] = '0'
    if len(repeat_range) == 1:
        repeat_range.append(repeat_range[0])
    s[1] = list(map(int, repeat_range))
    s = [
        ''.join(s) for t in
        [product(s[0], repeat=j) for j in range(s[1][0], s[1][1] + 1)]
        for s in t
    ]
    return s


def possibilities(parsed):
    parsed = replace_char_ranges(parsed)
    for i in range(len(parsed)):
        x = parsed[i]
        print(1, x)
        # x = regex.sub(inside_parens_full_str, lambda m: f'({m.group(0)})', x)
        # print(2, x)
        x = re.sub(r'\[(.+)\]', lambda m: f"({'|'.join(list(m.group(1)))})", x)
        print(3, x)
        x = re.sub(f'([^)])({repeat})',
                   lambda s: f'({s.group(1)}){s.group(2)}', x)
        x = re.sub(parens + '$', lambda m: m.group(0) + '{1,1}', x)
        # x = re.sub(rf'{char_range}$', lambda m: m.group(0) + '{1,1}', x)
        print(x)
        if re.match(parens, x):
            x = parens_product(x)
        parsed[i] = x
    parsed = [[p] if type(p) is str else p for p in parsed]
    print('parsed', parsed)
    return [''.join(l) for l in product(*parsed)]


def regex_possibilities(input):
    if not is_valid_regex(input):
        return 'invalid regex'
    print(input)
    input = replace_metas(input)
    print(input)
    input = parse(input)
    print(input)
    input = possibilities(input)
    return input


# test_regex = r'\\h?el\d\W\\wl??o\\s\S\t\d\\d\d\a\a\a(ef){,}?df\\\\\d\d'
# test_regex = r'\{0,3}'
test_regex = r'bu|[rn]t|[coy]e|[mtg]a|j|iso|n[hl]|[ae]d|lev|sh|[lnd]i|[po]o|ls'
# test_regex = r'[an][er]\d?[0-9]\w?'
# test_regex = r'(help){2}'
# test_regex = r'(yu(az|sd)yu){0,2}'
# test_regex = r'(adf|ert)'
# test_regex = r'\(e|uiop\)'
# test_regex = r'yu(az|sd)yu(sd)'
# test_regex = r'asdf'

# test_regex = r'hi[45]'
# test_regex = r'(yu[as]yu){0,2}'
# test_regex = r'yu(az|sd)yu'
# test_regex = r'(yuazyu|yusdyu){0,2}'

# test_regex = r'.'
# test_regex = r'e.'

# test_regex = r'112(3[102]|42)'

parsed = regex_possibilities(test_regex)
print(parsed)

# import cProfile
# cProfile.run('u = regex_possibilities(test_regex)')
