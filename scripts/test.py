import argparse
import pandas as pd
import pickle
import functions_train as funcTrain
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
	roc = 1
	# "response" option for glm (i.e. logit) returns the probability value, not the 0/1 response.
	# That's why you need a designated AnalyzeError function for logit (i.e. AnalyzeError_logitonly)
	# AnalyzeError_logitonly assumes your probability threshold is 0.5
	pf = trainedmodel.predict(test_data.drop(columns=["anid", "exam_total"]))
	if (roc == 0):
		results = funcTest.AnalyzeError_logitonly(pf, test_data["exam_total"])
	elif (roc == 1):
		# If you want to use ROC curve, this generates ROC curve and determines the best probability threshold
		ROCresults = funcTest.DrawROCCurve(course, test_data["exam_total"], pf)
		results = funcTest.AnalyzeError(pf, test_data["exam_total"], ROCresults["bestthreshold"])
elif (model == 1 or model == 3):
	if (tune == 0 or tune == 2 or tune == 3):
		# 0 - classweight only, 2 - sigma, C, classweight
		pf = trainedmodel.predict(test_data.drop(columns=["anid", "exam_total"]))
		results = funcTrain.AnalyzeErrorResp(pf, test_data["exam_total"])
		pf_prob = trainedmodel.predict_proba(test_data.drop(columns=["anid", "exam_total"]))

		# Write to csv file
		funcTest.AnalyzeConfidence(course, test_data["exam_total"], results["total"], pf, pf_prob)

		#
		# Haven't tested
		#
		ROCresults = funcTest.DrawROCCurve(course, test_data["exam_total"], pf_prob)
		resuls = funcTest.AnalyzeError(pf_prob, test_data["exam_total"], ROCresults["bestthreshold"])
	elif (tune == 1):
		# 1 - classweight + probability threshold
		pf = trainedmodel.predict_proba(test_data.drop(columns=["anid", "exam_total"]))
		#results = funcTest.AnalyzeError(!!!!)
elif (model == 2):
	# rf
	pass

print(" ########## Modeling Summary ##########")
print("pass/fail cutoff is bottom: " + str(train_failing_percentage) + " %")

print(results)
print("Failing student = 1, Succeeding student = 0")

sum = results["fp"] + results["fn"] + results["tp"] + results["tn"]
#print (c(round(100*results$tp/sum,1), round(100*results$tn/sum,1), round(100*results$fp/sum,1), round(100*results$fn/sum,1)))

