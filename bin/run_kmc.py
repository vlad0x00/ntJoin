#!/usr/bin/env python3
"""
Runs KMC kmer-counting on an assembly, basing the maximum memory on the supplied genome size (bp)
Written by Lauren Coombe (@lcoombe)
"""

import argparse
import shlex
import subprocess
from read_fasta import read_fasta

def main():
    "Run KMC kmer counting"
    parser = argparse.ArgumentParser(description="Run KMC kmer counting on an assembly",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("FASTA", help="Fasta file")
    parser.add_argument("-l", help="Minimum length threshold (bp) [500]", default=500, type=int)
    parser.add_argument("-g", help="Approximate genome size (bp)", required=True, type=float)
    parser.add_argument("-k", help="Kmer size", required=True, type=int)
    parser.add_argument("-t", help="Number of threads [4]", type=int, default=4)
    parser.add_argument("-c", help="Lower threshold for kmer counting [2]", default=2, type=int)
    parser.add_argument("-p", help="Output prefix [fastafile.k<k>.w<w>.kmc]", type=str, required=False)
    args = parser.parse_args()

    # Make TMP directory
    tmpdir = args.FASTA + "k" + str(args.k) + ".w" + str(args.l) + ".kmc.tmp"
    cmd = "mkdir -p " + tmpdir
    print(cmd)
    cmd_shlex = shlex.split(cmd)
    ret = subprocess.call(cmd_shlex)
    if ret != 0:
        raise subprocess.CalledProcessError(ret, cmd_shlex)

    # Filter the fasta file based on length threshold
    filtered_fasta_name = args.FASTA + "k" + str(args.k) + ".w" + str(args.l)+ "." + str(args.l) + "plus.fa"
    filtered_fasta = open(filtered_fasta_name, 'w')
    with open(args.FASTA, 'r') as fasta:
        for header, seq, _, _ in read_fasta(fasta):
            if len(seq) >= args.l:
                filtered_fasta.write(">" + header + "\n" + seq + "\n")
    filtered_fasta.close()

    # Run KMC (1st step)
    max_mem = args.g/1e9 * 2.0
    max_mem = max(max_mem, 1) # KMC require at least 1GB of RAM
    kmc_out_prefix = args.p if args.p is not None else "%s.k%d.w%d.kmc" % (args.FASTA, args.k, args.l)
    cmd = "kmc -ci%d -k%d -m%d -t%d -fm %s %s %s" % \
          (args.c, args.k, max_mem, args.t, filtered_fasta_name, kmc_out_prefix, tmpdir)
    print(cmd)
    cmd_shlex = shlex.split(cmd)
    ret = subprocess.call(cmd_shlex)
    if ret != 0:
        raise subprocess.CalledProcessError(ret, cmd_shlex)

    # Run KMC (2nd step)
    cmd = "kmc_dump %s %s" % (kmc_out_prefix, kmc_out_prefix + ".tsv")
    print(cmd)
    cmd_shlex = shlex.split(cmd)
    ret = subprocess.call(cmd_shlex)
    if ret != 0:
        raise subprocess.CalledProcessError(ret, cmd_shlex)

    # Clean-up tmp files
    cmd = "rm -r %s %s" % (tmpdir, filtered_fasta_name)
    cmd_shlex = shlex.split(cmd)
    ret = subprocess.call(cmd_shlex)
    if ret != 0:
        raise subprocess.CalledProcessError(ret, cmd_shlex)


if __name__ == "__main__":
    main()
