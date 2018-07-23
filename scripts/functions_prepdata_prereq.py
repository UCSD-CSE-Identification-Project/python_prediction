import pandas as pd
import numbers
import math

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

def transform2(e):
	if (e == ""):
		return float("NaN")
	elif (isinstance(e, numbers.Number)):
		return e
	# For all the other strings
	else:
		return float(e)

def preprocess(df):
	return df.applymap(transform1)

def load_prereq_csv(course):
	if (course == "cse12"):
		raw_data_train = pd.read_csv("../data/cse12/prerec_SP14.csv", na_values=["<NA>"])
		raw_data_test = pd.read_csv("../data/cse12/prerec_SP15.csv", na_values=["<NA>"])
	elif (course == "cse100"):
		raw_data_train = pd.read_csv("../data/cse100/prerec_FA13.csv", na_values=["<NA>"])
		raw_data_test = pd.read_csv("../data/cse100/prerec_WI15.csv", na_values=["<NA>"])
	elif (course == "cse141"):
		raw_data_train1 = pd.read_csv("../data/cse141/prerec_FA14a.csv", na_values=["<NA>"])
		raw_data_train2 = pd.read_csv("../data/cse141/prerec_FA14b.csv", na_values=["<NA>"])
		raw_data_train = pd.concat([raw_data_train1, raw_data_train2], ignore_index=True)

		raw_data_test = pd.read_csv("../data/cse141/prerec_FA15.csv", na_values=["<NA>"])

	# Fill NAs, convert from float to string
	raw_data_train = raw_data_train.fillna("NA")
	raw_data_test = raw_data_test.fillna("NA")

	prep_train = preprocess(raw_data_train)
	prep_test = preprocess(raw_data_test)

	return (prep_train, prep_test)

def convert_to_numeric(df):
	return df.applymap(transform2)

def preprocess_prerequisite_of_cse12(df, mergeorkeep):
	if (mergeorkeep == "merge"):
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

def preprocess_prerequisite_of_cse100(df, mergeorkeep):
	result = df[["anid", "cse12", "cse15l", "cse21"]]
	going_to_merge = df[["cse5a", "cse30", "mae9", "ece15"]]

	if (mergeorkeep == "merge"):
		mergedcse30 = (going_to_merge.mean(axis=1)).apply(lambda mean: round(mean, 2) if not math.isnan(mean) else mean)
		return result.assign(mergedcse30=mergedcse30)
	elif (mergeorkeep == "keep"):
		return pd.concat([result, going_to_merge], axis=1)

def convert_NA_to_avg(train, test):
	merged = pd.concat([train, test], ignore_index=True)

	mean = merged.mean(axis=0).drop(["anid"])

	train = train.fillna(mean)
	test = test.fillna(mean)

	return (train, test)

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