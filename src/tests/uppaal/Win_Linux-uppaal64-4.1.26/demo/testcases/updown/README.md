# Uppaal Test Case Generator demo

The following describes the test case generation features in Uppaal by using a simple Java program toggling value up and down.

## Model Annotations

* Open the `updown.xml` model file in Uppaal in the `Editor` tab.

* Select the `System` automaton and observe the system requirements:
  - Three locations corresponding to `Off`, `On` and `Max`.
  - Synchronization on `up` increments the value with `++val`.
  - Synchronization on `down` decrements the value with `--val`.
  - `Max` location is special as it does not allow increments.
  - `Off` location is special as it does not allow decrements.

* Double click a location and observe:
  - `Test Code` contains expected outcomes checks (assertions).
  - The code may contain `$(variable)` expressions which are replaced with the corresponding variable value.

* Select `User` automaton and observe the environment assumptions:
  - Single location where either `up` or `down` are permitted at any time
  - The channels `up` and `down` are hand-shake channels,
    meaning that the sender `User` must agree to synchronize with `System`
    and `User` is not allowed issue `up` or `down` if `System` does not agree.

* Double click an edge and observe:
  - `Test Code` contains actions applied on the implementation.

* Select `System declarations` section and observe:
  - `system` declaration containing two processes: `System` and `User`.
  - `TEST_FILENAME` comment to specify the prefix for test case file names.
  - `TEST_FILEEXT` comment to specify the extension for test case file names.
  - `TEST_PREFIX` comment to specify the fixed prolog (beginning) for each test case file.
  - `TEST_POSTFIX` comment to specify the fixed epilog (ending) for each test case file.

* Select `Declaration` section and observe two additional special variables:
  - `__reach__` counts the number of transition taken (used in random walk test case generation).
  - `__single__` used to annotate edges when their coverage is required (used in coverage based test case generation).

## Test Case Generation

Test case generator uses verification engine to find the system traces, collect the `Test Code` along those traces and save them as test script files.

* In the `Tools` menu enable `Test Cases` tool and observe a new tab `Test Cases` appear to the left of `Verifier`.

* Select `Test Cases` tab.

* There a three modes of generating test cases:
  1) `Query`-based is guided by a specific purpose expressed as verification query, e.g. `E<> System.Max` adds a test case where the `System` reaches `Max` location. The queries can be added and edited in the `Verifier` tab. This mode is useful to compute optimal length/duration test cases.
  2) `Depth`-based random walks, where the depth is the number of transitions: it keeps adding random test cases until the coverage does not improve any more. This mode targets long scenarios with a hope of exercising as many edges in series as possible.
  3) `Edge` coverage based: select all or specific process edges to be covered. It targets specific edges, thus it may generate many shallow test cases with overlapping coverage, this mode is mostly suitable when the above modes are exhausted.

* Each mode has two options:
  - `Search` specifies the search order over the state space. The search effort depends on the shape of the state space, which can be deep (long sequences of transitions), wide (a lot of non-deterministic choices, e.g. many parallel processes) or any combination of them. `Breadth`-first order is usually prefered for narrow state spaces. `Depth`-first is for shallow state spaces. `Random`-depth-first is similar to `Depth`-first except it randomizes the non-deterministic choices.
  - `Trace` specifies the optimality criterion: `Shortest` takes least transitions/steps, `Fastest` takes least amout of time, `Some` is the first found trace.
  - Other search options can be manipulated directly in the `Options` menu.

* One can choose arbitrary mode to generate test cases by clicking the corresponding `Add` button.

* The computed trace are added to the `Traces` field where:
  - The trace can be selected and its coverage examined in the `Trace statistics`.
  - The trace can be loaded into `Simulator` by double-clicking the trace.

* The combined coverage of all traces can be examined by clicking `Total Coverage` button.

* The traces can then be translated and exported as test case scripts by clicking `Save Test Cases`.

* The generated traces can be cleared by reloading the simulator (press `F5` or `View`-`Reload Simulator`).

## Test Case Execution

The generated test cases are executed by running the following scripts: `test.sh` on Unix or `test.bat` on Windows. The scripts assume that all test cases are saved in their current directory by following the `TestCase-*.java` pattern (as specified in `updown.xml`), compile the `app/AppC.java` implementation, compile the test case and run it.

The `app` dirctory also contains faulty implementation and the test cases can be run against it by executing the corresponding scripts: `testMutant.sh` on Unix and `testMutant.bat` on Winduws.
