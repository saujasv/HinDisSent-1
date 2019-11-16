from sklearn.model_selection import train_test_split
s1_data = open("s1","r").readlines()
s2_data = open("s2","r").readlines()
labels_data = open("labels","r").readlines()

s1 = []
s2 = []
labels = []

for i in s1_data:
    s1.append(i.strip())

for i in s2_data:
    s2.append(i.strip())


for i in labels_data:
    labels.append(i.strip())


indices = []
for i in range(len(s1)):
    indices.append(i)
import numpy as np
val_size = 0.05
test_size = 0.05

x_train, x_remain = train_test_split(indices, test_size=(val_size + test_size))
new_test_size = np.around(test_size / (val_size + test_size), 2)
# To preserve (new_test_size + new_val_size) = 1.0 
new_val_size = 1.0 - new_test_size

x_val, x_test = train_test_split(x_remain, test_size=new_test_size)

fo = open("s1.train","w")
fo1 = open("s2.train","w")
fo2 = open("labels.train","w")

for i in(x_train):
    print(i)
    fo.write(s1[i])
    fo.write("\n")
    fo1.write(s2[i])
    fo1.write("\n")
    fo2.write(labels[i])
    fo2.write("\n")

fo.close()
fo1.close()
fo2.close()



fo = open("s1.val","w")
fo1 = open("s2.val","w")
fo2 = open("labels.val","w")

for i in(x_val):
    fo.write(s1[i])
    fo.write("\n")
    fo1.write(s2[i])
    fo1.write("\n")
    fo2.write(labels[i])
    fo2.write("\n")

fo.close()
fo1.close()
fo2.close()

fo = open("s1.test","w")
fo1 = open("s2.test","w")
fo2 = open("labels.test","w")

for i in(x_test):
    fo.write(s1[i])
    fo.write("\n")
    fo1.write(s2[i])
    fo1.write("\n")
    fo2.write(labels[i])
    fo2.write("\n")

fo.close()
fo1.close()
fo2.close()


