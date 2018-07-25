import argparse
import pandas as pd
import functions_prepdata_final as prepFinal
import functions_prepdata_prereq as prepPrerec
import functions_prepdata_midterm as prepMidterm
import functions_prepdata_clicker as prepClicker

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
	prereq = prepPrerec.load_prereq(course, mergeorkeep)

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
	# 2 - it merges the clicker responses per week
	correctness_scaling = 1

	if (correctness_scaling == 0):
		# Scale correctness properly with both trainset and testset
		(correctness_train, correctness_test) = prepClicker.scale_correctness(correctness_train, correctness_test)
	elif (correctness_scaling == 1):
		# Adds up the clicker correctness 1 + 1 + 0 + (-1) + ... and generate one column
		(correctness_train, correctness_test) = prepClicker.merge_correctness(correctness_train, correctness_test)
	else:
		# Adds up the clicker responses within each week and generate per-week column
		(correctness_train, correctness_test) = prepClicker.merge_perweek_correctness(course, cutoffweek, paired_qs, correctness_train, correctness_test)
		





































# TODO
# Change quiz files readingq1w1 for q!!!!!!