from nltk.corpus import stopwords
import fasttext


stopWords = set(stopwords.words('english'))
model = fasttext.load_model("title_model_norm_e25_mc20.bin")
synonyms = model.get_nearest_neighbors('iphone', k=10)
with open('top_words.txt','r') as in_file, open('synonym_file.txt','w') as out_file:
    for line in in_file:
        w = line.strip()
        if w.lower() not in stopWords:
            synonyms = model.get_nearest_neighbors(w, k=100)
            #print(w)
            #print(synonyms)
            word_list = [w]
            for s in synonyms:
                if s[0] >= 0.8:
                    word_list.append(s[1])
                else:
                    break
            #print (word_list)
            if len(word_list) > 1:
                out_file.write(','.join(word_list)+'\n')
                

