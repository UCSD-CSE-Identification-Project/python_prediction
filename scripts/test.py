import argparse
import pandas as pd
import math
import pickle
import functions_train as funcTrain
import functions_test as funcTest
from pathlib import Path

# Parse command line arguments, run python3 script with -h for more information
parser = argparse.ArgumentParser(description="Start the testing process")
parser.add_argument("course", choices=["cs1", "cse8a", "cse12", "cse100", "cse141"], help="choose one from: cs1, cse8a, cse12, cse100, cse141 to test")
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

if (model == 0):
	roc = 1
	#
	# TODO: resolve the comment
	#
	# "response" option for glm (i.e. logit) returns the probability value, not the 0/1 response.
	# That's why you need a designated AnalyzeError function for logit (i.e. AnalyzeError_logitonly)
	# AnalyzeError_logitonly assumes your probability threshold is 0.5
	pf = trainedmodel.predict(test_data.drop(columns=["anid", "exam_total"]))
	if (roc == 0):
		results = funcTest.AnalyzeError_logitonly(pf, test_data["exam_total"])
	elif (roc == 1):
		# If you want to use ROC curve, this generates ROC curve and determines the best probability threshold
		#ROCresults = funcTest.DrawROCCurve(course, test_data["exam_total"], pf)
		ROCresults = funcTest.DrawbasicROCCurve(course, test_data["exam_total"], pf)
		results = funcTest.AnalyzeError(pf, test_data["exam_total"], ROCresults["bestthreshold"])
elif (model == 1 or model == 3):
	if (tune == 0 or tune == 2 or tune == 3):
		# 0 - classweight only, 2 - sigma, C, classweight
		pf = trainedmodel.predict(test_data.drop(columns=["anid", "exam_total"]))
		results = funcTrain.AnalyzeErrorResp(pf, test_data["exam_total"])
		pf_prob = trainedmodel.predict_proba(test_data.drop(columns=["anid", "exam_total"]))

		print(pf_prob)
		# Write to csv file
		funcTest.AnalyzeConfidence(course, test_data["exam_total"], results["total"], pf, pf_prob)
		#???????????????
		ROCresults = funcTest.DrawROCCurve(course, test_data["exam_total"], [pair[1] for pair in pf_prob])
		resuls = funcTest.AnalyzeError([pair[1] for pair in pf_prob], test_data["exam_total"], ROCresults["bestthreshold"])
	elif (tune == 1):
		pass
		# 1 - classweight + probability threshold
		#pf = trainedmodel.predict_proba(test_data.drop(columns=["anid", "exam_total"]))
		#resuls = funcTest.AnalyzeError([pair[0] for pair in pf_prob], test_data["exam_total"], probth)
elif (model == 2):
	# rf
	pass

print(" ########## Modeling Summary ##########")
print("pass/fail cutoff is bottom: " + str(train_failing_percentage) + " %")

print(results)
print("Failing student = 1, Succeeding student = 0")

Sum = results["fp"] + results["fn"] + results["tp"] + results["tn"]
print (round(100 * results["tp"]/Sum, 1), round(100 * results["tn"]/Sum, 1), round(100 * results["fp"]/Sum, 1), round(100 * results["fn"]/Sum, 1))

Acc = (results["tp"] + results["tn"]) / Sum
Expected_Acc = ((results["tp"] + results["fn"]) * (results["tp"] + results["fp"]) + 
                  (results["tn"] + results["fp"]) * (results["tn"] + results["fn"])) / Sum ** 2
kappa = (Acc - Expected_Acc) / (1 - Expected_Acc)
MCC = ((results["tp"] * results["tn"]) - (results["fp"] * results["fn"])) / math.sqrt((results["tp"] + results["fp"]) * (results["tp"] + results["fn"]) * (results["tn"] + results["fp"]) * (results["tn"] + results["fn"]))

Specificity = round(results["tn"] / (results["tn"] + results["fp"]) ,2)
NPV = round(results["tn"] / (results["tn"] + results["fn"]) ,2)
Sensitivity = round(results["tp"] / (results["tp"] + results["fn"]) ,2)
PPV = round(results["tp"] / (results["tp"] + results["fp"]) ,2)
F1_pos = (2 * PPV * Sensitivity) / (PPV + Sensitivity)

print("Accuracy: ", round(Acc, 4))
print("Specificity:", Specificity, "NPV: ", NPV, 
    "Sensitivity: ", round(results["tp"] / (results["tp"] + results["fn"]) ,2), "PPV: ", round(results["tp"] / (results["tp"] + results["fp"]) ,2))
print("F1-Negative score: ", round((2 * NPV * Specificity) / (NPV + Specificity), 2))
print("F1-Positive score: ", round(F1_pos, 2))

print("Weighted Accuracy: ", round(((results["tp"] + results["fn"]) * Sensitivity + (results["tn"] + results["fp"]) * Specificity) / Sum, 2))
print("MCC: ", round(MCC, 2))
print("Cohen's Kappa: ", round(kappa,2))

print(modelparameter)
print("AUC: ", ROCresults["auc"])
#print("AUC 95% CI: ", ROCresults["ci"])
print(round(100 * results["tp"] / Sum, 1), round(100 * results["fp"] / Sum, 1), round(100 * results["fn"] / Sum, 1), round(100 * results["tn"] / Sum, 1),
        round(100 * Acc, 2), PPV, Sensitivity, round(F1_pos, 2), round(kappa, 2),round(MCC, 2))

fname = "../results/" + str(course) + "/results_earlytolate.csv"
old_file = Path(fname)

if (old_file.is_file()):
	csvresults = pd.read_csv(fname, na_values=["<NA>"])
	newrow = pd.DataFrame({"option": datasource, "AUC": ROCresults["auc"], "Sensitivity": Sensitivity, "Specificity": Specificity, "Accuracy": round(Acc, 2), "FP": round(100*results["fp"]/Sum, 1), "FN": round(100*results["fn"]/Sum, 1)}, index=[0])
	csvresults = pd.concat([csvresults, newrow], axis=1)
else:
	csvresults = pd.DataFrame({"option": datasource, "AUC": ROCresults["auc"], "Sensitivity": Sensitivity, "Specificity": Specificity, "Accuracy": round(Acc, 2), "FP": round(100*results["fp"]/Sum, 1), "FN": round(100*results["fn"]/Sum, 1)}, index=[0])


csvresults.to_csv(fname)

# Save image
with open("../results/" + str(course) + "/week#.out", "wb") as outFile:
	pickle.dump([datasource, modelparameter, model, tune, test_data, trainedmodel], outFile)