import regex
from itertools import product, chain
import cProfile
import random


def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)


bs = r'(?<!\\)\\'
no_bs = rf'(?<!{bs})'
range_regex = rf'{no_bs}\{{(?:\d+,?\d*|,\d+){no_bs}\}}'
char_range = rf'(?:{no_bs}\[)[^\[\]]+(?:{no_bs}\])'
backslash = r'\e' [0]

# metas = r'[\|\(\)\?\*\+\{\}\.\[\]]'
# metas = r'(\[|\]|\\|\||\(|\)|\?|\*|\+|\{|\}|\.)'
# metas = r'(\[|\]|\\|\||\(|\)|\?|\*|\+|\{|\}|\.)'
metas = r'[|(){}?*+[\]\.\\]'
# metas = r'\\|[|(){}?*+[\].]'
#
# all_chars = ''.join(chr(i) for i in range(43, 92))
# all_chars = regex.sub(metas, lambda x: rf'{backslash}{x.group()}', all_chars)
# all_chars = r'[' + all_chars + r']'

all_chars = [chr(i) for i in range(0, 128)]
all_chars = [regex.sub(metas, lambda x: f'\{x.group(0)}', q) for q in all_chars]
# random.shuffle(all_chars)
print(all_chars)
print(len(all_chars))
all_chars = r'|'.join(a for a in all_chars)
all_chars = r'(' + all_chars + r')'

all_chars = regex.sub(r'\\\\', r'\\\\\\', all_chars)

print([all_chars])


# all_chars = r'(\\\\)'



def is_valid_regex(input):
    try:
        regex.compile(input)
        return True
    except regex.error:
        return False


def replace_metas(input):
    # input = regex.sub(rf'{no_bs}\.', '\\w', input)
    input = regex.sub(rf'{no_bs}\.', all_chars, input)
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


def tokenize_regex(s, group_char_ranges=True):
    print(s)
    pattern = rf'{range_regex}|{char_range}|[|()\\?*+{{}}]|[^|(){{}}\\?*+]'
    crange = char_range + '|' if group_char_ranges else ''
    pattern = rf'{range_regex}|{crange}[|()\\?*+{{}}]|[^|(){{}}\\?*+]'
    tokens = regex.findall(pattern, s)
    print(tokens)

    for i, (a, b) in enumerate(zip(tokens, tokens[1:])):
        if regex.match(r'\\[(){}?*+[\]\.\\|]', a + b):
            tokens[i] = a + b
            tokens[i + 1] = ''
    tokens = [token for token in tokens if token != '']
    print('TOKZ', tokens)
    return tokens


def replace_char_range(char_range):
    pattern = rf'{no_bs}[\[|\]]|[^-]-[^-\]]|.'
    sub_tokens = regex.findall(pattern, char_range)[1:-1]
    for i, sub_token in enumerate(sub_tokens):
        if len(sub_token) == 3:
            min_num = ord(sub_token[0])
            max_num = ord(sub_token[2])
            all_chars = map(chr, range(min_num, max_num + 1))
            all_chars = [x if x != '\\' else r'\\' for x in all_chars]
            sub_tokens[i] = '|'.join(all_chars)
    return f"({'|'.join(sub_tokens)})"


def replace_char_ranges(tokens):
    for i, token in enumerate(tokens):
        if regex.match(char_range, token):
            tokens[i] = replace_char_range(token)
    return tokens


def clean_up(input):
    if not is_valid_regex(input):
        return 'invalid regex'
    input = replace_metas(input)
    input = tokenize_regex(input)
    input = replace_char_ranges(input)
    print(input, 'testssss')
    input = r''.join(input)
    print([input], 'stett')
    input = tokenize_regex(input, False)

    i = 0
    while i < len(input):
        token = input[i]
        if regex.match(range_regex, token):
            range_tokens = regex.findall(r'\d+|,', token)
            if range_tokens[-1] == ',':
                return 'invalid regex'
            if range_tokens[0] == ',':
                range_tokens[0] = '0'
            elif len(range_tokens) == 1:
                range_tokens.insert(0, range_tokens[0])
            else:
                i += 1
                continue
            input[i] = f'{{{range_tokens[0]},{range_tokens[1]}}}'
            i += 1
            continue
        if i != len(input) - 1:
            if regex.match(range_regex, input[i + 1]):
                if token != ')':
                    input.insert(i, '(')
                    input.insert(i + 2, ')')
                    i += 3
                    continue
        i += 1
    return input


def tokens_to_dict(tokens):
    lists = {0: []}
    are_done = {0: False}
    curr_key = 0
    highest_key = 0
    for i, token in enumerate(tokens):
        if token == '(':
            highest_key += 1
            lists[curr_key].append(highest_key)
            curr_key = highest_key
            are_done[curr_key] = False
            if curr_key not in lists:
                lists[curr_key] = []
            continue
        if token == ')':
            are_done[curr_key] = True
            while are_done[curr_key]:
                curr_key -= 1
            continue
        lists[curr_key].append(token)
    return lists


def group_or_operands(list_dict):
    for key, lis in list_dict.items():
        if '|' in lis:
            new_list = [[]]
            for item in lis:
                if item == '|':
                    new_list.append('|')
                    new_list.append([])
                else:
                    new_list[-1].append(item)
            new_list = [[''] if item == [] else item for item in new_list]
            list_dict[key] = new_list
    return list_dict


def regex_product(tokens):
    if all(type(x) is str for x in tokens):
        return [''.join(tokens)]
    else:
        poss = [''.join(flatten(x)) for x in product(*tokens)]
    if poss == []:
        poss = ['']
    return poss


def evaluate_group(tokens, list_dict):
    for i, t in enumerate(tokens):
        if type(t) is int:
            tokens[i] = list_dict[t]
        if type(t) is str and len(t) == 2 and t[0] == backslash:
            tokens[i] = t[1]
    tokens = regex_product(tokens)
    return tokens


def range_token_to_range(range_token):
    range_tokens = list(map(int, regex.findall(r'\d+', range_token)))
    return range(range_tokens[0], range_tokens[1] + 1)


def evaluate(tokens, list_dict):
    if '|' in tokens:
        tokens = [token for token in tokens if token != '|']
        tokens = [evaluate_group(t, list_dict) for t in tokens]
    else:
        tokens = evaluate_group(tokens, list_dict)
    return tokens


def possibilities(list_dict):
    keys = sorted(list_dict.keys(), reverse=True)
    for key in keys:
        tokens = list_dict[key]
        if len(tokens) == 1 and type(tokens[0]) is int:
            list_dict[key] = list_dict.pop(tokens[0])
            continue

    keys = sorted(list_dict.keys(), reverse=True)

    for key in keys:
        tokens = list_dict[key]

        i = 0
        while i < len(tokens):
            t = tokens[i]
            if type(t) is str and regex.match(range_regex, t):
                the_range = range_token_to_range(t)
                repeated = [[tokens[i - 1]] * n for n in the_range]
                for j in range(1, len(repeated) * 2 - 1, 2):
                    repeated.insert(j, '|')
                repeated = evaluate(repeated, list_dict)
                repeated = list(flatten(repeated))
                tokens.pop(i)
                new_key = max(list_dict.keys()) + 1
                list_dict[new_key] = repeated
                tokens[i - 1] = new_key
                continue
            i += 1

        tokens = evaluate(tokens, list_dict)
        list_dict[key] = tokens
    poss = list_dict[keys[-1]]
    if len(poss) > 0 and type(poss[0]) is list:
        poss = list(flatten(poss))
    poss = set(poss)
    return poss


def regex_possibilities(s):
    s = clean_up(s)
    s = tokens_to_dict(s)
    s = group_or_operands(s)
    return possibilities(s)


# test = r'bu|[rn]t|[coy]e|[mtg]a|j|iso|n[hl]|[ae]d|lev|sh|[lnd]i|[po]o|ls'
# test = r'a.a|i..n|j|oo|a.t|i..o|a..i|bu|n.e|ay.|r.e|po|ma|nd'
# test = r'...'
test = r'[^a]'
test = r'.'
# test = r'\['
com = regex_possibilities(test)
for a in com:
    if len(a) != 1:
        print(a)
print(len(com))

print(sorted(com))

# s = b'426c616168'

# print(b"\077\046\014".decode("utf-8"))
# s = b"\000".decode("utf-8")
# s = '\x00' # hexadecimal character
# print(regex.findall(".", s))
# for i in range(128):
#     print(chr(i))
# print(''.join(chr(i) for i in range(128)))


#
# cProfile.run('regex_possibilities(test)', 'stats')
#
# import pstats
# from pstats import SortKey
# p = pstats.Stats('stats')
# p.strip_dirs().sort_stats(-1).print_stats()
# p.sort_stats(SortKey.CUMULATIVE).print_stats(20)
# # p.sort_stats('tottime').print_stats(10)
