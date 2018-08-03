def AnalyzeConfidence(coursename, examscore, total, response, confidence):
	return

def chooseROCCurvecolor(coursename):
	return

def DrawROCCurve(coursename, actualpf, predictedresponse, predictedprobability):
	return

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
	return

def AnalyzeExamscore(coursename, category, predictedprob, actualresp, actualscores):
	return