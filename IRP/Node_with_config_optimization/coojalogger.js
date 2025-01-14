/* A simple log file generator script */

TIMEOUT(3605000); /* 3600 seconds or 1 hour */
// TIMEOUT(600000); /* 600 seconds or 10 minutes */

log.log("Starting COOJA logger\n");

timeout_function = function () {
    log.log("Script timed out.\n");
    log.testOK();
}

while (true) {
    if (msg) {
        log.log(time + " " + id + " " + msg + "\n");
    }

    YIELD();
}