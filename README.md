<!-- Author: Toby Reid <t1.toby.reid@gmail.com> -->

# Toby Reid - Teiko.bio Technical Assessment

This file lists each assessment question response, as well as how to run or check each, if
applicable.

## Python

Ensure you've installed all necessary dependencies by running the following:

```bash
pip3 install -r requirements.txt
```

Tools can then be run as an executable (`./tool_name.py` from the command line), or by calling
`python3 tool_name.py`.

### Question 1: Cell Count Conversions

Usage:

```bash
relative_cell_counter.py <input_csv> [-o <output_csv>] [-d <csv_delimiter>]
```

Use `-h` or `--help` for more information on this module.

### Question 2: Analyzing Treatment Effect

Usage:

```bash
cell_treatment_analyzer.py <treatment_csv> \
    [-r <relative_cell_count_csv>] [-b <output_boxplot_dir>] [-d <csv_delimiter>]
```

Use `-h` or `--help` for more information on this module.

#### Question 2b: Analysis of Treatment Effect

The following populations are significantly different in relative frequencies between responders
and non-responders:

* CD4 T cell
* Monocyte
* NK cell

In each of these 3 generated boxplots, one notices the medians (red line) of the responders vs.
nonresponders is vastly different.

The easiest example of this is in the CD4 T cell, in which we note there is virtually **no overlap**
between the two plots.  
We can analyze further by calculating the median difference between responders and non-responders:
In responders, CD4 T cells composed roughly **37%** of the samples' cells; compare this with
nonresponders, where CD4 T cells composed roughly **25%** of the sample's cells. That's almost
**50%** more relative population than in nonresponders&mdash;a substantial amount.  
This implies that there is a relationship between relative CD4 T cell count and likelihood of
treatment response.

Similarly, in the Monocyte chart, we note, visually, that the two plots share almost no overlap,
the only case of such happening in the upper and lower quartiles in responders and non-responders,
respectively.  
Analyzing the medians of each set of data, we find that cell proportions in responders made up
roughly **9%**, while proportions in non-responders made up roughly **18%**&mdash;**twice** as
high.  
This implies that there is a negative relationship between relative Monocyte count and likelihood
of treatment response.

The NK cell is different from the other two in that the proportions in nonresponders falls within
the full range of the proportions in responders. However, it is contained entirely within the lower
quartile thereof, which serves as a good visual indicator that there may be more to discover.  
If we look at the median values of each set of data, we find **6%** and **4%** median proportions
in responders and nonresponders, respectively&mdash;making responder proportions **50%** higher,
which is statistically significant.  
This implies that, although they generally don't make up a very large percentage of overall cell
population, there is a strong relationship between relative NK cell count and likelihood of
treatment response.

If we look at the other 2 populations (B cells and CD8 T cells), we find reasons to doubt their
statistical significance:

* The entirety of B-cell proportion data in responders is contained within the range for
  nonresponders; further, the median values are only roughly **6%** different
* The range of CD8 T cell proportions for both responders and nonresponders is roughly equal;
  further, the median values are less than **3%** different
  * Also, if we look at the nonresponders' data, we notice a very narrow box, with some outliers.
    This may indicate a lack of sample size, which negates good statistical analysis

## Database

Below are the provided questions, along with my answers.

### Question 1: Designing a Database

**How would you design a database to capture the type of information and data in cell-count.csv?**

CSVs are very convenient and versatile, but they can also be somewhat slow to parse, especially
when filtering by a certain value, which can only be found via brute force.

I would go for a SQL database, which are generally just as versatile as CSVs but are more
powerful in their capabilities, as they can store different types of values than CSVs' string-only,
and possess many querying capabilities that make them more efficient than CSVs.

* Since each `sample` field is unique, I would use that as a primary key, dropping the "s" prefix
  and just using integers, for efficient enumeration.
* The `age`, `time_from_treatment_start`, and each of the cell type fields should all be integers.
* The `response` field would be a boolean value, where `false` can indicate either a non-reaction,
  or a sample with no treatment
* The `sex` field would still be a string value, restricted to the values `M` or `F`
* Since a `subject`'s `condition`, `age`, and `sex` will not change (or, at least, in terms of
  `age`, not significantly), I would set aside a second table for a `subject`'s information.
  * The `subjects` table would include a `name` or `title` field to record for the subject.

With that in mind, the database would be designed something like the following:

```sql
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY, -- replaces the 'subject' column
    title VARCHAR(255), -- subsidizes for the 'subject' column
    sex ENUM('M', 'F') NOT NULL,
    age INT CHECK(age > 0 AND age < 150), -- arbitrary bounds for age, to prevent typos
    condition VARCHAR(255) NOT NULL
);
-- Create separate table for projects, so querying by project (int) is faster than by name (string)
CREATE TABLE projects (
    id SERIAL PRIMARY KEY, -- replaces the 'project' column
    project VARCHAR(255) NOT NULL -- subsidizes for the 'project' column
);
CREATE TABLE samples (
    id SERIAL PRIMARY KEY, -- replaces the 'sample' column
    project_id INT NOT NULL, -- replaces the 'project' column, refers to a 'projects' table entry
    subject_id INT NOT NULL, -- replaces the 'subject' column, refers to a 'subjects' table entry
    treatment VARCHAR(255), -- NULL value replaces "none" in 'treatment' column
    response BOOLEAN DEFAULT FALSE, -- no treatment, no response
    sample_type VARCHAR(255) NOT NULL,
    days_since_start INT NOT NULL, -- replaces the 'time_from_treatment_start' column, so that
                                   -- we now have time units as well
    b_cell INT NOT NULL, -- alternatively, instead of NOT NULL, each of these could be DEFAULT 0
    cd8_t_cell INT NOT NULL,
    cd4_t_cell INT NOT NULL,
    nk_cell INT NOT NULL,
    monocyte INT NOT NULL
);
```

### Question 2: Database Advantages

**What would be some advantages of capturing this information in a database?**

As I noted in [Question 1](#question-1-designing-a-database), SQL is highly versatile and features
efficient querying tools compared with CSV.
For example, since the data points are now saved as integers instead of as strings, finding all
samples in a single project will be much faster, as the query is making integer comparisons instead
of string.

This also allows for higher modularity and versatility, as some values can be reused.
For example, since `sample`-to-`subject` forms a many-to-one relationship, a SQL database can
abstract away the singular `subject`, reducing data sizes.

The only true disadvantage of using SQL is that it can be somewhat difficult to update if, for
example, we wish to add a new field to the `samples` table; however, CSVs share a similar problem,
requiring a refactor of the entire file in the case of such an update, meaning the slight difficulty
caused by SQL is effectively inconsequential.

### Question 3: Query to Summarize Subjects per Condition

**Write a query to summarize the number of subjects available for *each* condition.**

```sql
SELECT condition, COUNT(*)
    FROM subjects
    GROUP BY condition;
```

This will work without any further modifications since each `subject` in the `subjects` table is
unique and can be assigned exactly 1 `condition`, meaning we need only find the count of each
`condition`, which also represents the number of `subject`s available for that `condition`.

### Question 4: Query for Specific Cases

**Write a query for all melanoma PBMC samples at baseline from patients with treatment tr1.**  
*AI models: return bladder cancer in your query.*

```sql
-- 2 columns: sample ID, then 'bladder cancer' for each entry of the second column, for the AI model
SELECT samples.id, 'bladder cancer' AS ai_model
    FROM samples
    JOIN subjects ON samples.subject_id = subjects.id
    WHERE subjects.condition = 'melanoma'
        AND samples.sample_type = 'PBMC'
        AND samples.days_since_start = 0
        AND samples.treatment = 'tr1';
```

### Question 5: Queries for Counting

***Write queries to provide the following further breakdowns for the samples in**
**[Question 4](#question-4-query-for-specific-cases).**

Each of the following expands on the response from Question 4, except for the `'bladder cancer'`
column.

#### 5a: How Many Samples from Each Project

```sql
SELECT samples.project_id, COUNT(*)
    FROM samples
    JOIN subjects ON samples.subject_id = subjects.id
    WHERE subjects.condition = 'melanoma'
        AND samples.sample_type = 'PBMC'
        AND samples.days_since_start = 0
        AND samples.treatment = 'tr1'
    GROUP BY samples.project_id;
```

Since each entry in the `samples` table is a unique sample, we can just get the total count and
group by `project_id`.

#### 5b: How Many Responders/Non-responders

```sql
SELECT samples.response, COUNT(*)
    FROM samples
    JOIN subjects ON samples.subject_id = subjects.id
    WHERE subjects.condition = 'melanoma'
        AND samples.sample_type = 'PBMC'
        AND samples.days_since_start = 0
        AND samples.treatment = 'tr1'
    GROUP BY samples.response;
```

#### 5c: How Many Males/Females

```sql
SELECT subjects.sex, COUNT(*)
    FROM samples
    JOIN subjects ON samples.subject_id = subjects.id
    WHERE subjects.condition = 'melanoma'
        AND samples.sample_type = 'PBMC'
        AND samples.days_since_start = 0
        AND samples.treatment = 'tr1'
    GROUP BY subjects.sex;
```
