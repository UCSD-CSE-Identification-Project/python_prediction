import pandas as pd

#
# Note: anid column will be a list of floats, because NaN is a float in Python
#

def pair_data(course):
	# Obtain paired question data from csv file in data frame format
	if (course == "cs1"):
		paired_qs = pd.read_csv("../data/cs1/corresponding_questions.csv", na_values=["<NA>"])
	elif (course == "cse8a"):
		paired_qs = pd.read_csv("../data/cse8a/corresponding_questions.csv", na_values=["<NA>"])
	elif (course == "cse12"):
		paired_qs = pd.read_csv("../data/cse12/corresponding_questions.csv", na_values=["<NA>"])
	elif (course == "cse100"):
		paired_qs = pd.read_csv("../data/cse100/corresponding_questions.csv", na_values=["<NA>"])
	elif (course == "cse141"):
		paired_qs = pd.read_csv("../data/cse141/corresponding_questions.csv", na_values=["<NA>"])

	# Initialize universal question ID (qid) column of paired questions
	q = 0
	qq = 0
	new_uids = []

	for i in range(paired_qs.shape[0]):
		if (course == "cs1"):
			# When reading in corresponding_questions_original.csv, the last column will be float because of NaN
			if (pd.isna(paired_qs["FA13_ID"][i]) or pd.isna(paired_qs["FA14_ID"][i])):
				new_uids.append("qq"+str(qq))
				qq += 1
			else:
				new_uids.append("q"+str(q))
				q += 1
		else:
			new_uids.append("q"+str(q))
			q += 1

	# Make sure the first column is "qid"
	paired_qs = paired_qs.rename(columns={paired_qs.columns[0]: "qid"})
	return paired_qs.assign(qid=new_uids)

def load_data_with_anid(fname, pairinfo, ID):
	data = pd.read_csv(fname, na_values=["<NA>"])
	names = ["anid", "exam_total"] + list(pairinfo[ID])
	data = data.filter(items=names)
	return data

def combine_with_anid(data1, data2, pair, data1_col, data2_col):
	aggregated_anid = list(data1["anid"]) + list(data2["anid"])
	aggregated_exam = list(data1["exam_total"]) + list(data2["exam_total"])
	aggregated = pd.DataFrame(data={"anid": aggregated_anid, "exam_total": aggregated_exam})
	
	data1_names = data1.columns
	data2_names = data2.columns

	for i in range(pair.shape[0]):
		name1 = pair[pair.columns[data1_col]][i]
		name2 = pair[pair.columns[data2_col]][i]

		if (name1 not in data1_names or name2 not in data2_names):
			print(str(i) + str(pair["qid"][i]) + " has no corresponding questions... so move on!")
			continue

		column = list(data1[name1]) + list(data2[name2])
		tempDf = pd.DataFrame(data={pair["qid"][i]: column})
		aggregated = pd.concat([aggregated, tempDf], axis=1)

	return aggregated

def addCS1Anid(data, term):
	if (term == "train"):
		nametable = pd.read_csv("../data/cs1/nametable_FA13.csv", na_values=["<NA>"])
	else:
		nametable = pd.read_csv("../data/cs1/nametable_FA14.csv", na_values=["<NA>"])

	# NA/NaN will convert list type to float
	anid = [None] * data.shape[0]
	for student in range(data.shape[0]):
		remote = data["remote"][student]
		for match in range(nametable.shape[0]):
			if (nametable["remote"][match] == remote):
				anid[student] = nametable["anid"][match]
				break

	# Overwrite remote column with anid data
	data = data.assign(remote=anid)
	# Change remote column name to anid
	data = data.rename(columns={"remote": "anid"})
	return data

def load_filter_questions(course, pairinfo):
	if (course == "cs1"):
		# CS1-Python data has no anid!
		raw_data_train = pd.read_csv("../data/cs1/data_FA13.csv", na_values=["<NA>"])
		raw_data_test = pd.read_csv("../data/cs1/data_FA14.csv", na_values=["<NA>"])

		# Add anid column to cs1 train and test data
		raw_data_train = addCS1Anid(raw_data_train, "train")
		raw_data_test = addCS1Anid(raw_data_test, "test")
	elif (course == "cse8a"):
		# Load and filter two terms of clicker data
		fa14_1 = load_data_with_anid("../data/cse8a/data_FA14a.csv", pairinfo, "FA14_ID")
		fa14_2 = load_data_with_anid("../data/cse8a/data_FA14b.csv", pairinfo, "FA14b_ID")
		raw_data_train = combine_with_anid(fa14_1, fa14_2, pairinfo, 1, 2)
		raw_data_test = load_data_with_anid("../data/cse8a/data_FA15.csv", pairinfo, "FA15_ID")
	elif (course == "cse12"):
		raw_data_train = load_data_with_anid("../data/cse12/data_SP14.csv", pairinfo, "SP14_ID")
		raw_data_test = load_data_with_anid("../data/cse12/data_SP15-secB.csv", pairinfo, "SP15b_ID")
		print(raw_data_train)
	elif (course == "cse100"):
		raw_data_train = load_data_with_anid("../data/cse100/data_FA13.csv", pairinfo, "FA13_ID")
		raw_data_test = load_data_with_anid("../data/cse100/data_WI15.csv", pairinfo, "WI15_ID")
	elif (course == "cse141"):
		####################################
		## usefa14
		## TRUE: train-FA14 and test-FA15
		## FALSE: train-FA15 and test-FA16
		####################################
		usefa14 = True

		if (usefa14):
			# Load and filter two terms of clicker data
			fa14_1 = load_data_with_anid("../data/cse141/data_FA14a.csv", pairinfo, "FA14a_ID")
			fa14_2 = load_data_with_anid("../data/cse141/data_FA14b.csv", pairinfo, "FA14b_ID")
			raw_data_train = combine_with_anid(fa14_1, fa14_2, pairinfo, 1, 2)
			raw_data_test = load_data_with_anid("../data/cse141/data_FA15.csv", pairinfo, "FA15_ID")
		else:
			raw_data_train = load_data_with_anid("../data/cse141/data_FA15.csv", pairinfo, "FA15_ID")
			raw_data_test = load_data_with_anid("../data/cse141/data_FA16.csv", pairinfo, "FA16_ID")

	# Temporary: remove exam_total column
	raw_data_train = raw_data_train.drop(columns=["exam_total"])
	raw_data_test = raw_data_test.drop(columns=["exam_total"])

	# Remove rows with no data
	# Remove rows with no anid
	raw_data_train = raw_data_train[pd.notna(raw_data_train["anid"])]
	raw_data_test = raw_data_test[pd.notna(raw_data_test["anid"])]

	# Convert anid column to int
	raw_data_train = raw_data_train.assign(anid=raw_data_train["anid"].astype(int))
	raw_data_test = raw_data_test.assign(anid=raw_data_test["anid"].astype(int))

	# Order rows by anid
	raw_data_train = raw_data_train.sort_values(by=["anid"]).reset_index(drop=True)
	raw_data_test = raw_data_test.sort_values(by=["anid"]).reset_index(drop=True)

	return (raw_data_train, raw_data_test)

def getLectureNum(str):
	lecnum = 0

	# lecnum is below 10 (0 ~ 9)
	if (str[2:3] == "q"):
		lecnum = int(str[1:2])
	# lecnum is >= 10
	else:
		lecnum = int(str[1:3])
	return lecnum

def getLectureNum141(str):
	lecnum = int(str[1:3])
	return lecnum

def DropLateLectures(data, dropfromthislecture, course):
	drops = []

	for i in range(1, len(data.columns)):
		if (course == "cse141"):
			lectureNumber = getLectureNum141(data.columns[i])
		else:
			lectureNumber = getLectureNum(data.columns[i])

		if (lectureNumber >= dropfromthislecture):
			drops.append(data.columns[i])

	data = data.drop(columns=drops)

	return data

def fromWhatLecture(course, keep_up_to_this_week):
	dropLecturefrom = 0
	if (course == "cs1"):
		if (keep_up_to_this_week == 1):
			dropLecturefrom = 4
		elif (keep_up_to_this_week == 2):
			dropLecturefrom = 7
		elif (keep_up_to_this_week == 3):
			dropLecturefrom = 10
		elif (keep_up_to_this_week == 4):
			dropLecturefrom = 13
		elif (keep_up_to_this_week == 5):
			dropLecturefrom = 16
		elif (keep_up_to_this_week == 6):
			dropLecturefrom = 17
		elif (keep_up_to_this_week == 7):
			dropLecturefrom = 20
		elif (keep_up_to_this_week == 8):
			dropLecturefrom = 23
		elif (keep_up_to_this_week == 9):
			dropLecturefrom = 26
		elif (keep_up_to_this_week == 10):
			dropLecturefrom = 29
		elif (keep_up_to_this_week == 11):
			dropLecturefrom = 32
		else:
			dropLecturefrom = 100
	elif (course == "cse8a"):
		if (keep_up_to_this_week == 1):
			dropLecturefrom = 4
		elif (keep_up_to_this_week == 2):
			dropLecturefrom = 5
		elif (keep_up_to_this_week == 3):
			dropLecturefrom = 7
		elif (keep_up_to_this_week == 4):
			dropLecturefrom = 9
		elif (keep_up_to_this_week == 5):
			dropLecturefrom = 11
		elif (keep_up_to_this_week == 6):
			dropLecturefrom = 13
		elif (keep_up_to_this_week == 7):
			dropLecturefrom = 15
		elif (keep_up_to_this_week == 8):
			dropLecturefrom = 16
		elif (keep_up_to_this_week == 9):
			dropLecturefrom = 17
		else:
			dropLecturefrom = 100
	elif (course == "cse12"):
		if (keep_up_to_this_week == 1):
			dropLecturefrom = 4
		elif (keep_up_to_this_week == 2):
			dropLecturefrom = 6
		elif (keep_up_to_this_week == 3):
			dropLecturefrom = 9
		elif (keep_up_to_this_week == 4):
			dropLecturefrom = 12
		elif (keep_up_to_this_week == 5):
			dropLecturefrom = 15
		elif (keep_up_to_this_week == 6):
			dropLecturefrom = 18
		elif (keep_up_to_this_week == 7):
			dropLecturefrom = 21
		elif (keep_up_to_this_week == 8):
			dropLecturefrom = 23
		elif (keep_up_to_this_week == 9):
			dropLecturefrom = 25
		else:
			dropLecturefrom = 100
	elif (course == "cse100"):
		if (keep_up_to_this_week == 1):
			dropLecturefrom = 4
		elif ((keep_up_to_this_week == 2) or (keep_up_to_this_week == 3)): # there is no week 3 data. Week 3 will produce same results as week 2
			dropLecturefrom = 7
		elif (keep_up_to_this_week == 4):
			dropLecturefrom = 10
		elif (keep_up_to_this_week == 5):
			dropLecturefrom = 13
		elif (keep_up_to_this_week == 6):
			dropLecturefrom = 16
		elif (keep_up_to_this_week == 7):
			dropLecturefrom = 18
		else:                   			# CSE 100 WI15 has only 19 lectures
			dropLecturefrom = 100          # Weeks 9 and 10 will produce the same results as week 8
	elif (course == "cse141"):
		## even when using FA15 as test set, 
		## week3 is until lecture 5, so keep_up_to_this_week still needs to be 6
		if (keep_up_to_this_week == 1):
			dropLecturefrom = 3
		elif (keep_up_to_this_week == 2):
			dropLecturefrom = 4
		elif (keep_up_to_this_week == 3):
			dropLecturefrom = 6
		elif (keep_up_to_this_week == 4):
			dropLecturefrom = 8
		elif (keep_up_to_this_week == 5):
			dropLecturefrom = 10
		elif (keep_up_to_this_week == 6):
			dropLecturefrom = 11
		elif (keep_up_to_this_week == 7):
			dropLecturefrom = 13
		elif (keep_up_to_this_week == 8):
			dropLecturefrom = 15
		elif (keep_up_to_this_week == 9):
			dropLecturefrom = 16
		else:
			dropLecturefrom = 100

	return dropLecturefrom

def DropLectures(data, dropWeek, course):
	# Determine from what lecture to drop
	dropLecture = fromWhatLecture(course, dropWeek)

	# Drop late lectures
	newData = DropLateLectures(data, dropLecture, course)

	return newData

def ProcessClickerQData(pair, data, whichcolumn):
	final_data = data
	return final_data

def convert_to_universal_qid(pairinfo, train, test, course):
	train_results = train
	test_results = test

	return (train_results, test_results)

def count_NAs(data):
	return data

def do_fill_NAs_to_6(data):
	return data

def convert_responses_to_correctness(data, pair):
	return data

def change_columnnames(df):
	return df

def convert_responses_to_correctness_train_test(course, train, test, pair):
	return (train_results, test_results)

def scale_correctness(train, test):
	return (train, test)

def merge_correctness(train, test):
	return (train_clicker, test_clicker)

def add_lecture_number(course, pair):
	return

def merge_perweek_correctness(course, uptowhatweek, pair, train, test):
	return (train_clicker, test_clicker)

def factorize_responses(df):
	return

def process_dynamic_data(data):
	return data

def append_dynamic_data(course, trainData, testData, option):
	return































