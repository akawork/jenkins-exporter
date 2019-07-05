NODE_SLAVE = 'hudson.slaves.SlaveComputer'

NODE_LABELS = 'totalExecutors,busyExecutors,computer[_class,displayName,offline,numExecutors,monitorData[*]]'

SWAP_SPACE_MONITOR = 'hudson.node_monitors.SwapSpaceMonitor'
SWAP_SPACE_LABELS = ['availablePhysicalMemory','availableSwapSpace','totalPhysicalMemory','totalSwapSpace']
TEMPORARY_SPACE_MONITOR = 'hudson.node_monitors.TemporarySpaceMonitor'
DISK_SPACE_MONITOR = 'hudson.node_monitors.DiskSpaceMonitor'
MONITOR_LABELS = ['availablePhysicalMemory','availableSwapSpace','totalPhysicalMemory','totalSwapSpace','temporarySpace','diskSpace']