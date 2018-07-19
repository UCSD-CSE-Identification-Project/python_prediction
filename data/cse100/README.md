# README #

This has the latest (and best) modeling results so that whenever we modify the code, we can ensure the results stay the same under the identical method.

## Modeling Results as of 6/11/2017 ##
### clicker only + findprobthreshold() ###
**svm-rbf**  .. (MAYBE) UP TO WEEK4

Probability threshold 0.35
TP 27.7 TN 20.9 FP 39.8 FN 11.5
[1] "Accuracy: " "0.49"      
[1] "specificity:"  "0.34"          "NPV: "         "0.65"         
[5] "Sensitivity: " "0.71"          "PPV: "         "0.41"         
[1] "F1-Negative score: " "0.45"               
[1] "F1-Positive score: " "0.52"               



### clicker only + findclassweight(naive k-fold validation) ###

**svm-rbf** .. UP TO WEEK3

[1] TP 27.2 TN 27.2 FP 33.5 FN 12.0
[1] "Accuracy: " "0.5445"    
[1] "specificity:"  "0.45"          "NPV: "         "0.69"         
[5] "Sensitivity: " "0.69"          "PPV: "         "0.45"         
[1] "F1-Negative score: " "0.54"               
[1] "F1-Positive score: " "0.54"               
[1] "Weighted Accuracy: " "0.54"               
[1] "MCC: " "0.14" 
[1] "Cohen's Kappa: " "0.13"           


**svm-rbf** .. UP TO WEEK4

Class-weight for Fail class: 1.6
[1] TP 19.4 TN 44.0 FP 16.8 FN 19.9
[1] "Accuracy: " "0.63"      
[1] "specificity:"  "0.72"          "NPV: "         "0.69"         
[5] "Sensitivity: " "0.49"          "PPV: "         "0.54"         
[1] "F1-Negative score: " "0.7"                
[1] "F1-Positive score: " "0.51"     




### (clicker + quiz) + findclassweight(naive k-fold validation) ###

**svm-rbf** .. UP TO WEEK3

Class-weight for Fail class: 1.9
[1] TP 16.8 TN 42.9 FP 17.8 FN 22.5
[1] "Accuracy: " "0.5969"    
[1] "specificity:"  "0.71"          "NPV: "         "0.66"         
[5] "Sensitivity: " "0.43"          "PPV: "         "0.48"         
[1] "F1-Negative score: " "0.68"               
[1] "F1-Positive score: " "0.45"               
[1] "Weighted Accuracy: " "0.6"                
[1] "MCC: " "0.14" 
[1] "Cohen's Kappa: " "0.14" 


**svm-rbf** .. UP TO WEEK4

Class-weight for Fail class: 1.8
[1] TP 20.4 TN 45.0 FP 15.7 FN 18.8
[1] "Accuracy: " "0.65"      
[1] "specificity:"  "0.74"          "NPV: "         "0.7"          
[5] "Sensitivity: " "0.52"          "PPV: "         "0.57"         
[1] "F1-Negative score: " "0.72"               
[1] "F1-Positive score: " "0.54" 
