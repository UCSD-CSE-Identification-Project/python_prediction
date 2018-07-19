# README #

This has the latest (and best) modeling results so that whenever we modify the code, we can ensure the results stay the same under the identical method.

## Modeling Results as of 5/17/2017 ##
### clicker only + findprobthreshold() ###
**svm-rbf**

Probability threshold 0.35
TP 33 TN 29 FP 9.1 FN 29
[1] "Accuracy: " "0.62"      
[1] "specificity:"  "0.53"          "NPV: "         "0.78"         
[5] "Sensitivity: " "0.76"          "PPV: "         "0.5"         
[1] "F1-Negative score: "0.45"              
[1] "F1-Positive score: " "0.6"               



### clicker only + findclassweight(naive k-fold validation) ###

**svm-rbf** .. UP TO WEEK3
[1] "classweight: 1.5"
[1] TP 16.5 TN 40.3 FP 21.6 FN 21.6
[1] "Accuracy: " "0.5682"    
[1] "specificity:"  "0.65"          "NPV: "         "0.65"         
[5] "Sensitivity: " "0.43"          "PPV: "         "0.43"         
[1] "F1-Negative score: " "0.65"               
[1] "F1-Positive score: " "0.43"               
[1] "Weighted Accuracy: " "0.57"               
[1] "MCC: " "0.08" 
[1] "Cohen's Kappa: " "0.08"           


**svm-rbf** .. UP TO WEEK4

Class-weight for Fail class: 1.7
[1] TP 30.1 TN 24.4 FP 37.5 FN 8.0
[1] "Accuracy: " "0.55"      
[1] "specificity:"  "0.39"          "NPV: "         "0.75"         
[5] "Sensitivity: " "0.79"          "PPV: "         "0.45"         
[1] "F1-Negative score: " "0.51"               
[1] "F1-Positive score: " "0.57"
[1] "Weighted Accuracy: " "0.54"               
[1] "MCC: " "0.19" 
[1] "Cohen's Kappa: " "0.16" 


### (clicker + quiz) + findclassweight(naive k-fold validation) ###

**svm-rbf** .. UP TO WEEK3
[1] "classweight: 1.9"
[1] TP 26.7 TN 36.4 FP 25.6 FN 11.4
[1] "Accuracy: " "0.6307"    
[1] "specificity:"  "0.59"          "NPV: "         "0.76"         
[5] "Sensitivity: " "0.7"           "PPV: "         "0.51"         
[1] "F1-Negative score: " "0.66"               
[1] "F1-Positive score: " "0.59"               
[1] "Weighted Accuracy: " "0.63"               
[1] "MCC: " "0.28" 
[1] "Cohen's Kappa: " "0.27"           

**svm-rbf** .. UP TO WEEK4

Class-weight for Fail class: 1.8
[1] TP 24.4 TN 38.1 FP 23.9 FN 13.6
[1] "Accuracy: " "0.62"      
[1] "specificity:"  "0.61"          "NPV: "         "0.74"         
[5] "Sensitivity: " "0.64"          "PPV: "         "0.51"         
[1] "F1-Negative score: " "0.67"               
[1] "F1-Positive score: " "0.57"               
