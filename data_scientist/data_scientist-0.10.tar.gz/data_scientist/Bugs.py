runtime_log=[]
runtime_log.append(['0 || START || '+str(dt.datetime.now())])
exception_handling_index=1
def successful_event():
    runtime_log.append([str(exception_handling_index)+' || SUCCESS || '+ str(dt.datetime.now())])
    globals()['exception_handling_index'] += 1
def bug_event():
    runtime_log.append([str(exception_handling_index)+' || BUG || '+ str(dt.datetime.now())
                        +' || '+str(sys.exc_info())])
    globals()['exception_handling_index'] += 1
def final_event():
    runtime_log.append([str(exception_handling_index)+' || END || '+str(dt.datetime.now())])
    with open('/'.join(sys.argv[0].split('/')[:-1])
              +'/LOG_runtime_'+(sys.argv[0].split('/')[-1]).split('.')[0]+'.csv',
              'a',newline='') as output:
        L = csv.writer(output)
        L.writerow('\n')
        L.writerow(['RUNTIME RECORD',str(dt.datetime.now())])
        for log_item in runtime_log:
            L.writerow(log_item)

