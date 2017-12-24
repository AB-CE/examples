# ABCE examples

To run the examples, first install the ABCE dependency
```
pip install -r requirements.txt
```
then run the start.py file from one of the examples.

# Directory

- [2sectors](examples/2sectors): The "hello, world!" of ABCE
- [50000_firms](examples/50000_firms): Title says it all - 50k firms up and running
- [calendar](examples/calendar): Shows how day/month can be incorporated
- [create_and_delete_agents](examples/create_and_delete_agents): A simple illustration of how to create/delete agents during a
  simulation
- [mesa_example](examples/mesa_example): A simple model of how to integrate ABCE and Mesa. The model and
  scheduler are implemented with ABCE while the space is implemented with Mesa.
- [one_household_one_firm](examples/one_household_one_firm): TODO
- [one_household_one_firm_with_logic](examples/one_household_one_firm_with_logic): one_household_one_firm with decision making
  control flow of a firm to choose an action (adjust_price)
- [pid_controller](examples/pid_controller): TODO
- [sugarscape](examples/sugarscape): Implementation of Sugarscape ({G1}, {M, T}) from Epstein
  Chapter 4. Heavily uses Mesa library.
