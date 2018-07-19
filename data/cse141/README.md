# README #

This has the latest (and best) modeling results so that whenever we modify the code, we can ensure the results stay the same under the identical method.

## Modeling Results as of 6/10/2017 ##

### clicker only + findclassweight(naive k-fold validation) ###

**svm-rbf**

Class-weight for Fail class: 1.5

[1] TP 16.9 TN 49.6 FP 12.0 FN 21.4
[1] "Accuracy: " "0.67"      
[1] "specificity:"  "0.8"           "NPV: "         "0.7"          
[5] "Sensitivity: " "0.44"          "PPV: "         "0.58"         
[1] "F1-Negative score: " "0.75"               
[1] "F1-Positive score: " "0.5"                
[1] "Weighted Accuracy: " "0.66"               
[1] "MCC: " "0.26" 
[1] "Cohen's Kappa: " "0.26"           



### (clicker + quiz) + findclassweight(naive k-fold validation) ###

**svm-rbf**
Class-weight for Fail class: 1.5

[1] 18.8 47.4 14.3 19.5
[1] "Accuracy: " "0.66"      
[1] "specificity:"  "0.77"          "NPV: "         "0.71"         
[5] "Sensitivity: " "0.49"          "PPV: "         "0.57"         
[1] "F1-Negative score: " "0.74"               
[1] "F1-Positive score: " "0.53"               
[1] "Weighted Accuracy: " "0.66"               
[1] "MCC: " "0.27" 
[1] "Cohen's Kappa: " "0.27"           
 [1] 18.80 47.40 14.30 19.50 66.17  0.71  0.77  0.53  0.57  0.49
