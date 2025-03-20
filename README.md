<!Author: Toby Reid>

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
