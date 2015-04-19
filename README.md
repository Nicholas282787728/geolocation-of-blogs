# geolocation-of-blogs

Our goal is to identify the geo-location of the users on Google blogger by analyzing contents in their blogs.
We used two classification methods: Naive Bayes and SVM.

For Feature Selection, we implemented four methods:
1. chi-squared
2. Information-Gain
3. Heuristic-Based
4. Local Sords Selection



geolocation_of_blogs.py

Main function of our program. To run it, put train.csv and test.csv in the same folder and execute it.

preprocess.py

Filter and Split the original data into training set and testing set.
