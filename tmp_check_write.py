import os
from pathlib import Path
print('CWD:', os.getcwd())
print('LIST:', os.listdir())
p = Path('data') / 'chunks_test.tmp'
print('PATH_REPR:', repr(p))
try:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write('x')
    print('WROTE', p)
except Exception as e:
    print('EXC', type(e), e)

try:
    with open('test_write.txt', 'w', encoding='utf-8') as f:
        f.write('ok')
    print('WROTE test_write.txt')
except Exception as e:
    print('EXC2', type(e), e)

print('\nDIAGNOSTICS:')
print('abs data:', os.path.abspath('data'))
print('exists data:', os.path.exists('data'))
print('isdir data:', os.path.isdir('data'))
print('isfile data:', os.path.isfile('data'))
try:
    print('data listing:', os.listdir('data'))
except Exception as e:
    print('list data EXC', type(e), e)

abs_path = os.path.join(os.getcwd(), 'data', 'chunks_test_abs.tmp')
print('abs_path repr:', abs_path)
try:
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write('y')
    print('WROTE abs_path')
except Exception as e:
    print('abs_path EXC', type(e), e)
