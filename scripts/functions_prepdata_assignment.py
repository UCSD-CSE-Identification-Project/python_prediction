import pandas as pd
import numpy as np

# Called by load_assignment
def load_csv(course):
	if (course == "cs1"):
		train = pd.read_csv("../data/cs1/assignments_FA13.csv", na_values=["<NA>"])
		test = pd.read_csv("../data/cs1/assignments_FA14.csv", na_values=["<NA>"])
	elif (course == "cse8a"):
		train = pd.read_csv("../data/cse8a/assignments_FA14.csv", na_values=["<NA>"])
		test = pd.read_csv("../data/cse8a/assignments_FA15.csv", na_values=["<NA>"])
	elif (course == "cse12"):
		train = pd.read_csv("../data/cse12/assignments_SP14.csv", na_values=["<NA>"])
		test = pd.read_csv("../data/cse12/assignments_SP15.csv", na_values=["<NA>"])
	elif (course == "cse100"):
		train = pd.read_csv("../data/cse100/assignments_FA13.csv", na_values=["<NA>"])
		test = pd.read_csv("../data/cse100/assignments_WI15.csv", na_values=["<NA>"])
	elif (course == "cse141"):
		train = pd.read_csv("../data/cse141/assignments_FA15.csv", na_values=["<NA>"])
		test = pd.read_csv("../data/cse141/assignments_FA16.csv", na_values=["<NA>"])

	return (train, test)

# Called by load_assignment ??????????
def remove_extra_columns(train, test):
	train = train.drop(columns=["remote"])
	test = test.drop(columns=["remote"])

	return (train, test)

# Called by remove_later_assignment
def filter_testset(data, week, course):
	# Remove anid column
	names = data.columns[1:]
	dueweekinfo = []

	for name in names:
		dueweekinfo.append(name.split("w"))

	tempDf = pd.DataFrame(data={"fullname": names})
	dueweek = pd.DataFrame(np.matrix(dueweekinfo))

	dueweek = pd.concat([tempDf, dueweek], axis=1)
	dueweek.columns = ["fullname", "a", "dueweek"]
	dueweek = dueweek.assign(dueweek=[int(num) for num in dueweek["dueweek"]])

	filtered = dueweek.loc[dueweek["dueweek"] <= week]

	if (filtered.shape[0] == 0):
		result = data[["anid"]]
	else:
		filtered_names = ["anid"] + filtered["fullname"]
		result = data.filter(items=filtered_names)

		result.columns = ["anid"] + filtered["a"]

		if (course == "cse141" and week >= 8):
			if (week == 8):
				# Name a4 to a5
				result = result.rename(columns={"a4": "a5"})
			else:
				# Calculate avg(a4,a5) and name it as a5
				a4 = result[["a4", "a5"]].mean(axis=1)
				result = result.drop(columns=["a4", "a5"])
				result = pd.concat([result, a4], axis=1)
	return result

# Called by remove_later_assignments
def filter_trainset(data, testnames, course):
	# If the course is cse141 and its testset has a3
	if (course == "cse141" and ("a3" in testnames)):
		# Calculate avg(a3, a4) of the trainset and name it as a3
		a3 = data[["a3", "a4"]].mean(axis=1)
		result = data.drop(columns=["a3", "a4"])
		result = pd.concat([result, a3], axis=1)
	else:
		result = data

	result = result.filter(items=testnames)

	if (result.shape[1] == 1):
		result.columns = ["anid"]

	return result

# Called by load_assignment
def remove_later_assignments(train, test, course, week):
	result_test = filter_testset(test, week, course)
	result_train = filter_trainset(train, result_test.columns, course)

	return (result_train, result_test)

# Called by load_assignment
# Merge assignment scores per row and get mean score
def merge_assignment_scores(data):
	if (data.shape[1] == 1):
		# No assignment, simply return "anid" only
		result = data
	elif (data.shape[1] == 2):
		# Only one assignment, name of that assignment becomes "mergedassignment"
		result = data
		result.columns = ["anid", "mergedassignment"]
	else:
		tempDf = pd.DataFrame(data={"anid": data["anid"]})
		data = data.drop(columns=["anid"])
		result = tempDf.assign(mergedassignment=data.mean(axis=1))

	return result

# Called by convert_NAs_to_avg_for_dataframe
def convert_NAs_to_avg_for_dataframe(df):
	columnavgs = df.mean(axis=0)
	df = df.fillna(columnavgs)

	return df

# Called by load_assignment
def convert_NAs_to_avg(train, test):
	processed_train = convert_NAs_to_avg_for_dataframe(train)
	processed_test = convert_NAs_to_avg_for_dataframe(test)

	return (processed_train, processed_test)

# Called by prepdata.py
def load_assignment(course, uptowhatweek):
	(raw_train, raw_test) = load_csv(course)
	(filterer_train, filterer_test) = remove_extra_columns(raw_train, raw_test)
	(result_train, result_test) = remove_later_assignments(filterer_train, filterer_test, course, uptowhatweek)
	(filled_train, filled_test) = convert_NAs_to_avg(result_train, result_test)

	merged_train = merge_assignment_scores(filled_train)
	merged_test = merge_assignment_scores(filled_test)

	return (merged_train, merged_test)