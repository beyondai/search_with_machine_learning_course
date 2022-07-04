cat_freq = {}
with open('shuf_norm_all_cat_prod.txt', 'r') as f:
    for line in f:
        tokens = (line.split())
        cat = tokens[0]
        cat_freq[cat] = cat_freq.get(cat, 0) + 1

prod_cnt = 0

with open('shuf_norm_all_cat_prod.txt', 'r',) as in_file, open('filtered_shuf_norm.txt', 'w') as out_file:
    for line in in_file:
        cat = line.split()[0]
        if cat_freq[cat] >= 500:
            out_file.write(line)
            prod_cnt +=1


