COMPILE:
Execute the command "ant" in the project root directory.
In order to compile the test build that also contains a fake client connecting to the local host use "ant test".

TEST BUILD:
The test build also provides a fake client for testing purposes. Note that the logging configurations are also different as it allows to log all communications happening over the sockets. This build will log to "test_middleware.log" in the root directory.

LOGFILE:
The logfile should be situated in the root directory of the project and is named "middleware.log".

LAUNCH:
To launch the application use:
    java -cp . asl_project.RunMW -l external_IP -p 8000 -t 3 -s false -m localhost:11211
