# MIT License
# 
# Copyright (c) 2018 Thomas Darde
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#------------------------------------------#
# Keras prediction :
#       - https://www.youtube.com/watch?v=hd81EH1g1bE
#       - https://www.datacamp.com/community/tutorials/keras-r-deep-learning
#------------------------------------------#

#------------------------------------------#
# Read inputs
#------------------------------------------#
Sign.Name                    <- commandArgs(TRUE)[1]
Sign.File                    <- commandArgs(TRUE)[2]
Input.File                   <- commandArgs(TRUE)[3]
Input.Model                  <- commandArgs(TRUE)[4]
Association.File             <- commandArgs(TRUE)[5]
Output.Dir                   <- commandArgs(TRUE)[6]
#------------------------------------------#

#------------------------------------------#
# Test 
#------------------------------------------#
#Model.Group.Asso   <- "/app/tools/predict/association_matrix_PE.tsv"
#Output.Dir         <- "/app/tools/predict/results/"
#Input.Model        <- "/app/tools/predict/model_PE.h5"
#Input.File         <- "/app/tools/predict/mat_chempsy_final_10793.tsv"
#Sign.File          <- "/app/tools/predict/TSS1.sign"

#------------------------------------------#

dir.create(c(Output.Dir),recursive=TRUE,showWarnings=FALSE)

#------------------------------------------#
#Libraries
#------------------------------------------#
#installation du package CRAN
if("keras" %in% rownames(installed.packages()) == FALSE) { install.packages("keras",quiet = TRUE)}
if("caret" %in% rownames(installed.packages()) == FALSE) { install.packages("caret",quiet = TRUE)}
if("e1071" %in% rownames(installed.packages()) == FALSE) { install.packages("e1071",quiet = TRUE)}


#chargement de la librairie
library(keras)
library(caret)
library(e1071)

#------------------------------------------#
# Load Model
#------------------------------------------#
print("Import model...")
model <- load_model_hdf5(Input.Model)
print("Model loaded")
#------------------------------------------#

#------------------------------------------#
# Read Signature
#------------------------------------------#
print("Import signature...")
Sign.Data <- read.table(Sign.File,sep="\t",blank.lines.skip=TRUE,fill=TRUE,header=FALSE)

Up.List  <- unique(as.character(Sign.Data[which(is.na(Sign.Data[,3])== FALSE & Sign.Data[,5] == "1"),3]))
Down.List  <- unique(as.character(Sign.Data[which(is.na(Sign.Data[,3])== FALSE & Sign.Data[,5] == "-1"),3]))

print("Signature loaded")
#------------------------------------------#


#------------------------------------------#
# Load files 
#------------------------------------------#
print("Import files ...")
Association.matrix                      <- as.matrix(read.table(Input.File,sep="\t",header=F,quote="",check.names=FALSE))
D                                       <- read.table(Input.File,sep="\t",header=T,quote="",check.names=FALSE)
#------------------------------------------#
# ADD signature 
#------------------------------------------#
max_dim = length(colnames(D))
D2                                      <- rbind(D,0)
D2[3023,intersect(as.character(Up.List),colnames(D2))]          <- 1
D2[3023,intersect(as.character(Down.List),colnames(D2))]        <- -1 


test <- D2[3023, 16:max_dim]
data <- as.matrix(test)

prob <- model %>%
  predict_proba(data)


Group.Matrix           <- as.matrix(read.table(Association.File,sep="\t",header=F,quote="\"",check.names=FALSE))
rownames(Group.Matrix) <- as.numeric(Group.Matrix[,1])
final_matrix           <- matrix(ncol = 1, nrow = length(prob))
names                  <- c()
for(pos in 1:length(prob)){
  val = prob[pos]
  group                <- Group.Matrix[as.character(pos-1),2]
  names                <- c(names,group)
  final_matrix[pos,1]  <- val
}

rownames(final_matrix) <- names
final_matrix           <- final_matrix[order(final_matrix[,1], decreasing = TRUE),]

write.table(final_matrix,file=sprintf("%sprediction_results.tsv",Output.Dir),sep = "\t")
