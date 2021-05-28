IDS, = glob_wildcards("data/fastq_pass/{id}.fastq") #Create list of ids from fastq files

rule all:
    input: expand("sorted/{ids}.bam",ids=IDS) 

rule map: #Map against reference
    input:
        REF="data/ref.mmi", #Use ref.mmi instead of ref.fa for speed, created using minimap2
        FASTQ="data/fastq_pass/{ids}.fastq"
    output:
        "mapped/{ids}.sam"
    benchmark:
        "benchmarks/map/{ids}.bwa.benchmark.txt"
    run:
        shell("minimap2 -ax map-ont {input.REF} {input.FASTQ} > {output}")
        shell("mv {input.FASTQ} data_used/") #remove .fastq from data file

rule samtools_sort: #Sort .sam into .bam
    input:
        "mapped/{ids}.sam"
    output:
        "sorted/{ids}.bam"
    benchmark:
        "benchmarks/sort/{ids}.bwa.benchmark.txt"
    shell:
        "samtools sort -T sorted/{wildcards.ids} "
        "-O bam {input} > {output}"
