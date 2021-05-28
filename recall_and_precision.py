import vcf


def precision(vcfname,truthname):
        true_run=vcf.Reader(open(truthname,"r"))
        insertion=open("insertions.txt","a")
        deletions=open("deletions.txt","a")
        bnds=open("breakpoints.txt","a")

        vcf_reader=vcf.Reader(open(vcfname,"r"))

        true_pos=0
        false_pos=0

        for record in vcf_reader: #Parse through vcf file
                test_truth=true_pos 
                if record.INFO["SVTYPE"]=="BND": #Checks if vcf is a breakpoint
                        A=record.ALT[0] #record.ALT contains info needed to compare breakpoints
                        for truth in true_run: #Parse through truth set
                                B=truth.ALT[0]
                                if not "BND" in truth.ID: #If not a BND skip
                                        continue
                                if A.chr==B.chr and A.orientation==B.orientation and A.remoteOrientation==B.remoteOrientation and abs(A.pos-B.pos)<=10 and abs(record.POS - truth.POS) <= 10: 
                                        true_pos+=1 
                else:
                        for truth in true_run: #All other variants
                                if "BND" in truth.ID:
                                        continue
                                if record.INFO["SVTYPE"]==truth.INFO["SVTYPE"] and record.CHROM == truth.CHROM and abs(record.POS - truth.POS) <= 10 and abs(record.INFO["SVLEN"]-truth.INFO["SVLEN"])<=20:
                                        true_pos+=1
                if true_pos==test_truth: #If it isn't a true positive, must be a false positive
                        false_pos+=1
                true_run=vcf.Reader(open(truthname,"r")) #Reopen truthset from start
        f.write(str(true_pos)+" " + str(false_pos)+"\n") #Write true positives and false positives to file
        f.close()
