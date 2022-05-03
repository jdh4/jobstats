import importlib.machinery
import importlib.util
loader = importlib.machinery.SourceFileLoader('jobstats', '/usr/local/bin/jobstats')
spec = importlib.util.spec_from_loader('jobstats', loader)
mymodule = importlib.util.module_from_spec(spec)
loader.exec_module(mymodule)

# Use mymodule
stats = mymodule.JobStats("40376693", cluster="della")
print(type(stats))
stats.report_job()
