# refs/ (runtime — contents are gitignored)

Reference genomes, the dRep-dereplicated DB, the bowtie2 index (`vagref.*`), the
scaffold-to-bin map (`vagref.stb`), and downloaded helper binaries (e.g. NCBI
`datasets`) live here. None are committed — rebuild them with `scripts/02_build_ref.sh`
after placing genomes in `refs/genomes/`.
