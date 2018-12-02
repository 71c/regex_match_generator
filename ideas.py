{
    0: ['u', 1, '\\+', 2],
    1: [['i', 'o', '\\|', 'p', '\\?', 'a'], '|', ['b']],
    2: [3, 'e', 5],
    3: ['c', 4, 'd'],
    4: [['d'], '|', ['e'], '|', ['f']],
    5: ['d', 'f']
}

a = {
    0: ['u', ['io|p?a', 'b'], '+', ['cddedf', 'cededf', 'cfdedf']],
    1: ['io|p?a', 'b'],
    2: ['cddedf', 'cededf', 'cfdedf'],
    3: ['cdd', 'ced', 'cfd'],
    4: ['d', 'e', 'f'],
    5: 'df'
}

{
    0: [[1, '\\{', '{0,1}'], '|', ['\\{']],
    1: [['Z'], '|', ['['], '|', ['\\'], '|', [']'], '|', ['^'], '|', ['_'],
        '|', ['`'], '|', ['a']]
}

import itertools
# print([''.join(x) for x in itertools.product(*a[0])])
# print([''.join(x) for x in itertools.product(*['d', 'f'])])
# print([''.join(x) for x in itertools.product(*['f', 'd', 'f'])])

tokens = [[['r'], ['n']], 't']


def flatten(listOfLists):
    "Flatten one level of nesting"
    return itertools.chain.from_iterable(listOfLists)


# print([''.join(flatten(x)) for x in itertools.product(*tokens)])

# for i in range(10):
#     i -= 1
#     print(i)

{
    0: [1],
    1: [[2], '|', [4]],
    2: [['i'], '{2,3}'],
    3: ['i'],
    4: ['u', 'uu', 'uuu'],
    5: ['u']
}

{
    0: [1],
    1: [[2], '|', [4]],
    2: [3, '{2,3}', 'o', 'i', 'p'],
    3: ['i'],
    4: [5, '{2,3}'],
    5: ['u']
}

{0: [1, '{0,1}'], 1: [['i'], '|', ['u']]}
{0: [[''], '|', ['i', 'u']], 1: ['i', 'u']}
{0: ['', 'i', 'u'], 1: ['i', 'u']}

test = r'(hb|dsf){2,3}o'
test = r'(hb|dsf){2,3}o'
test = r'((hb|dsf)(hb|dsf)|(hb|dsf)(hb|dsf)(hb|dsf))o'

{
    0: [1, 'o'],
    1: [[2, 3], '|', [4, 5, 6]],
    2: [['h'], '|', ['o']],
    3: [['h'], '|', ['o']],
    4: [['h'], '|', ['o']],
    5: [['h'], '|', ['o']],
    6: [['h'], '|', ['o']]
}

# l = [
#     'Mick', 'Rick', 'allocochick', 'backtrick', 'bestick', 'candlestick',
#     'counterprick', 'heartsick', 'lampwick', 'lick', 'lungsick', 'potstick',
#     'quick', 'rampick', 'rebrick', 'relick', 'seasick', 'slick', 'tick',
#     'unsick', 'upstick'
# ]
# l = ['fu', 'tofu', 'snafu']
# s = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
# for w in l:
#     s = s & set(w)
# print(s)
#
# m = [
#     'Kickapoo', 'Nickneven', 'Rickettsiales', 'billsticker', 'borickite',
#     'chickell', 'fickleness', 'finickily', 'kilbrickenite', 'lickpenny',
#     'mispickel', 'quickfoot', 'quickhatch', 'ricksha', 'rollicking',
#     'slapsticky', 'snickdrawing', 'sunstricken', 'tricklingly', 'unlicked',
#     'unnickeled'
# ]
# m = ['futz', 'fusillade', 'functional', 'discombobulated']
# s = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
# for w in m:
#     s = s & set(w)
# print(s)

import re

# letters = map(chr, range(129))
# letters = 'abcdefghijklmnopqrstuvwxyz()+*?}{0123456789,'
# letters = list(''.join(x) for x in itertools.product(letters, repeat=3))
# print(l)

# for letter in letters:
#     # print(letter)
#     # if letter in '()+':
#     #     letter = rf'\{letter}'
#     # letter = re.sub(r'[\(\)\+]', lambda x: rf'\{x.group(0)}', letter)
#     try:
#         matches_all_l = all(re.search(letter, x) for x in l)
#         matches_no_m = not any(re.search(letter, x) for x in l)
#         if matches_all_l and matches_no_m:
#             print(letter, matches_all_l and matches_no_m)
#     except:
#         continue

# 5: 8
# 4: 7
# 3: 5
# 2: 3


# stuff = [5] * 1
#
#
# for i in range(1, len(stuff) * 2 - 1, 2):
#     stuff.insert(i, '|')
# print(stuff)





a = '''civic
deedeed
degged
hallah
kakkak
kook
level
murdrum
noon
redder
repaper
retter
reviver
rotator
sexes
sooloos
tebbet
tenet
terret'''




b = '''✔arrogatingly
✔camshach
✔cinnabar
✔defendress
✔derivedly
✔gourmet
✔hamleteer
✔hydroaviation
✔lophine
✔nonalcohol
✔outslink
✔pretest
✔psalterium
✔psorosperm
✔scrummage
✔sporous
✔springer
✔sunburn
✔teleoptile
✔unstuttering
✔womanways'''


a = ' '.join(re.findall(r'\w+', a))
b = ' '.join(re.findall(r'\w+', re.sub(r' \(no match\)', '', b)))
print(a)
