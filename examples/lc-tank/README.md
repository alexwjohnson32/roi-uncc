# HELICS Example - LC Tank Cosimulation

This example demonstrates basic HELICS timing concepts for cosimualtion using a simple LC tank. It consists of two federates, the first modeling a capacitor and the second modeling an inductor. Both simulators are run with a resolution of 100 microseconds and the total simulation time is set to 10 seconds.

The cosimulation is invoked by,

```bash
helics run --path=fundamental_integration_runner.json
```

