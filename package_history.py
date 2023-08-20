import pkg_resources

dists = [d for d in pkg_resources.working_set]
# Filter out distributions you don't care about and use.
print(dists)
