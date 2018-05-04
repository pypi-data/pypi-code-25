import random
import time
from utils import secs_to_time
from pprint import pprint
import copy


class Queue(object):
    """
    A generic queue object.
    """
    _ID = 0

    def __init__(self):
        self.id = self._ID
        self.__class__._ID += 1
        self.contents = []


class FIFOQueue(Queue):
    """
    A FIFO queue. Inherits from / subclass of Queue.
    """
    def __init__(self):
        super(FIFOQueue, self).__init__()
        self.priority = 1


class SearchQueue(Queue):
    """
    A search-type queue. Inherits from Queue.
    """
    def __init__(self):
        super(SearchQueue, self).__init__()


class Site(object):
    _ID = 0

    def __init__(self, name):
        self.id = self._ID
        self.__class__._ID += 1
        self.name = name
        self.tz = None


class Schedule(object):
    _ID = 0

    def __init__(self):
        self.id = self._ID
        self.__class__._ID += 1

# eventually, AgentSchedule should inherit from this class??
# the idea is to also have Schedules be possible for Queues.
# should Queues just have a regular schedule or do they need a
# QueueSchedule object??


class Agent(object):
    _ID = 0
    def __init__(self, schedule): # maybe schedule shouldn't be required for agent to simply exist...
        self.id = self._ID; self.__class__._ID += 1
        self.schedule = schedule
        self.status = 'logged_off'
        self.last_status = 'initialized'
        self.time_in_status = 0
        self.active_call = False
        self.previously_active = False
        self.handling_call = None
        self.outbound_reserved = False
        self.previously_outbound = False
        self.skills = []

    def reset(self):
        self.status = 'logged_off'
        self.last_status = 'initialized'
        self.time_in_status = 0
        self.active_call = False
        self.previously_active = False
        self.handling_call = None
        self.outbound_reserved = False
        self.previously_outbound = False

class AgentSchedule(object):
    _ID = 0
    def __init__(self, regular_start=28800, regular_end=(3600*16.5), regular_lunch=(3600*12), lunch_duration=1800, tz='America/Chicago', work_days=[1,2,3,4,5]):
        self.id = self._ID; self.__class__._ID += 1
        self.regular_start = regular_start
        self.regular_end = regular_end
        self.regular_lunch = regular_lunch
        self.lunch_duration = lunch_duration
        self.tz = tz
        self.work_days = work_days
        self.site = None

class Day(object):
    _ID = 0
    def __init__(self, agents, calls, outbound_list=[], outbound_reservation=0.0, dials_per_reservation=0.0, reservation_length=0.0):
        self.id = self._ID; self.__class__._ID += 1
        self.agents = agents
        self.calls = calls
        self.outbound_list = outbound_list
        self.outbound_reservation = outbound_reservation
        self.dials_per_reservation = dials_per_reservation
        self.reservation_length = reservation_length
        self.INITIAL_OUTBOUND_LIST_COUNT = len(outbound_list)
        self.sl_threshold = 20
        self.sl_target = 0.90
        self.sl_upper_limit = 1.0
        self.interval = 15 * 60 # 15 minutes

        self.sl_interval_dict = {}

        earliest_arrival = 99999

        for call in self.calls:
            if call.arrival_timestamp < earliest_arrival:
                earliest_arrival = call.arrival_timestamp

        self.earliest_arrival = earliest_arrival

        self.agents_currently_available = 0
        self.agents_currently_logged_on = 0

        self.offered_calls = 0
        self.completed_calls = 0
        self.completed_calls_total_duration = 0
        self.active_calls = 0
        self.queued_calls = 0
        self.abandoned_calls = 0
        self.calls_within_sl = 0
        self.average_aht = '--'

    def percent_agents_available(self):
        try:
            return self.agents_currently_available / self.agents_currently_logged_on
        except ZeroDivisionError:
            return 0.0

    def dials_made(self):
        return self.INITIAL_OUTBOUND_LIST_COUNT - len(self.outbound_list)

    def dials_remaining(self):
        return len(self.outbound_list)

    def service_level(self):
        try:
            return 1.0 * self.calls_within_sl / self.offered_calls
        except ZeroDivisionError:
            return 1.0

    def print_status_line(self):
        return (' offered: ' + str(self.offered_calls) + ' queued: ' + str(self.queued_calls) + ' active: ' + str(self.active_calls) +
                ' completed: ' + str(self.completed_calls) + ' abandoned: ' + str(self.abandoned_calls) +
                ' SL: ' + "{0:.2f}%".format(100*self.service_level()) +
                ' aht: ' + str(self.average_aht) +
                ' dials: ' + str(self.dials_made()) +
                ' dials left: ' + str(self.dials_remaining())
               )

    def list_of_completed_calls(self):
        return [call for call in self.calls if call.status=='completed']

    def aht(self):
        try:
            return self.completed_calls_total_duration / self.completed_calls
        except ZeroDivisionError:
            return '--'

    def reset(self):
        for call in self.calls:
            call.reset()
        for agent in self.agents:
            agent.reset()

class Call(object):
    _ID = 0
    def __init__(self, arrival_timestamp, duration, direction='in'):
        self.id = self._ID; self.__class__._ID += 1
        self.arrival_timestamp = arrival_timestamp
        self.duration = duration
        self.status = 'pre-call'
        self.queued_at = None
        self.answered_at = None
        self.abandoned_at = None
        self.queue_elapsed = None
        self.handled_by = None
        self.met_sl = False
        self.queue = None

    def reset(self):
        self.status = 'pre-call'
        self.queued_at = None
        self.answered_at = None
        self.queue_elapsed = None
        self.handled_by = None
        self.met_sl = False

def simulate_one_step(timestamp, day, abandon_dist, skip_sleep=True, fast_mode=True, verbose_mode=False):
    i = timestamp
    day = reserve_outbound(day, i)
    day = cancel_reservation(day, i)

    c = 0
    pc = 0

    day.agents_currently_available = 0
    day.agents_currently_logged_on = 0
    day.offered_calls = 0
    day.completed_calls = 0
    day.completed_calls_total_duration = 0
    day.active_calls = 0
    day.queued_calls = 0
    day.abandoned_calls = 0
    day.calls_within_sl = 0
    day.average_aht = day.aht()

    for agent in day.agents:
        agent = agent_logons(agent, i)
        agent = agent_logoffs(agent, i)
        agent = update_agent_status_stats(agent, i)
        day = agents_currently_available(day, agent)
        day = agents_currently_logged_on(day, agent)

    for call in day.calls:
        call = queue_calls(call, i)
        call = answer_calls(call, day, i)
        call = hangup_calls(call, i)
        call = update_queued_call_stats(call, i)
        call = abandon_calls(call, i, abandon_dist)
        if call.status == 'completed':
            c += 1
        elif call.status == 'pre-call':
            pc += 1
        day = offered_calls(day, call)
        day = completed_calls(day, call)
        day = active_calls(day, call)
        day = queued_calls(day, call)
        day = abandoned_calls(day, call)
        day = calls_within_sl(day, call)
    
    if pc == len(day.calls) or c == len(day.calls):
        fast_mode = True # enters fast mode when all calls are pre-call or done

    if not skip_sleep:
        if fast_mode:
            time.sleep(0.00001)
        else:
            time.sleep(0.05)
    
    if verbose_mode:
        print(secs_to_time(i) + day.print_status_line())

    return day

def simulate_day(day, abandon_dist, skip_sleep=True, fast_mode=True, verbose_mode=False):
    for i in range(3600*24):
        day = simulate_one_step(timestamp=i, day=day, abandon_dist=abandon_dist, skip_sleep=skip_sleep, fast_mode=fast_mode, verbose_mode=verbose_mode)
    return day

def simulate_days(day_list, abandon_dist, skip_sleep=True, fast_mode=True, verbose_mode=False):
    for day in day_list:
        day = simulate_day(day, abandon_dist, skip_sleep, fast_mode, verbose_mode)
    return day_list

def simulate_days_alt(projected_volume_df, vol_dim, day_of_week_dist, day_start_time, handles_base,
                      agent_list, abandon_dist, outbound_list=[], outbound_reservation=0.0,
                      dials_per_reservation=0.0, reservation_length=0,
                      skip_sleep=True, fast_mode=True, verbose_mode=False):
    
    simulated_days = []
    
    for i, day in projected_volume_df.iterrows():
        count_calls = day[vol_dim]
        arrival_rates = count_calls * day_of_week_dist
        arrival_times = []

        start_time = day_start_time

        for x in arrival_rates:
            for xx in range(start_time, start_time + 900):
                threshold = x / 900
                if random.random() < threshold:
                    arrival_times.append(xx)
            start_time += 900

        calls_list = []
        actual_num_calls = len(arrival_times)
        call_durations = handles_base.sample(actual_num_calls)

        for arr, dur in zip(arrival_times, call_durations):
            calls_list.append(Call(arr,dur))

        day_object = Day(agent_list, calls_list, outbound_list=outbound_list, 
                         outbound_reservation=outbound_reservation,
                         dials_per_reservation=dials_per_reservation,
                         reservation_length=reservation_length)

        simulated_day = simulate_day(day_object, abandon_dist)
        simulated_days.append(simulated_day)
    
    return simulated_days


def agent_logons(agent, timestamp):
    if agent.schedule.regular_start == timestamp and agent.status == 'logged_off':
        agent.status = 'logged_on'
    return agent

def agent_logoffs(agent, timestamp):
    if agent.active_call == False and agent.status == 'logged_on' and agent.schedule.regular_end <= timestamp and agent.outbound_reserved == False:
        agent.status = 'logged_off'
    return agent

def update_agent_status_stats(agent, timestamp):
    if agent.last_status != agent.status or agent.previously_active != agent.active_call or agent.previously_outbound != agent.outbound_reserved:
        agent.last_status = agent.status
        agent.previously_active = agent.active_call
        agent.previously_outbound = agent.outbound_reserved
        agent.time_in_status = 0
    else:
        agent.time_in_status += 1
    return agent

def agents_currently_available(day, agent):
    if agent.status == 'logged_on' and agent.active_call == False and agent.outbound_reserved == False:
        day.agents_currently_available += 1
    return day

def agents_currently_logged_on(day, agent):
    if agent.status == 'logged_on':
        day.agents_currently_logged_on += 1
    return day

def queue_calls(call, timestamp):
    if call.arrival_timestamp == timestamp:
        call.status = 'queued'
        call.queued_at = timestamp
    return call

def update_queued_call_stats(call, timestamp):
    if call.status == 'queued':
        call.queue_elapsed = timestamp - call.queued_at
    return call

def answer_calls(call, day, timestamp):
    if call.status == 'queued':
        for agent in day.agents:
            if agent.status == 'logged_on' and agent.active_call == False and agent.outbound_reserved == False:
                agent.active_call = True
                agent.handling_call = call.id
                call.handled_by = agent
                call.answered_at = timestamp
                call.queue_elapsed = timestamp - call.queued_at
                call.met_sl = (call.queue_elapsed <= day.sl_threshold)
                call.status = 'active'
                break
    return call

def hangup_calls(call, timestamp):
    if call.status == 'active' and (call.duration + call.answered_at) <= timestamp:
        call.status = 'completed'
        call.completed_at = timestamp
        call.handled_by.active_call = False
        call.handled_by.handling_call = None
    return call

def abandon_calls(call, timestamp, abandon_distribution):
    abandon_distribution = sorted(abandon_distribution)
    if call.status == 'queued':
        for aban_tuple in abandon_distribution:
            if aban_tuple[0] >= call.queue_elapsed:
                if random.random() >= aban_tuple[1]:
                    call.status = 'abandoned'
                    call.abandoned_at = timestamp
                    break
    return call

def offered_calls(day, call):
    if call.status != 'pre-call':
        day.offered_calls += 1
    return day

def completed_calls(day, call):
    if call.status == 'completed':
        day.completed_calls += 1
        day.completed_calls_total_duration += call.duration
    return day

def active_calls(day, call):
    if call.status == 'active':
        day.active_calls += 1
    return day

def queued_calls(day, call):
    if call.status == 'queued':
        day.queued_calls += 1
    return day

def abandoned_calls(day, call):
    if call.status == 'abandoned':
        day.abandoned_calls += 1
    return day

def calls_within_sl(day, call):
    if call.met_sl:
        day.calls_within_sl += 1
    return day

def reserve_outbound(day, timestamp):
    if not day.outbound_list == [] and day.percent_agents_available() < day.outbound_reservation and day.agents_currently_available() >= 2:
        longest_available_time = 0 
        reservation_candidate = None
        for agent in day.agents:
            if agent.status == 'logged_on' and agent.active_call == False and agent.outbound_reserved == False:
                if agent.time_in_status > longest_available_time:
                    reservation_candidate = agent
                    longest_available_time = agent.time_in_status
        if reservation_candidate is not None:
            reservation_candidate.outbound_reserved = True
    return day

def cancel_reservation(day, timestamp):
    for agent in day.agents:
        if agent.outbound_reserved == True:
            if agent.time_in_status == day.reservation_length:
                agent.outbound_reserved = False
                # strike dials_per_reservation from front of list
                day.outbound_list = day.outbound_list[day.dials_per_reservation:]
    return day

def round_down_900(stamp):
    return stamp - (stamp % 900)

def binary_search(current, previous, forward=True):
    difference = abs(previous - current)
    previous = current
    if forward:
        current += 0.5 * difference
    else:
        current -= 0.5 * difference
        if current < 0:
            current = 0
    current = int(current)
    return current, previous

def calculate_required_headcount(day, abandon_dist, agent_counts={}, skip_sleep=True, fast_mode=True, verbose_mode=False):
    
    first_agent_start = round_down_900(day.earliest_arrival)

    day_completed = False

    saved_day_state = copy.deepcopy(day)
    completed_time = first_agent_start

    prev_agent_counts = {x: 0 for x in range(3600*24) if x % 900 == 0}

    while not day_completed:
        
        day = copy.deepcopy(saved_day_state)
        
        agent_list = []

        for i in list(agent_counts.keys()):
            for ii in range(0, int(agent_counts[i])):
                agent_list.append(Agent(AgentSchedule(regular_start=i, regular_end=i+900, regular_lunch=3600*24)))

        day.agents = agent_list
        
        for stamp in range(completed_time,3600*24):
            day = simulate_one_step(timestamp=stamp, day=day, abandon_dist=abandon_dist, skip_sleep=skip_sleep, fast_mode=fast_mode, verbose_mode=verbose_mode)
            if stamp % 900 == 0:
                day.sl_interval_dict[stamp] = day.service_level()
                last_interval = stamp-900
                if day.service_level() < day.sl_target:
                    agent_counts[last_interval], prev_agent_counts[last_interval] = binary_search(
                        agent_counts[last_interval],
                        prev_agent_counts[last_interval],
                    )
                    #pprint(agent_counts)
                    print(agent_counts[last_interval])
                    break
                elif (day.service_level() >= day.sl_upper_limit) and (agent_counts[last_interval] > 0):
                    agent_counts[last_interval], prev_agent_counts[last_interval] = binary_search(
                        agent_counts[last_interval],
                        prev_agent_counts[last_interval],
                        forward=False,
                    )
                    #pprint(agent_counts)
                    print(agent_counts[last_interval])
                    break
                else:
                    saved_day_state = copy.deepcopy(day)
                    completed_time = stamp
            if stamp == 86399:
                day_completed = True

    pprint(agent_counts)
    return agent_counts, day

