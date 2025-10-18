# Databricks Crypto Trading Data Pipeline
## Project Summary & Progress Report

**Date**: October 17, 2025  
**Student**: Your Name  
**Project**: Crypto Trading Data Engineering with Databricks, AWS S3, PostgreSQL

---

## 🎯 Project Overview

**Goal**: Build a production-grade data engineering pipeline for crypto trading analytics using the Medallion Architecture (Bronze → Silver → Gold).

**Tech Stack**:
- **Databricks**: Data processing and transformation
- **AWS S3**: Data lake storage
- **RDS PostgreSQL**: Relational database for reference data and metrics
- **Delta Lake**: ACID-compliant data format
- **PySpark**: Distributed data processing
- **Git/GitHub**: Version control

---

## ✅ Phase 1: AWS Infrastructure Setup (COMPLETED)

### What We Built:

#### 1. AWS CLI Configuration
```bash
# Installed and configured AWS CLI
aws configure
# Region: us-east-1
```

#### 2. S3 Buckets (Medallion Architecture)
```
crypto-databricks-1760666848-raw-trades       (Bronze - Raw data)
crypto-databricks-1760666848-processed-ohlcv  (Silver - Cleaned data)
crypto-databricks-1760666848-analytics        (Gold - Aggregated metrics)
```

#### 3. RDS PostgreSQL Database
- **Instance**: crypto-trades-db.cmr4ggym4bcr.us-east-1.rds.amazonaws.com
- **Database**: cryptodb
- **User**: dbadmin
- **Instance Type**: db.t3.micro (free tier eligible)

**Database Schema Created**:
```sql
crypto.symbols            -- 5 crypto symbols (BTC, ETH, SOL, MATIC, AVAX)
crypto.exchanges          -- 4 exchanges (Coinbase, Binance, Kraken, Gemini)
crypto.daily_metrics      -- OHLCV data (to be populated)
crypto.trading_indicators -- RSI, Moving Averages (to be populated)
```

#### 4. IAM Configuration
- Created IAM user: `databricks-user`
- Attached S3 access policy: `DatabricksS3Access`
- Generated access keys for Databricks

#### 5. Cost Management
- Set up billing alert: $15 budget
- Expected monthly cost: $10-15 (RDS + S3)
- Databricks: ~$2-4/hour when cluster running

#### 6. GitHub Repository
- **Repo**: crypto-databricks-project
- Connected to Databricks Repos
- Version control for all notebooks

---

## ✅ Phase 2: Databricks Workspace Setup (COMPLETED)

### What We Built:

#### 1. Databricks Workspace
- **URL**: https://dbc-86345576-d5d4.cloud.databricks.com
- **Workspace ID**: 2781165862743205
- Deployed via AWS Marketplace

#### 2. Cluster Configuration
- **Name**: crypto-cluster
- **Type**: Single Node (cost-optimized)
- **Runtime**: 13.3 LTS (Spark 3.4.1)
- **Instance**: m5d.large (8 GB RAM, 2 cores)
- **Auto-termination**: 120 minutes (saves cost!)

#### 3. S3 Integration
- S3 access configured via cross-account IAM role
- Successfully reading/writing to all 3 buckets
- No credentials hardcoded (secure!)

#### 4. PostgreSQL JDBC Connection
- Successfully connected to RDS
- Tested read/write operations
- Can query reference data (symbols, exchanges)

#### 5. Sample Data Generated
- **Location**: `s3a://crypto-databricks-1760666848-raw-trades/trades/crypto_trades.parquet/`
- **Records**: 100,000 crypto trades
- **Format**: Parquet (partitioned into 2 files)
- **Columns**: trade_id, symbol, price, volume, trade_type, exchange, timestamp, user_id
- **Time Range**: 90 days of synthetic trading data

#### 6. Notebooks Created
- `00_setup_connections` - Connection testing
- `01_bronze_ingestion` - Bronze layer (in progress)

---

## ✅ Phase 3: Bronze Layer (COMPLETED)

### What We Built:

**Notebook**: `01_bronze_ingestion`

#### Architecture:
```
Raw Parquet (S3)  →  Add Metadata  →  Delta Lake (Bronze)
   100K trades         +timestamp        ACID compliant
                       +source_file
```

#### Implementation:

**Cell 1: Read Raw Data**
```python
raw_path = "s3a://crypto-databricks-1760666848-raw-trades/trades/crypto_trades.parquet"
raw_df = spark.read.parquet(raw_path)
# Loaded 100,000 trades
```

**Cell 2: Add Metadata**
```python
from pyspark.sql.functions import current_timestamp, lit

bronze_df = raw_df \
    .withColumn("ingestion_timestamp", current_timestamp()) \
    .withColumn("source_file", lit("crypto_trades.parquet"))
```

**Cell 3: Write to Delta Lake**
```python
bronze_path = "s3a://crypto-databricks-1760666848-raw-trades/delta/bronze_trades"

bronze_df.write \
    .format("delta") \
    .mode("overwrite") \
    .save(bronze_path)
```

**Cell 4: Verify Delta Table**
```python
bronze_df = spark.read.format("delta").load(bronze_path)
# Verified: 100,000 records with metadata
```

**Cell 5: Check Delta History**
```python
from delta.tables import DeltaTable
delta_table = DeltaTable.forPath(spark, bronze_path)
delta_table.history()  # Version 0 created
```

### Delta Lake Structure Created:
```
s3://crypto-databricks-1760666848-raw-trades/delta/bronze_trades/
├── _delta_log/
│   └── 00000000000000000000.json (transaction log)
├── part-00000-...parquet (1.3 MB)
└── part-00001-...parquet (1.3 MB)
```

---

## 🔄 Phase 3: Silver Layer (IN PROGRESS)

### What We're Building:

**Notebook**: `02_silver_transformation`

#### Plan:
1. Read from Bronze Delta table
2. Data quality checks (nulls, duplicates)
3. Clean data (remove bad records)
4. Calculate OHLCV metrics:
   - Open, High, Low, Close prices
   - Volume aggregation
   - VWAP (Volume Weighted Average Price)
5. Join with PostgreSQL reference data (symbol metadata)
6. Write to Silver Delta table

#### Started Implementation:

**Cell 1: Read Bronze** ✅
```python
bronze_df = spark.read.format("delta").load(bronze_path)
```

**Cell 2: Data Quality Checks** ✅
```python
# Check nulls, duplicates
# Found some null volumes (expected - realistic data)
```

**Cell 3: Clean Data** ✅
```python
clean_df = bronze_df \
    .filter(col("volume").isNotNull()) \
    .filter(col("price") > 0) \
    .dropDuplicates(["trade_id"])
```

**Next Steps** (TODO):
- Cell 4: Calculate OHLCV by symbol and time window
- Cell 5: Join with PostgreSQL symbols table
- Cell 6: Write to Silver Delta table

---

## 📚 Key Concepts Learned

### 1. Spark vs Pandas

| Concept | Spark | Pandas |
|---------|-------|--------|
| Mutability | Immutable (returns new DF) | Mutable (modifies in place) |
| Add column | `.withColumn("col", value)` | `df["col"] = value` |
| Filter | `.filter(condition)` | `df[condition]` |
| Select | `.select("col1", "col2")` | `df[["col1", "col2"]]` |
| Processing | Distributed (parallel) | Single machine |

### 2. Delta Lake vs Parquet

| Feature | Parquet | Delta Lake |
|---------|---------|-----------|
| Format | Columnar file format | Parquet + transaction log |
| ACID | ❌ No | ✅ Yes |
| Updates | ❌ Can't update | ✅ UPDATE/DELETE/MERGE |
| Time Travel | ❌ No | ✅ Version history |
| Schema Evolution | ❌ Limited | ✅ Full support |

**ACID = Atomic, Consistent, Isolated, Durable**

### 3. Partitioning

**What**: Split data into chunks for parallel processing

```
100K records → 2 partitions
├── part-00000.parquet (50K rows)
└── part-00001.parquet (50K rows)
```

**Why**: Faster processing (parallel workers)

### 4. PySpark Functions

```python
from pyspark.sql.functions import current_timestamp, lit, col

current_timestamp()    # Current time (like pd.Timestamp.now())
lit("value")          # Constant value column
col("name")           # Reference existing column
```

### 5. Medallion Architecture

```
Bronze (Raw)     →  Silver (Clean)    →  Gold (Analytics)
├── Raw data         ├── Cleaned           ├── Aggregations
├── Minimal          ├── Validated         ├── Business metrics
├── As-is            ├── Joined            ├── Ready for BI
└── Full history     └── Transformed       └── Optimized
```

---

## 📊 Current Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                            │
├─────────────────────────────────────────────────────────────┤
│  S3 Parquet Files              PostgreSQL RDS              │
│  └── 100K crypto trades        └── Reference data          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   BRONZE LAYER ✅                           │
├─────────────────────────────────────────────────────────────┤
│  Location: s3://.../delta/bronze_trades                    │
│  Format: Delta Lake                                         │
│  Records: 100,000                                           │
│  Schema: 10 columns (original 8 + 2 metadata)              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   SILVER LAYER 🔄                           │
├─────────────────────────────────────────────────────────────┤
│  Location: s3://.../delta/silver_ohlcv                     │
│  Status: IN PROGRESS                                        │
│  Plan: Clean data + OHLCV calculation                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   GOLD LAYER 📋                             │
├─────────────────────────────────────────────────────────────┤
│  Location: s3://.../delta/gold_indicators                  │
│  Status: TODO                                               │
│  Plan: RSI, Moving Averages, VWAP, Correlations           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   OUTPUT                                    │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL: crypto.daily_metrics                          │
│  PostgreSQL: crypto.trading_indicators                     │
│  Ready for dashboards/BI tools                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 💰 Cost Tracking

### Current Monthly Costs:

**AWS Services**:
- RDS PostgreSQL (db.t3.micro): ~$10-12/month (FREE for 12 months with free tier)
- S3 Storage (~10 MB): ~$0.01/month
- **Subtotal**: ~$10-12/month (or $0 with free tier)

**Databricks**:
- Workspace: FREE
- Cluster (m5d.large): ~$2-4/hour when running
- **Cost Control**: Auto-terminate after 2 hours idle

**Total Expected**: ~$50-100/month with 3 hours/day usage

### Cost Optimization:
✅ Single node cluster (cheapest)  
✅ Auto-termination enabled  
✅ Smallest instance type  
✅ Billing alerts set at $12 and $100  

---

## 🛠️ Technical Configuration

### Environment Variables (saved in `~/.databricks-crypto-config`):

```bash
# AWS
AWS_ACCOUNT_ID=...
AWS_REGION=us-east-1

# S3 Buckets
RAW_BUCKET=crypto-databricks-1760666848-raw-trades
PROCESSED_BUCKET=crypto-databricks-1760666848-processed-ohlcv
ANALYTICS_BUCKET=crypto-databricks-1760666848-analytics

# RDS PostgreSQL
DB_ENDPOINT=crypto-trades-db.cmr4ggym4bcr.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=cryptodb
DB_USER=dbadmin
DB_PASSWORD=<your-password>

# Databricks
DATABRICKS_WORKSPACE_URL=https://dbc-86345576-d5d4.cloud.databricks.com
DATABRICKS_WORKSPACE_ID=2781165862743205
DATABRICKS_CLUSTER_NAME=crypto-cluster

# IAM
DATABRICKS_ACCESS_KEY=AKIA...
DATABRICKS_SECRET_KEY=...
```

---

## 📝 Next Steps (When You Resume)

### 1. Complete Silver Layer (30 mins)
- [ ] Calculate OHLCV aggregations
- [ ] Join with PostgreSQL reference data
- [ ] Write to Silver Delta table
- [ ] Verify data quality

### 2. Build Gold Layer (45 mins)
- [ ] Read from Silver
- [ ] Calculate trading indicators:
  - RSI (Relative Strength Index)
  - Moving Averages (7, 30, 200 day)
  - VWAP (Volume Weighted Average Price)
- [ ] Write to Gold Delta table
- [ ] Write to PostgreSQL for dashboards

### 3. Job Orchestration (30 mins)
- [ ] Create Databricks Job
- [ ] Link notebooks (Bronze → Silver → Gold)
- [ ] Set up scheduling
- [ ] Configure alerts

### 4. Testing & Documentation (30 mins)
- [ ] Data quality tests
- [ ] End-to-end pipeline test
- [ ] Update README
- [ ] Create architecture diagram

### 5. (Optional) Terraform Automation (Course 2)
- [ ] Convert all manual AWS setup to Terraform
- [ ] Infrastructure as Code
- [ ] Multi-environment support

---

## 🎓 Skills Demonstrated

### Data Engineering:
✅ Medallion Architecture (Bronze/Silver/Gold)  
✅ ETL pipeline design  
✅ Data quality validation  
✅ Incremental data processing  
✅ ACID transactions with Delta Lake  

### Cloud & DevOps:
✅ AWS S3 data lake architecture  
✅ RDS PostgreSQL management  
✅ IAM security best practices  
✅ Cost optimization strategies  
✅ Git version control  

### Big Data Technologies:
✅ Apache Spark (PySpark)  
✅ Databricks platform  
✅ Delta Lake  
✅ Distributed computing concepts  
✅ Partitioning strategies  

### Database Skills:
✅ SQL schema design  
✅ JDBC connectivity  
✅ Relational vs columnar storage  
✅ Indexing strategies  

---

## 📚 Resources & References

### Documentation:
- Databricks: https://docs.databricks.com
- Delta Lake: https://docs.delta.io
- PySpark: https://spark.apache.org/docs/latest/api/python/
- AWS S3: https://docs.aws.amazon.com/s3/

### Commands Reference:

**Start Cluster:**
```
Go to Compute → crypto-cluster → Start
Wait 3-5 minutes
```

**Stop Cluster (IMPORTANT!):**
```
Go to Compute → crypto-cluster → Terminate
Or: Auto-terminates after 120 min idle
```

**Check Costs:**
```bash
# On Mac
aws ce get-cost-and-usage \
  --time-period Start=2025-10-01,End=2025-10-31 \
  --granularity MONTHLY \
  --metrics "UnblendedCost"
```

**Common PySpark Operations:**
```python
# Read Delta
df = spark.read.format("delta").load(path)

# Write Delta
df.write.format("delta").mode("overwrite").save(path)

# Filter
df.filter(col("price") > 100)

# Add column
df.withColumn("new_col", lit("value"))

# Group by
df.groupBy("symbol").agg(sum("volume"))

# Join
df1.join(df2, "key")
```

---

## ⚠️ Important Reminders

### Before You Leave:
1. ✅ **STOP THE CLUSTER** (or it keeps charging!)
2. ✅ Commit notebooks to Git
3. ✅ Save progress in this document

### When You Return:
1. Start cluster (3-5 min wait)
2. Review this document
3. Continue with Silver layer Cell 4

### Security:
- ❌ Never commit passwords to Git
- ✅ Use Databricks Secrets (we'll set up later)
- ✅ Keep `~/.databricks-crypto-config` file safe

### Cost Alerts:
- Check AWS billing dashboard daily
- Alert at $12 (80% of budget)
- Expected: $2-4 per session

---

## 🎯 Project Success Metrics

### Phase 1: Infrastructure ✅
- [x] S3 buckets created
- [x] RDS PostgreSQL running
- [x] IAM configured
- [x] Billing alerts set

### Phase 2: Databricks Setup ✅
- [x] Workspace deployed
- [x] Cluster configured
- [x] S3 connected
- [x] PostgreSQL connected
- [x] Git integrated

### Phase 3: Data Pipeline 🔄
- [x] Bronze layer complete
- [ ] Silver layer (50% done)
- [ ] Gold layer (pending)
- [ ] PostgreSQL integration
- [ ] Job orchestration

### Final Goal 📋
- [ ] End-to-end automated pipeline
- [ ] Production-ready code
- [ ] Complete documentation
- [ ] Ready for interviews!

---

## 📞 Quick Reference

**When things break:**
1. Check cluster is running
2. Verify S3 paths are correct
3. Check PostgreSQL security group allows your IP
4. Review error messages carefully
5. Check Delta log for issues

**Common Issues:**
- "Can't read Delta": Check path, ensure `format("delta")`
- "PostgreSQL timeout": Update security group with your IP
- "S3 access denied": Check IAM role attached to cluster
- "Partition not found": Use folder path, not file path

---

## 🎉 Achievements Unlocked

✅ Set up production AWS infrastructure  
✅ Deployed Databricks workspace  
✅ Generated 100K realistic crypto trades  
✅ Implemented Bronze layer with Delta Lake  
✅ Learned PySpark fundamentals  
✅ Mastered Medallion Architecture concept  
✅ Cost-optimized cloud deployment  
✅ Git version control integrated  

**Progress**: ~60% complete  
**Time invested**: ~4-5 hours  
**Remaining**: ~2-3 hours  

---

**Great job so far! See you tomorrow!** 🚀

---

*Document generated: October 17, 2025*  
*Last updated: Phase 3 - Bronze Layer Complete*