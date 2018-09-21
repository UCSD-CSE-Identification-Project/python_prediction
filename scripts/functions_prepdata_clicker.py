import pandas as pd
import numpy as np
import sys
from sklearn.preprocessing import scale

#
# Note: anid column will be a list of floats, because NaN is a float in Python
#

# Called by prepdata.py
# Give each row of train/test questions a universal qid
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

# Called by load_filter_questions
# From pairinfo get all question names, make data only contain those questions
def load_data_with_anid(fname, pairinfo, ID):
	data = pd.read_csv(fname, na_values=["<NA>"])
	names = ["anid", "exam_total"] + list(pairinfo[ID])

	# This step created different question sequence comparing to R, but doesn't affect correctness
	data = data.filter(items=names)
	return data

# Called by load_filter_questions
# Unify question name to qid
def combine_with_anid(data1, data2, pair, data1_col, data2_col):
	aggregated_anid = list(data1["anid"]) + list(data2["anid"])
	aggregated_exam = list(data1["exam_total"]) + list(data2["exam_total"])
	aggregated = pd.DataFrame(data={"anid": aggregated_anid, "exam_total": aggregated_exam})
	
	data1_names = data1.columns
	data2_names = data2.columns

	for i in range(pair.shape[0]):
		# Find 2 corresponding names for each qid
		name1 = pair[pair.columns[data1_col]][i]
		name2 = pair[pair.columns[data2_col]][i]

		if (name1 not in data1_names or name2 not in data2_names):
			print(str(i) + str(pair["qid"][i]) + " has no corresponding questions... so move on!")
			continue

		column = list(data1[name1]) + list(data2[name2])
		tempDf = pd.DataFrame(data={pair["qid"][i]: column})
		aggregated = pd.concat([aggregated, tempDf], axis=1)

	return aggregated

# Called by load_filter_questions
# Find each student's anid from nametable
def addCS1Anid(data, term):
	if (term == "train"):
		nametable = pd.read_csv("../data/cs1/nametable_FA13.csv", na_values=["<NA>"])
	else:
		nametable = pd.read_csv("../data/cs1/nametable_FA14.csv", na_values=["<NA>"])

	# NA/NaN will convert list type to float
	anid = [None] * data.shape[0]
	for student in range(data.shape[0]):
		remote = data["remote"][student]
		# Can possibly use list.index to find the index
		for match in range(nametable.shape[0]):
			if (nametable["remote"][match] == remote):
				anid[student] = nametable["anid"][match]
				break

	# Overwrite remote column with anid data
	data = data.assign(remote=anid)
	# Change remote column name to anid
	data = data.rename(columns={"remote": "anid"})

	return data

# Called by prepdata.py
# Load questions data, form columns with original qname or combined qid
# Filter out improper rows
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
	elif (course == "cse100"):
		raw_data_train = load_data_with_anid("../data/cse100/data_FA13.csv", pairinfo, "FA13_ID")
		raw_data_test = load_data_with_anid("../data/cse100/data_WI15.csv", pairinfo, "WI15_ID")
	elif (course == "cse141"):
		####################################
		## usefa14
		## TRUE: train-FA14 and test-FA15
		## FALSE: train-FA15 and test-FA16
		####################################
		usefa14 = False

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

	# (Remove rows with no data)
	# Remove rows with no anid: this is essentially what is wanted in R code
	raw_data_train = raw_data_train[pd.notna(raw_data_train["anid"])]
	raw_data_test = raw_data_test[pd.notna(raw_data_test["anid"])]

	# Convert anid column to int
	raw_data_train = raw_data_train.assign(anid=raw_data_train["anid"].astype(int))
	raw_data_test = raw_data_test.assign(anid=raw_data_test["anid"].astype(int))

	# Order rows by anid
	raw_data_train = raw_data_train.sort_values(by=["anid"]).reset_index(drop=True)
	raw_data_test = raw_data_test.sort_values(by=["anid"]).reset_index(drop=True)

	return (raw_data_train, raw_data_test)

# Called by DropLateLectures
def getLectureNum(str):
	lecnum = 0

	# lecnum is below 10 (0 ~ 9)
	if (str[2:3] == "q"):
		lecnum = int(str[1:2])
	# lecnum is >= 10
	else:
		lecnum = int(str[1:3])

	return lecnum

# Called by DropLateLectures
def getLectureNum141(str):
	lecnum = int(str[1:3])
	return lecnum

# Called by DropLectures
def DropLateLectures(data, dropfromthislecture, course):
	drops = []

	for i in range(1, len(data.columns)):
		if (course == "cse141"):
			lectureNumber = getLectureNum141(data.columns[i])
		else:
			lectureNumber = getLectureNum(data.columns[i])

		# Prepare to drop
		if (lectureNumber >= dropfromthislecture):
			drops.append(data.columns[i])

	data = data.drop(columns=drops)

	return data

# Called by DropLectures
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
		else:                              # CSE 100 WI15 has only 19 lectures
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

# Called by prepdata.py
# Drop the lectures after the cutoff week
def DropLectures(data, dropWeek, course):
	# Determine from what lecture to drop
	dropLecture = fromWhatLecture(course, dropWeek)

	# Drop late lectures
	newData = DropLateLectures(data, dropLecture, course)

	return newData

# Called by convert_to_universal_qid
def ProcessClickerQData(pair, data, whichcolumn):
	new_name = []
	keep = []
	uname = list(pair[pair.columns[0]])

	for qname in range(data.shape[1]):
		orig_name = data.columns[qname]

		# The question has a corresponding pair with the other set
		if (orig_name in list(pair[pair.columns[whichcolumn]])):
			ind = list(pair[pair.columns[whichcolumn]]).index(orig_name)

			keep.append(orig_name)
			new_name.append(uname[ind])

	final_data = data[keep]
	final_data.columns = new_name
	return final_data

# Called by prepdata.py
# Convert any remaining question names to universal qid
def convert_to_universal_qid(pairinfo, train, test, course):
	trainclickerdata = train.drop(columns=[train.columns[0]])
	testclickerdata = test.drop(columns=[test.columns[0]])

	if (course == "cs1"):
		clickerqdata_train = ProcessClickerQData(pairinfo, trainclickerdata, 1)
		clickerqdata_test = ProcessClickerQData(pairinfo, testclickerdata, 2)
	elif (course == "cse8a"):
		clickerqdata_train = trainclickerdata
		clickerqdata_test = ProcessClickerQData(pairinfo, testclickerdata, 3)
	elif (course == "cse12"):
		clickerqdata_train = ProcessClickerQData(pairinfo, trainclickerdata, 1)
		clickerqdata_test = ProcessClickerQData(pairinfo, testclickerdata, 2)
	elif (course == "cse100"):
		clickerqdata_train = ProcessClickerQData(pairinfo, trainclickerdata, 1)
		clickerqdata_test = ProcessClickerQData(pairinfo, testclickerdata, 2)
	elif (course == "cse141"):
		####################
		## usefa14:
		## TRUE: train-fa14, test-fa15
		## FALSE: train-fa15, test-fa16
		####################
		usefa14 = False

		if (usefa14):
			clickerqdata_train = trainclickerdata
			clickerqdata_test = ProcessClickerQData(pairinfo, testclickerdata, 3)
		else:
			clickerqdata_train = ProcessClickerQData(pairinfo, trainclickerdata, 3)
			clickerqdata_test = ProcessClickerQData(pairinfo, testclickerdata, 4)

	tempDf = pd.DataFrame(data={"anid": train["anid"]})
	train_result = pd.concat([tempDf, clickerqdata_train], axis=1)

	tempDf = pd.DataFrame(data={"anid": test["anid"]})
	test_result = pd.concat([tempDf, clickerqdata_test], axis=1)

	return (train_result, test_result)

# Called by prepdata.py
def do_fill_NAs_to_6(data):
	return data.fillna(6)

# Called by prepdata.py
def convert_responses_to_correctness(data, pair):
	for i in range(data.shape[1]):
		qname = data.columns[i]
		qrownum = list(pair["qid"]).index(qname)
		cans = pair["cans"][qrownum]
		resp = list(data[data.columns[i]])

		# Make sure cans is a list
		if (cans >= 10):
			cans = [int(d) for d in str(cans)]
		else:
			cans = [cans]

		correctness = []
		for r in range(len(resp)):
			raw_resp = resp[r]

			if (raw_resp in cans):
				correctness.append(1)
			elif (raw_resp == 6):
				correctness.append(0)
			else:
				correctness.append(-1)

		data = data.assign(**{data.columns[i]: correctness})

	return data

def change_columnnames(df):
	new_names = []

	for i in range(df.shape[1]):
		new_names.append(df.columns[i] + "_c")

	df.columns = new_names
	return df

def convert_responses_to_correctness_train_test(course, train, test, pair):
	trainclickerdata = train.drop(columns=[train.columns[0]])
	testclickerdata = test.drop(columns=[test.columns[0]])

	if (course != "cse100"):
		scaled_data_train_correctness = convert_responses_to_correctness(trainclickerdata, pair)
		scaled_data_test_correctness = convert_responses_to_correctness(testclickerdata, pair)
	# cse100 has two correctness columns for each term
	else:
		# Generate separate paired_qs for each term of cse100
		pair_train = pair.drop(columns=["cans_WI15"])
		pair_test = pair.drop(columns=["cans_FA13"])

		pair_train = pair_train.rename(columns={pair_train.columns[pair_train.shape[1]-1]: "cans"})
		pair_test = pair_test.rename(columns={pair_test.columns[pair_test.shape[1]-1]: "cans"})

		# Generate correctness columns for cse100
		scaled_data_train_correctness = convert_responses_to_correctness(trainclickerdata, pair_train)
		scaled_data_test_correctness = convert_responses_to_correctness(testclickerdata, pair_test)

	# Each clicker question will have QNAME_c columns to represent students' correctness
	scaled_data_train_correctness = change_columnnames(scaled_data_train_correctness)
	scaled_data_test_correctness = change_columnnames(scaled_data_test_correctness)

	tempDf = pd.DataFrame(data={"anid": train[train.columns[0]]})
	train_results = pd.concat([tempDf, scaled_data_train_correctness], axis=1)

	tempDf = pd.DataFrame(data={"anid": test[test.columns[0]]})
	test_results = pd.concat([tempDf, scaled_data_test_correctness], axis=1)

	return (train_results, test_results)

# Called by prepdata.py
def scale_correctness(train, test):
	start = 1
	if (train.columns[start] == "exam_total"):
		start = 2

	for i in range(start, train.shape[1]):
		qname = train.columns[i]
		total_correctness = list(train[train.columns[i]])

		if (qname in list(test.columns)):
			total_correctness = total_correctness + list(test[qname])
		scaled_total_correctness = scale(total_correctness)

		if (qname in list(test.columns)):
			scaled_train_correctness = scaled_total_correctness[:train.shape[0]]
			scaled_test_correctness = scaled_total_correctness[train.shape[0]:]

			train = train.assign(**{train.columns[i]: scaled_train_correctness})
			test = test.assign(**{qname: scaled_test_correctness})
		else:
			train = train.assign(**{train.columns[i]: scaled_total_correctness})

	return (train, test)

# Called by prepdata.py
# For each student, merge all clickers to one column (average value)
def merge_correctness(train, test):
	# New column name changed to merged_clicker for convenience
	tempDf = pd.DataFrame(data={"anid": train[train.columns[0]]})
	train = train.drop(columns=[train.columns[0]])
	train_clicker = tempDf.assign(merged_clicker=train.mean(axis=1))

	tempDf = pd.DataFrame(data={"anid": test[test.columns[0]]})
	test = test.drop(columns=[test.columns[0]])
	test_clicker = tempDf.assign(merged_clicker=test.mean(axis=1))

	return (train_clicker, test_clicker)

# Called by merge_correctness_by_correctratio
# Calculate the correct percentage
def correctratio(x):
	correct = list(x).count(1)
	incorrect = list(x).count(-1)

	ratio = None
	if (correct != 0 or incorrect != 0):
		ratio = correct / (correct + incorrect)

	return ratio

# Called by prepdata.py
# The correct ratio of each row
def merge_correctness_by_correctratio(train, test):
	tempDf = pd.DataFrame(data={"anid": train[train.columns[0]]})
	train = train.drop(columns=[train.columns[0]])
	train_clicker = train.apply(correctratio, axis=1)
	train_clicker = train_clicker.fillna(train_clicker.mean())
	train_clicker = tempDf.assign(train_clicker=train_clicker)

	tempDf = pd.DataFrame(data={"anid": test[test.columns[0]]})
	test = test.drop(columns=[test.columns[0]])
	test_clicker = test.apply(correctratio, axis=1)
	test_clicker = test_clicker.fillna(test_clicker.mean())
	test_clicker = tempDf.assign(test_clicker=test_clicker)

	return (train_clicker, test_clicker)

#
# Haven't tested, doesn't work yet
#
def add_lecture_number(course, pair):
	testsetcolumn = 0
	lecture = []

	if (course == "cs1"):
		testsetcolumn = 2
	elif (course == "cse8a"):
		testsetcolumn = 3
	elif (course == "cse12"):
		testsetcolumn = 2
	elif (course == "cse100"):
		testsetcolumn = 2
	elif (course == "cse141"):
		# FA14-15
		testsetcolumn <- 3
		
		# FA15-16
		#testsetcolumn <- 4

	if (course == "cse141"):
		lecture = list(pair[pair.columns[testsetcolumn]].apply(getLectureNum141))
	else:
		lecture = list(pair[pair.columns[testsetcolumn]].apply(getLectureNum))

	return pair.assign(lecture=lecture)

#
# Haven't tested, doesn't work yey
#
def merge_perweek_correctness(course, uptowhatweek, pair, train, test):
	train_clicker = pd.DataFrame(index=range(train.shape[0]), columns=range(1, uptowhatweek+1))
	test_clicker = pd.DataFrame(index=range(test.shape[0]), columns=range(1, uptowhatweek+1))

	pair = add_lecture_number(course, pair)

	print(train_clicker)
	lec = 0
	prevw_lec = 1
	new_names = []

	for w in range(1, uptowhatweek+1):
		new_names.append("w" + str(w) + "clicker")

		lec = fromWhatLecture(course, w) - 1
		print("week " + str(w) + ": from " + str(prevw_lec) + " ~ " + str(lec))
		targets = [list(pair["lecture"]).index(lecture) for lecture in list(pair["lecture"]) if lecture <= lec and lecture >= prevw_lec]
		print(targets)
		questions = [pair["qid"][index] for index in targets]
		qs_of_the_week = [str(q)+"_c" for q in questions]

		train_of_the_week = train.filter(items=[name for name in train.columns if name in qs_of_the_week])
		test_of_the_week = test.filter(items=[name for name in test.columns if name in qs_of_the_week])

		if (len(targets) > 1):
			train_clicker.assign(**{str(train_clicker.columns[w]): train_of_the_week.apply(np.sum, axis=1)})
			test_clicker.assign(**{str(train_clicker.columns[w]): test_of_the_week.apply(np.sum, axis=1)})
		else:
			train_clicker.assign(**{str(train_clicker.columns[w]): train_of_the_week})
			test_clicker.assign(**{str(train_clicker.columns[w]): test_of_the_week})

		prevw_lec = lec + 1

	train_clicker.columns = new_names
	test_clicker.columns = new_names

	tempDf = pd.DataFrame(data={train.columns[0]: train[train.columns[0]]})
	train_clicker = pd.concat([tempDf, train_clicker], axis=1)

	tempDf = pd.DataFrame(data={test.columns[0]: test[test.columns[0]]})
	test_clicker = pd.concat([tempDf, test_clicker], axis=1)

	return (train_clicker, test_clicker)

def factorize_responses(train, test):
	for i in range(1, train.shape[1]):
		raw_cat = pd.Categorical(train[train.columns[i]], categories=[1,2,3,4,5,6], ordered=True)
		train[train.columns[i]] = pd.Series(raw_cat)

		raw_cat = pd.Categorical(test[test.columns[i]], categories=[1,2,3,4,5,6], ordered=True)
		test[test.columns[i]] = pd.Series(raw_cat)

	return (train, test)