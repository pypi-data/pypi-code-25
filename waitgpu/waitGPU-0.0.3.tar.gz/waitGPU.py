import os
import gpustat
import time

def proc_sat(gpu, nproc):
    """ Return true if the number of processes on gpu is at most nproc"""
    return len(gpu.entry['processes']) <= nproc

def util_sat(gpu, util):
    """ Return true if the gpu utilization is at most util """
    return float(gpu.entry['utilization.gpu']) <= util

def mem_ratio_sat(gpu, mem_ratio):
    """ Return true if the memory utilization is at most mem_ratio """
    r = float(gpu.entry['memory.used'])/float(gpu.entry['memory.total'])
    return r <= mem_ratio

def avail_mem_sat (gpu, mem):
    """ Return true if there is at least mem available memory """
    avail_mem = float(gpu.entry['memory.total'])-float(gpu.entry['memory.used'])
    return mem <= avail_mem

def gpu_id_sat(gpu, gpu_ids):
    gid = int(gpu.entry['index'])
    return gid in gpu_ids

def wait(utilization=None, memory_ratio=None, available_memory=None,
         interval=10, gpu_ids=None, nproc=None, ngpu=1):
    print("waitGPU: Waiting for the following conditions, checking every {} seconds. "
          .format(interval))
    conditions = []
    if utilization is not None:
        conditions.append(lambda gpu: util_sat(gpu, utilization))
        print("+ utilization <= {}".format(utilization))
    if memory_ratio is not None:
        conditions.append(lambda gpu: mem_ratio_sat(gpu, memory_ratio))
        print("+ memory_ratio <= {}".format(memory_ratio))
    if available_memory is not None:
        conditions.append(lambda gpu: avail_mem_sat(gpu, available_memory))
        print("+ available_memory >= {}".format(available_memory))
    if gpu_ids is not None:
        conditions.append(lambda gpu: gpu_id_sat(gpu, gpu_ids))
        print("+ GPU id is {}".format(gpu_ids))
    if nproc is not None:
        conditions.append(lambda gpu: proc_sat(gpu, nproc))
        print("+ n_processes <= {}".format(nproc))

    while True:
        free_gpu_ids = []
        stats = gpustat.GPUStatCollection.new_query()
        for gpu in stats:
            if all(c(gpu) for c in conditions):
                free_gpu_ids.append(int(gpu.entry['index']))
            if len(free_gpu_ids) == ngpu:
                break
        if len(free_gpu_ids) < ngpu:
            time.sleep(interval)
        else:
            break

    print("waitGPU: Setting GPU to: {}".format(free_gpu_ids))
    os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
    os.environ['CUDA_VISIBLE_DEVICES'] = ",".join(map(str, free_gpu_ids))
