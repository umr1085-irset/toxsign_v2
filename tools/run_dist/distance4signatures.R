#--------------------------------------------#
Sign.In.File  <- commandArgs(TRUE)[1]
RData.File    <- commandArgs(TRUE)[2]
Out.File      <- commandArgs(TRUE)[3]
#--------------------------------------------#

#--------------------------------------------#
Sign.In.Name <- gsub("\\.sign$","",basename(Sign.In.File))

load(RData.File)
if (exists("signmatrix") == FALSE) {
   cat("signmatrix does not exist\n")
}
#--------------------------------------------#
cat(dim(signmatrix))
#--------------------------------------------#
New.Data <- matrix(NA,ncol=12,nrow=nrow(signmatrix))
colnames(New.Data) <- c("Signature", "EuclideanDistance", "CorrelationDistance", "AdjustedPvalue", "Pvalue", "Ratio", "r", "R", "n", "N", "Zscore", "HomologeneIds")
rownames(New.Data) <- rownames(signmatrix)
Sign.In.values <- as.double(signmatrix[Sign.In.Name,])
for (Sign.Name in rownames(signmatrix)) {
   Sign.values    <- as.double(signmatrix[Sign.Name,])
   indexes        <- which(is.na(Sign.In.values) == FALSE & is.na(Sign.values) == FALSE)
   sub.Sign.values    <- Sign.values[indexes]
   sub.Sign.In.values <- Sign.In.values[indexes]
   #--------------------------------------------#

   #--------------------------------------------#
   euc.dist <- sqrt(sum((sub.Sign.In.values - sub.Sign.values) ^ 2))
   cor.dist <- cor(sub.Sign.In.values,sub.Sign.values)
   #--------------------------------------------#
   
   #--------------------------------------------#
   N <- length(sub.Sign.values)
   R <- length(which(sub.Sign.In.values != 0))
   n <- length(which(sub.Sign.values != 0))
   r.IDs <- colnames(signmatrix)[indexes[which(sub.Sign.values == sub.Sign.In.values & sub.Sign.values != 0)]]
   r <- length(r.IDs)
   rR <- r/(R+n-r)
   #--------------------------------------------#

   p.dist <- phyper(r-1,n,N-n,R,lower.tail=FALSE)
   z.dist <- (r-n*R/N) / sqrt( (n*R/N) * (1-R/N) * (1-(n-1)/(N-1)))
   #--------------------------------------------#
   New.Data[Sign.Name,1]  <- Sign.Name
   New.Data[Sign.Name,2]  <- euc.dist
   New.Data[Sign.Name,3]  <- cor.dist
   New.Data[Sign.Name,4]  <- p.dist
   New.Data[Sign.Name,5]  <- z.dist
   New.Data[Sign.Name,6]  <- rR
   New.Data[Sign.Name,7]  <- r
   New.Data[Sign.Name,8]  <- R
   New.Data[Sign.Name,9] <- n
   New.Data[Sign.Name,10] <- N
   New.Data[Sign.Name,12] <- paste(r.IDs,collapse="|")

colnames(New.Data) <- c("Signature", "Euclidean dist", "Correlation dist", "Adj Pvalue", "Pvalue", "r/R", "r", "R", "n", "N", "Zscore", "HomologeneIds")

}
#--------------------------------------------#

#--------------------------------------------#
New.Data <- New.Data[which(as.double(New.Data[,7]) > 0),,drop=FALSE]
New.Data[,11] <- p.adjust(as.double(New.Data[,4]),method="BH")
#--------------------------------------------#

#--------------------------------------------#
New.Data <- New.Data[sort(as.double(New.Data[,5]),decreasing=TRUE,index.return=TRUE)$ix,]
New.Data <- New.Data[sort(as.double(New.Data[,4]),decreasing=FALSE,index.return=TRUE)$ix,]
#--------------------------------------------#

#--------------------------------------------#
write.table(gsub("^ +","",New.Data),file=Out.File,row.names=FALSE,col.names=TRUE,sep="\t",quote=FALSE)
#--------------------------------------------#

quit()
