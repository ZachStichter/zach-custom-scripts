__provides__ = {
    "write_bash_submission_script": "get_bash_script",
    "default_bash_submission_script": "get_default_bash_script"
}

REGISTERED=False

def write_bash_submission_script(user:str, kwargs:dict, required_source:str|None=None, required_modules:list[str]|None=None, required_conda_env:str|None=None, shebang:str="#!/bin/bash")->str:
    """
    Returns a dummy submission script header with the provided options. The user will need to redirect this to a file.

    Args:
        user (str): the full username for the person submitting the job, formatted like an email address.
        required_source (str|None): source this file inside the job submission script, before executing any further commands. Default None.
        required_modules (list[str]|None): activate these required modules inside the job submission script, before executing any further commands. Default None.
        required_conda_env (str|None): load this conda environment inside the job submission script, before executing any further commands. Default None.
        shebang (str): Execute the submission script from this environment. Default #!/bin/bash for a bash script
        *kwargs: Any of the SGE queue commands in the form [option]=[target]. These include:
            @: optionfile. string to a file containing any number of valid options. Takes precedence over other specified options here.
            a: date_time. sets a valid start time for job execution. Conform to [[CC]YY]MMDDhhmm[.SS].
            ac: list[str] of form variable(=value). Include an environment variable with the job. Note: this must be a list, as it will be unpacked like a list.
            cwd: cwd. Execute the job from the current working directory. The value of the key:value pair in this argument is ignored, as this is a flag.
            dc: list[str] of form variable. Remove environment variables from the job's context. Note: this must be a list, as it will be unpacked like a list.
            e: path. Change job standard error to output to path.
            hold_jid: job_id. place a hold on the job until after job_id completes.
            i: path. Change standard input file name.
            j: 'y' or 'n'. Merge stdout and stderr for this job.
            jsv: path. Requries job to be verified with corresponding job verification script before launch.
            m: 'b|e|a|s|n'. Provide a string specifying when you want to send mail 'b'eginnning, 'e'nd, 'a'borted, 's'uspended, 'n'ever
            M: email address. where to send mail to?
            now: 'y' or 'n'. Should the job abort if it cannot be run right away?
            N: job name. Give the job a name. Note that there is a 10 character display limit.
            pe: parallel environment. Provide a string for the parallel environment. Default smp 1 for simple multiprocessing on one core. Could use mpi for multiple nodes
            q: queue name. Use this queue.
            t: range. Set the job to run multiple copies according to provided range. 1-2 will submit 2 jobs at once.
            tc: integer. set the maximum number of concurrent copies of the job.
            v: list[str]. Add these variables to the environment context.
            V: add all variables to the environment context. Note: ignores value in the key:value pair.
            wd: path. Use the path as the working directory for this job.
    """
    options_string = ""
    for arg, val in kwargs.items():
        if arg in ['ac','dc']:
            for kw in val:
                options_string += f"#$ -{str(arg)} {str(kw)}\n"
        elif arg in ['cwd', 'V']:
            options_string += f"#$ -{str(arg)}\n"
        elif arg == 'M':
            if val == None or val == 'default':
                options_string += f"#$ -{str(arg)} {str(user)}"
            else:
                options_string += f"#$ -{str(arg)} {str(val)}"
        else:
            options_string += f"#$ -{str(arg)} {str(val)}\n"

    source_string = f"source {required_source}" if required_source is not None else ""
    required_modules_string = ""
    if required_modules is not None:
        for module in required_modules:
            required_modules_string += f"module load {module}\n"
    conda_activation_string = f"conda activate {required_conda_env}" if required_conda_env is not None else ""
    job_parts = []
    for part in [shebang, options_string, source_string, required_modules_string, conda_activation_string]:
        if part != "":
            job_parts.append(part)
    job_string = "\n\n".join(job_parts) + "\n"
    
    return job_string

def default_bash_submission_script(jobname):
    if not REGISTERED:
        raise ValueError("Please register with register_job_script_config.py before using this function.")
    default_args = {
        "M": None,
        "m":"abe",
        "q": None,
        "pe":"smp 2",
        "N":jobname
    }
    default_modules = None
    default_conda = None
    default_source = None
    default_user = None

    return write_bash_submission_script(default_user,default_args,default_source,default_modules,default_conda, "#!/bin/bash")
    
