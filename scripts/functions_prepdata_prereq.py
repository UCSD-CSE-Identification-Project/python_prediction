import pandas as pd
import numbers
import math

# Called by preprocess
# Change all letter scores to GPA based, except the anid column
def transform1(e):
	# To take care of the anid column
	if (isinstance(e, numbers.Number)):
		return e

	e = e.split()[0]

	if (e == "A+"):
		result = 4.33
	elif (e == "A"):
		result = 4.0
	elif (e == "A-"):
		result = 3.67
	elif (e == "B+"):
		result = 3.33
	elif (e == "B"):
		result = 3.0
	elif (e == "B-"):
		result = 2.67
	elif (e == "C+"):
		result = 2.33
	elif (e == "C"):
		result = 2.0
	elif (e == "C-"):
		result = 1.67
	elif (e == "D+"):
		result = 1.33
	elif (e == "D"):
		result = 1.0
	elif (e == "F" or e == "W"):
		result = 0
	else:
		result = ""

	return result

# Called by convert_to_numeric
# Make sure the dataframe is made of numbers
def transform2(e):
	if (e == ""):
		return float("NaN")
	elif (isinstance(e, numbers.Number)):
		return e
	# For all the other strings
	else:
		return float(e)

# Called by load_prereq_csv
def preprocess(df):
	return df.applymap(transform1)

# Called by load_prereq
# Read in data files for each course
def load_prereq_csv(course):
	if (course == "cse12"):
		raw_data_train = pd.read_csv("../data/cse12/prereq_SP14.csv", na_values=["<NA>"])
		raw_data_test = pd.read_csv("../data/cse12/prereq_SP15.csv", na_values=["<NA>"])
	elif (course == "cse100"):
		raw_data_train = pd.read_csv("../data/cse100/prereq_FA13.csv", na_values=["<NA>"])
		raw_data_test = pd.read_csv("../data/cse100/prereq_WI15.csv", na_values=["<NA>"])
	elif (course == "cse141"):
		#raw_data_train1 = pd.read_csv("../data/cse141/prereq_FA14a.csv", na_values=["<NA>"])
		#raw_data_train2 = pd.read_csv("../data/cse141/prereq_FA14b.csv", na_values=["<NA>"])
		#raw_data_train = pd.concat([raw_data_train1, raw_data_train2], ignore_index=True)

		raw_data_train = pd.read_csv("../data/cse141/prereq_FA15.csv", na_values=["<NA>"])
		raw_data_test = pd.read_csv("../data/cse141/prereq_FA16.csv", na_values=["<NA>"])

	# Fill NAs, convert from float to string
	raw_data_train = raw_data_train.fillna("NA")
	raw_data_test = raw_data_test.fillna("NA")

	prep_train = preprocess(raw_data_train)
	prep_test = preprocess(raw_data_test)

	return (prep_train, prep_test)

# Called by load_prereq
def convert_to_numeric(df):
	return df.applymap(transform2)

# Called by load_prereq
# CSE8A - needs to merge cse11 and cse8b column,
# because students can take either one to fulfill the requirement.
def preprocess_prerequisite_of_cse12(df, mergeorkeep):
	if (mergeorkeep == "merge"):
		# A dataframe with one column: anid
		df_anid = df[["anid"]]
		cse8bor11 = []

		# For each row
		for i in range(df.shape[0]):
			if (math.isnan(df["cse8b"][i])):
				cse8bor11.append(df["cse11"][i])
			else:
				cse8bor11.append(df["cse8b"][i])

		result = df_anid.assign(cse8bor11=cse8bor11)
	elif (mergeorkeep == "keep"):
		result = df[["anid", "cse8b", "cse11"]]
	return result

# Called by load_prereq
# CSE100 - 1) remove math154 and math184a
#          2) merge cse5a, cse30, mae9, and ece15. May have to calculate average
# At the end, the result would have cse12, cse15l, cse21, cse30(merged)
def preprocess_prerequisite_of_cse100(df, mergeorkeep):
	result = df[["anid", "cse12", "cse15l", "cse21"]]
	going_to_merge = df[["cse5a", "cse30", "mae9", "ece15"]]

	if (mergeorkeep == "merge"):
		mergedcse30 = (going_to_merge.mean(axis=1)).apply(lambda mean: round(mean, 2) if not math.isnan(mean) else mean)
		return result.assign(mergedcse30=mergedcse30)
	elif (mergeorkeep == "keep"):
		return pd.concat([result, going_to_merge], axis=1)

# Called by load_prereq
# Fill NA with the mean of train test combined
def convert_NA_to_avg(train, test):
	merged = pd.concat([train, test], ignore_index=True)

	mean = merged.mean(axis=0).drop(["anid"])

	train = train.fillna(mean)
	test = test.fillna(mean)

	return (train, test)

# Called by prepdata.py
def load_prereq(course, mergeorkeep):
	if (course == "cs1" or course == "cse8a"):
		print("cs1 and cse8a have no prerequisite course data... so not adding any data")
		train = None
		test = None
	else:
		data = load_prereq_csv(course)

		train = convert_to_numeric(data[0])
		test = convert_to_numeric(data[1])

		if (course == "cse12"):
			train = preprocess_prerequisite_of_cse12(train, mergeorkeep)
			test = preprocess_prerequisite_of_cse12(test, mergeorkeep)
		elif (course == "cse100"):
			train = preprocess_prerequisite_of_cse100(train, mergeorkeep)
			test = preprocess_prerequisite_of_cse100(test, mergeorkeep)

		# Make NaNs of qi column to be avg(qi)
		processed = convert_NA_to_avg(train, test)
		train = processed[0]
		test = processed[1]

	return (train, test)