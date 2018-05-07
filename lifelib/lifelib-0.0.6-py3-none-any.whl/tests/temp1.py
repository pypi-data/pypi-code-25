import numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set(style="whitegrid") #, color_codes=True)

titanic = sns.load_dataset("titanic")
data = titanic.groupby("deck").size()   # data underlying bar plot in question

pal = sns.color_palette("RdBu", len(data))
rank = data.argsort().argsort()   # http://stackoverflow.com/a/6266510/1628638
sns.barplot(x=data.index, y=data, palette=np.array(pal)[rank])

plt.show()