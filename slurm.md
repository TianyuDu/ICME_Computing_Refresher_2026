# Learn Slurm on FarmShare

This lab teaches you to run programs on a shared computing cluster using Slurm. We use Stanford FarmShare so students can follow the same examples with their own accounts. Estimate π with a Monte Carlo simulation, submit it as a scheduled job, inspect its accuracy, and then repeat the experiment with different random seeds using a job array.

All application code, input data, and batch scripts are included in [slurm_example/](slurm_example/). Clone this repository on the cluster and use those files directly. The [demo README](slurm_example/README.md) provides a shorter run-through if you already know the basics.

**Before class:** confirm that you can log in to FarmShare. Students with a full-service SUNet ID are eligible, but the first login and account setup still need to happen. See the [FarmShare access policy](https://docs.farmshare.stanford.edu/policy/).

**What you need:** your SUNet ID, Duo authentication, a terminal or browser, and basic familiarity with changing directories and reading files. The examples use Python 3 and its standard library; no additional packages or GPU are needed. Allow about 50–60 minutes plus queue waiting time.

## Learning goals

By the end, you should be able to:

- Explain the difference between a login node and a compute node.
- Read a batch script and identify its CPU, memory, and time requests.
- Submit a job with `sbatch` and record its job ID.
- Use `squeue`, `sacct`, and log files to determine what happened.
- Run independent inputs concurrently as an array.
- Cancel your own job and identify which failed task needs attention.

## Contents

1. [Understand what Slurm does](#1-understand-what-slurm-does)
2. [Connect and download the examples](#2-connect-and-download-the-examples)
3. [Read and submit your first job](#3-read-and-submit-your-first-job)
4. [Find out what happened](#4-find-out-what-happened)
5. [Run several inputs with a job array](#5-run-several-inputs-with-a-job-array)
6. [Practice on your own](#6-practice-on-your-own)
7. [Connect the lesson to a research project](#7-connect-the-lesson-to-a-research-project)

See also [optional extensions](#optional-extensions), [troubleshooting](#troubleshooting), and [instructor notes and answer key](#instructor-notes-and-answer-key).

## 1 Understand what Slurm does

FarmShare provides the computers and shared storage. Slurm manages requests to use the compute resources: you describe what your program needs, submit the job, and wait for the scheduler to allocate resources. The program then runs on a compute node.

- **Your laptop:** connect to FarmShare and download your results.
- **Login node:** prepare files, submit jobs, and inspect status and results.
- **Compute node:** run the work allocated through Slurm.

Your home directory is accessible across FarmShare nodes, so a job can read files you prepare there. Keep intensive computation inside scheduled jobs. See the [FarmShare introduction](https://docs.farmshare.stanford.edu/).

Learn these commands as you use them:

- `sbatch` submits a batch script.
- `srun` launches work using allocated resources; it can also request an allocation.
- `squeue` shows pending and running jobs.
- `sacct` shows accounting records, including completed or failed jobs.
- `scancel` cancels a job you own.
- `sinfo` shows partitions and node availability.

A **partition** groups compute nodes. A **job** requests resources; once they are allocated, a **job step** launches work within that allocation. We use one process and one CPU for each calculation. See [FarmShare's job guide](https://docs.farmshare.stanford.edu/slurm/).

## 2 Connect and download the examples

### Choose one way to connect

From a terminal on **your laptop**, replace `SUNetID` with your username:

```bash
ssh SUNetID@login.farmshare.stanford.edu
```

Complete the password and Duo prompts. On your first SSH connection, compare the host fingerprint with the [official connection page](https://docs.farmshare.stanford.edu/connecting/) before accepting it.

Alternatively, open [FarmShare OnDemand](https://ondemand.farmshare.stanford.edu), sign in, and select **Clusters → FarmShare Shell Access**. Your first login-node shell session creates your Slurm account; complete this before trying OnDemand apps. Both routes lead to the shell used in this lab.

### Orient yourself

Run on **FarmShare**, after logging in:

```bash
whoami
hostname
pwd
sinfo
```

Record the login hostname. Node names and available resources may differ from another student's output. `sinfo` lists partitions; an asterisk after a partition name marks the default. See the [sinfo reference](https://slurm.schedmd.com/sinfo.html).

### Clone this repository on the login node

```bash
cd ~
git clone https://github.com/TianyuDu/ICME_Computing_Refresher_2026.git
cd ICME_Computing_Refresher_2026/slurm_example
mkdir -p logs
python3 --version
ls
```

If you already cloned the repository, skip `git clone` and enter your existing checkout's `slurm_example` directory. If you downloaded a ZIP instead, extract it on the cluster and enter that same folder. Use your actual checkout path in later commands if it differs from the path above.

The files are ready to use:

- [estimate_pi.py](slurm_example/estimate_pi.py): estimate π from random points and report the absolute error.
- [pi.sbatch](slurm_example/pi.sbatch): submit one simulation with one million points and seed 42.
- [seeds.txt](slurm_example/seeds.txt): six random seeds for the array example.
- [array_pi.py](slurm_example/array_pi.py): select a seed and run the same simulation.
- [array.sbatch](slurm_example/array.sbatch): submit six independent array elements.
- `logs/`: output and error files will appear here; generated logs are ignored by Git.

**Run every `sbatch` command below from `slurm_example/`.** Both batch scripts use the submission directory to find the Python programs, inputs, and log directory. The `logs/` directory must exist before submission because Slurm opens the log files before running the script. The repository includes it, and `mkdir -p logs` also restores it if needed.

**On another Slurm cluster:** these scripts use FarmShare's `normal` partition. Check your site's instructions and change `--partition` in both `.sbatch` files, plus any required account or QoS settings, before submitting. Python 3 and these files must be accessible from the compute nodes.

**Checkpoint:** are you on your laptop, a login node, or a compute node? What evidence tells you?

## 3 Read and submit your first job

All commands in this section run in `slurm_example/` on the login node.

### Read the application and batch script

```bash
cat estimate_pi.py
cat pi.sbatch
```

`estimate_pi.py` runs a small Monte Carlo experiment:

1. Draw random points `(x, y)` uniformly from the unit square, with both coordinates between 0 and 1.
2. Count points inside the quarter circle: `x*x + y*y <= 1`.
3. Estimate π using `4 * points_inside / total_points`.

The unit square has area 1 and the quarter circle has area π/4, so the fraction of points inside estimates π/4. The program processes one point at a time and only keeps a count, which uses little memory even as the number of samples increases.

A **random seed** selects a repeatable sequence of points. Keeping the seed and sample count fixed makes this example reproducible; changing the seed gives another run of the experiment. The program reports its estimate and `abs_error`, the absolute difference from Python's `math.pi` reference value.

`pi.sbatch` describes the resources and runs this application command:

```bash
srun python3 -u estimate_pi.py --samples 1000000 --seed 42
```

You do not need to run that command separately; submit the batch script below. Its arguments make the experiment settings explicit: one million samples and random seed 42.

Read the resource requests in the supplied script:

- `--partition=normal`: use FarmShare's normal partition.
- `--nodes=1`: use one compute node.
- `--ntasks=1`: request one task; `srun` launches one Python process.
- `--cpus-per-task=1`: request one CPU for that task.
- `--mem=1G`: request 1 GiB of memory on the allocated node.
- `--time=00:02:00`: set a two-minute execution limit; queue waiting is additional.
- `--output=logs/pi-%j.out` and `--error=logs/pi-%j.err`: put standard output and errors in separate files, using the job ID in place of `%j`.

After the directives, `set -euo pipefail` helps expose failures by stopping on failed commands or unset variables and propagating pipeline failures. `cd "$SLURM_SUBMIT_DIR"` selects the directory from which you submitted. `hostname` records the compute node, and `srun` launches Python in the allocation with unbuffered output (`-u`).

Keep `#SBATCH` directives before executable shell statements. Requesting more CPUs alone does not make this sequential Python calculation run in parallel. See the [sbatch reference](https://slurm.schedmd.com/sbatch.html).

### Submit it

```bash
sbatch pi.sbatch
```

You should see something like this; your job ID will be different:

```text
Submitted batch job 123456
```

Record that number. Set a shell variable using **your actual job ID**, replacing the example below:

```bash
job_id=123456
```

`sbatch` returns when the job is accepted; the program may still be waiting to start. A batch job continues independently of your SSH connection.

Shell variables do not persist after you disconnect. After reconnecting, return to your checkout's `slurm_example/` directory and set `job_id`, `smoke_id`, or `array_id` again using the numbers you recorded.

**Checkpoint:** why use `sbatch pi.sbatch` instead of `bash pi.sbatch`? Think about what interprets the `#SBATCH` lines.

## 4 Find out what happened

### Check the queue

```bash
squeue -u "$USER"
```

Look for your job ID. `PD` means pending; `R` means running. A pending reason such as `Resources` or `Priority` describes why it is waiting. This small simulation may finish before you see it running. See the [squeue reference](https://slurm.schedmd.com/squeue.html).

### Read the output and check the outcome

After the job finishes:

```bash
cat "logs/pi-${job_id}.out"
cat "logs/pi-${job_id}.err"
sacct -j "$job_id" --format=JobID,State,ExitCode,Elapsed
```

The output should contain a compute hostname followed by:

```text
seed=42 samples=1000000 pi=3.140592 abs_error=0.001001
```

Compare the hostname with the login hostname you recorded. The estimate is close to π, but sampling introduces numerical error. That `abs_error` value is an experimental result; runtime errors would appear in the separate `.err` file, which should contain no unexpected errors. The example output assumes the supplied seed, sample count, and code.

In accounting, look for `COMPLETED` and exit code `0:0`. You may see several rows for a job and its steps, and accounting can appear after a short delay. See the [sacct reference](https://slurm.schedmd.com/sacct.html).

**Success requires both the expected result and the expected job outcome.** Disappearing from `squeue` alone does not establish success.

### Know how to stop a job

For a job you own that is still pending or running, this command cancels it:

```bash
scancel "$job_id"
```

Use this only when you intend to stop that job. You do not need to cancel the completed simulation.

**Checkpoint:** show your job ID, the π estimate and its absolute error, and the final job state. Explain why a nonzero numerical error does not mean that the job failed.

## 5 Run several inputs with a job array

An array is useful when you need the same calculation for several independent inputs. Here, each element repeats the π experiment with a different random seed. Comparing runs shows how the estimate varies even when the sample count is fixed.

### Read the inputs and application

```bash
cat seeds.txt
cat array_pi.py
cat array.sbatch
```

`seeds.txt` contains one random seed per line: `42`, `43`, `44`, `45`, `46`, and `47`, without a header or blank lines. Slurm sets `SLURM_ARRAY_TASK_ID` for each array element. The Python program uses it as a zero-based index into that file: index `0` selects seed `42`, and index `5` selects seed `47`. An array index identifies a line; it is distinct from the seed stored on that line.

`array_pi.py` imports the simulation function from `estimate_pi.py`, so both jobs use the same algorithm. Each element draws one million points with its selected seed. The expected application output is:

```text
task=0 seed=42 samples=1000000 pi=3.140592 abs_error=0.001001
task=1 seed=43 samples=1000000 pi=3.139776 abs_error=0.001817
task=2 seed=44 samples=1000000 pi=3.138120 abs_error=0.003473
task=3 seed=45 samples=1000000 pi=3.141224 abs_error=0.000369
task=4 seed=46 samples=1000000 pi=3.139116 abs_error=0.002477
task=5 seed=47 samples=1000000 pi=3.140300 abs_error=0.001293
```

Each line goes to a separate log file. Elements can start and finish in any order. Element 0 reproduces the single-job estimate because it uses the same seed and sample count. The other estimates differ because they use different random points.

### Read the array options

The resource requests are the same as the single job. The new settings in `array.sbatch` are:

- `--array=0-5`: submit six elements, indexed 0 through 5, all eligible to run concurrently.
- `--output=logs/array-%A_%a.out`: include the parent array ID (`%A`) and element index (`%a`) in each output filename.
- `--error=logs/array-%A_%a.err`: give each element its own error log too.

Each element requests one CPU and 1 GiB, so this array requests up to six CPUs and 6 GiB concurrently. Available resources and cluster scheduling limits determine when each element starts; simultaneous starts are not guaranteed. An array distributes independent executions; it does not make one execution a parallel algorithm. See [Slurm job arrays](https://slurm.schedmd.com/job_array.html).

### Test one element first

```bash
sbatch --array=0 array.sbatch
```

Record the returned job ID and assign it below, replacing the example:

```bash
smoke_id=123457
squeue -u "$USER"
```

After it finishes:

```bash
sacct -j "$smoke_id" --format=JobID,State,ExitCode
cat "logs/array-${smoke_id}_0.out"
cat "logs/array-${smoke_id}_0.err"
```

Expect `task=0 seed=42 samples=1000000 pi=3.140592 abs_error=0.001001`, a `COMPLETED` state with `0:0`, and no unexpected errors. The command-line `--array=0` overrides the range in the script for this submission; it does not edit the script.

### Submit all six elements

After the one-element test succeeds:

```bash
sbatch array.sbatch
```

Record the new parent array ID, replace the example below, and inspect the array:

```bash
array_id=123458
squeue -r -j "$array_id"
```

`-r` displays array elements individually. If the array already finished, use accounting and logs to check its outcome. Once all elements finish:

```bash
sacct -j "$array_id" --format=JobID,State,ExitCode
cat logs/array-${array_id}_*.out
cat logs/array-${array_id}_*.err
```

Check all six element outcomes and compare the output with the six expected lines above. Here, output logs also hold the results; a larger application would usually write separate result files.

**Checkpoint:** trace element 3 from its index to its seed and π estimate. Which seed gives the smallest absolute error in this run? Explain why six elements do not mean six must run at once.

## 6 Practice on your own

**Finish the earlier jobs before editing code or inputs.** Slurm submits the batch script but does not snapshot its companion files. Keep the Python programs and input list stable while jobs are queued or running.

1. **Change the sample count.** In `pi.sbatch`, change `--samples 1000000` to `--samples 100000`, keeping seed 42. Submit again and record the new ID. Compare its estimate, absolute error, and elapsed time with the original run. Does ten times more work guarantee ten times less error? Restore the original sample count afterward.
2. **Explain a resource request.** If you request four CPUs for the single job, will this Python program automatically use all four? Explain before running anything.
3. **Add a seventh random seed.** After the previous array finishes, append `48` to `seeds.txt` once, then submit indexes 0–6:

   ```bash
   printf '48\n' >> seeds.txt
   sbatch --array=0-6 array.sbatch
   ```

   Record the new array ID. Check its accounting and logs as before, including element 6. If repeating this exercise, inspect `seeds.txt` first so you do not append the same input again.
4. **Diagnose an outcome.** Explain which command and file you would inspect if one element failed. Identify it by parent array ID and index.

### What to submit for the lab

- Your single-job batch script, job ID, output, and final state.
- Your array script and an example showing index → seed → π estimate.
- The verified result for the seventh seed and your sample-count comparison.
- A short explanation of `sbatch` versus `srun`, and why an empty queue is not enough to prove success.

## 7 Connect the lesson to a research project

After completing this lab, use the same questions to read a project's submission scripts:

- Which program performs one unit of work, as `estimate_pi.py` or `array_pi.py` does here?
- Where are its resource requests defined?
- Which experiment, sample, or configuration does each array index select?
- Where are its logs and result files written?
- How can you run and verify one small case before expanding to an array?

The original lesson suggests [TianyuDu/example-slurm-array](https://github.com/TianyuDu/example-slurm-array) as an optional follow-on. That separate project's scripts, dependencies, and FarmShare compatibility have not been verified here. This lab's runnable examples are all included in `slurm_example/` and do not depend on it.

Before using a research project on FarmShare, read its actual README and scripts, check its resource and software requirements, and demonstrate one case. Record the project commit and submission command with the results.

## Optional extensions

Run the following cluster commands from your checkout's `slurm_example/` directory. If you left it, return with:

```bash
cd ~/ICME_Computing_Refresher_2026/slurm_example
```

Use your actual checkout path and restore any needed job-ID variables from your notes.

### Explore an interactive compute session

From the login node, request a short shell allocation:

```bash
srun --partition=interactive --qos=interactive \
  --nodes=1 --ntasks=1 --cpus-per-task=1 \
  --mem=1G --time=00:05:00 --pty bash
```

Once the allocation starts:

```bash
hostname
python3 estimate_pi.py
exit
```

Python runs inside the allocated compute-node shell, using the application's defaults of one million samples and seed 42. `exit` releases the session and returns you to the login node. FarmShare documents this partition and QoS combination in its [interactive job instructions](https://docs.farmshare.stanford.edu/slurm/); resource availability controls when the session starts.

### Inspect or retry an individual element

For element 2 of the parent array stored in `array_id`:

```bash
cat "logs/array-${array_id}_2.err"
sacct -j "${array_id}_2" --format=JobID,State,ExitCode,Elapsed
```

After diagnosing a failure and waiting for the original run to finish, submit only the indexes that need another attempt. For example:

```bash
sbatch --array=2,4 array.sbatch
```

This creates a new array ID and new logs. Track which attempt produced each accepted result. If you changed the calculation or input mapping, run a fresh consistent set instead of mixing results. To cancel only element 2 while it is pending or running, use `scancel "${array_id}_2"`. See [managing array elements](https://slurm.schedmd.com/job_array.html).

### Learn job dependencies after mastering arrays

An aggregation job can wait for every array element to succeed using `--dependency=afterok:ARRAY_ID`. Build and verify the aggregation script first, then submit it with the array ID as its dependency. An aggregation script is an additional exercise; the core lab checks each output directly. See [array dependencies](https://slurm.schedmd.com/job_array.html#job_dependencies).

### Download your logs

Run on **your laptop**, replacing `SUNetID` and adjusting the remote path if you cloned elsewhere:

```bash
scp -r \
  SUNetID@dtn.farmshare.stanford.edu:~/ICME_Computing_Refresher_2026/slurm_example/logs \
  ./farmshare-lab-logs
```

FarmShare recommends its data transfer node for large transfers. See the [data transfer instructions](https://docs.farmshare.stanford.edu/transfer/).

### Add a software environment for a real project

The classroom programs use the Python standard library. For a project with additional requirements, inspect available Python modules with `module spider python`, follow the project's environment instructions, and load or activate that environment in its batch script. Set it up once before submitting an array. See [FarmShare software](https://docs.farmshare.stanford.edu/software/).

## Troubleshooting

- **First login or account error:** complete a login-node shell session; ask for help if the problem persists.
- **`sbatch` is not found:** check that you are in a cluster shell with Slurm available.
- **Invalid partition or account:** check the site's settings; the supplied scripts target FarmShare's `normal` partition.
- **Pending with `Resources` or `Priority`:** the job is waiting; inspect the reason instead of resubmitting duplicates.
- **No output file yet:** check whether the job started, whether you submitted from `slurm_example/`, and whether `logs/` existed before submission.
- **`FAILED`:** read that element's `.err` file; check filenames, seed indexes, positive sample counts, and Python availability. A seventh element needs a seventh seed line.
- **Estimate differs from the example:** check the seed, sample count, and code version. Changing those changes the experiment. A nonzero `abs_error` measures numerical accuracy and does not by itself indicate a failed job.
- **`OUT_OF_MEMORY` or `TIMEOUT`:** inspect the program and its resource needs before increasing requests.
- **No job in `squeue`:** use `sacct` and output files to establish its final outcome; accounting may take a short time to appear.

For [FarmShare support](https://docs.farmshare.stanford.edu/help/), include the job ID, script, and error text.

## Instructor notes and answer key

Suggested pacing: 5 minutes on the cluster model, 5 on connection and checkout, 15 on the first job and outcome, 15 on the array, and 10–20 on practice. Allow extra time for queue delays. Have each student use their own account and checkout.

Before class, test the examples with a student account and check `sinfo` and `scontrol show partition normal`. Keep the small per-element resource requests used here. Published examples may include older transcripts; use live output for current limits and software versions.

- **Why `sbatch` instead of `bash`?** `sbatch` submits a scheduled job. Bash treats `#SBATCH` lines as comments and does not submit their resource requests.
- **Has a job succeeded when it disappears from the queue?** Not necessarily; check its final state, exit code, and application output.
- **Will four CPUs automatically speed up this simulation?** No; this Python loop is sequential. The array runs separate simulations concurrently.
- **What does `0-5` mean?** Six elements, indexes 0 through 5, all eligible to run concurrently. Available resources and cluster scheduling limits determine how many actually run at once.
- **What does element 3 compute?** It reads the fourth seed, 45, and estimates π as `3.141224` from one million points. Its absolute error, `0.000369`, is the smallest among these six runs.
- **What changes for the seventh input?** Append seed 48 and use `--array=0-6`; element 6 gives `pi=3.140864 abs_error=0.000729` with one million samples.
- **What happens with fewer samples?** Seed 42 with 100,000 samples gives `pi=3.137280 abs_error=0.004313`. More samples improve accuracy statistically, but a particular run is not guaranteed to improve, and ten times as many samples does not guarantee ten times less error. These jobs are short enough that Slurm's elapsed-time display may not resolve the runtime difference.
- **Why fix the seed?** It lets students reproduce a result. Different seeds provide repeated runs; comparing their errors illustrates sampling variability.
- **How do `sbatch` and `srun` differ here?** `sbatch` submits the batch job; `srun` inside the script launches Python using that allocation.

The Python calculations and Bash syntax have been checked locally. No FarmShare jobs were submitted during preparation; an instructor's cluster test is still needed before teaching the lab.
