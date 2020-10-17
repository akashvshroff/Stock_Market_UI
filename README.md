### Outline:

- A simple GUI application to visualise stock market data that has been scraped from the web, processed and stored using SQL via sqlite. The visualisation is done by embedding matplotlib in tkinter - here is a snapshot of the final GUI.

    ![alt-text]() #IMAGE HERE

- The UI has been designed to be clean and minimal, with pops of colour to add relief.
- The program effectively calculates a value for each day and then must calculate the ratio of the average of said value over the last k days and over the last n days (where k < n) in order to indicate how this value has grown with respect to the past. It then calculates this ratio for a number of days and displays it as a line graph.
- A more detailed description of what the application does and how it has been created can be found in the description below.

