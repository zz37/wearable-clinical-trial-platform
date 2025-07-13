# Task 0a – Data Volume Estimation


## 1. Raw Data-Point Counts

Lets estimate how many time-series data points can be generated in a high frequency scenario. This will help us to understand the scael of the design, using a high-frequency scenario will represent the upper-bound estimate based on the storage, processing and scale decisions, considerding also that in reality **Fitbit** samples less frequently.

As we know → 1 data point every 1 second, means we have 1 Hz (1 sample / 1 second)

**Assumptions**:

* **Metrics:** 4 (`heart_rate`, `steps`, `distance`, `spo2`).
* **Sampling rate:** 1 Hz (1 data point per second, per metric).
* **Duration:** 1 year = 365 days = `3.1536 × e7` seconds.
* The data points grows linearly with the number of participants, metrics, and time.

We compute the total data points for 1 year across multiple participant counts using the derived equation, assuming the 4 time-series metrics:

Derived formula:

```
DataPoints = metrics per second × seconds/year × years × participants
```

Where seconds/year = `S_YR = 3.1536 × 10⁷`

### 1a. One-year study, scale by participant count (m = 4 metrics/s)

| **Participants (`n`)** | **Formula**        | **Total Data Points** |
| ---------------------- | ------------------ | --------------------- |
| 1                      | `4 × S_YR × 1`     | `1.26144e8`           |
| 1,000                  | `4 × S_YR × 1000`  | `1.26144e11`          |
| 10,000                 | `4 × S_YR × 10000` | `1.26144e12`          |

### 1b. Single participant, scale by study length

| **Years (`y`)** | **Formula**    | **Total Data Points** |
| --------------- | -------------- | --------------------- |
| 1               | `4 × S_YR`     | `1.26144e8`           |
| 2               | `4 × S_YR × 2` | `2.52288e8`           |
| 5               | `4 × S_YR × 5` | `6.30720e8`           |

>Note: Change the leading 4 if you there is a different number of 1-Hz time-series streams. For leap years, add 86 400 s to S_YR for each leap year included.

**Why 1 Hz?**
We assume 1 Hz (1 sample / 1 second) data to have a rough estimation of the highest amount of data we can deal in future. This number can help in diong stress tests for **storage**, **compression**, and **system throughput**.


---

## 2. To store 1 data point, how many bytes of data should this take?

-	Lets assume 1 point is a `8-byte`,  a 64 bit `integer` or `float`. In **PostgreSQL**, this aligns with the size of a `BIGINT` or `DOUBLE PRECISION` value. That point can be considered a timestamp or a numeric metric (like previous metrics). 

Why is this relevant, because:
- Using 8 byts keeps precision acceptable and avoid rounding issues.
- Vs. to smaller `int` or `float` types, helps avoid underestimating storage needs.

### 2a. For n = 1 000 / 2 years / 3 metrics at 1-second resolution, how many bytes if uncompressed?

Lets assume each data point uses `16 B (8 B timestamp + 8 B value)`, `(B = bytes)`. 

- A timestamp (8 bytes): A 64-bit integer (`BIGINT`) or `TIMESTAMP`, both standard in **PostgreSQL** and **TimescaleDB**.
- A value (8 bytes): a `DOUBLE PRECISION`, which supports **Fitbit** metrics with full decimal precision.

So, `BytesPerPoint = 8 (timestamp) + 8 (value) = 16 bytes`

A more realistic row would be: `timestamp (8 B) + metric (1 B) + value (4 B) + overhead (3 B) = ∑16 B ` (being the total still 16 bytes)

For calculation then we know, **3 metrics per secons**, **S_YR seconds per year**, **2 year**, **1 000 participants**.

Formula:
```
DataPoints = 3 metrics × S_YR × 2 years × 1 000 participants
           = 1.89216e11 points

Bytes = 1.89216e11 × 16 B
      = 3.02746e12 bytes
      ≈ 3.03 TB (uncompressed)
```

### 2 b. Compressed time-series storage with >90% reduction. Assuming 80% compression, how much data?

Assuming the 80% reduction, as stated, the compression would be 20% of the original uncompresed size. So, 

```
CompressedBytes = (1 - Reduction) × TotalBytes = 0.20 × 3.03 TB = 0.606 TB 
```

### 2 b i. How can time-series databases compress so well? When would compression be poor? Would Fitbit data compress well?

- With time-series data we have regular, evenly spaced timestamps → translate to good differnece storing (delta-encoding) [1,2]. 
- Metrics slowly change over time → So, repeted number can be stored (run-length encoding) [3]. 
- Time-series dbs offer column storage → which supports tight packing and compresion. 

Compression may be poor with:
- Compression is poor, when presented is random (high-entropy), has many words string data or does not follow a clear pattern. 

**Fitbit** data seems comptible for the specified metris, as being recored regularly and change slowly. The important factor is the periodicity: data points are collected at consistent intervals (around 1 Hz, which equals 1 divided by the sampling period T, i.e., f=1/T )
---

## 3. For questions 1 and 2, we assumed 3 metrics at a 1-second resolution. In reality, depending on the metric, the resolution can vary considerably. Look into the Fitbit Web API explorer. What may be some useful metrics to run a physical activity affecting sleep study?

Assuming data every 1 sec is a safe case, based on storage needs. But, for real for **Fitbit** data.  Based on the web api, Fitbit records data every 1 min or slower, meaning that data is smaller. Could be enough for the study? Let see

### 3a. What metrics and how often are they recorded? (e.g. every 1 sec, 1 min, 5 min, etc.)

Confirming the use metric in the website below as given. The official site:

Reference: [Fitbit Web API Explorer](https://dev.fitbit.com/build/reference/web-api/explore/)

Based on the webiste the useful Fitbit metrics for studying physical activity and sleep, with their fastest recording times are:

```text
Heart rate          → every 1 second (during or lower outside workouts )
Steps               → every 1 minute
Calories burned     → every 1 minute
Blood oxygen (SpO2) → every 5 minutes (during main sleep only)
Heart rate variability (HRV) → every 5 seconds (during sleep only)
Sleep stages        → every 30 seconds to 5 minutes (summary)
Breathing rate      → once per sleep period or daily
Skin temperature    → once per night (summary during sleep)
```

[Source](https://dev.fitbit.com/build/reference/web-api/intraday/)

For this challenge the best metrics to use are: 1) To show how a person moves and how the active body works during the day. During the day: heart rate (how much is the body moving), steps(activity lvl), calories burned(energy use). And, during the night: sleep stages(depth of sleep), SpO2(blood oxygen lvl), skin, in order to know how the recovery phase is working or not.

### 3b. How much data is created for 1,000 people over 1 year?

Using the given numbers: 1 metric measured every 1 second (`heart rate`),  2 metrics measured every 1 minute (`steps and calories`) and `1 year = 3.1536e7 seconds`

```
Points/person = (1 × S_YR) + (2 × (S_YR / 60)) = 3.25872e7 points

For 1,000 participants:
Total = 3.25872e7 × 1,000 = 3.25872e10 points

Total bytes (16 bytes per point):
Bytes = 3.25872e10 × 16 = 5.21395e11 bytes ≈ 521.4 GB (uncompressed)
```

### 3c. How much space after compression (assuming 80% compression)?

With 80% compression, only 20% of the original data size remains:

```
Compressed size = 0.20 × 521.4 GB = 104.3 GB
```

---

## 4. When retrieving time-series data from a database, it may be too expensive an operation to access all the data at the finest resolution.

### 4a. How would you solve this issue? What would you do to make queries “less expensive”? (Hint: this may come at an added data storage cost)

In this context using **postgregresql** and **timescaledb**, I keep separate containers if the same data of different sizes (`1 min`, `5min`, `1hr` resolutions). Then data can be only accesed as needed and not in the whole resolution (a specific time box frame or downsampling) making sure that queries run much faster as grabing data as needed.

- Instead of scanning `1-second` data every time, store multiple versions:
- Per resolution: `1s = second, 1m = 1 minute, 5m = 5 minutes, 1h = 1 hour, 1d = 1 day`

| **Metric**        | **Resolution** | **Table**                    |
| ----------------- | -------------- | ---------------------------- |
| `heart_rate`      | 1s, 1m, 1h, 1d | `heart_rate_data_1_second_...`     |
| `steps`           | 1m, 1h, 1d     | `step_data_1_minute_...`     |
| `calories_burned` | 1m, 1h, 1d     | `calorie_data_...`             |
| `breathing_rate`  | 1d             | `breathing_rate_data_1_day`  |
| `hrv`             | 5m, 1d         | `heart_ratevr_data_...`        |
| `spo2`            | 5m, 1d         | `spo2_data_...`                |
| `skin_temp`       | 1d             | `skin_temp_data_1_day`       |
| `sleep_stages`    | processed, 1d  | `sleep_stage_data_processed` |

Then based on the latter table, the application lets you picks the right format or table(once in the database) based on how much detail is needed, scales up the resolution, like the small diagram below:

```text
heart_rate_data_1_second
            ↑
heart_rate_data_1_minute
            ↑
heart_rate_data_1_hour
            ↑
heart_rate_data_1_day
```

---

## 5. Vertical scaling (one strong machine)

### 5a. Vertical Limits (1 Server)

Thinking of a sinlge machine is hard but the limits could be around: 

| **Part** | **Limit**         | **Why?**                                   |
| -------- | ----------------- | ------------------------------------------ |
| CPU      | 32–64 cores       | More cores → more parallel work            |
| Memory   | 256 GB – 2 TB RAM | More RAM → faster access, but +RAM = +cost |
| SSD      | 10–50 TB SSD/NVMe | Fast SSD → faster x-r, but big cos         |

* Based on previous calculations, we can assume that the limit is around 1000 participants.

### 5b. Horizontal Scaling

To spread the work across various machines can be with these in mind:

| **What**      | **Why**                                   |
| ------------- | -----------------------------------------          |
| Sharding      | Split data → each machine handles a slice          |
| Query Routing | Coordinator node sends to correct shard            |
| Schema Sync   | All machines = same schema                         |
| Replication   | Copies = backups → if machine fails no  data loss  |
| Time Sync     | Needed for 1s metrics to align timestamps          |
| Fast Network  | LAN (+Ethernet speed = less lag)                   |

Based on previous number: Each server handles 250 users. Four machines can cover 1,000 users.

---

**References**

1. Jun Rao et al. "TSDB: A Time Series Database for Real-time Analytics." IEEE Big Data 2019
2. Facebook. "Gorilla: A Fast, Scalable, In-Memory Time Series Database." SIGMOD 2016
3. B. O’Connor et al. "Efficient Run-Length Encoding for Time Series Data." J. Data Compression, 2018
