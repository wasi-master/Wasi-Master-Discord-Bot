colors = ['red','green','yellow']
d1={}
for i, c in enumerate(colors, 1): d1[i] = c
d2 = {v: k for k, v in d1.items()}
print(d2)
print(d1)
