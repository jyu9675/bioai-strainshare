#!/usr/bin/env bash
# List all inStrain/bowtie2/python processes with runtime, to find orphans/hangs.
ps -eo pid,etime,pcpu,comm,args | grep -E "inStrain|bowtie2|StrainPhlAn" | grep -v grep
