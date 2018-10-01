import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc

# Called by FindParameters
def create_validation_train_test2(data, vmethod, seed):
	sampled_train = None
	sampled_test = None

	if (vmethod == 0):
		print("naive k-fold validation")
		# Split => train/test = 66.7/33.3
		(sampled_train, sampled_test) = train_test_split(data, test_size=0.333, train_size=0.667, random_state=seed, shuffle=True)
	elif (vmethod == 1):
		print("stratified sampling")

		failed = data.loc[data["exam_total"] == 1]
		(sampled_train_fail, sampled_test_fail) = train_test_split(failed, test_size=0.333, train_size=0.667, random_state=seed, shuffle=True)

		passed = data.loc[data["exam_total"] == 0]
		(sampled_train_pass, sampled_test_pass) = train_test_split(passed, test_size=0.333, train_size=0.667, random_state=seed, shuffle=True)

		sampled_train = pd.concat([sampled_train_fail, sampled_train_pass])
		sampled_test = pd.concat([sampled_test_fail, sampled_test_pass])

	return (sampled_train, sampled_test)

# Called by FindParameters
# Gives back tp, tn, fp, fn
def AnalyzeErrorResp(predicted, actual):
	true_positive = 0
	true_negative = 0
	false_positive = 0
	false_negative = 0
	totalresults = []
	actual = list(actual)

	for i in range(len(actual)):
		if (predicted[i] == 1 and actual[i] == 1):
			true_positive += 1
			totalresults.append("2")
		elif (predicted[i] == 1 and actual[i] == 0):
		 	false_positive += 1
		 	totalresults.append("4")
		elif (predicted[i] == 0 and actual[i] == 0):
			true_negative += 1
			totalresults.append("3")
		else:
			false_negative += 1
			totalresults.append("1")

	return {"fn": false_negative, "fp": false_positive, "tn": true_negative, "tp": true_positive, "total": totalresults}

# Called by train.py
def FindParameters(coursename, data):
	# (1, 5): 60.8%, (6, 8): 64.2%, 9: 61.93%, (10, 11, 12, 18): 65.34%
	random.seed(18)

	# iteration can be changed
	iteration = 10
	weightseq = np.arange(1.0, 2.1, 0.1)
	costseq = [2 ** i for i in range(-5, 2)]
	gammaseq = [2 ** i for i in range(-9, 0)]

	totalLength = len(weightseq) * len(costseq) * len(gammaseq)
	variablesetting = pd.DataFrame(index=range(totalLength), columns=range(3))
	sensitivity = pd.DataFrame(index=range(totalLength), columns=range(iteration))
	#
	# For some reason using the name fpr will cause error, changed to fpr1
	#
	fpr1 = pd.DataFrame(index=range(totalLength), columns=range(iteration))
	dist = pd.DataFrame(index=range(totalLength), columns=range(iteration))
	kappa = pd.DataFrame(index=range(totalLength), columns=range(iteration))
	labels = pd.DataFrame(index=range(totalLength), columns=range(iteration))
	accuracy = pd.DataFrame(index=range(totalLength), columns=range(iteration))
	trainaccuracy = pd.DataFrame(index=range(totalLength), columns=range(iteration))
	numofSVs = pd.DataFrame(index=range(totalLength), columns=range(iteration))

	AUC = pd.DataFrame(index=range(totalLength), columns=range(iteration))

	# Validation method == 0, 0 means naive k-fold validation, 1 means stratified
	print("choosing validation method... 0: naive k-fold validation, 1: stratified")
	print ("We are using default value - 0")
	validation_method = 0   # naive k-fold validation is default value

	for it in range(iteration):
		# Pass in "random" number to reproduce output
		sample = create_validation_train_test2(data, validation_method, random.randint(0, 2**32-1))
		my_train = sample[0]
		my_test = sample[1]
		print("iteration #" + str(it+1))

		cnt = 0
		for c in costseq:
			for g in gammaseq:
				for w in weightseq:
					# K-fold not used for now
					valid_svm = SVC(C=c, gamma=g, class_weight={1:w, 0:1}).fit(my_train.drop(columns=["exam_total"]), my_train["exam_total"])

					valid_pred = valid_svm.predict(my_test.drop(columns=["exam_total"]))
					train_pred = valid_svm.predict(my_train.drop(columns=["exam_total"]))

					(fpr, tpr, thresholds) = roc_curve(my_test["exam_total"], valid_pred)
					AUC[it][cnt] = auc(fpr, tpr)

					numofSVs[it][cnt] = len(valid_svm.support_)

					trainresults = AnalyzeErrorResp(train_pred, my_train["exam_total"])
					trainaccuracy[it][cnt] = (trainresults["tp"]+trainresults["tn"])/(trainresults["tp"]+trainresults["tn"]+trainresults["fp"]+trainresults["fn"])

					results = AnalyzeErrorResp(valid_pred, my_test["exam_total"])
					accuracy[it][cnt] = (results["tp"]+results["tn"])/(results["tp"]+results["tn"]+results["fp"]+results["fn"])
					labels[it][cnt] = "(" + str(c) + "," + str(g) + "," + str(w) + ")"
					variablesetting.iloc[cnt] = [c, g, w]

					# For ROC curve
					new_s = results["tp"] / (results["tp"] + results["fn"])
					new_fpr = 1 - results["tn"] / (results["tn"] + results["fp"])

					sensitivity[it][cnt] = new_s
					fpr1[it][cnt] = new_fpr
					dist[it][cnt] = round((1-new_s) ** 2 + new_fpr ** 2, 3)

					# Kappa
					observed_acc = round((results["tp"]+results["tn"])/len(results["total"]), 3)
					GP = results["tp"] + results["fn"]
					GN = results["tn"] + results["fp"]
					CP = results["tp"] + results["fp"]
					CN = results["tn"] + results["fn"]
					expected_acc = round( (GP*GN + CP*CN)/len(results["total"])**2, 3)
					new_kappa = (observed_acc - expected_acc)/(1 - expected_acc)
					kappa[it][cnt] = new_kappa

					cnt += 1

	avg_AUC = AUC.mean(axis=1)
	avg_dist = dist.mean(axis=1)
	avg_sensitivity = sensitivity.mean(axis=1)
	avg_fpr = fpr1.mean(axis=1)
	avg_kappa = kappa.mean(axis=1)
	avg_accuracy = accuracy.mean(axis=1)
	avg_trainaccuracy = trainaccuracy.mean(axis=1)
	avg_numofSVs = numofSVs.mean(axis=1)

	resultstable = pd.concat([variablesetting, avg_AUC, avg_dist, avg_numofSVs, avg_sensitivity, avg_fpr, avg_kappa, avg_accuracy, avg_trainaccuracy], axis=1)
	resultstable.columns = ["C", "gamma", "classweight", "avg_AUC", "avg_dist", "avg_numofSVs", "avg_sensitivity", "avg_fpr", "avg_kappa", "avg_accuracy", "avg_trainaccuracy"]
	#print(resultstable)

	# Generates validation graph
	if (validation_method == 0):
		pp = PdfPages("../results/" + str(coursename) + "/ROC-naive.pdf")
		plt.plot(list(avg_fpr), list(avg_sensitivity), "b.")
		plt.axis([0, 1, 0, 1])
		plt.xlabel("avg_fpr")
		plt.ylabel("avg_sensitivity")
		plt.title(str(coursename) + ": ROC-naive")
		plt.savefig(pp, format="pdf")
		pp.close()
		plt.close("all")

		pp = PdfPages("../results/" + str(coursename) + "/validation.pdf")
		plt.figure(1)
		plt.plot(list(resultstable.index), list(avg_accuracy), "b.-", linewidth=1.0)
		for i in range(len(resultstable.index)):
			plt.text(list(resultstable.index)[i], list(avg_accuracy)[i], list(resultstable.index)[i], fontsize=4)

		plt.plot(list(resultstable.index), list(avg_trainaccuracy), "g.-", linewidth=1.0)
		plt.plot(list(resultstable.index), list(avg_dist), "r.-", linewidth=1.0)
		for i in range(len(resultstable.index)):
			plt.text(list(resultstable.index)[i], list(avg_dist)[i], list(resultstable.index)[i], fontsize=4)

		plt.xlabel("rownames(resultstable)")
		plt.ylabel("avg_accuracy")
		plt.legend(("train", "validation", "dist"), loc="upper left")
		plt.savefig(pp, format="pdf")

		plt.figure(2)
		plt.plot(list(resultstable.index), list(avg_numofSVs), "r.-", linewidth=1.0)
		plt.xlabel("rownames(resultstable)")
		plt.ylabel("avg_numofSVs")
		plt.savefig(pp, format="pdf")

		plt.figure(3)
		plt.plot(list(resultstable.index), list(avg_AUC), "g.-", linewidth=1.0)
		for i in range(len(resultstable.index)):
			plt.text(list(resultstable.index)[i], list(avg_AUC)[i], list(resultstable.index)[i], fontsize=5)
		plt.xlabel("rownames(resultstable)")
		plt.ylabel("avg_AUC")
		plt.savefig(pp, format="pdf")

		pp.close()
		plt.close("all")
	else:
		pp = PdfPages("../results/" + str(coursename) + "/ROC-stratified.pdf")
		plt.plot(list(avg_fpr), list(avg_sensitivity), 'b.-')
		plt.axis([0, 1, 0, 1])
		plt.xlabel("avg_fpr")
		plt.ylabel("avg_sensitivity")
		plt.title(str(coursename) + ": ROC-stratified")

		# Double Check when encountered
		#plt.text(avg_fpr, avg_sensitivity, labels)
		plt.savefig(pp, format="pdf")
		pp.close()

	# validation_method == 0, 0 means naive k-fold validation, 1 means stratified
	print ("choosing pruning method.. 0: ROC-curve , 2: Cohen's Kappa")
	print ("We are using default value - 0")
	optimizing_method = 0   # ROC-curve is default value

	if (optimizing_method == 0):
		resultstable_no_overfitting = resultstable.loc[resultstable["avg_trainaccuracy"]-resultstable["avg_accuracy"] < 0.2]

		if (resultstable_no_overfitting.shape[0] != 0):
			resultstable = resultstable_no_overfitting

		print("Original...")
		print("max avg_AUC is:")
		# Find the last parameters, use a reversed list to find that index
		AUCind = len(resultstable["avg_AUC"]) - list(resultstable["avg_AUC"][::-1]).index(max(resultstable["avg_AUC"])) - 1
		print(max(resultstable["avg_AUC"]))
		minpair = resultstable.iloc[AUCind]
		print("minpair is:")
		print(minpair)
		print("MAX avg_acc IS:", max(list(resultstable["avg_accuracy"])))

	elif (optimizing_method == 1):
		# Tuning with distance between roc point and (0,1)
		resultstable = resultstable.loc[resultstable["avg_trainaccuracy"]-resultstable["avg_accuracy"] < 0.3]
		minpair = resultstable.loc[resultstable["avg_dist"] == min(list(avg_dist))]
	elif (optimizing_method == 2):
		# Kappa
		minpair = resultstable.loc[resultstable["avg_kappa"] == max(list(avg_kappa))]

	return (minpair["classweight"], minpair["gamma"], minpair["C"])

def Obtain_PreTuned_Parameters(week):
	cs1 = [None] * 3
	cse8a = [None] * 3
	cse12 = [None] * 3
	cse100 = [None] * 3
	cse141 = [None] * 3


	# Following numbers hardcoded, obtained from R
	if (week == 1):
		cs1    =   [0.25, 	0.125,		1.4]
		cse8a  =   [0.125, 	0.03125,	1.5]
		cse12  =   [2,		0.0078125,	1.4]
		cse100 =   [2, 		0.00390625,	1.8]
		cse141 =   [0.25,	0.0078125,	1.5]
	elif (week == 2):
		cs1    =   [2, 		0.001953125,1.5]
		cse8a  =   [0.25,	0.015625,	1.6]
		cse12  =   [1,		0.03125,	1.7]
		cse100 =   [1, 		0.001953125,1.6]
		cse141 =   [1,		0.00390625,	2.0]
	elif (week == 3):
		cs1    =   [0.5,	0.00390625, 1.5]
		cse8a  =   [0.5, 	0.0078125,	1.5]
		cse12  =   [0.5,	0.015625,	1.6]
		cse100 =   [1,		0.001953125,1.6]
		cse141 =   [0.5,	0.015625,	1.8]
	elif (week == 4):
		cs1    =   [0.5, 	0.001953125,1.5]
		cse8a  =   [0.5, 	0.015625,	1.5]
		cse12  =   [2,		0.001953125,1.7]
		cse100 =   [1,		0.001953125,1.6]
		cse141 =   [0.25,	0.00390625,	1.5]
	elif (week == 5):
		cs1    =   [0.5, 	0.001953125,1.5]
		cse8a  =   [0.5, 	0.001953125,1.6]
		cse12  =   [2,		0.001953125,1.3]
		cse100 =   [1, 		0.001953125,1.6]
		cse141 =   [0.25,	0.00390625,	1.5]
	elif (week == 6):
		cs1    =   [0.5, 	0.001953125,1.5]
		cse8a  =   [0.25, 	0.0078125,	1.7]
		cse12  =   [1,		0.001953125,1.5]
		cse100 =   [0.25, 	0.00390625,	1.6]
		cse141 =   [0.5,	0.001953125,1.5]
	elif (week == 7):
		cs1    =   [0.25, 	0.0078125,	1.5]
		cse8a  =   [1,		0.001953125,2.0]
		cse12  =   [1,		0.001953125,1.7]
		cse100 =   [0.5,	0.00390625,	1.7]
		cse141 =   [0.5,	0.001953125,1.6]
	elif (week == 8):
		cs1    =   [0.25, 	0.0078125,	1.5]
		cse8a  =   [1,		0.001953125,1.6]
		cse12  =   [0.5,	0.00390625,	1.6]
		cse100 =   [0.5,	0.001953125,1.7]
		cse141 =   [0.25,	0.00390625,	1.5]
	elif (week == 9):
		cs1    =   [0.25,	0.00390625,	1.4]
		cse8a  =   [0.25,	0.0078125,	1.4]
		cse12  =   [0.5,	0.00390625,	1.8]
		cse100 =   [0.5,	0.001953125,1.7]
		cse141 =   [0.5,	0.00390625,	1.4]
	elif (week == 10):
		cs1    =   [1,		0.001953125,1.3]
		cse8a  =   [0.25,	0.001953125,1.6]
		cse12  =   [0.5,	0.00390625,	1.9]
		cse100 =   [0.5,	0.001953125,1.7]
		cse141 =   [0.5,	0.001953125,1.5]
	elif (week == 11):
		cs1    =   [1,		0.001953125,1.3]
	# Week 12
	else:
		cs1    =   [1,		0.001953125,1.7]

	return (cs1, cse8a, cse12, cse100, cse141)