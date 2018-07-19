import sys
import csv
import glob

#|----------------------------------------------------------------------------|
#|--------------------------Function Definitions------------------------------|
#|----------------------------------------------------------------------------|

def convert_dict_to_list(data, result):
	for a in data:
		print a
		result.append(data[a])

	return result

#|----------------------------------------------------------------------------|
#|---------------------------Beginning of Script------------------------------|
#|----------------------------------------------------------------------------|
if(len(sys.argv) != 2):
	print("Error: You must run this script with two cmd line args")
	sys.exit()

nametable = {}

# Read nametable and initialize lists
with open("nametable_FA" + str(sys.argv[1]) + ".csv") as table:
	nametable_reader = csv.reader(table)
	for row in nametable_reader:
		nametable[row[5]] = [row[0], row[1]]
		
print nametable

assignment = {}
exam = {}
# obtain quiz data
with open("CSE_141_FA16_Fall_2016_grades.csv") as newdata:
	new_reader = csv.reader(newdata)
	for row in new_reader:
		#print row
		if row[1] == 'email':
			continue
		else:
			#print row
			if (nametable.has_key(row[1])):
				assignment[row[1]] = nametable[row[1]]
				exam[row[1]] = nametable[row[1]]

				for i in range(1,8):					
					if i == 5:
						if row[i*2] == '':
							score = ""
						else:
							score = round(float(row[i*2])/float(row[i*2+1]),3)

						exam[row[1]] = exam[row[1]] + [score]

					else:
						if row[i*2] == '':
							score = ""
						else:
							score = round(float(row[i*2])/float(row[i*2+1]),3)

							assignment[row[1]] = assignment[row[1]] + [score]

					#print i, i*2, assignment[row[1]]

print assignment


list_assignment = convert_dict_to_list(assignment, [["anid", "remote", "a1", "a2", "a3", "a4", "a5", "a6"]])
list_exam = convert_dict_to_list(exam, [["anid", "remote", "midterm"]])

	
with open("assignments_FA" + str(sys.argv[1]) + ".csv", 'wb') as f:
	assignmentparsed_writer = csv.writer(f)
	assignmentparsed_writer.writerows(list_assignment)

with open("exams_FA" + str(sys.argv[1]) + ".csv", 'wb') as f:
	examparsed_writer = csv.writer(f)
	examparsed_writer.writerows(list_exam)

