// TIMEOUT(100000, log.log("last msg: " + msg + "\n")); /* milliseconds. print last msg at timeout */
// 
// log.log("first mote output: '" + msg + "'\n");
// 
// YIELD(); /* wait for another mote output */
// 
// log.log("second mote output: '" + msg + "'\n");
// 
// log.log("waiting for hello world output from mote 1\n");
// WAIT_UNTIL(id == 1 && msg.equals("Hello, world"));
// 
// write(mote, "Hello, mote\n"); /* Write to mote serial port */
// 
// GENERATE_MSG(15000, "continue");
// YIELD_THEN_WAIT_UNTIL(msg.equals("continue"));
// 
// log.log("ok, reporting success now\n");
// log.testOK(); /* Report test success and quit */
// // log.testFailed(); /* Report test failure and quit */
TIMEOUT(100000);
