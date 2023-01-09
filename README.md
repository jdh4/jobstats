# jobstats

## How does it work?

Consider the command below:

```
$ jobstats 123456
```

The code makes a JobStats class. It then prints the report of the class.

What happens when a JobStats class is made? Here is the constructor:

```python
def __init__(self, jobid=None, jobidraw=None, start=None, end=None, gpus=None, cluster=None, debug=False):
```

Right now only the jobid, cluster and debug can be set when the object is made since there is no way to pass in other parameter values such as `start`. It always has `jobidraw == None` so first step is always to call `self.__get_job_info()` calls `sacct`. Need to add user and other seff quantities here. The output is handled as CSV with a header:

```
$ sacct -P -X -o jobidraw,start,end,cluster,reqtres,admincomment -j 8554568 -M tiger2
JobIDRaw|Start|End|Cluster|ReqTRES|AdminComment
8554568|2022-05-07T13:02:41|Unknown|tiger2|billing=30,cpu=30,mem=120000M,node=1|
```

The output is parsed to get `gpus`, `start`, `end`, etc. `admincomment` is stored in `self.data`. This will be empty for running jobs so an explicit call to the prometheus server is later required.

Note that `self.__get_job_info()` will return False is end is not Unknown or not numeric. Same if start is not numeric. These two cases result in failure of jobstats.

On return, compute the elapsed wall-clock time and convert self.data to json if sufficient payload. If self.data is empty then call prometheus using `self.get_job_stats()`. That call creates a dictionary which gets passed using `requests.get()` which returns json which is parsed in `get_data()`.

Lastly, `report_job()` is called.

NEW: Get netid, state, group, nn

```
Job ID: 8554568
Cluster: tiger2
User/Group: pa1643/cee
State: RUNNING
Nodes: 1
Cores per node: 30
CPU Utilized: 00:00:00
CPU Efficiency: 0.00% of 1-20:57:00 core-walltime
Job Wall-clock time: 01:29:54
Memory Utilized: 0.00 MB (estimated maximum)
Memory Efficiency: 0.00% of 117.19 GB (3.91 GB/core)
WARNING: Efficiency statistics may be misleading for RUNNING jobs.
```

Now focus on format.


## Useful Links

[https://prometheus.io/docs/instrumenting/exporters/](https://prometheus.io/docs/instrumenting/exporters/)  


## issues

Crashes when try to make a jobstats  object without jobid

## How to call `jobstats` from a Python script?

```python
def get_stats_for_running_job(jobid, cluster):
  import importlib.machinery
  import importlib.util
  cluster = cluster.replace("tiger", "tiger2")
  loader = importlib.machinery.SourceFileLoader('jobstats', '/usr/local/bin/jobstats')
  spec = importlib.util.spec_from_loader('jobstats', loader)
  mymodule = importlib.util.module_from_spec(spec)
  loader.exec_module(mymodule)
  stats = mymodule.JobStats(jobid=jobid, cluster=cluster)
  time.sleep(0.5)
  return eval(stats.report_job_json(False))
```

## demo

```
$ sacct -j 39861033 -o jobid,admincomment%200
JobID                                                                                                                                                                                                    AdminComment 
------------ -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
39861033                             JS1:H4sIACj7KWIC/1XNQQrCMBCF4bvMOkonIzNpLyOhGUVIGmnSRSm5u1FEcPt/PN4BSw5aYDogaIz+tNoZF+R3qLn6eE2a8rrDxE5wvAgLsYGtaPiJFbRCxCMP5juqj6QdHJE79zg/t37hWvt34gEN3D9487FoewEKn+eojwAAAA== 
39861033.ba+                                                                                                                                                                                                          
39861033.ex+                                                                                                                                                                                                          
39861033.0                                                                                                                                                                                                            
[jdh4@della8 ~]$ python3
Python 3.6.8 (default, Nov 14 2021, 17:38:41) 
[GCC 8.5.0 20210514 (Red Hat 8.5.0-4)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import json
>>> import gzip
>>> import base64
>>> t = json.loads(gzip.decompress(base64.b64decode("H4sIACj7KWIC/1XNQQrCMBCF4bvMOkonIzNpLyOhGUVIGmnSRSm5u1FEcPt/PN4BSw5aYDogaIz+tNoZF+R3qLn6eE2a8rrDxE5wvAgLsYGtaPiJFbRCxCMP5juqj6QdHJE79zg/t37hWvt34gEN3D9487FoewEKn+eojwAAAA==")))
>>> t
{'nodes': {'della-r2c1n16': {'total_memory': 68719476736, 'used_memory': 27127336960, 'total_time': 28338.0, 'cpus': 8}}, 'total_time': 3601, 'gpus': False}
```

```
[jdh4@della8 ~]$ python3
Python 3.6.8 (default, Nov 14 2021, 17:38:41) 
[GCC 8.5.0 20210514 (Red Hat 8.5.0-4)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import json
>>> import gzip
>>> import base64
>>> t = json.loads(gzip.decompress(base64.b64decode("H4sIACj7KWIC/1XNQQrCMBCF4bvMOkonIzNpLyOhGUVIGmnSRSm5u1FEcPt/PN4BSw5aYDogaIz+tNoZF+R3qLn6eE2a8rrDxE5wvAgLsYGtaPiJFbRCxCMP5juqj6QdHJE79zg/t37hWvt34gEN3D9487FoewEKn+eojwAAAA==")))
>>> t
{'nodes': {'della-r2c1n16': {'total_memory': 68719476736, 'used_memory': 27127336960, 'total_time': 28338.0, 'cpus': 8}}, 'total_time': 3601, 'gpus': False}
>>> 27127336960/1.024**3
25264301300.04883
>>> 68719476736/1.024**3
63999999999.99999
>>> 8*3601
28808
>>> 28338.0/(8*3601)
0.9836850874757012
```

```
$ jobstats 39861033
Memory usage per node - used/allocated
    della-r2c1n16: 25.3GB/64.0GB (3.2GB/8.0GB per core of 8)
Total used/allocated: 25.3GB/64.0GB (3.2GB/8.0GB per core of 8)

CPU Usage per node (cpu time used/runtime)
    della-r2c1n16: 07:52:18/08:00:08 (efficiency=98.4%)
Total used/runtime: 07:52:18/08:00:08, efficiency=98.4%
```

```
>>> import json
>>> import gzip; import base64
>>> encoding = "H4sIAH+lZmIC/8WSywqDMBBF/yVrK5NJzMOfEalBAvGBJotW/PdGa0vFlYvicmbOzOWQTKTtKjOSfCKVca68WcprSpfad750RWOabniQnKPmWkjUAhISRlN9J5QCAnBEnmw73jaG5KgRMMWE3PsQA2jcq/tQ7M9OBHa35ze0C1gZwRRkKmIfwltnn6W3XbsRMMfRjwQ7KSGFlFQdJKjOUnWVhDj7EJxxBkcHptPsKge+tP8dOB/+npYrHoX9EMz8AoVh1T3pAgAA"
>>> json.loads(gzip.decompress(base64.b64decode(encoding)))
{'nodes': {'della-i14g11': {'total_memory': 42949672960, 'used_memory': 1102004224, 'total_time': 29202.2, 'cpus': 10, 'gpu_total_memory': {'0': 42949672960}, 'gpu_used_memory': {'0': 638058496}, 'gpu_utilization': {'0': 0}}, 'della-i14g13': {'total_memory': 42949672960, 'used_memory': 1107677184, 'total_time': 29195.8, 'cpus': 10, 'gpu_total_memory': {'0': 42949672960}, 'gpu_used_memory': {'0': 638058496}, 'gpu_utilization': {'0': 0}}, 'della-i14g6': {'total_memory': 42949672960, 'used_memory': 1102434304, 'total_time': 29139.5, 'cpus': 10, 'gpu_total_memory': {'0': 42949672960}, 'gpu_used_memory': {'0': 638058496}, 'gpu_utilization': {'0': 0}}, 'della-i14g4': {'gpu_total_memory': {'0': 42949672960}, 'gpu_used_memory': {'0': 638058496}, 'gpu_utilization': {'0': 0}}}, 'total_time': 29297, 'gpus': True}
```

```
{'tiger-i19g12': {'total_memory': 68719476736, 'used_memory': 1875886080, 'total_time': 221.7, 'cpus': 16, 'gpu_total_memory': {'3': 17071734784, '2': 17071734784, '1': 17071734784, '0': 17071734784}, 'gpu_used_memory': {'1': 414318592, '0': 16717578240, '2': 414318592, '3': 414318592}, 'gpu_utilization': {'1': 0, '3': 0.3, '2': 0, '0': 87.1}}}
```

#### json.loads return a Python dict

There are three attributes at the highest level:

```
t['nodes'], t['total_time'], t['gpus']
```

```
[jdh4@della8 ~]$ jobstats 40409215
Memory usage per node - used/allocated
    della-i14g11: 1.0GB/40.0GB (105.1MB/4.0GB per core of 10)
    della-i14g13: 1.0GB/40.0GB (105.6MB/4.0GB per core of 10)
    della-i14g6: 1.0GB/40.0GB (105.1MB/4.0GB per core of 10)
Traceback (most recent call last):
  File "/usr/local/bin/jobstats", line 300, in <module>
    stats.report_job()
  File "/usr/local/bin/jobstats", line 226, in report_job
    used = sp_node[n]['used_memory']
KeyError: 'used_memory'
```

```
>>> pprint.pprint(t)
{'gpus': True,
 'nodes': {'della-i14g11': {'cpus': 10,
                            'gpu_total_memory': {'0': 42949672960},
                            'gpu_used_memory': {'0': 638058496},
                            'gpu_utilization': {'0': 0},
                            'total_memory': 42949672960,
                            'total_time': 29202.2,
                            'used_memory': 1102004224},
           'della-i14g13': {'cpus': 10,
                            'gpu_total_memory': {'0': 42949672960},
                            'gpu_used_memory': {'0': 638058496},
                            'gpu_utilization': {'0': 0},
                            'total_memory': 42949672960,
                            'total_time': 29195.8,
                            'used_memory': 1107677184},
           'della-i14g4': {'gpu_total_memory': {'0': 42949672960},
                           'gpu_used_memory': {'0': 638058496},
                           'gpu_utilization': {'0': 0}},
           'della-i14g6': {'cpus': 10,
                           'gpu_total_memory': {'0': 42949672960},
                           'gpu_used_memory': {'0': 638058496},
                           'gpu_utilization': {'0': 0},
                           'total_memory': 42949672960,
                           'total_time': 29139.5,
                           'used_memory': 1102434304}},
 'total_time': 29297}
```

```
$ jobstats 39861033
Memory usage per node - used/allocated
    della-r2c1n16: 25.3GB/64.0GB (3.2GB/8.0GB per core of 8)
Total used/allocated: 25.3GB/64.0GB (3.2GB/8.0GB per core of 8)

CPU Usage per node (cpu time used/runtime)
    della-r2c1n16: 07:52:18/08:00:08 (efficiency=98.4%)
Total used/runtime: 07:52:18/08:00:08, efficiency=98.4%
```

## jobid vs. jobidraw

```
$ sacct -j 39861033 -o jobid%30,jobidraw%30
                         JobID                       JobIDRaw 
------------------------------ ------------------------------ 
                      39861033                       39861033 
                39861033.batch                 39861033.batch 
               39861033.extern                39861033.extern 
                    39861033.0                     39861033.0

$ sacct -j 40345776_97 -o jobid%30,jobidraw%30
                         JobID                       JobIDRaw 
------------------------------ ------------------------------ 
                   40345776_97                       40356660 
             40345776_97.batch                 40356660.batch 
            40345776_97.extern                40356660.extern 
                 40345776_97.0                     40356660.0

$ sacct -j 40345776_98 -o jobid%30,jobidraw%30
                         JobID                       JobIDRaw 
------------------------------ ------------------------------ 
                   40345776_98                       40356661 
             40345776_98.batch                 40356661.batch 
            40345776_98.extern                40356661.extern 
                 40345776_98.0                     40356661.0
```

## Using the class externally

```python
stats = mymodule.JobStats("40376693", cluster="della")
print(stats.report_job_json(False))
```

```
$ python3 demo.py 
{
    "gpus": 4,
    "nodes": {
        "della-i14g11": {
            "cpus": 24,
            "gpu_total_memory": {
                "0": 42949672960,
                "1": 42949672960
            },
            "gpu_used_memory": {
                "0": 35640573952,
                "1": 35640573952
            },
            "gpu_utilization": {
                "0": 72.6,
                "1": 72.9
            },
            "total_memory": 68719476736,
            "total_time": 1159766.2,
            "used_memory": 17839022080
        },
        "della-i14g7": {
            "cpus": 24,
            "gpu_total_memory": {
                "0": 42949672960,
                "1": 42949672960
            },
            "gpu_used_memory": {
                "0": 38834536448,
                "1": 35640508416
            },
            "gpu_utilization": {
                "0": 68.9,
                "1": 70.4
            },
            "total_memory": 68719476736,
            "total_time": 1165097.3,
            "used_memory": 16258260992
        }
    },
    "total_time": 518710
}
```


## busted

```
# tiger
$ jobstats 8448964
Memory usage per node - used/allocated
    tiger-i19g10: 178.5MB/32.0GB (8.9MB/1.6GB per core of 20)
    tiger-i20g14: 0.0B/32.0GB (0.0B/1.6GB per core of 20)
    tiger-i20g16: 0.0B/32.0GB (0.0B/1.6GB per core of 20)
    tiger-i20g3: 0.0B/32.0GB (0.0B/1.6GB per core of 20)
    tiger-i21g12: 0.0B/32.0GB (0.0B/1.6GB per core of 20)
    tiger-i21g13: 0.0B/32.0GB (0.0B/1.6GB per core of 20)
Total used/allocated: 178.5MB/192.0GB (1.5MB/1.6GB per core of 120)

CPU Usage per node (cpu time used/runtime)
    tiger-i19g10: 00:00/10:00 (efficiency=0.1%)
    tiger-i20g14: 00:00/10:00 (efficiency=0.0%)
    tiger-i20g16: 00:00/10:00 (efficiency=0.0%)
    tiger-i20g3: 00:00/10:00 (efficiency=0.0%)
    tiger-i21g12: 00:00/10:00 (efficiency=0.0%)
    tiger-i21g13: 00:00/10:00 (efficiency=0.0%)
Total used/runtime: 00:00/01:00:00, efficiency=0.0%

GPU Memory utilization, per node(GPU) - maximum used/total
    tiger-i19g10(GPU#0): 0.0B/15.9GB (0.0%)
    tiger-i19g10(GPU#2): 0.0B/15.9GB (0.0%)
    tiger-i20g14(GPU#0): 0.0B/15.9GB (0.0%)
    tiger-i20g14(GPU#3): 0.0B/15.9GB (0.0%)
    tiger-i20g16(GPU#0): 0.0B/15.9GB (0.0%)
    tiger-i20g16(GPU#3): 0.0B/15.9GB (0.0%)
Traceback (most recent call last):
  File "/usr/local/bin/jobstats", line 300, in <module>
    stats.report_job()
  File "/usr/local/bin/jobstats", line 251, in report_job
    gpus = list(d['gpu_total_memory'].keys())
KeyError: 'gpu_total_memory'
```


```
# trying traverse job on tiger (need to add "make sure you are on the right login node")
$ jobstats 296059
I found no stats for job 296059, either because it is too old or because it expired from jobstats database.
```
