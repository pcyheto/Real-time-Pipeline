rule all:
    input:

rule map:
    input:
        "data/reference.fa",
        "data/{sample}.fastq"
    output:
        "mapped/{sample}.sam"
    shell:
        "minimap2 -ax map-ont {input} > {output}"

rule samtools_sort:
    input:
        "mapped/{sample}.sam"
    output:
        "sorted/{sample}.bam"
    shell:
        "samtools sort -T sorted/{wildcards.sample} "
        "-O bam {input} > {output}"

rule samtools_index:
    input:
        "sorted/{sample}.bam"
    output:
        "sorted/{sample}.bam.bai"
    shell:
        "samtools index {input}"

rule call_cutesv:
    input:
        BAM = "sorted/{sample}.bam",
        REF = "data/reference.fa",
        BAI = "sorted/{sample}.bam.bai"
    output:
        VCF = "vcf_files/{sample}.vcf"
    params:
        min_read_support = 9,
    benchmark:
        repeat("benchmarks/{sample}.bwa.benchmark.txt",5)
    shell:
        "cuteSV -t 4 -s {params.min_read_support} --report_readid --max_cluster_bias_INS 100 --diff_ratio_merging_INS 0.3 --max_cluster_bias_DEL 100 --diff_ratio_merging_DEL 0.3 {input.BAM} {input.REF} {output.VCF} cuteSV/ "
