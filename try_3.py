import regex
from itertools import product, chain


def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)


no_bs = r'(?<=(?:[^\\]|^)(?:\\\\)*)'
range_regex = rf'{no_bs}\{{(?:\d+,?\d*|,\d+){no_bs}\}}'
char_range = rf'{no_bs}\[\]?(?:[^\]\\]|\\.)+{no_bs}\]'
backslash = r'\e'[0]

metas = r'[|(){}?*+[\]\.\\]'

def make_excluded_char_range(excluded):
    chars = [c for c in map(chr, range(0, 128)) if c not in excluded]
    chars = [regex.sub(metas, lambda x: rf'\{x.group(0)}', q) for q in chars]
    chars = '(' + '|'.join(chars) + ')'
    return chars

dot_chars = make_excluded_char_range(['\n', '\r'])
dot_chars = regex.sub(r'\\\\', r'\\\\\\\\', dot_chars)


def is_valid_regex(s):
    try:
        regex.compile(s)
        return True
    except regex.error:
        return False


def replace_metas(s):
    toks = regex.findall(f'{char_range}|.', s)
    both = r'\\W|\\D|\\S|.'
    yes = r'\\W|\\D|\\S'
    for i, tok in enumerate(toks):
        if regex.match(char_range, tok):
            contents = tok[1:-1]
            if regex.search(yes, contents):
                subtoks = regex.findall(both, contents)
                specials = []
                regulars = []
                for subtok in subtoks:
                    if regex.match(yes, subtok):
                        specials.append(subtok)
                    else:
                        regulars.append(subtok)
                regular_part = f'[{"".join(regulars)}]'
                special_part = '|'.join(specials)
                stra = []
                if len(regular_part) != 2:
                    stra += [regular_part]
                if len(special_part) != 0:
                    stra += [special_part]
                toks[i] = rf'({"|".join(stra)})'
    s = ''.join(toks)

    # filler = r'(?:(?:\[(?:[^\]\\]|\\.)+\])|[^\]\\]|\\.)*'
    filler = r'(?:[^\]\\]|\\.)*'
    before_charrange_part = rf'(?<={no_bs}\[{filler})'
    after_charrange_part  = rf'(?={filler}{no_bs}\])'
    
    s = regex.sub(rf'{before_charrange_part}\\w{after_charrange_part}', 'A-Za-z0-9_', s)
    s = regex.sub(rf'{before_charrange_part}\\d{after_charrange_part}', '0-9', s)
    s = regex.sub(rf'{before_charrange_part}\\s{after_charrange_part}', r' \t\n\r\f\v', s)
    s = regex.sub(rf'{before_charrange_part}\\b{after_charrange_part}', '\b', s)

    s = regex.sub(rf'{no_bs}\.', dot_chars, s)
    s = regex.sub(rf'{no_bs}\\w', '[a-zA-Z0-9_]', s)
    s = regex.sub(rf'{no_bs}\\W', '[^a-zA-Z0-9_]', s)
    s = regex.sub(rf'{no_bs}\\d', '[0-9]', s)
    s = regex.sub(rf'{no_bs}\\D', '[^0-9]', s)
    s = regex.sub(rf'{no_bs}\\s', r'[ \t\n\r\f\v]', s)
    s = regex.sub(rf'{no_bs}\\S', r'[^ \t\n\r\f\v]', s)
    s = regex.sub(rf'{no_bs}\\f', '\f', s)
    s = regex.sub(rf'{no_bs}\\n', '\n', s)
    s = regex.sub(rf'{no_bs}\\r', '\r', s)
    s = regex.sub(rf'{no_bs}\\t', '\t', s)
    s = regex.sub(rf'{no_bs}\\v', '\v', s)
    s = regex.sub(rf'{no_bs}\\a', '\a', s)

    s = regex.sub(rf'{no_bs}\*', '{0,}', s)
    s = regex.sub(rf'{no_bs}\+', '{1,}', s)
    s = regex.sub(rf'(?<!{no_bs}\\|{range_regex})\?(?=\?)', '{0,1}', s)
    s = regex.sub(rf'(?<!{no_bs}\\|{range_regex})\?', '{0,1}', s)
    return s


def tokenize_regex(s, group_char_ranges=True):
    pattern = rf'{range_regex}|{char_range}|[|()\\?*+{{}}]|[^|(){{}}\\?*+]'
    crange = char_range + '|' if group_char_ranges else ''
    pattern = rf'{range_regex}|{crange}[|()\\?*+{{}}]|[^|(){{}}\\?*+]'
    tokens = regex.findall(pattern, s)
    for i, (a, b) in enumerate(zip(tokens, tokens[1:])):
        if regex.match(r'\\[(){}?*+[\]\.\\|]', a + b):
            tokens[i] = a + b
            tokens[i + 1] = ''
    tokens = [token for token in tokens if token != '']
    return tokens


def replace_char_range(char_range):
    pattern = r'(?:[^-\]\\]|\\[\]\\]|^\])(?:-(?:[^-\]\\]|\\[\]\\]))?|-'
    char_range = char_range[1:-1]
    if char_range[0] == '^':
        complemented = True
        char_range = char_range[1:]
    else:
        complemented = False
    sub_tokens = regex.findall(pattern, char_range)
    # print('char class tokens', sub_tokens)
    new_sub_tokens = []
    for i, sub_token in enumerate(sub_tokens):
        if len(sub_token) == 3:
            min_num = ord(sub_token[0])
            max_num = ord(sub_token[2])
            all_chars = map(chr, range(min_num, max_num + 1))
            all_chars = [x if x != '\\' else r'\\' for x in all_chars]
            for c in all_chars:
                new_sub_tokens.append(c)
        else:
            new_sub_tokens.append(sub_token)
    if complemented:
        new_sub_tokens = [t if t != r'\\' else '\\' for t in sub_tokens]
        new_sub_tokens = make_excluded_char_range(new_sub_tokens)
        return new_sub_tokens
    # print('new char class tokens', new_sub_tokens)
    return f"({'|'.join(new_sub_tokens)})"


def replace_char_ranges(tokens):
    for i, token in enumerate(tokens):
        if regex.match(char_range, token):
            tokens[i] = replace_char_range(token)
    return tokens


def clean_up(s):
    if not is_valid_regex(s):
        return 'invalid regex'
    s = replace_metas(s)
    s = tokenize_regex(s)
    s = replace_char_ranges(s)
    s = ''.join(s)
    s = tokenize_regex(s, False)

    i = 0
    while i < len(s):
        token = s[i]
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
            s[i] = f'{{{range_tokens[0]},{range_tokens[1]}}}'
            i += 1
            continue
        if i != len(s) - 1:
            if regex.match(range_regex, s[i + 1]):
                if token != ')':
                    s.insert(i, '(')
                    s.insert(i + 2, ')')
                    i += 3
                    continue
        i += 1
    return s


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
        elif token == ')':
            are_done[curr_key] = True
            while are_done[curr_key]:
                curr_key -= 1
        else:
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
        for i, token in enumerate(tokens):
            if len(token) > 0 and type(token[0]) is list:
                tokens[i] = list(flatten(token))
        poss = [''.join(flatten(x)) for x in product(*tokens)]
    if poss == []:
        poss = ['']
    return poss


def evaluate_group(tokens, list_dict):
    # replace eg a{0,2} with (|a|aa)
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if type(t) is str and regex.match(range_regex, t):
            the_range = range_token_to_range(t)
            repeated = [[tokens[i - 1]] * n for n in the_range]
            if len(repeated) == 1:
                repeated = [evaluate(repeated[0], list_dict)]
            else:
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
        list_dict[key] = evaluate(list_dict[key], list_dict)
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





def test_regex_1():
    test = '.alo[oefag]n.\\+'
    com = regex_possibilities(test)
    dot = tuple(map(chr, range(0, 128)))
    dot = tuple(x for x in dot if x not in ('\n', '\r'))
    prod = product(dot, ('alo',), ('o', 'e', 'f', 'a', 'g'), ('n',), dot, ('+',))
    null = {''.join(x) for x in prod}
    assert null == com

def test_regex(test):
    result = sorted(regex_possibilities(test))
    if result != ['invalid regex']:
        return all(bool(regex.match(f'^{test}$', x)) for x in result)
    return True

# test = r'bu|[rn]t|[coy]e|[mtg]a|j|iso|n[hl]|[ae]d|lev|sh|[lnd]i|[po]o|ls'
# test = r'a.a|i..n|j|oo|a.t|i..o|a..i|bu|n.e|ay.|r.e|po|ma|nd')
# test = r'(a|u|(o|ias{2,4}df))END{1}'
# test = r'a{,11}o{0,11}[asdfjklqwer]{0,3}'
# test = r'.{2}[asdfjklqwer]{0,3}'
# test = r'.{2}'
# test = r'\{(\d{1,1},?\d{0,1}|,\d{1,1})\}'
# test = r'\\\\n'
# test = r'[\^a]'
# test = r'[\p]'
# test = r'[\\]'
# test = r'[\s]'
# test = r'[^-b]'

tests = [
    r'[^-b]', 
    r'[\s]', 
    r'[\\]', 
    r'[\p]', 
    r'[\^a]', 
    r'\\\\n',
    r'[]abc]',
    r'[ab]c]',
    r'[ab\]c]',
    r'[ab\^c]',
    r'[ab^c]',
    r'\{(\d{1,1},?\d{0,1}|,\d{1,1})\}',
    r'.{2}',
    r'(a|u|(o|ias{2,4}df))END{1}',
    r'bu|[rn]t|[coy]e|[mtg]a|j|iso|n[hl]|[ae]d|lev|sh|[lnd]i|[po]o|ls',
    r'((a|b)|c) ',
    r'm?',
    r'[\SA-Z]?P',
    r'[bui\-p]',
    r'[bu\i\-p]',
    r'((a|[bui\-p]b)|c|[^abdd^])',
    # r'(([^\\])(\\\\){,5})'
    r'[^\\]',
    r'[\x00-\x7F]'
]
tests = [r'[\x00-\x7f]']
# tests = [r'[\\]']
# tests = [r'[^\\]']
# r'((a|[bui\-p]b)|c|[^abdd^]) ?',
# tests = [r'[bu\i\-p]']
# tests = [r'[abc\]def]']
for test in tests:
    result = sorted(regex_possibilities(test))
    print('result', result)
    # print(len(result))
    if not test_regex(test):
        print(test)


# test = r'[\Wjin-r]uio[asd-hoa]as' # ^, -, ] or \
# test = r'[\SA-Z]?P'
# test = r'((a|b)|c) '
# test = r'([abc]|AASSSD?DFF|(e|on))vo'
# test = r'(D?D|u)vo'
# test = r'a?'
# test = r'm?'
# print([test])










