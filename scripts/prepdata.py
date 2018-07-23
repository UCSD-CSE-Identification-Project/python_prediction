import argparse
import functions_prepdata_final as prepFinal
import functions_prepdata_prereq as prepPrerec

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















# TODO
# Change quiz files readingq1w1 for q!!!!!!