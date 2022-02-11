#--------------------------------------------#
Reduced.Data        <- commandArgs(TRUE)[1]
Group.Dir           <- commandArgs(TRUE)[2]
HomoloGene.File     <- commandArgs(TRUE)[3]
Output.Dir          <- commandArgs(TRUE)[4]
#--------------------------------------------#

#--------------------------------------------#
load(Reduced.Data)
#--------------------------------------------#

#--------------------------------------------#
HomoloGene.Data <- gsub(" ","",as.matrix(read.table(HomoloGene.File,sep="\t",quote="",header=FALSE)))
rownames(HomoloGene.Data) <- HomoloGene.Data[,3]
#--------------------------------------------#

#--------------------------------------------#
Data <- Reduced.Data.bin
Data <- Data[intersect(rownames(Data),rownames(HomoloGene.Data)),,drop=FALSE]
rownames(Data) <- HomoloGene.Data[rownames(Data),1]
t <- table(rownames(Data))
Data <- Data[ rownames(Data) %in% rownames(t)[which(as.vector(t) == 1)] , ,drop=FALSE]
#--------------------------------------------#

#--------------------------------------------#
Group.Files <- sprintf("%s/%s",Group.Dir,list.files(path=Group.Dir,pattern=".txt"))
Group.Names <- gsub(".txt","",basename(Group.Files))
Medoid.Data   <- matrix(0,nrow=nrow(Data),ncol=length(Group.Files),dimnames=list(rownames(Data),Group.Names))
Centroid.Data <- matrix(0,nrow=nrow(Data),ncol=length(Group.Files),dimnames=list(rownames(Data),Group.Names))

Samples2Groups <- matrix(0,nrow=ncol(Data),ncol=length(Group.Names),dimnames=list(colnames(Data),Group.Names))
for (i in 1:length(Group.Files)) {
    Group.File <- Group.Files[i]
    Group.Name <- Group.Names[i]
    Group.IDs  <- as.character(as.matrix(read.table(Group.File,header=FALSE,sep='\t',quote=""))[,1])
    Samples2Groups[Group.IDs,Group.Name] <- 1

    Group.name <- gsub(".txt","",basename(Group.File))
    cat(Group.File,"->",Group.name,"\n")

    Medoid.Data[,Group.Name] <- apply(Data[,Group.IDs],1,median,na.rm=FALSE)
    Centroid.Data[,Group.Name] <- apply(Data[,Group.IDs],1,mean,na.rm=FALSE)
}

save(Data,Medoid.Data,Centroid.Data,Samples2Groups, file=sprintf("%s/method.RData",Output.Dir))

#--------------------------------------------#
quit()
