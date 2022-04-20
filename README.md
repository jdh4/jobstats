# jobstats

## Useful Links

[https://prometheus.io/docs/instrumenting/exporters/](https://prometheus.io/docs/instrumenting/exporters/)  


## issues

Crashes when try to make a jobstats  object without jobid

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
