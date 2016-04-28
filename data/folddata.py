import sys, random


def FoldData():
	
	rows = []
	with open('./login.csv', 'rb') as file:
		rows = file.readlines()

	num = len(rows)


	ChooseToWrtie(rows, num, 40000)
	ChooseToWrtie(rows, num, 25000)
	ChooseToWrtie(rows, num, 10000)
	ChooseToWrtie(rows, num, 5000)

# Randomly choose row to wrtie
def ChooseToWrtie(rows, num, choose):
	with open('./' +str(choose) + 'login.csv', 'wb') as file:
		for row in rows:
			if random.randint(0, num) < choose and choose > 0:
				file.write(row)
				choose -= 1
			num -= 1


def main():
	FoldData()


if __name__ == '__main__':
	main()