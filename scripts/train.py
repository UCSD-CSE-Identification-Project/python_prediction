import argparse
import pandas as pd
import functions_prepdata_final as prepFinal
import functions_prepdata_prereq as prepPrerec
import functions_prepdata_midterm as prepMidterm
import functions_prepdata_clicker as prepClicker
import functions_prepdata_quiz as prepQuiz
import pickle

# Parse command line arguments, run python3 script with -h for more information
parser = argparse.ArgumentParser(description="Preprocess student data based on user input")
parser.add_argument("course", choices=["cs1", "cse8a", "cse12", "cse100", "cse141"], help="choose one from: cs1, cse8a, cse12, cse100, cse141 to prep data")
parser.add_argument("cutoffweek", type=int, help="up to which week will be in the testset (cs1 can model up to weeks 3-12, all other courses can model up to weeks 3-10)")
parser.add_argument("components", help="combination of course components to model with, at least 1 component, at most all 4 components: c (clicker), m (midterm), p (prereq), q (quiz)")
args = parser.parse_args()


fileObject = open("../results/cse12/PreppedData_train_and_test.out",'rb')  
# load the object from the file into var b
b = pickle.load(fileObject) 