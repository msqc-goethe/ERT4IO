# Empirical Roofline Tool for I/O (ERT4IO)
To better understand the I/O of emerging workloads and to provide a more comprehensive characterization of HPC systems and implement a consistent scoring model in the future, we have adopted the classic Roofline model for I/O workload analysis. Our model provides a basic understanding of how close observed I/O performance is to peak performance and can also be used to identify performance bottlenecks.

ERT4IO is a python script to plot the I/O Roofline graph for applications and benchmarks. It is based on the parsed text file from darshan outputs. Through the integration of pydarshan .darshan files can be used directly.


## The I/O Roofline Model
To tailor the model for characterizing I/O performance, our I/O Roofline model is based on the most widely accepted performance metric for I/O, i.e., IOPS and the corresponding bandwidth. 
- IOPS measures the number of reads and writes that a storage system can perform per second. The metric indicates how many operations the storage system can handle within a fixed period of time, which is important for applications that require a large number of small operations.
- Throughput measures the total amount of data that can be read or written per second. It reflects the bandwidth of the storage system, which is important for applications where large amounts of data need to be transferred quickly, such as scientific simulations and training phases for machine learning.

Regarding the I/O stack, the I/O operations on each layer are different. In this work, we focus on POSIX and MPI-IO, therefore the I/O operations of both layers can be examined. 

### Attainable performance
The upper bound for the attainable performance in terms of IOPS is defined by: 

$\text{Attainable Performance} = Min(
\text{Peak IOPS}, \\\ 
\text{Peak I/O Bandwidth} \times \text{ I/O Intensity})$

### I/O intensity 
Corresponds to the total number of I/O operations (IOP) per bytes read and written, as shown below:  

$\text{I/O Intensity} = \frac{\text{Total I/O Operations}}{(\text{Read Bytes} + \text{Write Bytes})}$


# 
If you use ERT4IO or our I/O Roofline model in your research, we would appreciate the following citation in any publications to which it has contributed:

Zhu, Zhaobin, Niklas Bartelheimer, and Sarah Neuwirth. "An Empirical Roofline Model for Extreme-Scale I/O Workload Analysis." 2023 IEEE International Parallel and Distributed Processing Symposium Workshops (IPDPSW). IEEE, 2023.

## Usage
```sh
python3 ERT4IO.py -p <"darshan_outputs_dir"> -d <is_darshan_output>
```
## Examples
To run the demo without any parameters:
```sh
python3 ERT4IO.py
```
Runs the ERT4IO with specified darshan outputs 
```sh
python3 ERT4IO.py python3 ERT4IO.py -p demo_darshan_outputs -d 1
```
## Notes
- The darshan output files should be in the same directory.
- The darshan output files should be in the following format:
  - <"system_name"_"app_name"_n"num_process">.<"api">
  - For example: fuchs_ior_n1.posix
- Peak outputs should be renamed to the following format:
  - peak_<"system_name"_"app_name"_n"num_process">.<api>
  - For example: peak_fuchs_ior_n900.posix
