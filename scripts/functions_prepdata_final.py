import pandas as pd
from sklearn.preprocessing import scale

def score_to_binary(df):
	# Change exam_total to 1/0 (depending on cutoff)
	failing_percentage = 0.4

	fail_score = df["exam_total"].quantile(failing_percentage, interpolation="nearest")

	# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	# Currently no factor feature in the python version, not the same as R's factor

	#print([ (1 if (score<fail_score) else 0) for score in df["exam_total"] ])
	#print(pd.factorize([ (1 if (score<fail_score) else 0) for score in df["exam_total"] ]))
	return (df.assign(exam_total=[ (1 if (score<fail_score) else 0) for score in df["exam_total"] ]))

def load_final(course):
	if (course == "cs1"):
		raw_data_train = pd.read_csv("../data/cs1/nametable_FA13.csv", na_values=["<NA>"])
		raw_data_test = pd.read_csv("../data/cs1/nametable_FA14.csv", na_values=["<NA>"])
	elif (course == "cse8a"):
		raw_data_train1 = pd.read_csv("../data/cse8a/nametable_FA14a.csv", na_values=["<NA>"])
		raw_data_train2 = pd.read_csv("../data/cse8a/nametable_FA14b.csv", na_values=["<NA>"])

		# Combine 2 nametables and reassign indices
		raw_data_train = pd.concat([raw_data_train1, raw_data_train2], ignore_index=True)

		raw_data_test = pd.read_csv("../data/cse8a/nametable_FA15.csv", na_values=["<NA>"])
	elif (course == "cse12"):
		raw_data_train = pd.read_csv("../data/cse12/nametable_SP14.csv", na_values=["<NA>"])
		raw_data_test = pd.read_csv("../data/cse12/nametable_SP15.csv", na_values=["<NA>"])
	elif (course == "cse100"):
		raw_data_train = pd.read_csv("../data/cse100/nametable_FA13.csv", na_values=["<NA>"])
		raw_data_test = pd.read_csv("../data/cse100/nametable_WI15.csv", na_values=["<NA>"])
	elif (course == "cse141"):
		####################################
		## usefa14
		## TRUE: train-FA14 and test-FA15
		## FALSE: train-FA15 and test-FA16
		####################################
		usefa14 = False

		if (usefa14):
			raw_data_train1 = pd.read_csv("../data/cse141/nametable_FA14a.csv", na_values=["<NA>"])
			raw_data_train2 = pd.read_csv("../data/cse141/nametable_FA14b.csv", na_values=["<NA>"])

			raw_data_train = pd.concat([raw_data_train1, raw_data_train2], ignore_index=True)

			raw_data_test = pd.read_csv("../data/cse141/nametable_FA15.csv", na_values=["<NA>"])
		else:
			raw_data_train = pd.read_csv("../data/cse141/nametable_FA15.csv", na_values=["<NA>"])
			raw_data_test = pd.read_csv("../data/cse141/nametable_FA16.csv", na_values=["<NA>"])

	prep_train = raw_data_train[["anid", "exam_total"]]
	prep_test = raw_data_test[["anid", "exam_total"]]

	# Scale final exam scores
	prep_train = prep_train.assign(exam_total=scale(prep_train["exam_total"]))
	prep_test = prep_test.assign(exam_total=scale(prep_test["exam_total"]))

	binary_train = score_to_binary(prep_train)
	binary_test = score_to_binary(prep_test)

	return (binary_train, binary_test)