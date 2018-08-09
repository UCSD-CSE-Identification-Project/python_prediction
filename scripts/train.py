import argparse
import pandas as pd
import statsmodels.api as sm
import math
from sklearn.svm import SVC
import pickle
import functions_train as funcTrain

# Parse command line arguments, run python3 script with -h for more information
parser = argparse.ArgumentParser(description="Start the training process based on user selected model")
parser.add_argument("course", choices=["cs1", "cse8a", "cse12", "cse100", "cse141"], help="choose one from: cs1, cse8a, cse12, cse100, cse141 to train")
parser.add_argument("model", type=int, choices=[0, 1, 2], help="0 - logit, 1 - svm-rbf, 2 - rf")
parser.add_argument("tunemethod", type=int, choices=[0, 1, 2, 3], help="0 - tune classweight, 1 - tune classweight and probability threshold, 2 - tune C/sigma/classweight")
args = parser.parse_args()

# Get the arguments
course = args.course
model = args.model
tunemethod = args.tunemethod

scaled_data_train = None
scaled_data_test = None

# Load image
with open("../results/" + course + "/PreppedData_train_and_test.out", "rb") as inFile:
	(scaled_data_train, scaled_data_test, datasource) = pickle.load(inFile) 

# Match with testset
names = [name for name in scaled_data_train.columns if name in scaled_data_test.columns]
if (scaled_data_train.columns[0] not in names):
	names = [scaled_data_train.columns[0]] + names
scaled_data_train = scaled_data_train.filter(items=names)

# variable (clicker question) importance
# when doing the regular SVM modeling, Soo recommends to comment the below method,
# because the final modeling results change due to sharing random number generator
# deactivated for now
# 	varimp_analysis(args[1], scaled.data.train[,-1], paired.qs)

# FOR CS1 var importance
#	readingq <- scaled.data.train[,c("exam_total", "readingq2","readingq3","readingq4","readingq5","readingq6","readingq7","readingq8")]
#	print (readingq)
#	varimp_analysis(args[1], readingq, paired.qs)

print("modeling method: 0 - logit, 1 - svm-rbf, 2 - rf")
print("We are using -", model)

parameter = None
# Drop anid column
trainset = scaled_data_train.drop(columns=[scaled_data_train.columns[0]])

if (model == 1):
	# No tunemethod 0 or 1
	if (tunemethod == 2):
		parameter = funcTrain.FindParameters(course, trainset)
	elif (tunemethod == 3):
		print("We are using pre-tuned modeling parameters... these values are valid only when the data is corr only, and up to any week")
		parameter_values = funcTrain.Obtain_PreTuned_Parameters(model)

		week4_respcorr_parameter = pd.DataFrame.from_dict({"cs1": parameter_values[0], "cse8a": parameter_values[1], "cse12": parameter_values[2], "cse100": parameter_values[3], "cse141": parameter_values[4]})
		week4_respcorr_parameter.index = ["C", "sigma", "classweight"]

		if (course == "cs1"):
			parameter = [week4_respcorr_parameter["cs1"][2], week4_respcorr_parameter["cs1"][1], week4_respcorr_parameter["cs1"][0]]
		elif (course == "cse8a"):
			parameter = [week4_respcorr_parameter["cse8a"][2], week4_respcorr_parameter["cse8a"][1], week4_respcorr_parameter["cse8a"][0]]
		elif (course == "cse12"):
			parameter = [week4_respcorr_parameter["cse12"][2], week4_respcorr_parameter["cse12"][1], week4_respcorr_parameter["cse12"][0]]
		elif (course == "cse100"):
			parameter = [week4_respcorr_parameter["cse100"][2], week4_respcorr_parameter["cse100"][1], week4_respcorr_parameter["cse100"][0]]
		elif (course == "cse141"):
			parameter = [week4_respcorr_parameter["cse141"][2], week4_respcorr_parameter["cse141"][1], week4_respcorr_parameter["cse141"][0]]

#######################
# actual model training
#######################

# model: 0 - logit, 1 - svm, 2 - rf


# for testing 
#parameter = [2,		0.001953125,	1.3]


if (model == 0):
	mymodel = sm.GLM(trainset["exam_total"], trainset.drop(columns=["exam_total"]), family=sm.families.Binomial()).fit()
	print(mymodel.summary())
	# Odds ratios only
	#exp(coef(mymodel))
	#
	#???/
	#
	# math.exp(list(mymodel.params))

elif (model == 1):

	# Not setting seed for now
	# set.seed(389)
	print("SVM model training starts...")

	# No tunemethod 0 or 1
	mymodel = SVC(C=parameter[2], gamma=parameter[1], class_weight={1:parameter[0], 0:1}).fit(trainset.drop(columns=["exam_total"]), trainset["exam_total"])
elif (model == 3):
	# Method: svm

	# Not setting seed for now
	# set.seed(389)s
	print("SVM model training starts...")
	mymodel = SVC().fit(trainset.drop(columns=["exam_total"]), trainset["exam_total"])

print("Training end")
# Save image
with open("../results/" + course + "/TrainedModel.out", "wb") as outFile:
	pickle.dump([datasource, parameter, model, tunemethod, scaled_data_test, mymodel], outFile)