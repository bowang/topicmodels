library(RTextTools)
library(topicmodels)

data = read.csv('~/Downloads/topicmodels/output.csv', sep=';')
matrix <- create_matrix(cbind(as.vector(data$Title),as.vector(data$Abstract)), language="english", removeNumbers=TRUE, stemWords=TRUE, removeStopwords=TRUE, weighting=weightTf)
lda = LDA(matrix, 10)
terms(lda)

