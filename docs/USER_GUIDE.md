# strainshare — Step-by-Step User Guide

*A beginner-friendly guide. You do **not** need to know Python. Just follow the steps for your
operating system and copy-paste the commands.*

---

## What this tool does (in plain words)

You give strainshare bacterial DNA data from **two body sites of the same person** (for example a
person's **gut** and **vagina**). It tells you whether the two sites carry the **exact same bacterial
strain**, and whether that sharing is real biology or just **contamination**. It works for any pair of
sites (oral↔gut, mother↔infant, etc.).

## Two ways to use it — pick your level

| | What you need | Difficulty |
|---|---|---|
| **Level 1 — Analysis** | You already have a comparison table (or use the example data we ship). Runs on **any computer**, no biology tools. | Easy |
| **Level 2 — Full pipeline** | You start from raw sequencing files (FASTQ). Needs bioinformatics tools; **Mac/Linux or Windows-with-WSL**. | Advanced |

**Most people should start with Level 1** using the example data — it proves everything works in 5 minutes.

---

# PART 1 · Set up your computer

You only do this once. The goal is to get a **terminal** (a text window where you type commands) and a
tool called **conda** that installs everything for you.

<details open>
<summary><h2>🪟 Windows</h2></summary>

1. **Install Miniforge** (this gives you Python + conda without needing to know either):
   - Go to https://conda-forge.org/download/ and download the **Windows** installer (`.exe`).
   - Double-click it → click **Next** through the installer → **Install** (default options are fine).
2. **Open your terminal:** click the Start menu, type **`Miniforge Prompt`**, and open it. A black
   text window appears. This is where you'll type commands.
3. That's it for Level 1. *(For Level 2 you'll also need WSL — see Part 6.)*

</details>

<details>
<summary><h2>🍎 Mac</h2></summary>

1. **Open Terminal:** press `Cmd + Space`, type **`Terminal`**, press Enter.
2. **Install Miniforge** — paste this into Terminal and press Enter:
   ```bash
   curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
   bash Miniforge3-$(uname)-$(uname -m).sh -b
   ~/miniforge3/bin/conda init "$(basename $SHELL)"
   ```
3. **Close and reopen Terminal** so conda activates. You should see `(base)` at the start of the line.

</details>

<details>
<summary><h2>🐧 Linux</h2></summary>

1. **Open your terminal** (Ctrl+Alt+T on most systems).
2. **Install Miniforge:**
   ```bash
   curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
   bash Miniforge3-$(uname)-$(uname -m).sh -b
   ~/miniforge3/bin/conda init bash
   ```
3. **Close and reopen the terminal.** You should see `(base)` at the start of the line.

</details>

---

# PART 2 · Get strainshare and install it

Do this in your terminal (Miniforge Prompt on Windows, Terminal on Mac/Linux). The same commands work
on all three systems.

**2a. Download the tool.** Two options — pick one:

- **If you have `git`:**
  ```bash
  git clone https://github.com/jyu9675/bioai-strainshare.git
  cd bioai-strainshare
  ```
- **If you don't:** open https://github.com/jyu9675/bioai-strainshare in a browser → click the green
  **`< > Code`** button → **Download ZIP** → unzip it → then in the terminal `cd` into the unzipped
  folder (e.g. `cd Downloads/bioai-strainshare-main`).

**2b. Make a clean workspace and install:**
```bash
conda create -n strainshare python=3.11 -y
conda activate strainshare
pip install .
```
> `conda create`/`activate` makes an isolated space so this can't break anything else on your
> computer. `pip install .` installs strainshare and everything it needs. This takes a minute.

**2c. Check it worked:**
```bash
strainshare version
```
You should see something like `strainshare 0.1.3 (standard spec 0.1.0)`.

---

# PART 3 · Prove it works (30 seconds, no data)

```bash
strainshare benchmark --selftest
```
If you see `[benchmark] selftest PASSED`, the tool is installed correctly. ✅

---

# PART 4 · Run a real analysis on the example data

The repository ships a tiny example so you can see real output immediately — **no biology tools, no
downloads needed.**

```bash
strainshare analyze \
  --compare example/genomeWide_compare.tsv \
  --meta example/metadata.tsv \
  --metaphlan example/merged_metaphlan.tsv \
  --outdir my_first_run
```
> On Windows, if a command spread across lines gives an error, put it all on **one line** and remove
> the `\` marks.

When it finishes you'll have a new folder `my_first_run/` with result tables and figures.

---

# PART 5 · Understand your results

Open the `my_first_run` folder. The important files:

| File | What it tells you |
|---|---|
| `translocation_candidates.tsv` | The headline: which shared strains look like **real translocation** vs **contamination**. |
| `species_within_between.tsv` | Are shared strains real? (Same-person sharing should be **much higher** than between-person.) |
| `direction_calls.tsv` | For each shared strain: which site had it first (e.g. `gut_to_vagina`), or `direction_unresolved`. |
| `genome_generalist_flags.tsv` | Flags "strains" that are shared by unrelated people too (usually artifacts). |
| `figures/fig1..3.png` | Pictures of the above. Open them by double-clicking. |

**The one plot to look at first** — is a "shared strain" trustworthy, or a fluke on too little data?
```bash
strainshare diagnostic --pairs my_first_run/pairs_tagged.tsv --out my_first_run/check.png
```
Open `my_first_run/check.png`. Only points in the **top-right green box** (high similarity **and**
enough genome compared) are confident shared-strain calls.

---

# PART 6 · Use your own or public data

## 6a. Download a public dataset automatically

strainshare can pull a public study from the ENA database and prepare it for you. Example:
```bash
strainshare fetch --bioproject PRJNA982400 --site-map "V=vagina,C=cervix" --max-subjects 4
```
This creates `data/samples.tsv` listing the samples. Add `--download` to actually download the DNA
files (these can be large — hundreds of MB to several GB each).

> **What makes a dataset usable?** It must be **shotgun sequencing** (not "16S") and must sample
> **two body sites from the same people**. Good open examples: **HMP** (gut + vaginal), **PRJNA826539**
> (Fijian: rectal + vaginal + cervical). See [`tutorial.md`](tutorial.md) for more.

## 6b. Use a comparison table you already have

If you (or a bioinformatician) already ran **inStrain compare**, just point strainshare at the outputs:
```bash
strainshare analyze --compare YOUR_compare.tsv --meta YOUR_metadata.tsv \
  --metaphlan YOUR_community_table.tsv --outdir results --site-pair gut,vagina
```
Your `metadata.tsv` needs 4 columns: `sample`, `subject`, `timepoint`, `bodysite`.

---

# PART 7 · (Advanced) The full pipeline, from raw FASTQ files

This turns raw sequencing files into results end-to-end. It needs heavy bioinformatics tools that only
run on **Mac, Linux, or Windows-with-WSL**.

<details>
<summary><b>🪟 Windows users: first install WSL (one-time)</b></summary>

The heavy tools don't run on Windows directly, so you install a small Linux inside Windows:
1. Open **PowerShell as Administrator** (Start → type PowerShell → right-click → Run as administrator).
2. Run: `wsl --install` → restart your computer when asked.
3. After restart, open **Ubuntu** from the Start menu, create a username/password.
4. Inside that Ubuntu window, install Miniforge (follow the **Linux** steps in Part 1), then continue below.

</details>

**Install the bioinformatics stack** (Mac/Linux/WSL), from inside the `bioai-strainshare` folder:
```bash
conda env create -f environment.yml
conda activate bioai
pip install .
```

**Run the whole pipeline** with one command (after editing two small config files):
1. Edit `workflow/samples.tsv` — list your samples and the paths to their FASTQ files.
2. Edit `workflow/config.yaml` — set where your reference genomes are.
3. Run:
   ```bash
   snakemake -j4 --configfile workflow/config.yaml -n     # -n = practice run (shows the plan)
   snakemake -j4 --configfile workflow/config.yaml        # the real run
   ```

> Building the reference genome set is the one genuinely advanced step — see
> `scripts/02_build_ref.sh` and [`strain_pilot_plan.md`](strain_pilot_plan.md). If you're not
> comfortable with this, ask a bioinformatician, or stick to Level 1 with a comparison table they
> provide.

---

# Troubleshooting

| Problem | Fix |
|---|---|
| **`command not found: strainshare`** | You forgot `conda activate strainshare`. Run it, then try again. |
| **`command not found: conda`** | Close and reopen your terminal after installing Miniforge (Part 1). |
| **A multi-line command errors on Windows** | Put it on one line and delete the `\` characters. |
| **`No such file or directory: example/...`** | You're not inside the `bioai-strainshare` folder. Run `cd bioai-strainshare` first. |
| **Results are empty / "no comparable pairs"** | Your samples are too shallow, or the two sites share no species — expected when comparing very different communities (e.g. gut vs vagina) without deep data. |
| **Downloads are huge/slow** | Sequencing files are big. Start with a couple of samples (`--max-subjects 2`) and low-depth studies. |

---

# Getting help & citing

- **Full reference:** [`README.md`](../README.md), [`install.md`](install.md), [`tutorial.md`](tutorial.md)
- **Report a problem:** open an Issue at https://github.com/jyu9675/bioai-strainshare/issues
- **Cite it:** Yu J., Kwon D.S. *strainshare*. Zenodo. https://doi.org/10.5281/zenodo.22275588
