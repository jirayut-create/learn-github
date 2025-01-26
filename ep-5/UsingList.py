# โครงสร้างฐานข้อมูล
data =['Python','C++','C#','html']
data2 =['P','C+','C','html']
# print (data)
# print(type(data))
# print(len(data))

# print('Python' in data) #True
# print('A' in data)
# print('A' not in data)

# print(data[0:]) 
# print(data[0:3]) 

# data.append('API') #ต่อท้าย
# print(data)
# data.insert(2,'JS') #แทรกตำแหน่งที่ 2
# print(data)
# del data[2]
# print(data)

# data.sort() #เรียงลำดับ
# print(data)
# data.sort(reverse=True)
# print(data)

# Book =['Python','C++','C#','html']
# price = ['100','200','150','500']
# for b,p in zip(Book , price) :
#     print(f'{b} ราคา {p}')

# data1 = ['A','B','C'] #เปรียบเทียบ
# data2 = ['a','b','c']
# print(data1 > data2)

# datamap = [222,33,44,555]
# print(datamap)
# result = map(str,datamap)
# print(list(result))

from tabulate import tabulate

Book =[['Python',1000],['C++' ,500] ,['HTML' , 200]]  #Table Tabulate
header = ['name','Price']

print(tabulate(Book,header))
