import argparse
import pandas as pd
import pickle
import functions_test as funcTest

# Parse command line arguments, run python3 script with -h for more information
parser = argparse.ArgumentParser(description="Start the testing process")
parser.add_argument("course", choices=["cs1", "cse8a", "cse12", "cse100", "cse141"], help="choose one from: cs1, cse8a, cse12, cse100, cse141 to train")
args = parser.parse_args()

# Get the arguments
course = args.course

#
# set.seed(1)
#

# Load image
with open("../results/" + course + "/TrainedModel.out", "rb") as inFile:
	(datasource, modelparameter, model, tune, test_data, trainedmodel) = pickle.load(inFile)


train_failing_percentage = 40 # failing_percentage
exam_scores = 0 # exam_scores.test NEED TO FIX IT!

results = None

##BUG: Inconsistent 2nd parameter to predict()##
if (model == 0):
	# "response" option for glm (i.e. logit) returns the probability value, not the 0/1 response.
	# That's why you need a designated AnalyzeError function for logit (i.e. AnalyzeError_logitonly)
	# AnalyzeError_logitonly assumes your probability threshold is 0.5
	pf = trainedmodel.predict(test_data.drop(columns=["exam_total"]))
	results = funcTest.AnalyzeError_logitonly(pf, test_data["exam_total"])

	# If you want to use ROC curve, this generates ROC curve and determines the best probability threshold
