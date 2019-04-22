'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    schedule = []
    current_time = 0
    waiting_time = 0
    completed_count = 0

    # put the first process in queue
    queue = []
    # an task consists of process object and remaining time
    task = [process_list[0], process_list[0].burst_time]
    queue.append(task)

    while completed_count < len(process_list):   # some task not yet finished
        if len(queue) == 0:  # waiting for new arrival
            next_process = filter(lambda proc:proc.arrive_time>current_time, process_list)[0]
            current_time = next_process.arrive_time
            # print 'add process {} to queue scheduled for time {}'.format(next_process, current_time)
            queue.append([next_process, next_process.burst_time])
            continue

        # pick next task
        cur_task = queue.pop(0)
        schedule.append((current_time, cur_task[0].id))
        time_used = min(cur_task[1], time_quantum)
        previous_time = current_time
        current_time += time_used

        # check new tasks arrived while task is being executed
        # resolve tie: if task 1 finishes current cycle at the same time as task 2 arrives, task 2 enters queue FIRST
        new_arrivals = filter(lambda proc:previous_time<proc.arrive_time<=current_time, process_list)
        # if len(new_arrivals):
            # print "between time %s and %s, new arrivals are %s" % (previous_time, current_time, new_arrivals)
        for process in new_arrivals:
            queue.append([process, process.burst_time])

        cur_task[1] -= time_used

        if cur_task[1] > 0:
            queue.append(cur_task) # put back to end of queue
        else:
            waiting_time += current_time - cur_task[0].arrive_time - cur_task[0].burst_time
            completed_count += 1

    # print "Completion time: {}".format(current_time)
    avg_waiting_time = 1.0 * waiting_time / completed_count

    return schedule, avg_waiting_time

def SRTF_scheduling(process_list):
    schedule = []
    current_time = process_list[0].arrive_time
    complete_count = 0
    arrival_count = 0
    waiting_time = 0
    queue = []

    while complete_count < len(process_list):

        arrivals = filter(lambda proc:proc.arrive_time==current_time, process_list)
        for arrival in arrivals:
            # print "added task {} @ time {}".format(arrival, current_time)
            queue.append([arrival, arrival.burst_time])
            arrival_count += 1

        queue.sort(key=lambda task:task[1])
        cur_task = queue[0]
        next_arrival = process_list[arrival_count] if arrival_count < len(process_list) else None
        # switch
        if len(schedule) == 0 or cur_task[0].id != schedule[-1][1]:
            schedule.append((current_time, cur_task[0].id))

        if cur_task[1] == 0:   # the task has finished
            complete_count += 1
            waiting_time += current_time - cur_task[0].arrive_time - cur_task[0].burst_time
            queue.pop(0)
            # print "finished task {} at time {}".format(cur_task, current_time)
            if complete_count == len(process_list): # just finished the last job
                continue
            if len(queue) > 0:
                cur_task = queue[0]
                schedule.append((current_time, cur_task[0].id))
            else:   # waiting for next arrival
                current_time = next_arrival.arrive_time
                continue

        time_step = min(cur_task[1], next_arrival.arrive_time-current_time if next_arrival else 9999)
        cur_task[1] -= time_step
        current_time += time_step

    avg_waiting_time = 1.0*waiting_time/complete_count

    return schedule, avg_waiting_time

def SJF_scheduling(process_list, alpha):
    predictions = [5, 5, 5, 5]

    complete_count = 0
    queue = []
    schedule = []
    task = [process_list[0], process_list[0].burst_time]
    queue.append(task)
    current_time = 0
    prev_time = 0
    waiting_time = 0

    while complete_count < len(process_list):
        # add arrivals during execution of current task
        new_arrivals = filter(lambda proc: prev_time<proc.arrive_time<=current_time, process_list)
        for arrival in new_arrivals:
            queue.append([arrival, arrival.burst_time])

        prev_time = current_time

        if queue[0][1] == 0:  # first task in queue has completed
            completed_process = queue[0][0]
            complete_count += 1
            # print 'complete task {} at time {}, new pred {}'.format(complete_count, current_time, predictions)
            waiting_time += current_time - completed_process.arrive_time - completed_process.burst_time
            new_prediction = 1.0 * alpha * completed_process.burst_time + 1.0 * (1-alpha) * predictions[completed_process.id]
            predictions[completed_process.id] = new_prediction
            queue.pop(0)  # remove the completed process

            if len(queue) > 0:
                queue.sort(key=lambda task:predictions[task[0].id])
                cur_task = queue[0]
                schedule.append((current_time, cur_task[0].id))
                # prepare for next event time
                current_time += cur_task[1]
                cur_task[1] = 0
            elif complete_count<len(process_list):
                current_time = filter(lambda proc:proc.arrive_time>current_time, process_list)[0].arrive_time
                continue
        else:
            cur_task = queue[0]
            schedule.append((current_time, cur_task[0].id))
            current_time += queue[0][1]
            queue[0][1] = 0

    avg_waiting_time = 1.0*waiting_time/complete_count

    return schedule, avg_waiting_time


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

    print "Experiment RR"
    for i in range(1, 11, 1):
        _, time = RR_scheduling(process_list, time_quantum=i)
        print 'time_quantum=%s, average_waiting_time=%s' % (i, time)
    print "Experiment SJF"
    for i in range(0, 11, 1):
        alpha = 1.0*i/10
        _, time = SJF_schedule, SJF_avg_waiting_time = SJF_scheduling(process_list, alpha = alpha)
        print "alpha=%s, average_waiting_time=%s" % (alpha, time)


if __name__ == '__main__':
    main(sys.argv[1:])


