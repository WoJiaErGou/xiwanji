import re
pp='我今天：“ '
print(len(pp))
if ' ' == pp[-1]:
    pp=pp[:-2]
print(len(pp))