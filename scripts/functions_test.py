import numpy as np
import csv
import pandas as pd
import random
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.metrics import roc_curve, auc


def AnalyzeConfidence(coursename, examscore, total, response, confidence):
	tempDf = pd.DataFrame.from_dict({"total": total, "examscore": examscore, "response": response, "confidence": confidence})
	tempDf.to_csv("../results/" + str(coursename) + "/confidence.csv")
	return

def chooseROCCurvecolor(coursename):
	linecolor = ["steelblue", "darkgreen", "orangered2", "darkorange4", "mediumpurple"]
	shapecolor = ["lightskyblue1", "palegreen2", "lightsalmon1", "sandybrown", "thistle1"]

	# Default line and shape color
	line = "black"
	shape = "#1c61b6AA"
	threstext = [1.1, -0.2]

	if (coursename == "cs1"):
		line = linecolor[0]
		shape = shapecolor[0]
		threstext = [-0.1, 0]
	elif (coursename == "cse8a"):
		line = linecolor[1]
		shape = shapecolor[1]
		threstext = [1.05, 0.8]
	elif (coursename == "cse12"):
		line = linecolor[2]
		shape = shapecolor[2]
		threstext = [1.0, 0.0]
	elif (coursename == "cse100"):
		line = linecolor[3]
		shape = shapecolor[3]
		threstext = [1.05, 0.6]
	elif (coursename == "cse141"):
		line = linecolor[4]
		shape = shapecolor[4]
		threstext = [1.0, -0.4]
	return (line, shape, threstext)

def DrawROCCurve(coursename, actualpf, predictedprobability):
	(line, shape, threstext) = chooseROCCurvecolor(coursename)

	fname = "../results/" + str(coursename) + "/ROC-" + str(coursename) + ".pdf"

	pp = PdfPages(fname)
	(fpr, tpr, thresholds) = roc_curve(actualpf, predictedprobability)
	roc_obj = (fpr, tpr, thresholds)
	AUC_final = auc(fpr, tpr)

	plt.title("Receiver Operating Characteristic")
	plt.plot(fpr, tpr, "b", label="AUC = %0.2f" % AUC, lw=1.0)
	plt.legend(loc = "lower right")
	plt.plot([0, 1], [0, 1], lw=1.0, color="navy", linestyle="--")
	plt.xlim([0, 1])
	plt.ylim([0, 1.05])

	# Find the best coordinates
	criterion = [(1-tpr[i])**2 + fpr[i]**2 for i in range(len(tpr))]
	(bestFpr, bestTpr) = criterion[criterion.index(min(criterion))]


	coords_tpr = np.linspace(0, 1, 21)
	targetX = np.interp(coords_tpr, tpr, fpr)
	plt.plot(targetX, coords_tpr, "go")
	fprs = []
	ci_lowers = []
	ci_uppers = []

	# Prepare 2000 stratified bootstrap samplings
	actualpf0 = []
	actualpf1 = []
	predictedp0 = []
	predictedp1 = []

	for i in range(len(list(actualpf))):
		if (actualpf[i] == 0):
			actualpf0.append(actualpf[i])
			predictedp0.append(predictedprobability[i])
		else:
			actualpf1.append(actualpf[i])
			predictedp1.append(predictedprobability[i])

	for i in range(2000):
		# Randomly select 75% of the data indices
		indices_0 = random.sample(range(len(actualpf0)), int(len(actualpf0)*30/100))
		indices_1 = random.sample(range(len(actualpf1)), int(len(actualpf1)*30/100))

		new_actualpf = list(np.array(actualpf0)[indices_0]) + list(np.array(actualpf1)[indices_1])
		new_predictedp = list(np.array(predictedp0)[indices_0]) + list(np.array(predictedp1)[indices_1])

		(fpr, tpr, thresholds) = roc_curve(new_actualpf, new_predictedp)
		fprs.append(np.interp(coords_tpr, tpr, fpr))
		fprs[-1][0] = 0.0

	for i in range(21):
		data = []
		for j in range(10):
			data.append(fprs[j][i])
		mean = np.mean(data)
		std = np.std(data)

		ci_lower = mean - 1.96*std/(math.sqrt(10))
		ci_upper = mean + 1.96*std/(math.sqrt(10))

		ci_lowers.append(ci_lower)
		ci_uppers.append(ci_upper)

	# Fill shades
	plt.plot(ci_lowers, coords_tpr, "ro")
	plt.plot(ci_uppers, coords_tpr, "ro")

	plt.ylabel("True Positive Rate")
	plt.xlabel("False Positive Rate")
	plt.savefig(pp, format="pdf")
	pp.close()

	AUC = round(AUC, 2)

	# Executing ROC-test to compare random guessing vs classification results
	# NOTE: In R the interval is 0.0<=x<=1.0, in Python the interval is 0.0<=x<1.0 
	rand_classifier = np.random.uniform(0.0, 1.0, len(predictedprobability))
	
	#
	# direction <
	#
	roc_obj_rand = roc_curve(actualpf, rand_classifier)
	AUC_rand = round(auc(roc_obj_rand[0], roc_obj_rand[1]), 2)

	# Skipping
	# roc.test
	#
	#roctest <- roc.test(roc_obj, roc_obj_rand)
    #print (paste0("AUC_rand: ", AUC_rand))
    #print (roctest)

    #roctest2 <- roc.test(roc_obj, roc_obj_rand, method="venkatraman")
    #print (roctest2)

    # Skipping ci=ci(roc_obj, of="auc")
	return {"roc": roc_obj, "auc": auc_final, "bestthreshold": (bestFpr, bestTpr)}

def DrawHeatMap(coursename, examscore, actualpf, predictedresults, cutoff):
	return

def save_results(num_students, test_results, coursename, dropWeek, NA_percentages):
	return

def DrawHeatMap_classification_with_anid_and_na(data, examScores, anids, course, dropWeek, cutoff):
	return

def DrawHeatMap_percentNAs(data, examScores, anids, course, dropWeek, cutoff):
	return

def AnalyzeError(predicted, actual, p):
	true_positive = 0
	true_negative = 0
	false_positive = 0
	false_negative = 0
	totalresults = []
	actual = list(actual)

	for i in range(len(actual)):
		if (predicted[i] >= p and actual[i] == 2):
			true_positive += 1
			totalresults.append("3")
		elif (predicted[i] >= p and actual[i] == 1):
		 	false_positive += 1
		 	totalresults.append("1")
		elif (predicted[i] < p and actual[i] == 1):
			true_negative += 1
			totalresults.append("4")
		else:
			false_negative += 1
			totalresults.append("2")

	return {"fn": false_negative, "fp": false_positive, "tn": true_negative, "tp": true_positive, "total": totalresults}

def AnalyzeError_logitonly(predicted, actual, p=0.5):
	true_positive = 0
	true_negative = 0
	false_positive = 0
	false_negative = 0
	totalresults = []
	actual = list(actual)

	for i in range(len(actual)):
		if (predicted[i] >= p and actual[i] == 1):
			true_positive += 1
			totalresults.append("3")
		elif (predicted[i] >= p and actual[i] == 0):
		 	false_positive += 1
		 	totalresults.append("1")
		elif (predicted[i] < p and actual[i] == 0):
			true_negative += 1
			totalresults.append("4")
		else:
			false_negative += 1
			totalresults.append("2")

	return {"fn": false_negative, "fp": false_positive, "tn": true_negative, "tp": true_positive, "total": totalresults}

def AnalyzeExamscore(coursename, category, predictedprob, actualresp, actualscores):
	return