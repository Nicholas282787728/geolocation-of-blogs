# geolocation-of-blogs

Our goal is to identify the geo-location of the users on Google blogger by analyzing contents in their blogs.
We used two classification methods: Naive Bayes and SVM.

For Feature Selection, we implemented four methods:
1. Chi-Squared
2. Information-Gain
3. Heuristic-Based
4. Local Words Selection

# Usage
    
    python geolocation_of_blogs.py [NB|igr|tficf|chi|nl] [percentage]

# description


* geolocation_of_blogs.py

    Main function of our program. To run it, put train.csv and test.csv in the same folder and execute it.

* preprocess.py

    Filter and Split the original data into training set and testing set.

* tficf.py

    Return top k percent of words ranked by icf then tf in decreasing order
    
* chiSquareLIW.py

    For each state, extract top 20 location indicative words (LIWs) using chi-squared statistcs. Words with frequency less than ten are removed.
    
* demo.py

    Program used for demo
    
* create_new_tables.sql

    Creates 3 new tables in addition to 6 original tables for preprocessing usage
