import pandas as pd

df1 = pd.read_csv('./crawl_normal_0k_250k.csv')
df2 = pd.read_csv('./Crawl_normal_250k_255k.csv')
df3 = pd.read_csv('./Crawl_normal_255k_260k.csv')
df4 = pd.read_csv('./Crawl_normal_260k_270k.csv')
df5 = pd.read_csv('./Crawl_normal_270k_280k.csv')
df6 = pd.read_csv('./Crawl_normal_280k_290k.csv')
df7 = pd.read_csv('./Crawl_normal_290k_300k.csv')
df8 = pd.read_csv('./Crawl_normal_300k_310k.csv')
df9 = pd.read_csv('./Crawl_normal_310k_325k.csv')
df10 = pd.read_csv('./Crawl_normal_325k_340k.csv')
df11 = pd.read_csv('./Crawl_normal_340k_350k.csv')

df = pd.concat([df1, df2, df3, df4, df5, df6,
               df7, df8, df9, df10, df11], axis=0)
print(df.shape)
df = df.drop_duplicates()
print(df.shape)
df.to_csv('./Crawl_normal_0k_350k.csv', index=False)
