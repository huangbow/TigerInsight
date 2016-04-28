import sys, csv, collections

class Food:
	"""docstring for Food"""
	def __init__(self, name, tags):
		self.name = name
		self.tags = tags



def main():
	arr = []
	with open('./business_chara.txt', 'rb') as file:
		foods = file.readlines()
		for food in foods:
			name = food[:food.index(':')]
			tags = food[food.index(':')+1:-2]
			arr.append(Food(name, tags))

	with open('./output.txt', 'wb') as file:
		for food in arr:
			file.write("(\"" + food.name + "\",\"" + food.tags + "\"),\n")

if __name__ == '__main__':
	main()