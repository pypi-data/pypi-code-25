from mtaf import mtaf_logging
log =mtaf_logging.get_logger('mtaf.log_test')
logging.console_handler.setLevel(logging.INFO)
log.debug("debug message")
log.trace("trace message")
log.info("info message")
log.warn("warn message")
# log1 =mtaf_logging.get_logger('mtaf.log1')
# log2 =mtaf_logging.get_logger('mtaf.log2')
# log1.info("goodbye")
# log2.info("hello")
#mtaf_logging.set_msg_src('just a test')
# log1.info("world")
#mtaf_logging.set_msg_src('jat')
# log1.info("goodbye")
# log2.info("goodbye")

