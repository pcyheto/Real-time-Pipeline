
import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

if __name__ == "__main__":
    patterns="*"
    ignore_patterns=""
    ignore_directories=True
    case_sensitive=True
    my_event_handler=PatternMatchingEventHandler(patterns,ignore_patterns,ignore_directories,case_sensitive)

def on_created(event): #Runs snakemake if file has been created
        print("file added")
        subprocess.run("snakemake --cores 1",shell=True)

my_event_handler.on_created = on_created

path="./data/fastq_pass/" #File that data will be added to
go_recursively=True
my_observer=Observer()
my_observer.schedule(my_event_handler,path,recursive=go_recursively)

start=time.time()
j=1
f=open("merge_benchmarking.txt","a") #File for merging benchmarks
g=open("cuteSV_benchmarking.txt","a") #File for cuteSV benchmarks

my_observer.start() #Start watching
try:
    while True:
        if (time.time()-start)>=900:
            vcf_name="vcf_files/"+str(j)+".vcf"
            bam_name="merged/merged_"+str(j)+".bam"
            dirs=os.listdir("./sorted")
            if len(dirs)==0:
                continue #Skips the rest of the loop if no files available to merge
            merge_str="samtools merge "+bam_name+" " #Start creation of merge string
            for file in dirs: 
                merge_str=merge_str+"sorted/"+file+" "
            if j>1: #There won't be a merged_0.bam
                merge_str=merge_str+"merged/merged_"+str(j-1)+".bam"
            merge_start=time.time() #Time merging
            subprocess.run(merge_str,shell=True) #Merge files
            merge_end=time.time()
            f.write(str(merge_end-merge_start)+"\n")
            if os.path.isfile(bam_name): #Check merged file exists
                print("Merge successful")
            else:
                continue #If merging was unsuccessful, skip rest of loop 
            subprocess.run("samtools index "+bam_name,shell=True)
            cute_start=time.time() #Time cuteSV
            subprocess.run("cuteSV -t 4 -s 9 --max_cluster_bias_INS 100 --diff_ratio_merging_INS 0.3 --max_cluster_bias_DEL 100 --diff_ratio_merging_DEL 0.3 "+bam_name+" data/reference.fa "+vcf_name+" cuteSV/",shell=True)
            cute_end=time.time()
            g.write(str(cute_end-cute_start)+"\n")
            subprocess.run("mkdir merged_bam/"+str(j),shell=True)
            for file in dirs: #Move merged files
                subprocess.run("mv sorted/"+file+" merged_bam/"+str(j)+"/",shell=True)
            j=j+1
            print("check")
            start=time.time()
        time.sleep(60) #Wait 1 minute before checking for added files
                           
except KeyboardInterrupt: #On interruption, close files and stop observer
        f.close()
        g.close()
        my_observer.stop()
        my_observer.join()
