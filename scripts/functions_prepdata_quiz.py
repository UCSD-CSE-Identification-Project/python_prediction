import pandas as pd
import numpy as np

# Called by load_quiz
def do_fill_NAs_to_average(data):
	mean = data.mean(axis=0)
	data = data.fillna(mean)
	return data

# Called by load_quiz
def do_fill_0s_to_average(data):
	mean_pairs = {}
	mean = data.mean(axis=0)

	# Push pairs into the dictionary
	for i in range(data.shape[1]):
		mean_pairs[data.columns[i]] = mean[i]

	data = data.replace(0, mean_pairs)
	return data

# Called by load_quiz
def divide_by_max(data):
	maxVals = data.max(axis=0)
	return data.divide(maxVals)	

# Called by load_quiz
# Based on quiz names, filter out the unwanted ones
def filter_quiz(column_names, uptowhatweek):
	names = []

	for quiz in column_names:
		if ("w" in quiz and "review" not in quiz and "avg_week" not in quiz):
			week = int(quiz[(quiz.index("w")+1):])

			if (week <= uptowhatweek):
				names.append(quiz)

	return names

# Called by prepdata.py
def load_quiz(course, uptowhatweek):
	# Up to which week do we want to include quiz data?
	# else only data up to week4 is included. Including data up to future weeks is not supported
	if (course == "cs1"):
		# Add trainset quiz data; Quiz data is only up to week 5
		quiz_train = pd.read_csv("../data/cs1/quiz_FA13.csv", na_values=["<NA>"])
		# Include anid, and quizzes up to that week
		# And the quiz names are all based on quiz names in the test set(FA14)

		# anid and late quiz are filtered out
		tempDf = pd.DataFrame(data={quiz_train.columns[0]: quiz_train[quiz_train.columns[0]]})
		quiz_train = quiz_train.filter(items=filter_quiz(quiz_train.columns, uptowhatweek))
		quiz_train = do_fill_NAs_to_average(quiz_train)
		quiz_train = divide_by_max(quiz_train)

		#mergedquiz = quiz_train.apply(np.sum, axis=1)
		mergedquiz = quiz_train.mean(axis=1)

		quiz_train = pd.concat([tempDf, mergedquiz], axis=1)
		quiz_train = quiz_train.rename(columns={0: "mergedquiz"})

		# Add testset quiz data
		quiz_test = pd.read_csv("../data/cs1/quiz_FA14.csv", na_values=["<NA>"])
		tempDf = pd.DataFrame(data={quiz_test.columns[0]: quiz_test[quiz_test.columns[0]]})
		quiz_test = quiz_test.filter(items=filter_quiz(quiz_test.columns, uptowhatweek))
		quiz_test = do_fill_NAs_to_average(quiz_test)
		quiz_test = divide_by_max(quiz_test)

		#mergedquiz = quiz_test.apply(np.sum, axis=1)
		mergedquiz = quiz_test.mean(axis=1)
		quiz_test = pd.concat([tempDf, mergedquiz], axis=1)
		quiz_test = quiz_test.rename(columns={0: "mergedquiz"})
	elif (course == "cse8a"):
		# Add trainset quiz data; Quiz data is only up to week 7
		quiz_train = pd.read_csv("../data/cse8a/quiz_FA14.csv", na_values=["<NA>"])
		# Second midterm is at week 7
		tempDf = pd.DataFrame(data={quiz_train.columns[0]: quiz_train[quiz_train.columns[0]]})
		quiz_train = quiz_train.filter(items=filter_quiz(quiz_train.columns, uptowhatweek))
		quiz_train = do_fill_NAs_to_average(quiz_train)
		quiz_train = divide_by_max(quiz_train)

		#mergedquiz = quiz_train.apply(np.sum, axis=1)
		mergedquiz = quiz_train.mean(axis=1)
		quiz_train = pd.concat([tempDf, mergedquiz], axis=1)
		quiz_train = quiz_train.rename(columns={0: "mergedquiz"})

		# Add testset quiz data; Quiz data is only up to week 8?
		quiz_test = pd.read_csv("../data/cse8a/quiz_FA15.csv", na_values=["<NA>"])
		# Second midterm is at week 8
		tempDf = pd.DataFrame(data={quiz_test.columns[0]: quiz_test[quiz_test.columns[0]]})
		quiz_test = quiz_test.filter(items=filter_quiz(quiz_test.columns, uptowhatweek))
		quiz_test = do_fill_0s_to_average(quiz_test)
		quiz_test = divide_by_max(quiz_test)

		#mergedquiz = quiz_test.apply(np.sum, axis=1)
		mergedquiz = quiz_test.mean(axis=1)
		quiz_test = pd.concat([tempDf, mergedquiz], axis=1)
		quiz_test = quiz_test.rename(columns={0: "mergedquiz"})
	elif (course == "cse12"):
		# Add trainset quiz data
		quiz_train = pd.read_csv("../data/cse12/quiz_SP14.csv", na_values=["<NA>"])
		# Remove "PID" column from quiz data
		quiz_train = quiz_train.drop(columns=[quiz_train.columns[0]])

		tempDf = pd.DataFrame(data={quiz_train.columns[0]: quiz_train[quiz_train.columns[0]]})
		quiz_train = quiz_train.filter(items=filter_quiz(quiz_train.columns, uptowhatweek))
		quiz_train = do_fill_0s_to_average(quiz_train)

		#mergedquiz = quiz_train.apply(np.sum, axis=1)
		mergedquiz = quiz_train.mean(axis=1)
		quiz_train = pd.concat([tempDf, mergedquiz], axis=1)
		quiz_train = quiz_train.rename(columns={0: "mergedquiz"})

		# Add testset quiz data
		quiz_test = pd.read_csv("../data/cse12/quiz_SP15.csv", na_values=["<NA>"])
		# Remove "PID" column from quiz data
		quiz_test = quiz_test.drop(columns=[quiz_test.columns[0]])

		tempDf = pd.DataFrame(data={quiz_test.columns[0]: quiz_test[quiz_test.columns[0]]})
		quiz_test = quiz_test.filter(items=filter_quiz(quiz_test.columns, uptowhatweek))
		quiz_test = do_fill_0s_to_average(quiz_test)

		#mergedquiz = quiz_test.apply(np.sum, axis=1)
		mergedquiz = quiz_test.mean(axis=1)
		quiz_test = pd.concat([tempDf, mergedquiz], axis=1)
		quiz_test = quiz_test.rename(columns={0: "mergedquiz"})
	elif (course == "cse100"):
		# Add trainset quiz data
		quiz_train = pd.read_csv("../data/cse100/quiz_FA13.csv", na_values=["<NA>"])
		# Remove "PID" column from quiz data
		quiz_train = quiz_train.drop(columns=[quiz_train.columns[0]])

		tempDf = pd.DataFrame(data={quiz_train.columns[0]: quiz_train[quiz_train.columns[0]]})
		quiz_train = quiz_train.filter(items=filter_quiz(quiz_train.columns, uptowhatweek))
		quiz_train = do_fill_0s_to_average(quiz_train)

		#mergedquiz = quiz_train.apply(np.sum, axis=1)
		mergedquiz = quiz_train.mean(axis=1)
		quiz_train = pd.concat([tempDf, mergedquiz], axis=1)
		quiz_train = quiz_train.rename(columns={0: "mergedquiz"})

		# Add testset quiz data
		quiz_test = pd.read_csv("../data/cse100/quiz_WI15.csv", na_values=["<NA>"])
		# Remove "PID" column from quiz data
		quiz_test = quiz_test.drop(columns=[quiz_test.columns[0]])

		tempDf = pd.DataFrame(data={quiz_test.columns[0]: quiz_test[quiz_test.columns[0]]})
		quiz_test = quiz_test.filter(items=filter_quiz(quiz_test.columns, uptowhatweek))
		quiz_test = do_fill_0s_to_average(quiz_test)

		#mergedquiz = quiz_test.apply(np.sum, axis=1)
		mergedquiz = quiz_test.mean(axis=1)
		quiz_test = pd.concat([tempDf, mergedquiz], axis=1)
		quiz_test = quiz_test.rename(columns={0: "mergedquiz"})
	elif (course == "cse141"):
		####################################
		## usefa14
		## TRUE: train-FA14 and test-FA15
		## FALSE: train-FA15 and test-FA16
		####################################
		usefa14 = False

		if (usefa14):
			# Add trainset quiz data
			quiz_train1 = pd.read_csv("../data/cse141/quizall_FA14a.csv", na_values=["<NA>"])
			quiz_train2 = pd.read_csv("../data/cse141/quizall_FA14b.csv", na_values=["<NA>"])
			quiz_train = pd.concat([quiz_train1, quiz_train2], ignore_index=True)

			# Remove "name" column from quiz data
			quiz_train = quiz_train.drop(columns=[quiz_train.columns[0]])

			tempDf = pd.DataFrame(data={quiz_train.columns[0]: quiz_train[quiz_train.columns[0]]})

			# Remove "anid" column from quiz data
			quiz_train = quiz_train.drop(columns=[quiz_train.columns[0]])
			quiz_train = do_fill_NAs_to_average(quiz_train)
			quiz_train = divide_by_max(quiz_train)

			#mergedquiz = quiz_train.apply(np.sum, axis=1)
			mergedquiz = quiz_train.mean(axis=1)
			quiz_train = pd.concat([tempDf, mergedquiz], axis=1)
			quiz_train = quiz_train.rename(columns={0: "mergedquiz"})

			# Add testset quiz data
			quiz_test = pd.read_csv("../data/cse141/quizall_FA15.csv", na_values=["<NA>"])

			# Will only have 5 quizzes up to week 3
			tempDf = pd.DataFrame(data={quiz_test.columns[1]: quiz_test[quiz_test.columns[1]]})
			quizzes = [quiz_test.columns[3], quiz_test.columns[8], quiz_test.columns[13], quiz_test.columns[18], quiz_test.columns[23]]
			quiz_test = quiz_test.filter(items=quizzes)
			quiz_test = do_fill_NAs_to_average(quiz_test)

			#mergedquiz = quiz_test.apply(np.sum, axis=1)
			mergedquiz = quiz_test.mean(axis=1)
			quiz_test = pd.concat([tempDf, mergedquiz], axis=1)
			quiz_test = quiz_test.rename(columns={0: "mergedquiz"})
		else:
			# Add trainset quiz data
			quiz_train = pd.read_csv("../data/cse141/quizall_FA15.csv", na_values=["<NA>"])

			# Will only have 5 quizzes up to week 3
			tempDf = pd.DataFrame(data={quiz_train.columns[1]: quiz_train[quiz_train.columns[1]]})
			quizzes = [quiz_train.columns[3], quiz_train.columns[8], quiz_train.columns[13], quiz_train.columns[18], quiz_train.columns[23]]
			quiz_train = quiz_train.filter(items=quizzes)
			quiz_train = do_fill_NAs_to_average(quiz_train)

			#mergedquiz = quiz_train.apply(np.sum, axis=1)
			mergedquiz = quiz_train.mean(axis=1)
			quiz_train = pd.concat([tempDf, mergedquiz], axis=1)
			quiz_train = quiz_train.rename(columns={0: "mergedquiz"})

			# Add testset quiz data
			quiz_test = pd.read_csv("../data/cse141/quizall_FA16.csv", na_values=["<NA>"])

			# Will only have 5 quizzes up to week 3
			tempDf = pd.DataFrame(data={quiz_test.columns[1]: quiz_test[quiz_test.columns[1]]})
			quizzes = [quiz_test.columns[3], quiz_test.columns[8], quiz_test.columns[13], quiz_test.columns[18], quiz_test.columns[23]]
			quiz_test = quiz_test.filter(items=quizzes)
			quiz_test = do_fill_NAs_to_average(quiz_test)

			#mergedquiz = quiz_test.apply(np.sum, axis=1)
			mergedquiz = quiz_test.mean(axis=1)
			quiz_test = pd.concat([tempDf, mergedquiz], axis=1)
			quiz_test = quiz_test.rename(columns={0: "mergedquiz"})

	return (quiz_train, quiz_test)