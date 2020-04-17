#--------------------------------------------#
Sign.File           <- commandArgs(TRUE)[1]
Output.Dir          <- commandArgs(TRUE)[2]
method.RData        <- commandArgs(TRUE)[3]
#--------------------------------------------#

#--------------------------------------------#
RLIBS<-"/opt/toxsign/var/upload/admin/soft/R/3.2.3/libs/"
.libPaths(RLIBS)
if("FactoMineR" %in% rownames(installed.packages()) == FALSE) {install.packages("FactoMineR")}
library(FactoMineR)
load(method.RData)
#--------------------------------------------#

#--------------------------------------------#
Sign.Data <- gsub(" ","",as.matrix(read.table(Sign.File,header=FALSE,blank.lines.skip=TRUE,fill=TRUE,sep='\t',quote="")))
rownames(Sign.Data) <- Sign.Data[,3]
Sign.Data <- matrix(as.double(Sign.Data[,5]),ncol=1,dimnames=list(rownames(Sign.Data),c("Sign")))
t <- table(rownames(Sign.Data))
Sign.Data <- Sign.Data[ rownames(Sign.Data) %in% rownames(t)[which(as.vector(t) == 1)] , ,drop=FALSE]
#--------------------------------------------#


#--------------------------------------------#
Common.IDs        <- intersect( rownames(Data), rownames(Sign.Data) )

Red.Data          <- Data[Common.IDs,,drop=FALSE]
Red.Medoid.Data   <- Medoid.Data[Common.IDs,,drop=FALSE]
Red.Centroid.Data <- Centroid.Data[Common.IDs,,drop=FALSE]
Red.Sign.Data     <- Sign.Data[Common.IDs,,drop=FALSE]
#--------------------------------------------#

#--------------------------------------------#
Medoid.cor.values <- as.matrix(apply(Red.Medoid.Data,2,function (X) cor(X, Red.Sign.Data[,1])))
Medoid.ed.values  <- as.matrix(apply(Red.Medoid.Data,2,function (X) sqrt(sum((X - Red.Sign.Data[,1]) ^ 2))))
Centroid.cor.values <- as.matrix(apply(Red.Centroid.Data,2,function (X) cor(X, Red.Sign.Data[,1])))
Centroid.ed.values  <- as.matrix(apply(Red.Centroid.Data,2,function (X) sqrt(sum((X - Red.Sign.Data[,1]) ^ 2))))

All.cor.values <- as.matrix(apply(Red.Data,2,function (X) cor(X, Red.Sign.Data[,1])))
All.ed.values <- as.matrix(apply(Red.Data,2,function (X) sqrt(sum((X - Red.Sign.Data[,1]) ^ 2))))
Closest.cor.values <- matrix(NA,ncol=1,nrow=ncol(Samples2Groups),dimnames=list(colnames(Samples2Groups),c("dist")))
Closest.ed.values <- matrix(NA,ncol=1,nrow=ncol(Samples2Groups),dimnames=list(colnames(Samples2Groups),c("dist")))
for (Group.Name in rownames(Closest.cor.values)) {
    Group.IDs        <- rownames(Samples2Groups)[which(Samples2Groups[,Group.Name] == 1)]

    Closest.Group.ID <- Group.IDs[sort(All.cor.values[Group.IDs,1],decreasing=TRUE,index.return=TRUE)$ix[1]]
    Closest.cor.values[Group.Name,1] <- All.cor.values[Closest.Group.ID,]

    Closest.Group.ID <- Group.IDs[sort(All.ed.values[Group.IDs,1],decreasing=FALSE,index.return=TRUE)$ix[1]]
    Closest.ed.values[Group.Name,1] <- All.ed.values[Closest.Group.ID,]
}
#--------------------------------------------#

#--------------------------------------------#
PCA.Red.Medoid.Data   = PCA( t(cbind(Red.Sign.Data,Red.Medoid.Data  )) , scale.unit=FALSE , ncp=ncol(Red.Medoid.Data)   , graph=F,ind.sup=c(1))
ncp.PCA.Red.Medoid.Data = which(PCA.Red.Medoid.Data$eig[,3]>90)[1]-1
if ( ncp.PCA.Red.Medoid.Data < 2 ) { ncp.PCA.Red.Medoid.Data = 2 }
PCA.Red.Medoid.Data   = PCA( t(cbind(Red.Sign.Data,Red.Medoid.Data  )) , scale.unit=FALSE , ncp=ncp.PCA.Red.Medoid.Data   , graph=F,ind.sup=c(1))
PCA.Red.Medoid.Data   = t( rbind( PCA.Red.Medoid.Data$ind.sup$coord , PCA.Red.Medoid.Data$ind$coord ) )

PCA.Red.Centroid.Data = PCA( t(cbind(Red.Sign.Data,Red.Centroid.Data)) , scale.unit=FALSE , ncp=ncol(Red.Centroid.Data) , graph=F,ind.sup=c(1))
ncp.PCA.Red.Centroid.Data = which(PCA.Red.Centroid.Data$eig[,3]>90)[1]-1
if ( ncp.PCA.Red.Centroid.Data < 2 ) { ncp.PCA.Red.Centroid.Data = 2 }
PCA.Red.Centroid.Data = PCA( t(cbind(Red.Sign.Data,Red.Centroid.Data)) , scale.unit=FALSE , ncp=ncp.PCA.Red.Centroid.Data , graph=F, ind.sup=c(1))
PCA.Red.Centroid.Data = t( rbind( PCA.Red.Centroid.Data$ind.sup$coord ,  PCA.Red.Centroid.Data$ind$coord ) )

PCA.Medoid.cor.values   <- as.matrix(apply( PCA.Red.Medoid.Data[,2:ncol(PCA.Red.Medoid.Data)] ,2,function (X) cor(X, PCA.Red.Medoid.Data[,1,drop=FALSE] )))
PCA.Centroid.cor.values <- as.matrix(apply( PCA.Red.Centroid.Data[,2:ncol(PCA.Red.Centroid.Data)] ,2,function (X) cor(X, PCA.Red.Centroid.Data[,1,drop=FALSE] )))

PCA.Medoid.ed.values   <- as.matrix(apply( PCA.Red.Medoid.Data[,2:ncol(PCA.Red.Medoid.Data)] ,2,function (X) sqrt(sum((X - PCA.Red.Medoid.Data[,1,drop=FALSE]) ^ 2))))     
PCA.Centroid.ed.values <- as.matrix(apply( PCA.Red.Centroid.Data[,2:ncol(PCA.Red.Centroid.Data)] ,2,function (X) sqrt(sum((X - PCA.Red.Centroid.Data[,1,drop=FALSE]) ^ 2))))  
#--------------------------------------------#

#--------------------------------------------#
m <- matrix(nrow=14,ncol=ncol(PCA.Red.Medoid.Data),dimnames=list( c("Class" , "Sample" , "X" , "Y" , "Correlation - Centroid" , "Correlation - Medoid" , "Correlation - Closest" , "Correlation - PCA(Medoid)" , "Correlation - PCA(Centroid)", "Euclidean distance - Centroid" , "Euclidean distance - Medoid" , "Euclidean distance - Closest" , "Euclidean distance - PCA(Medoid)" , "Euclidean distance - PCA(Centroid)")    , colnames(PCA.Red.Medoid.Data)))

m[1,] <- colnames(PCA.Red.Medoid.Data)
m[2,] <- colnames(PCA.Red.Medoid.Data)
m[3,] <- PCA.Red.Medoid.Data[1,]
m[4,] <- PCA.Red.Medoid.Data[2,]

m[5 ,] <- c(1,as.vector(Medoid.cor.values      ))
m[6 ,] <- c(1,as.vector(Centroid.cor.values    ))
m[7 ,] <- c(1,as.vector(Closest.cor.values     ))
m[8 ,] <- c(1,as.vector(PCA.Medoid.cor.values  ))
m[9 ,] <- c(1,as.vector(PCA.Centroid.cor.values))
m[10,] <- c(0,as.vector(Medoid.ed.values      ))
m[11,] <- c(0,as.vector(Centroid.ed.values    ))
m[12,] <- c(0,as.vector(Closest.ed.values     ))
m[13,] <- c(0,as.vector(PCA.Medoid.ed.values  ))
m[14,] <- c(0,as.vector(PCA.Centroid.ed.values))

write.table(m, file=sprintf("%s/output.txt",Output.Dir),quote=FALSE,sep="\t",col.names=FALSE,row.names=TRUE)
#--------------------------------------------#

quit()
