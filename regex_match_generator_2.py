import re
import regex
from itertools import product
from functools import reduce


def is_valid_regex(input):
    try:
        re.compile(input)
        return True
    except re.error:
        return False


bs = r'(?<!\\)\\'
no_bs = rf'(?<!{bs})'

# range_regex = r'(?<!\\)\{(\d+,?\d*|,\d+)(?<!\\)\}'
range_regex = rf'{no_bs}\{{(?:\d+,?\d*|,\d+){no_bs}\}}'
def replace_metas(input):
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
    sub_tokens = re.findall(pattern, char_range)[1:-1]
    for i, sub_token in enumerate(sub_tokens):
        if len(sub_token) == 3:
            min_num = ord(sub_token[0])
            max_num = ord(sub_token[2])
            all_chars = '|'.join(map(chr, range(min_num, max_num + 1)))
            sub_tokens[i] = all_chars
    print('subts', sub_tokens)
    return f"({'|'.join(sub_tokens)})"


def replace_char_ranges(tokens):
    for i, token in enumerate(tokens):
        if re.match(char_range, token):
            tokens[i] = replace_char_range(token)
    return tokens


def parens_product(s):
    print(s, 'wetiowjeoi')
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
# test_regex = r'bu|[rn]t|[coy]e|[mtg]a|j|iso|n[hl]|[ae]d|lev|sh|[lnd]i|[po]o|ls'
# test_regex = r'[an][er]\d?[0-9]\w?'
# test_regex = r'(help){2}'
# test_regex = r'(yu(az|sd)yu){0,2}'
# test_regex = r'(adf|ert)'
# test_regex = r'\(e|uiop\)'
# test_regex = r'yu(az|sd)yu(sd)'
# test_regex = r'asdf'

test_regex = r'[a-c0-9]{2}d|e'

# test_regex = r'hi[45]'
# test_regex = r'(yu[as]yu){0,2}'
# test_regex = r'yu(az|sd)yu'
# test_regex = r'(yuazyu|yusdyu){0,2}'

# test_regex = r'.'
# test_regex = r'e.'

# test_regex = r'112(3[102]|42)'

# parsed = regex_possibilities(test_regex)
# print(parsed)

# import cProfile
# cProfile.run('u = regex_possibilities(test_regex)')


def tokenize_regex(s):
    tokens = re.findall(rf'{range_regex}|[|()\\]|[^|(){{}}\\]+', s)
    for i, (a, b) in enumerate(zip(tokens, tokens[1:])):
        if re.match(r'\\[|(){}]', a + b):
            tokens[i] = a + b
            tokens[i + 1] = ''
        elif re.match(r'\\\\', a + b):
            tokens[i] = a
            tokens[i + 1] = ''
    tokens = [token for token in tokens if token != '']
    return tokens

def flatten_bads(l):
    for i, e in enumerate(l):
        if type(e) is list:
            if len(e) == 1 and type(e[0]) is list:
                l[i] = e[0]
            else:
                l[i] = flatten_bads(e)
    return l

# print('OMG LOOK', flatten_bads(['foo', [[['ba'], ['eh', [['i']], ['mon'], 'o'], 'r']], ['yo']]))




def parse_tokenized_regex(tokens):
    stack = []
    level = 0
    is_first = True
    for i, token in enumerate(tokens):
        last_token_is_or = False if i == 0 else tokens[i - 1] == '|'
        if last_token_is_or and level == 0:
            if type(stack[-2]) is list:
                # stack[-2].append(stack.pop(-1))
                stack.append([])
            print('da token is:::', token)
        if token not in '(){}|':
            if is_first:
                print('IS FIRST!', token)
                stack.append(token)
                stack.append([])
                is_first = False
            else:
                stack[-1].append(token)
        elif token == '(':
            level += 1
            if not last_token_is_or and i > 1 and len(stack[-1]) > 0:
                print(stack[-1])
                stack[-1][-1] = [stack[-1][-1]]
            if len(stack[-1]) > 0:
                stack.append([])
        elif token == ')':
            # print('LEVEL', level)
            level -= 1
            if not last_token_is_or and i > 1 and len(stack[-1]) > 0:
                print(stack[-1])
                stack[-1][-1] = [stack[-1][-1]]
            stack[-2].append(stack.pop(-1))
            if len(stack[-1]) > 0 and level == 0:
                stack.append([])
        print(stack)
    # stack = flatten_bads(stack)
    return stack


def homogeneous_type(seq):
    iseq = iter(seq)
    first_type = type(next(iseq))
    return first_type if all((type(x) is first_type) for x in iseq) else False


def parsed_regex_product(tokens):
    # print('tokens:', tokens)
    for i, token in enumerate(tokens):
        if any(type(sub_token) in [list, tuple] for sub_token in token):
            tokens[i] = parsed_regex_product_full(token)
    if all(type(x) is list for x in tokens):
        return [''.join(l) for l in product(*tokens)]

    new_tokens = []
    for token in tokens:
        if type(token) in [list, tuple]:
            for sub_token in token:
                new_tokens.append(sub_token)
        else:
            new_tokens.append(token)
    return new_tokens


def parsed_regex_product_full(tokens):
    if len(tokens) == 2:
        result = parsed_regex_product(tokens)
        print(f'GIVES {tokens}\t{result}')
        return result
    for _ in range(len(tokens) - 1):
        tokens[0] = parsed_regex_product_full([tokens[0], tokens.pop(1)])
    return tokens[0]


tokens = [['bu'], [['r', 'n'], 't']]
tokens = [['foo'], ['bar', 'baz']]
tokens = ['b', 'u', [['r', 'n'], 't']]
tokens = [['foo'], ['bar', 'baz'], 'hi']

# | means different type

# [a-c0-9]d|e
tokens = [[['a', 'b', 'c', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
           ['d']], 'e']
print(parsed_regex_product_full(tokens))

# yu(az|sd)yu
tokens = [['yu'], ['az', 'sd'], ['yu']]

# yu(az|s(oid|m)d)yu
tokens = [['yu'], ['az', [['s'], ['oid', 'm'], ['d']]], ['yu']]
tokens = [['az'], [['s'], ['oid', 'm'], 'd']]
print(parsed_regex_product_full(tokens))

tokens = ['a', 'b', 'c']
print(parsed_regex_product_full(tokens))


pattern = r'foo|ba(eh|i(mon)o)r|yo{1,2}'
# pattern = r'yu(az|s(oid|m)d)yu'
tokens = tokenize_regex(pattern)
print('tokens:', tokens)
parsed = parse_tokenized_regex(tokens)
print('parsed:', parsed)
parsed = ['foo', [['ba'], ['eh', ['i'], ['mon'], ['o']]], ['r'], 'yo']
print(parsed_regex_product_full(parsed))



# test_regex = r'\\h?el\d\W\\wl??o\\s\S\t\d\\d\d\a\a\a(ef){,}?df\\\\\d\d'
# test_regex = r'\{0,3}'
# test_regex = r'bu|[rn]t|[coy]e|[mtg]a|j|iso|n[hl]|[ae]d|lev|sh|[lnd]i|[po]o|ls'
# test_regex = r'[an][er]\d?[0-9]\w?'
# test_regex = r'(help){2}'
# test_regex = r'(yu(az|sd)yu){0,2}'
# test_regex = r'(adf|ert)'
# test_regex = r'\(e|uiop\)'
# test_regex = r'yu(az|sd)yu(sd)'
# test_regex = r'asdf'

test_regex = r'[a-c0-9]{2}d|e'

# test_regex = r'hi[45]'
# test_regex = r'(yu[as]yu){0,2}'
# test_regex = r'yu(az|sd)yu'
# test_regex = r'(yuazyu|yusdyu){0,2}'

# test_regex = r'.'
# test_regex = r'e.'

# test_regex = r'112(3[102]|42)'
