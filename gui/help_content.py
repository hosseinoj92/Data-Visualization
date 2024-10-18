# In gui/help_content.py

MIN_MAX_NORMALIZATION_HELP = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Min-Max Normalization Help</title>
    <!-- MathJax Configuration -->
    <script type="text/javascript"
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML">
    </script>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }
        h1, h2 {
            color: #2E8B57;
        }
        p, ul {
            font-size: 16px;
        }
        ul {
            margin-left: 20px;
        }
    </style>
</head>
<body>
    <h1>Min-Max Normalization</h1>
    <p>
        Min-Max Normalization is a feature scaling technique that rescales data to a fixed range, typically between 0 and 1. It is often used as a preprocessing step in machine learning to ensure that different features contribute equally to the analysis.
    </p>
    <h2>Formula:</h2>
    <p>
        Min-max normalization rescales a given value \(x\) using the formula:
    </p>
    <p>
        \\[
        x' = \\frac{x - \\text{min}(X)}{\\text{max}(X) - \\text{min}(X)}
        \\]
    </p>
    <p>Where:</p>
    <ul>
        <li>\(x\) is the original value,</li>
        <li>\(\text{min}(X)\) is the minimum value in the dataset,</li>
        <li>\(\text{max}(X)\) is the maximum value in the dataset,</li>
        <li>\(x'\) is the normalized value.</li>
    </ul>
    <h2>Usage:</h2>
    <ul>
        <li><strong>Preprocessing step:</strong> It ensures that features with different scales are transformed to a common scale, which is important for machine learning models that rely on distance calculations (e.g., k-nearest neighbors, support vector machines, neural networks).</li>
        <li><strong>Equal feature contribution:</strong> It prevents features with larger numerical ranges from dominating models, especially when distance or gradient-based algorithms are involved.</li>
    </ul>
    <h2>Advantages:</h2>
    <ul>
        <li><strong>Preserves data distribution:</strong> It maintains the original distribution shape of the data, which can be important when the relationship between features is essential.</li>
        <li><strong>Simple interpretation:</strong> Data is scaled between 0 and 1, making it easy to understand and compare.</li>
        <li><strong>Suitable for distance-based models:</strong> It works well in models where the absolute scale of features can affect performance, such as in clustering or regression.</li>
    </ul>
    <h2>Disadvantages:</h2>
    <ul>
        <li><strong>Sensitive to outliers:</strong> If there are extreme outliers in the data, they will skew the minimum and maximum values, leading to a compressed range for most of the data points.</li>
        <li><strong>Not robust for extrapolation:</strong> If a new data point falls outside the original min-max range, it will be assigned a value outside the [0, 1] range, which can be problematic for models.</li>
        <li><strong>Doesn't standardize variance:</strong> Unlike other normalization techniques (like Z-score normalization), it does not adjust for the variance of the data, which might be necessary for some algorithms.</li>
    </ul>
    <h2>When to use:</h2>
    <ul>
        <li>When features have different scales that need to be aligned for algorithms sensitive to such differences.</li>
        <li>When there is a need for preserving the original distribution without transforming the data into a standard normal distribution.</li>
    </ul>
</body>
</html>
"""



Z_SCORE_NORMALIZATION_HELP = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Z-score Normalization Help</title>
    <!-- MathJax Configuration -->
    <script type="text/javascript"
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML">
    </script>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }
        h1, h2 {
            color: #2E8B57;
        }
        p, ul {
            font-size: 16px;
        }
        ul {
            margin-left: 20px;
        }
    </style>
</head>
<body>
    <h1>Z-score Normalization</h1>
    <p>
        Z-score normalization, also known as standardization, is a feature scaling technique that transforms the data so that it has a mean of 0 and a standard deviation of 1. This method is particularly useful when the data follows a Gaussian (normal) distribution.
    </p>
    <h2>Formula:</h2>
    <p>
        Z-score normalization standardizes a given value \(x\) using the formula:
    </p>
    <p>
        \\[
        z = \\frac{x - \\mu}{\\sigma}
        \\]
    </p>
    <p>Where:</p>
    <ul>
        <li>\(x\) is the original value,</li>
        <li>\(\mu\) is the mean of the dataset,</li>
        <li>\(\sigma\) is the standard deviation of the dataset,</li>
        <li>\(z\) is the normalized value.</li>
    </ul>
    <h2>Usage:</h2>
    <ul>
        <li><strong>Preprocessing step:</strong> Z-score normalization is used to standardize features with different scales, especially for algorithms that assume normally distributed data (e.g., linear regression, PCA).</li>
        <li><strong>Handling outliers:</strong> It is less affected by extreme values than min-max normalization, since it considers the variance of the data.</li>
    </ul>
    <h2>Advantages:</h2>
    <ul>
        <li><strong>Centers the data:</strong> The transformed data will have a mean of 0, beneficial for models assuming normality.</li>
        <li><strong>Considers variance:</strong> It accounts for both the mean and the spread (variance) of the data, helping in situations where data distribution is essential.</li>
        <li><strong>Works well for distance-based models:</strong> Algorithms like SVMs and k-means clustering benefit from normalized features, as Z-scores ensure equal contribution from all features.</li>
    </ul>
    <h2>Disadvantages:</h2>
    <ul>
        <li><strong>Assumes normal distribution:</strong> Z-score normalization works best with normally distributed data. It may not perform well with skewed data or extreme outliers.</li>
        <li><strong>Not bounded to a specific range:</strong> Unlike min-max normalization, Z-score normalization does not scale data to a specific range (e.g., [0, 1]), which can be important in some applications.</li>
        <li><strong>Sensitive to small sample sizes:</strong> With small datasets, outliers can significantly impact the mean and standard deviation, making Z-scores unreliable.</li>
    </ul>
    <h2>When to use:</h2>
    <ul>
        <li>When the data follows a Gaussian distribution or is close to it.</li>
        <li>For algorithms that assume or perform better with normalized data (e.g., logistic regression, PCA).</li>
        <li>When outliers should not dominate: Z-score normalization is less sensitive to outliers compared to min-max normalization.</li>
    </ul>
</body>
</html>
"""


ROBUST_SCALING_NORMALIZATION_HELP = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Robust Scaling Normalization Help</title>
    <!-- MathJax Configuration -->
    <script type="text/javascript"
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML">
    </script>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }
        h1, h2 {
            color: #2E8B57;
        }
        p, ul {
            font-size: 16px;
        }
        ul {
            margin-left: 20px;
        }
    </style>
</head>
<body>
    <h1>Robust Scaling Normalization</h1>
    <p>
        Robust Scaling Normalization scales data based on the interquartile range (IQR) instead of the mean and variance, making it less sensitive to outliers. It centers the data around the median and scales it by the IQR, which is the range between the first quartile (25th percentile) and third quartile (75th percentile).
    </p>
    <h2>Formula:</h2>
    <p>
        Robust scaling normalization rescales a given value \(x\) using the formula:
    </p>
    <p>
        \\[
        x' = \\frac{x - \\text{Median}(X)}{IQR}
        \\]
    </p>
    <p>Where:</p>
    <ul>
        <li>\(x\) is the original value,</li>
        <li>\(\text{Median}(X)\) is the median of the dataset,</li>
        <li>\(IQR = Q_3 - Q_1\) is the interquartile range (the range between the 75th percentile \(Q_3\) and the 25th percentile \(Q_1\)),</li>
        <li>\(x'\) is the normalized value.</li>
    </ul>
    <h2>Usage:</h2>
    <ul>
        <li><strong>Preprocessing step for data with outliers:</strong> Robust scaling is useful when the dataset contains significant outliers that might distort other normalization methods.</li>
        <li><strong>Makes data more robust:</strong> This method is less sensitive to outliers because it uses the median and IQR rather than the mean and standard deviation.</li>
    </ul>
    <h2>Advantages:</h2>
    <ul>
        <li><strong>Less affected by outliers:</strong> Since it uses the median and IQR, robust scaling is less influenced by extreme values than methods like min-max or Z-score normalization.</li>
        <li><strong>Centers the data around the median:</strong> Instead of the mean, robust scaling focuses on the median, making it a more stable approach for datasets with skewed data.</li>
    </ul>
    <h2>Disadvantages:</h2>
    <ul>
        <li><strong>Does not scale to a specific range:</strong> Unlike min-max normalization, this method does not constrain the data to a particular range, such as [0, 1], which might be required in some cases.</li>
        <li><strong>Not ideal for normally distributed data:</strong> If the data is normally distributed without significant outliers, Z-score normalization may be more appropriate, as robust scaling does not capture the true distribution.</li>
    </ul>
    <h2>When to Use:</h2>
    <ul>
        <li>For datasets with significant outliers that can distort the performance of other normalization techniques.</li>
        <li>When the data distribution is not Gaussian or is heavily skewed, making other normalization methods like Z-score less effective.</li>
    </ul>
</body>
</html>
"""

AUC_NORMALIZATION_HELP = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AUC Normalization Help</title>
    <!-- Updated MathJax Configuration -->
    <script type="text/javascript"
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js">
    </script>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }
        h1, h2 {
            color: #2E8B57;
        }
        p, ul {
            font-size: 16px;
        }
        ul {
            margin-left: 20px;
        }
    </style>
</head>
<body>
    <h1>Area Under the Curve (AUC) Normalization</h1>
    <p>
        Area Under the Curve (AUC) normalization is a technique that normalizes data based on the area under its curve. It is often used in signal processing, time series data, or biological assays to ensure that variations in total magnitude or signal intensity are accounted for, allowing meaningful comparisons between datasets.
    </p>
    <h2>Formula:</h2>
<p>
    The area under the curve can be approximated using the <strong>Trapezoidal Rule</strong> for discrete data points \( (x_i, y_i) \):
    </p>
    <p>
        \\[
        \text{AUC} = \sum_{i=1}^{n-1} (x_{i+1} - x_i) \\times \\frac{(y_i + y_{i+1})}{2}
        \\]
    </p>
    <p>
        To normalize the dataset so that the total area under the curve equals 1, each \( y_i \) value is scaled by dividing it by the total AUC:
    </p>
    <p>
        \\[
        y'_i = \\frac{y_i}{\text{AUC}}
        \\]
    </p>
    <h2>Usage:</h2>
    <ul>
        <li><strong>Signal normalization:</strong> AUC normalization is often used to compare signals where the total magnitude varies, but the relative shape remains important.</li>
        <li><strong>Comparing time series data:</strong> In fields like finance, physiology, or engineering, AUC normalization allows the comparison of time series data by scaling based on the total area under the signal curve.</li>
    </ul>
    <h2>Advantages:</h2>
    <ul>
        <li><strong>Accounts for total intensity:</strong> This method normalizes data by its total intensity, which helps compare datasets with varying magnitudes but similar shapes.</li>
        <li><strong>Useful for non-parametric data:</strong> AUC normalization can be applied to various data types, regardless of the underlying distribution or parameters.</li>
        <li><strong>Easy to interpret:</strong> The normalized values represent the proportion of the signal's area contributed by each point, allowing intuitive comparisons across datasets.</li>
    </ul>
    <h2>Disadvantages:</h2>
    <ul>
        <li><strong>Sensitive to baseline shifts:</strong> If the curve has a significant baseline shift, it can distort the AUC and lead to inaccurate normalization.</li>
        <li><strong>Computational cost:</strong> Calculating the area under the curve for large datasets can be computationally intensive, especially for complex functions.</li>
        <li><strong>Not always relevant:</strong> In some cases, the total area may not be the most critical factor; local variations in the curve may be more important than the total magnitude.</li>
    </ul>
    <h2>When to Use:</h2>
    <ul>
        <li><strong>When comparing signal intensity:</strong> AUC normalization is useful when comparing datasets that represent signals with varying total magnitudes but similar shapes.</li>
        <li><strong>For datasets where total sum matters:</strong> In cases like chemical reactions, biological assays, or other scenarios where the total cumulative value is important, AUC normalization provides a meaningful method for comparison.</li>
        <li><strong>Non-parametric data:</strong> AUC normalization does not rely on parametric assumptions (such as normality), making it versatile across different data types.</li>
    </ul>
</body>
</html>
"""

INTERVAL_AUC_NORMALIZATION_HELP = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Interval AUC Normalization Help</title>
    <!-- MathJax Configuration -->
    <script type="text/javascript"
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js">
    </script>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }
        h1, h2 {
            color: #2E8B57;
        }
        p, ul {
            font-size: 16px;
        }
        ul {
            margin-left: 20px;
        }
    </style>
</head>
<body>
    <h1>Interval Area Under the Curve (AUC) Normalization</h1>
    <p>
        Interval AUC Normalization is a technique that rescales data based on the desired area under the curve (AUC) over a specified interval. This method is often used in time series data, signal processing, or experimental data where the total magnitude of the curve needs to be standardized across different datasets.
    </p>
    <h2>Formula:</h2>
    <p>
        First, the current area under the curve for the given interval is calculated using the Trapezoidal Rule:
    </p>
    <p>
        \\[
        \sum_{i=a}^{b-1} (x_{i+1} - x_i) \times \frac{(y_i + y_{i+1})}{2}
        \\]
    </p>
    <p>
        Where \(a\) and \(b\) represent the start and end indices of the selected interval, respectively.
    </p>
    <p>
        To normalize the curve to match the desired area under the curve (AUC), the following scaling is applied to the y-values:
    </p>
    <p>
        \\[
        y'_i = y_i \times \frac{\text{AUC}_{\text{desired}}}{\text{AUC}_{\text{current}}}
        \\]
    </p>
    <h2>Usage:</h2>
    <ul>
        <li><strong>Signal normalization:</strong> Interval AUC Normalization is often used to normalize signal intensity over a specified time or frequency interval to a desired AUC value.</li>
        <li><strong>Experimental data comparison:</strong> In fields like biology or chemistry, it allows researchers to compare datasets by adjusting the total magnitude of a response or signal within a specific range.</li>
        <li><strong>Time series data scaling:</strong> This method can be applied to normalize the amplitude of time series data over a specific time window.</li>
    </ul>

    <h2>Advantages:</h2>
    <ul>
        <li><strong>Adjusts for varying magnitudes:</strong> It ensures that data from different experiments or signals can be compared by scaling them to a common desired AUC value.</li>
        <li><strong>Focuses on specific intervals:</strong> The normalization is applied only to the selected interval, allowing for targeted scaling of data.</li>
        <li><strong>Maintains the overall shape of the curve:</strong> The method preserves the relative distribution and shape of the data points while scaling the magnitude.</li>
    </ul>

    <h2>Disadvantages:</h2>
    <ul>
        <li><strong>Sensitive to interval selection:</strong> The effectiveness of this method depends on the selection of the interval \(a\) to \(b\), and poor choices can lead to inaccurate normalization.</li>
        <li><strong>Requires accurate integration:</strong> Calculating the current AUC accurately is critical, and errors in this calculation can affect the final normalized values.</li>
        <li><strong>Not suitable for non-continuous data:</strong> This method assumes continuous data between the points; it may not work well for sparse or noisy data.</li>
    </ul>

    <h2>When to Use:</h2>
    <ul>
        <li><strong>Comparing datasets:</strong> When comparing datasets from different experiments, normalizing to the same AUC ensures comparability, especially when different datasets have different magnitudes.</li>
        <li><strong>Signal processing:</strong> Useful for signals with varying intensities where you want to normalize them over a specific interval.</li>
        <li><strong>Standardizing experiments:</strong> In experiments where a common response magnitude is required for different cases, this method can ensure consistency.</li>
    </ul>
</body>
</html>
"""

TOTAL_INTENSITY_NORMALIZATION_HELP = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Total Intensity Normalization Help</title>
    <!-- MathJax Configuration -->
    <script type="text/javascript"
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML">
    </script>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }
        h1, h2 {
            color: #2E8B57;
        }
        p, ul {
            font-size: 16px;
        }
        ul {
            margin-left: 20px;
        }
        img {
            max-width: 100%;
            height: auto;
        }
    </style>
</head>
<body>
    <h1>Total Intensity Normalization</h1>
    <p>
        Total Intensity Normalization scales the entire dataset so that the sum of all Y-values equals a specified desired total intensity. This method is particularly useful for standardizing datasets, allowing for meaningful comparisons across datasets with varying magnitudes.
    </p>
    <h2>Formula:</h2>
    <p>
        Given Y-values \( y_1, y_2, \ldots, y_n \), the normalized Y-values \( y'_i \) are calculated as:
    </p>
    <p>
        \\[
        y'_i = y_i \times \left( \frac{\text{Desired Total Intensity}}{\sum_{j=1}^{n} y_j} \right)
        \\]
    </p>
    <h2>Usage:</h2>
    <ul>
        <li>Standardizing datasets for comparative analysis.</li>
        <li>Preparing data for machine learning algorithms that require feature scaling.</li>
    </ul>
    <h2>Advantages:</h2>
    <ul>
        <li>Ensures consistency across datasets.</li>
        <li>Simplifies the comparison of datasets with different scales.</li>
    </ul>
    <h2>Disadvantages:</h2>
    <ul>
        <li>Does not account for the distribution of data within the dataset.</li>
        <li>May not be suitable for datasets where the total intensity is not a meaningful metric.</li>
    </ul>
    <h2>Example:</h2>
    <p>
        Consider a dataset with Y-values: [2, 4, 6, 8, 10]. To normalize this dataset to a desired total intensity of 1, each Y-value is scaled as follows:
    </p>
    <p>
        \[
        \text{Desired Total Intensity} = 1
        \]
        \[
        \sum_{j=1}^{5} y_j = 2 + 4 + 6 + 8 + 10 = 30
        \]
        \[
        y'_i = y_i \times \left( \frac{1}{30} \right) = \left[ \frac{2}{30}, \frac{4}{30}, \frac{6}{30}, \frac{8}{30}, \frac{10}{30} \right] = [0.0667, 0.1333, 0.2000, 0.2667, 0.3333]
        \]
    </p>
</body>
</html>
"""