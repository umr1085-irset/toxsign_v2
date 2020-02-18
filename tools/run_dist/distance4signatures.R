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
colnames(New.Data) <- c("Signature", "r", "R", "n", "N", "Ratio", "Zscore", "Pvalue", "AdjustedPvalue", "EuclideanDistance", "CorrelationDistance", "HomologeneIds")
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
   New.Data[Sign.Name,2]  <- r
   New.Data[Sign.Name,3]  <- R
   New.Data[Sign.Name,4]  <- n
   New.Data[Sign.Name,5]  <- N
   New.Data[Sign.Name,6]  <- rR
   New.Data[Sign.Name,7]  <- z.dist
   New.Data[Sign.Name,8]  <- p.dist
   New.Data[Sign.Name,10] <- euc.dist
   New.Data[Sign.Name,11] <- cor.dist
   New.Data[Sign.Name,12] <- paste(r.IDs,collapse="|")
}
#--------------------------------------------#

#--------------------------------------------#
New.Data <- New.Data[which(as.double(New.Data[,2]) > 0),,drop=FALSE]
#New.Data <- New.Data[which(as.double(New.Data[,2]) != as.double(New.Data[,3]) & as.double(New.Data[,2]) != as.double(New.Data[,4])),,drop=FALSE]
New.Data[,9] <- p.adjust(as.double(New.Data[,8]),method="BH")
#--------------------------------------------#

#--------------------------------------------#
New.Data <- New.Data[sort(as.double(New.Data[,7]),decreasing=TRUE,index.return=TRUE)$ix,]
New.Data <- New.Data[sort(as.double(New.Data[,8]),decreasing=FALSE,index.return=TRUE)$ix,]
#--------------------------------------------#

#--------------------------------------------#
write.table(gsub("^ +","",New.Data),file=Out.File,row.names=FALSE,col.names=TRUE,sep="\t",quote=FALSE)
#--------------------------------------------#

quit()
