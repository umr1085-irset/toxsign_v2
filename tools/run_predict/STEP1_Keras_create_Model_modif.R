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
# Keras cration model from :
#       - https://www.youtube.com/watch?v=hd81EH1g1bE
#       - https://www.datacamp.com/community/tutorials/keras-r-deep-learning
# Compatible with MLP multi classification
# To do: Condition if output class is binary + define default binary model
#------------------------------------------#
#------------------------------------------#

#------------------------------------------#
# Prompt functions
#------------------------------------------#
readActivation <- function()
{ 
  cat("Enter activation model (relu,softmax,elu,selu,sigmoid): ")
  activation_models <- c("relu","softmax","elu","selu","sigmoid")
  n <- readLines("stdin", n = 1)
  print(n)
  if (is.na(n) || !(n %in% activation_models)){
    n <- readActivation()
  }
  return(n)
}

readinteger <- function()
{ 
  cat("Enter an input number: ")
  n <- readLines("stdin", n = 1)
  n <- as.integer(n)
  print(n)
  if (is.na(n)){
    n <- readinteger()
  }
  return(n)
}

readContinue <- function()
{ 
  activation_models <- c("yes","y","no","n","Yes","No","YES","NO")
  cat("Add more layer (yes/no): ")
  n <- readLines("stdin", n = 1)
  if (is.na(n) || !(n %in% activation_models)){
    n <- readActivation()
  }else{
    if(n == "yes"){return(TRUE)}
    if(n == "Yes"){return(TRUE)}
    if(n == "YES"){return(TRUE)}
    if(n == "y"){return(TRUE)}
    if(n == "no"){return(FALSE)}
    if(n == "No"){return(FALSE)}
    if(n == "NO"){return(FALSE)}
    if(n == "n"){return(FALSE)}
  }
}

readSaving <- function()
{ 
  activation_models <- c("yes","y","no","n","Yes","No","YES","NO")
  cat("Save the model (yes/no): ")
  n <- readLines("stdin", n = 1)
  if (is.na(n) || !(n %in% activation_models)){
    n <- readSaving()
  }else{
    if(n == "yes"){return(TRUE)}
    if(n == "Yes"){return(TRUE)}
    if(n == "YES"){return(TRUE)}
    if(n == "y"){return(TRUE)}
    if(n == "no"){return(FALSE)}
    if(n == "No"){return(FALSE)}
    if(n == "NO"){return(FALSE)}
    if(n == "n"){return(FALSE)}
  }
}

AddLayer <- function(model)
{
  enter_unit          <- readinteger()
  enter_activation    <- readActivation()
  model %>%layer_dense(units = enter_unit, activation = enter_activation)
  add <- readContinue() 
  if (add){
    AddLayer(model)
  } else {
    return(model)
  }
}
#------------------------------------------#


#------------------------------------------#
# Read inputs
#------------------------------------------#
Input.File       <- commandArgs(TRUE)[1]
Output.Dir       <- commandArgs(TRUE)[2]
Target           <- commandArgs(TRUE)[3]
Normalize        <- commandArgs(TRUE)[4]
Modelize         <- commandArgs(TRUE)[5]
EPOCH_           <- commandArgs(TRUE)[6]
BATCH_           <- commandArgs(TRUE)[7]
OPTIMIZER_       <- commandArgs(TRUE)[8]
ITER_            <- commandArgs(TRUE)[9]
#------------------------------------------#

#------------------------------------------#
#Test
#------------------------------------------#
Input.File       <- "C:/Users/ikugathas/Documents/PROJECTS/TOXsIgN/mat_chempsy_final_10793.tsv"
Output.Dir       <- "C:/Users/ikugathas/Documents/PROJECTS/TOXsIgN/"
#Input.File       <- "/home/genouest/irset/ikugathas/Projects/TOXsIgN/mat_chempsy_final.tsv"
#Output.Dir       <- "/home/genouest/irset/ikugathas/Projects/TOXsIgN/"
Target           <- "tissue"
Normalize        <- "no"
Modelize         <- "no"
EPOCH_           <- 100
BATCH_           <- 50
OPTIMIZER_       <- "adam"
ITER_            <- 1
#------------------------------------------#

#------------------------------------------#
# Map to predict to the rigth column
#------------------------------------------#
if(Target == "tissue")              {col_value = 2}
if(Target == "chemical")            {col_value = 3}
if(Target == "time")                {col_value = 6}
if(Target == "PE")                  {col_value = 7}
if(Target == "recDTC_group_cor")    {col_value = 8}
if(Target == "recDTC_group_euc")    {col_value = 9}
if(Target == "DTC_group_cor")       {col_value = 10}
if(Target == "DTC_group_euc")       {col_value = 11}
if(Target == "Hopach_group")        {col_value = 12}
if(Target == "recHopach_group")     {col_value = 13}
if(Target == "Mclust_group")        {col_value = 14}
if(Target == "recMclust_group")     {col_value = 15}
#------------------------------------------#

dir.create(c(Output.Dir),recursive=TRUE,showWarnings=FALSE)

#------------------------------------------#
#Libraries
#------------------------------------------#
#installation du package ?? partir du d??p??t CRAN
if("keras" %in% rownames(installed.packages()) == FALSE) { install.packages("keras",quiet = TRUE)}
if("caret" %in% rownames(installed.packages()) == FALSE) { install.packages("caret",quiet = TRUE)}
if("e1071" %in% rownames(installed.packages()) == FALSE) { install.packages("e1071",quiet = TRUE)}


#chargement de la librairie
library(keras)
library(caret)
library(e1071)
#installation environnement
#install_keras()
#--------------------------------------------#


#--------------------------------------------#
#chargement des donnees
#--------------------------------------------#
print("Loading data ...")
D                         <- read.table(Input.File,sep="\t",header=T,quote="",check.names=FALSE)
nb.group                  <- unique(D[,col_value])
Association.matrix        <- matrix(ncol=1,nrow=length(nb.group))
Association.matrix[,1]    <- unique(as.vector(D[,col_value]))
D_                        <- D
print("Data loaded")
#head(D)
D_[,col_value]                    <- as.numeric(D_[,col_value]) -1 # Convert data for encoder
nb.group.numeric                  <- unique(D_[,col_value])
rownames(Association.matrix)      <- nb.group.numeric
#--------------------------------------------#

#--------------------------------------------#
# Change to matrix
#--------------------------------------------#
print("Conversion dataframe to matrix ...")
data <- as.matrix(D_)
print("Done")
max_dim = length(colnames(data))
dim_model = dim(data)[2]-15 # Remove first columns 
output_number = length(unique(data[,col_value])) # Select column between 1-15
dimnames(data) <- NULL

input_number =  dim(data)[1]

#--------------------------------------------#

#--------------------------------------------#
# Normalize
#--------------------------------------------#
if(Normalize == "yes" || Normalize =="y"){
  data[,16:max_dim] <- normalize(data[,16:max_dim])
  summary(data)
}
#--------------------------------------------#
# Rank table
#--------------------------------------------#
Rank.matrix            <- matrix(0,ncol=1,nrow=output_number)
rownames(Rank.matrix)  <- c(1:output_number)

total_target = 0
total_acc = 0
#--------------------------------------------#

#--------------------------------------------#
# Create sequential model
#--------------------------------------------#
if (Modelize == "no"){
  print("Creating model ...")
  model <- keras_model_sequential()
  model %>%
    layer_dense(units=input_number, activation = "relu", input_shape = dim_model) %>%
    layer_dense(units = mean(c(input_number,output_number)), activation = "relu")%>%
    layer_dense(units = output_number, activation = "softmax")
  summary(model)
} else {
  model <- keras_model_sequential()
  model %>%layer_dense(units=input_number, activation = "relu", input_shape = dim_model)
  model <- AddLayer(model)
  model %>%layer_dense(units = output_number, activation = "softmax")
  summary(model)
}
#--------------------------------------------#

#--------------------------------------------#
# Define an optimizer
#--------------------------------------------#
if(OPTIMIZER_ == "sgd"){optmizer <- optimizer_sgd(lr = 0.01)}
if(OPTIMIZER_ == "adam"){optmizer <- "adam"}
#--------------------------------------------#

#--------------------------------------------#
# Compile
#--------------------------------------------#
print("Model compilation ...")
model %>%
  compile(loss = 'categorical_crossentropy',
          optimizer = optmizer,
          metrics = 'accuracy')
#--------------------------------------------#


#------------------------------------------------------------------------------------------------------------------------------------#
#                                                     START ITERATION                                                                #
#------------------------------------------------------------------------------------------------------------------------------------#
Matrix.stat_iter              <- matrix(nrow = ITER_ + 1,ncol = 7)
colnames(Matrix.stat_iter)    <- c("Iteration","Model Accuracy","Group prediction precision (mean)","Group prediction recall (mean)","Train dataset","Validation dataset","Group predicted")



for(iter_round in 1:ITER_){
  
      #--------------------------------------------#
      # Data partition
      #--------------------------------------------#
      print("Data partition ...")
      set.seed(1234)
      # unique_val <- length(unique(data[,col_value])) -1
      # 
      # 
      # training          <- matrix(ncol=max_dim-9, nrow =0)
      # test              <- matrix(ncol=max_dim-9, nrow =0)
      # trainingtarget    <- c()
      # testtarget        <- c()
      # 
      # for(i in 0:unique_val){
      #   if(i<10){
      #     sub_data <- data[which(data[,col_value] == sprintf("  %s",i)),]
      #   }
      #   if(i>=10 && i<100){
      #     sub_data <- data[which(data[,col_value] == sprintf(" %s",i)),]
      #   }
      #   if(i>=100){
      #     sub_data <- data[which(data[,col_value] == sprintf("%s",i)),]
      #   }
      #   
      #   ind <- sample(2, nrow(sub_data), replace = T, prob = c(0.7, 0.3))
      #   #Split the data
      #   training_ <- sub_data[ind==1, 10:max_dim]
      #   test_     <- sub_data[ind==2, 10:max_dim]
      #   training <- rbind(training,training_)
      #   test <- rbind(test,test_)
      #   
      #   # Split the class attribute
      #   trainingtarget <- c(trainingtarget,sub_data[ind==1, col_value]) # Set number between 1 - 9 (8 == group_cor)
      #   testtarget <- c(testtarget,sub_data[ind==2, col_value])
      # }
      
      #--------------------------------------------#
      ind <- sample(2, nrow(data), replace = T, prob = c(0.7, 0.3))
      
      #Split the data
      training <- apply(data[ind==1, 16:max_dim],2,as.numeric)
      test <- apply(data[ind==2, 16:max_dim],2,as.numeric)
      
      # Split the class attribute
      trainingtarget <- data[ind==1, col_value] # Set number between 1 - 9 (8 == group_cor)
      testtarget <- data[ind==2, col_value]
      
      #--------------------------------------------#
      
      #--------------------------------------------#
      # Data Encoding
      #--------------------------------------------#
      print("Data encoding")
      trainLabels <- to_categorical(trainingtarget)
      testLabels <- to_categorical(testtarget)
      #print(dim(testLabels))
      #--------------------------------------------#
      
      #--------------------------------------------#
      # Fit model
      #--------------------------------------------#
      print("Fiting model ...")
      history <- model %>%
        fit(training,
            trainLabels,
            epoch = EPOCH_,
            batch_size = BATCH_,
            validation_split = 0.2)
      #--------------------------------------------#
      
      #--------------------------------------------#
      # Evaluate model with test data
      #--------------------------------------------#
      print("Model evaluation")
      model1 <- model %>%
        evaluate(test, testLabels)
      cat("Model Accuracy: ", model1$acc*100,"%")
      total_acc <- total_acc + model1$acc*100
      #--------------------------------------------#
      
      
      #--------------------------------------------#
      #PLOT
      #--------------------------------------------#
      
      png(sprintf("%s/model_history_%s",Output.Dir,iter_round))
      plot(history)
      dev.off()
      
      #--------------------------------------------#
      # Save model
      #--------------------------------------------#
      save_model_hdf5(model, sprintf("%s/model.h5"  ,Output.Dir))
      print("Model saved")
      #--------------------------------------------#
      
      #--------------------------------------------#
      # Prediction & confusion matrix - test data
      #--------------------------------------------#
      # Evaluate on test data and labels
      prob <- model %>%
        predict_proba(test)
      
      pred <- model %>%
        predict_classes(test)
      u         <- intersect(as.numeric(pred),as.numeric(testtarget))
      table1 <- table(Predicted = as.numeric(pred),Actual =as.numeric(testtarget))
      
      #--------------------------------------------#
      
      #--------------------------------------------#
      # Sensitivity / Specificity
      #--------------------------------------------#
      # Create subset because at least one class in the testing set that is never predicted
      # see: https://stackoverflow.com/questions/19871043/r-package-caret-confusionmatrix-with-missing-categories
      Group_stat           <- matrix(nrow = length(u),ncol=8)
      colnames(Group_stat) <- c("Group","TP","FP","FN","Precision [TP/(TP+FP)]","Recall (Sensibility) [TP/(FN+TP)]","TN","spec")
      Model_precision      <- 0
      Model_recall         <- 0
      
      for (x in 1:length(u)) {
        i <- u[x]
        TP_ <- table1[as.character(i), as.character(i)] #diagonal position
        FP_ <- sum(table1[,as.character(i)])-table1[as.character(i), as.character(i)] #sum of column i (without main diagonal)
        FN_ <- sum(table1[as.character(i),])-table1[as.character(i), as.character(i)] #sum of row i (without main diagonal),
        precision <- TP_/(TP_+FP_)
        recall <- TP_/(FN_+TP_)
        TN_ <- sum(table1)-(TP_+FP_+FN_)
        spec <- TN_/(TN_+FP_)
        
        Group_stat[x,1]    <- Association.matrix[as.character(i),1]
        Group_stat[x,2]    <- TP_
        Group_stat[x,3]    <- FP_
        Group_stat[x,4]    <- FN_
        Group_stat[x,5]    <- precision
        Group_stat[x,6]    <- recall
        Group_stat[x,7]    <- TN_
        Group_stat[x,8]    <- spec
        Group_stat[x,9]    <- roccurve
        Model_precision    <- Model_precision + precision
        Model_recall       <- Model_recall + recall
      }
      write.table(Group_stat,file=sprintf("%s/Groups_statistics_%s.tsv",Output.Dir,iter_round),sep = "\t",row.names=FALSE, col.names=TRUE)
      Model_precision    <- Model_precision/length(u)
      Model_recall       <- Model_recall/length(u)
      #plot(Group_stat[,"roccurve"])
      
      
      #--------------------------------------------#
      # Ranking
      #--------------------------------------------#
      final.df <- cbind(prob,pred,testtarget)
      total_target <- total_target + length(testtarget)
      
      for (i in 1:length(testtarget)){
        list_test <- as.numeric(final.df[i,1:length(nb.group)])
        list_orserINdex <- sort(list_test, decreasing = TRUE, index.return = TRUE)
        pos_target <- as.numeric(final.df[i,(length(nb.group)+2)])+1
        rank <- which( list_orserINdex$ix == pos_target)
        Rank.matrix[rank] <- Rank.matrix[rank] + 1
      }
      colnames(Matrix.stat_iter)          <- c("Iteration","Model Accuracy","Group prediction precision (mean)","Group prediction recall (mean)","Train dataset","Validation dataset","Group predicted")
      
      #
      # Iteration summary
      #
      
      Matrix.stat_iter[iter_round,1]      <- iter_round
      Matrix.stat_iter[iter_round,2]      <- model1$acc*100
      Matrix.stat_iter[iter_round,3]      <- Model_precision
      Matrix.stat_iter[iter_round,4]      <- Model_recall
      Matrix.stat_iter[iter_round,5]      <- length(trainLabels)
      Matrix.stat_iter[iter_round,6]      <- length(testLabels)
      Matrix.stat_iter[iter_round,7]      <- length(unique(pred))
      
}

accumulated_rank <- c()
acc = 0
for (rank in 1:output_number){
  acc = acc + Rank.matrix[rank,1]
  accumulated_rank <- c(accumulated_rank,acc)
}
percent_acc <- (accumulated_rank*100)/total_target

png(sprintf("%s/Cumulative_ranking.png",Output.Dir))
plot(x = 1:length(nb.group),y=percent_acc,ylim = c(0,100),col="blue", type="l",xlab = "Rank index",ylab = "Cumulative %",main="")
dev.off()

total_acc <- total_acc/ITER_
write.table(Group_stat,file=sprintf("%s/Model_statistics.tsv",Output.Dir),sep = "\t",row.names=FALSE, col.names=TRUE)
write.table(Association.matrix,file=sprintf("%s/association_matrix.tsv",Output.Dir),sep = "\t",row.names=TRUE, col.names=FALSE)

quit()

  #--------------------------------------------#
  # ROC curve binary
  #--------------------------------------------#
    #library(ROCR)
    #predtry <- prediction(as.vector(pred),testtarget)
    #perftry = performance(predtry,"tpr","fpr")
    #png(sprintf("%s/ROC_curve.png",Output.Dir))
    #plot(perftry)
    #dev.off()
    #auctry = performance(predtry,"auc")
    #auctry@y.values[[1]]

  #--------------------------------------------#
  # ROC curve multi-class
  #--------------------------------------------#
    #library(pROC)
    #perftry = multiclass.roc(as.vector(pred),as.numeric(testtarget))
    #rs = perftry[['rocs']]
    #png(sprintf("%s/ROC_curve.png",Output.Dir))
    #plot.roc(rs[[1]])
    #dev.off()





