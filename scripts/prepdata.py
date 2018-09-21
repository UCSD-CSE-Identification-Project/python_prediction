import argparse
import pandas as pd
import functions_prepdata_final as prepFinal
import functions_prepdata_prereq as prepPrereq
import functions_prepdata_midterm as prepMidterm
import functions_prepdata_clicker as prepClicker
import functions_prepdata_quiz as prepQuiz
import functions_prepdata_assignment as prepAssign
from sklearn.preprocessing import scale
import pickle

# Parse command line arguments, run python3 script with -h for more information
parser = argparse.ArgumentParser(description="Preprocess student data based on user input")
parser.add_argument("course", choices=["cs1", "cse8a", "cse12", "cse100", "cse141"], help="choose one from: cs1, cse8a, cse12, cse100, cse141 to prep data")
parser.add_argument("cutoffweek", type=int, help="up to which week will be in the testset (cs1 can model up to weeks 3-12, all other courses can model up to weeks 3-10)")
parser.add_argument("components", help="combination of course components to model with, at least 1 component, at most all 4 components: c (clicker), m (midterm), p (prereq), q (quiz)")
args = parser.parse_args()

# Get the arguments
course = args.course
cutoffweek = args.cutoffweek

elements = []
for option in args.components:
	elements += option

scaled_data_train = None
scaled_data_test = None

def normalize_data(data):
	for i in range(2, data.shape[1]):
		# TODO scale
		# data = data.assign(exam_total=scale(data["exam_total"]))

		return

# Loading Final Exam Data
print("**** Final Exam... ****")
# Obtain train and test sets as a tuple
final = prepFinal.load_final(course)
scaled_data_train = final[0]
scaled_data_test = final[1]

# Loading Prereq Data (DEFAULT, MERGE)
if ("p" in elements):
	print("**** Prerequisite... ****")
	mergeorkeep = "merge"
	prereq = prepPrereq.load_prereq(course, mergeorkeep)

	if prereq[0] is not None:
		scaled_data_train = scaled_data_train.merge(prereq[0], how="outer")
		scaled_data_test = scaled_data_test.merge(prereq[1], how="outer")

# Loading Midterm Data
if ("m" in elements):
	print("**** Midterm... so you are adding the other data you chose up to the midterm week ****")
	# Default to only use the first midterm if there are 2 midterms
	usefirstmiderm = 1

	cutoffweek = prepMidterm.reset_cutoffweek(course)
	midterm = prepMidterm.load_midterm(course, usefirstmiderm)

	scaled_data_train = scaled_data_train.merge(midterm[0], how="outer")
	scaled_data_test = scaled_data_test.merge(midterm[1], how="outer")

# Loading Clicker Data
if ("c" in elements):
	print("**** Clicker... ****")
	# Import paired data
	paired_qs = prepClicker.pair_data(course)

	# Load and filter clicker questions
	# Output has student clicker responses and the student responses are sorted by anid
	(raw_data_train, raw_data_test) = prepClicker.load_filter_questions(course, paired_qs)

	# Drop lectures in testset after specified week
	raw_data_test = prepClicker.DropLectures(raw_data_test, cutoffweek, course)

	# Convert qnames to universal qids
	(raw_data_train, raw_data_test) = prepClicker.convert_to_universal_qid(paired_qs, raw_data_train, raw_data_test, course)

	# Fill in missing responses
	raw_data_train = prepClicker.do_fill_NAs_to_6(raw_data_train)
	raw_data_test = prepClicker.do_fill_NAs_to_6(raw_data_test)

	# Remove questions that the other one doesn't have
	train_qs = [name for name in raw_data_train.columns if name in raw_data_test.columns]
	raw_data_train = raw_data_train[train_qs]

	test_qs = [name for name in raw_data_test.columns if name in raw_data_train.columns]
	raw_data_test = raw_data_test[test_qs]

	# Generate correctness columns for each clicker question; Also change column names to "qX_c"
	(correctness_train, correctness_test) = prepClicker.convert_responses_to_correctness_train_test(course, raw_data_train, raw_data_test, paired_qs)


	# correctness_scaling: 
	# 0 - it scales correctness
	# 1 - it simply adds up the clicker responses
	# 2 - it calculates correct/total responses
	# 3 - it merges the clicker responses per week
	correctness_scaling = 2#1

	if (correctness_scaling == 0):
		# Scale correctness properly with both trainset and testset
		(correctness_train, correctness_test) = prepClicker.scale_correctness(correctness_train, correctness_test)
	elif (correctness_scaling == 1):
		# Adds up the clicker correctness 1 + 1 + 0 + (-1) + ... and generate one column
		(correctness_train, correctness_test) = prepClicker.merge_correctness(correctness_train, correctness_test)
	elif (correctness_scaling == 2):
		# Calculates correct/total and generate one column
		(correctness_train, correctness_test) = prepClicker.merge_correctness_by_correctratio(correctness_train, correctness_test)
	else:
		# Adds up the clicker responses within each week and generate per-week column
		(correctness_train, correctness_test) = prepClicker.merge_perweek_correctness(course, cutoffweek, paired_qs, correctness_train, correctness_test)

	# factorize the clicker responses	
	(factored_train, factored_test) = prepClicker.factorize_responses(raw_data_train, raw_data_test)

	# add_correctness:0 clicker responses only / 
	#				  1 clicker correctness+responses / 
	#				  2 clicker correctness only
	add_correctness = 2

	if (add_correctness == 1):
		# Add correctness+responses to scaled_data
		clicker_train = pd.concat([final[0], correctness_train.drop(columns=[correctness_train.columns[0]]), factored_train.drop(columns=[factored_train.columns[0]])], axis=1)
		clicker_test = pd.concat([final[1], correctness_test.drop(columns=[correctness_test.columns[0]]), factored_test.drop(columns=[factored_test.columns[0]])], axis=1)
	elif (add_correctness == 0):
		# Add responses only to scaled_data
		clicker_train = pd.concat([final[0], factored_train.drop(columns=[factored_train.columns[0]])], axis=1)
		clicker_test = pd.concat([final[1], factored_test.drop(columns=[factored_test.columns[0]])], axis=1)
	else:
		# Add correctness only to scaled_data
		clicker_train = pd.concat([final[0], correctness_train.drop(columns=[correctness_train.columns[0]])], axis=1)
		clicker_test = pd.concat([final[1], correctness_test.drop(columns=[correctness_test.columns[0]])], axis=1)

		if (correctness_scaling == 1):
			clicker_train = clicker_train.rename(columns={clicker_train.columns[2]: "clicker"})
			clicker_test = clicker_test.rename(columns={clicker_test.columns[2]: "clicker"})

	# Exceptions ignored when add_correctness == 0 or 1
	scaled_data_train = scaled_data_train.merge(clicker_train, how="outer")
	scaled_data_test = scaled_data_test.merge(clicker_test, how="outer")

	# This has no exceptions, but will keep the duplicate columns
	#scaled_data_train = pd.concat([scaled_data_train, clicker_train], axis=1)
	#scaled_data_test = pd.concat([scaled_data_test, clicker_test], axis=1)

# Append quiz data
if ("q" in elements):
	print("**** Reading Quiz... ****")

	quiz = prepQuiz.load_quiz(course, cutoffweek)

	scaled_data_train = scaled_data_train.merge(quiz[0], how="outer")
	scaled_data_test = scaled_data_test.merge(quiz[1], how="outer")

# Not using R code
dynamic_option = 0
#if((course == "cs1" or course == "cse141") and (dynamic_option != 0)):
	#scaled.data.dynamic = append_dynamic_data(args[1], scaled.data.train, scaled.data.test, dynamic_option)
	#scaled.data.train = scaled.data.dynamic$train
	#scaled.data.test = scaled.data.dynamic$test

print("trainset columns: ")
print(scaled_data_train.columns)

print("testset columns: ")
print(scaled_data_test.columns)

# Already sorted by anid

# Save the image
with open("../results/" + course + "/PreppedData_train_and_test.out", "wb") as outFile:
	pickle.dump([scaled_data_train, scaled_data_test, args.components], outFile)