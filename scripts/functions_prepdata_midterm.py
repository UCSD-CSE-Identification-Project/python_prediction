import pandas as pd

# Called by prepdata.py
def reset_cutoffweek(course):
	newcutoffweek = 0

	if (course == "cs1"):
		newcutoffweek = 5
	elif (course == "cse8a"):
		newcutoffweek = 3
	elif (course == "cse12"):
		newcutoffweek = 5
	elif (course == "cse100"):
		newcutoffweek = 5
	elif (course == "cse141"):
		newcutoffweek = 5

	return newcutoffweek

# Called by load_midterm
# Based on the format of input csv file, dataframe only has 2 columns, anid & midterm
def do_fill_NAs_to_average2(data):
	# This translation only calculates the max of midterm column
	mean = data.mean(axis=0).drop(["anid"])
	maxVal = data["midterm"].max(axis=0)

	# This only fills midterm column
	data = data.fillna(mean)
	return data.assign(midterm=data["midterm"].divide(maxVal))

# Called by prepdata.py
def load_midterm(course, usefirstmidterm):
	if (course == "cs1"):
		train = pd.read_csv("../data/cs1/exams_FA13.csv", na_values=["<NA>"])
		test = pd.read_csv("../data/cs1/exams_FA14.csv", na_values=["<NA>"])
	elif (course == "cse8a"):
		train = pd.read_csv("../data/cse8a/exams_FA14.csv", na_values=["<NA>"])
		test = pd.read_csv("../data/cse8a/exams_FA15.csv", na_values=["<NA>"])
	elif (course == "cse12"):
		train = pd.read_csv("../data/cse12/exams_SP14.csv", na_values=["<NA>"])
		test = pd.read_csv("../data/cse12/exams_SP15.csv", na_values=["<NA>"])
	elif (course == "cse100"):
		train = pd.read_csv("../data/cse100/exams_FA13.csv", na_values=["<NA>"])
		test = pd.read_csv("../data/cse100/exams_WI15.csv", na_values=["<NA>"])
	elif (course == "cse141"):
		train = pd.read_csv("../data/cse141/exams_FA15.csv", na_values=["<NA>"])
		test = pd.read_csv("../data/cse141/exams_FA16.csv", na_values=["<NA>"])

	if (course == "cse8a" or course == "cse100"):
		# Because of the flag and resetting the cutoff week, midterm is not automatically
		# selected to be the closest one to the cutoff week user inputted
		if (usefirstmidterm == 1):
			train = train[["anid", "midterm1"]]
			test = test[["anid", "midterm1"]]
			# Change column name to midterm
			train.columns = ["anid", "midterm"]
			test.columns = ["anid", "midterm"]
		else:
			train = train[["anid", "midterm2"]]
			test = test[["anid", "midterm2"]]
			# Change column name to midterm
			train.columns = ["anid", "midterm"]
			test.columns = ["anid", "midterm"]
	else:
		train = train[["anid", "midterm"]]
		test = test[["anid", "midterm"]]

	train = do_fill_NAs_to_average2(train)
	test = do_fill_NAs_to_average2(test)

	return (train, test)