import uvsc
import time
import binascii
from time import sleep


def delay_secs(seconds):
    print ("Now sleeping for " + str(seconds) + " seconds")
    for i in xrange(seconds,0,-1):
        time.sleep(1)
        print (i)

uvsc.debug_on = 1
uvsc.Init()

print (uvsc.Version())
uvsc.OpenConnection(4823)

#uvsc.GEN_HIDE() 
#delay_secs(1)
#uvsc.GEN_SHOW()

uvsc.PRJ_CLOSE()
uvsc.PRJ_LOAD("D:\Temp\Blinky\Blinky.uvprojx")
#uvsc.PRJ_ADD_FILE("Source Files", "D:\Temp\Blinky\testfile.c")
#uvsc.PRJ_DEL_FILE("Source Files", "D:\Temp\Blinky\testfile.c")
uvsc.PRJ_BUILD()
uvsc.DBG_ENTER()
print (uvsc.DBG_STATUS())
print ("tid_PhaseA= "  , uvsc.DBG_CALC_EXPRESSION("tid_phaseA"))
print ("&tid_PhaseA= " , uvsc.DBG_CALC_EXPRESSION("&tid_phaseA"))
print ("Setting PC to: ", uvsc.DBG_CALC_EXPRESSION("PC=0"))
print ("SystemCoreClock= ", uvsc.DBG_CALC_EXPRESSION("SystemCoreClock"))
print ("External Clock= ", uvsc.DBG_VTR_GET("CLOCK"))

membuf = uvsc.DBG_MEM_READ (0, 256)
result = list(membuf)
print(result)
uvsc.DBG_MEM_WRITE(0x10000, 256, membuf)
uvsc.DBG_STEP_INSTRUCTION_N(4)
uvsc.DBG_STEP_HLL_N(4)

uvsc.DBG_EXEC_CMD("BS clock")

#uvsc.DBG_CREATE_BP("BRKTYPE_EXEC", r"\\Blinky\Blinky.c\125", 1)
#uvsc.DBG_CREATE_BP("BRKTYPE_EXEC", r"clock", 1)

uvsc.DBG_START_EXECUTION()
delay_secs(1)
#uvsc.DBG_STOP_EXECUTION()

#uvsc.DBG_EXIT()


#uvsc.CloseConnection()





