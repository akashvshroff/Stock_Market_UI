### Outline:

- A simple GUI application to visualise stock market data that has been scraped from the web, processed and stored using SQL via sqlite. The visualisation is done by embedding matplotlib in tkinter - here is a snapshot of the final GUI.

    ![alt-text]() #IMAGE HERE

- The UI has been designed to be clean and minimal, with pops of colour to add relief.
- The program effectively calculates a value for each day and then must calculate the ratio of the average of said value over the last k days and over the last n days (where k < n) in order to indicate how this value has grown with respect to the past. It then calculates this ratio for a number of days and displays it as a line graph.
- A more detailed description of what the application does and how it has been created can be found in the description below.

### Purpose:

- The program, albeit simple, was quite engaging to develop as the intensive data scraping and processing required moving beyond the standard data structures in order to work efficiently as well as some threading to make the I/O bound operations faster.
- For example, while calculating the average - in order to be more efficient there were a few changes I made. Instead of calculating the ratio for only one day, I found it to be much more efficient to calculate for some x days at once since a day and the day before it use n-1 common data points. Therefore to calculate the ratio of x days, you only need x + n data points. Then, once the values of these data points have been calculated and stored, instead of computing the average for each set of n and k, I employed a rolling average function, much like the [maximum sliding window]([https://www.geeksforgeeks.org/sliding-window-maximum-maximum-of-all-subarrays-of-size-k/](https://www.geeksforgeeks.org/sliding-window-maximum-maximum-of-all-subarrays-of-size-k/)) problem by creating a pseudo-queue.

    ```python
    num_points = len(values)
    avg_n, avg_k = [sum(values[0:self.n]) /
                self.n], [sum(values[0:self.k]) / self.k]
    num_remove = 0
    dates = []
    k_add = self.k
    for num_add in range(self.n, num_points):
    	avg_n.append(
    	    ((avg_n[-1]*self.n) - values[num_remove] +
    	     values[num_add])/self.n
    			)
    	avg_k.append(
    	    ((avg_k[-1]*self.k) - values[num_remove] + values[k_add])/self.k
    			)
    	dates.append(self.dates_used[num_remove])
    	num_remove += 1
    	k_add += 1
    	self.processed_data.append((stock, dates, avg_n, avg_k))
    ```
- Another area where I employed a new technique is when writing the data to the sql database, I employed threading so each stock could be handled on its own thread and make the storage faster.

    ```python
    workers = len(obj.stocks_dict)
    executor = concurrent.futures.ThreadPoolExecutor(workers)
    futures = [executor.submit(obj.process_data, item)
               for item in obj.stocks_dict.items()]
    concurrent.futures.wait(futures)
    ```

- This is explained more in depth in the description where I go into the sql schema.

### Description:

- Primarily, I want to tackle the SQL schema since it is slightly different from the usual relational schema I like to employ.
- There are number of stocks and for each stock I maintain a different table since I want to store the date, the averages as well as the ratio - this way each new day can have its own row rather than storing all the stocks in one massive table where each day gets its own column.
- The names of the stocks are obtained from a csv list of shares.
- The data is parsed from the NSE India site and then parsed using the pandas library and the read_csv method. Data is then processed using the methods mentioned above and inserted into a sqlite table.
- In the UI end, once the user picks a stock, all the data - for the dates and ratios - from that particular table is fetched and then displayed in a line plot. To properly generate the line plot, the ISO Format date objects are converted to datetime objects which matplotlib uses to tick the data appropriately and ensure that the x-axis labels are not crowded.
- The program allows users to refresh data as well as alter the K and N values (which causes all the data to be deleted and then regenerated).