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
    <h1>Total Intensity Normalization</h1>
    <p>
        Total Intensity Normalization is a technique used to scale data so that the sum (or total intensity) of the data values matches a specific desired total. It is often applied in fields such as spectrometry, bioinformatics, and other experimental data where different datasets may have varying overall magnitudes, but the relative values need to be preserved.
    </p>
    <h2>Formula:</h2>
    <p>
        The normalization process involves dividing each data point by the total sum of all data points and multiplying by the desired total intensity:
    </p>
    <p>
        \\[
        y'_i = y_i \times \frac{T_{\text{desired}}}{T_{\text{current}}}
        \\]
    </p>
    <p>
        Where:
    </p>
    <ul>
        <li>\(y'_i\) is the normalized value.</li>
        <li>\(y_i\) is the original value.</li>
        <li>\(T_{\text{desired}}\) is the target total intensity specified by the user.</li>
        <li>\(T_{\text{current}}\) is the sum of all current data points (i.e., the total intensity of the original dataset).</li>
    </ul>

    <h2>Usage:</h2>
    <ul>
        <li><strong>Data normalization:</strong> Total Intensity Normalization is often used in scenarios where the overall magnitude of the data may vary between datasets, but you want to make sure the sum of the values is consistent across all datasets.</li>
        <li><strong>Spectrometry:</strong> It is frequently used in mass spectrometry and other signal-based data where the total intensity or signal across a dataset needs to be normalized for comparative analysis.</li>
        <li><strong>Bioinformatics and gene expression:</strong> This method can also be used to normalize gene expression levels across different samples to account for varying total RNA levels in each sample.</li>
    </ul>

    <h2>Advantages:</h2>
    <ul>
        <li><strong>Preserves relative proportions:</strong> The method maintains the relative proportions of the data points while normalizing the overall magnitude.</li>
        <li><strong>Simple to apply:</strong> It is straightforward to calculate and apply, as it only requires computing the sum of the dataset and applying a scaling factor.</li>
        <li><strong>Ensures comparability:</strong> It allows for direct comparison of datasets by ensuring that they all have the same total intensity or sum.</li>
    </ul>

    <h2>Disadvantages:</h2>
    <ul>
        <li><strong>Sensitive to outliers:</strong> If the dataset contains extreme outliers, they will disproportionately affect the total intensity and may distort the normalization.</li>
        <li><strong>Does not account for distribution differences:</strong> While the total sum is normalized, the underlying distribution of values might still vary between datasets.</li>
        <li><strong>Not suitable for zero-sum data:</strong> If the sum of the original data points is zero or near zero, this method cannot be applied, as division by zero would occur.</li>
    </ul>

    <h2>When to Use:</h2>
    <ul>
        <li><strong>Comparing datasets:</strong> When comparing datasets with different overall magnitudes, Total Intensity Normalization ensures that they can be directly compared on a common scale.</li>
        <li><strong>Signal-based data:</strong> Useful in signal-based datasets, such as spectrometry or chromatography, where you want to normalize the total signal intensity.</li>
        <li><strong>Biological data:</strong> In fields such as bioinformatics or genomics, it is used to normalize experimental data like gene expression levels for cross-sample comparison.</li>
    </ul>
</body>
</html>
"""


REFERENCE_PEAK_NORMALIZATION_HELP = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Reference Peak Normalization Help</title>
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
    <h1>Reference Peak Normalization</h1>
    <p>
        Reference Peak Normalization is a technique used to rescale data by normalizing all values relative to a specific reference peak within the dataset. This method ensures that the intensity of the reference peak is consistent across different datasets, allowing for easier comparison. It is commonly used in fields such as chromatography, mass spectrometry, and spectroscopy.
    </p>
    <h2>Formula:</h2>
    <p>
        The normalization process involves dividing each data point by the value of the reference peak:
    </p>
    <p>
        \\[
        y'_i = \frac{y_i}{y_{\text{ref}}}
        \\]
    </p>
    <p>
        Where:
    </p>
    <ul>
        <li>\(y'_i\) is the normalized value.</li>
        <li>\(y_i\) is the original value.</li>
        <li>\(y_{\text{ref}}\) is the intensity of the reference peak.</li>
    </ul>

    <h2>Usage:</h2>
    <ul>
        <li><strong>Peak-based data:</strong> Reference Peak Normalization is often used in data types where individual peaks or signals are important, such as chromatography, mass spectrometry, or spectroscopy.</li>
        <li><strong>Comparing datasets:</strong> It helps standardize datasets by normalizing to a common reference point, typically the most intense or biologically relevant peak.</li>
        <li><strong>Signal correction:</strong> It can be used to correct for variations in signal intensity due to experimental conditions or instrument sensitivity.</li>
    </ul>

    <h2>Advantages:</h2>
    <ul>
        <li><strong>Consistent scaling:</strong> By normalizing to a reference peak, the method ensures that the relative intensities of peaks or features are consistent across datasets.</li>
        <li><strong>Simple and effective:</strong> It is straightforward to calculate and implement, especially when a clear reference peak is present in all datasets.</li>
        <li><strong>Accounts for experimental variation:</strong> Normalizing to a reference peak can help reduce variability introduced by differences in sample preparation or instrument sensitivity.</li>
    </ul>

    <h2>Disadvantages:</h2>
    <ul>
        <li><strong>Dependent on the reference peak:</strong> The method assumes that the reference peak is stable and not affected by experimental conditions, which may not always be the case.</li>
        <li><strong>Inapplicable to datasets without a clear peak:</strong> If the dataset does not have a well-defined reference peak, this method cannot be used.</li>
        <li><strong>Distorted normalization if the reference peak is noisy:</strong> If the reference peak has significant noise or variability, the normalization may distort the rest of the dataset.</li>
    </ul>

    <h2>When to Use:</h2>
    <ul>
        <li><strong>Peak-based data:</strong> When working with data that has distinct peaks or signals (e.g., chromatography or mass spectrometry), Reference Peak Normalization provides a simple and effective way to standardize datasets.</li>
        <li><strong>Standardizing experimental results:</strong> In situations where experimental variability is present (e.g., changes in instrument sensitivity or sample preparation), Reference Peak Normalization helps reduce the impact of such variability.</li>
        <li><strong>Comparing multiple datasets:</strong> If you are comparing datasets from different runs or conditions, this method can ensure that all data are scaled relative to a common reference point.</li>
    </ul>
</body>
</html>
"""

BASELINE_CORRECTION_NORMALIZATION_HELP = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Baseline Correction Normalization Help</title>
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
        .parameter-section {
            margin-top: 20px;
        }
        .parameter-section h3 {
            color: #4682B4;
        }
        .parameter-section ul {
            list-style-type: disc;
        }
    </style>
</head>
<body>
    <h1>Baseline Correction Normalization</h1>
    <p>
        Baseline Correction Normalization is a technique used to remove background noise or drift in data by subtracting the baseline from the data points. This method is commonly applied to datasets where the signal is affected by a non-zero baseline, such as in spectroscopy, chromatography, or time-series data. The goal is to bring the baseline of the data to zero, enabling clearer analysis of the signal or feature of interest.
    </p>
    <h2>Formula:</h2>
    <p>
        The normalization is typically performed by subtracting the baseline \(y_{\text{baseline}}\) from each data point:
    </p>
    <p>
        \\[
        y'_i = y_i - y_{\text{baseline}}
        \\]
    </p>
    <p>
        Where:
    </p>
    <ul>
        <li>\(y'_i\) is the baseline-corrected value.</li>
        <li>\(y_i\) is the original data value.</li>
        <li>\(y_{\text{baseline}}\) is the baseline value, which can be constant or variable depending on the method used to estimate it.</li>
    </ul>

    <h2>Usage:</h2>
    <ul>
        <li><strong>Signal correction:</strong> Baseline correction is often used in signal-based data, such as spectroscopy or chromatography, to remove background noise or drift and focus on the actual signal.</li>
        <li><strong>Time-series data:</strong> It is useful for removing trends or slow variations in time-series data, making the underlying features more prominent.</li>
        <li><strong>Experimental measurements:</strong> In experiments with drifting baselines (e.g., due to temperature changes, instrument variations), baseline correction ensures the data reflects only the significant changes or features.</li>
    </ul>

    <h2>Advantages:</h2>
    <ul>
        <li><strong>Removes background noise:</strong> By subtracting the baseline, the method ensures that the data focuses on the signal of interest, eliminating unwanted background trends.</li>
        <li><strong>Improves signal clarity:</strong> This normalization makes it easier to detect meaningful patterns or features in the data.</li>
        <li><strong>Applicable across different domains:</strong> It is widely used in various fields, such as spectroscopy, chromatography, and other signal-based analyses, making it versatile.</li>
    </ul>

    <h2>Disadvantages:</h2>
    <ul>
        <li><strong>Requires accurate baseline estimation:</strong> The success of baseline correction depends heavily on how accurately the baseline is estimated. Poorly estimated baselines can lead to inaccurate results.</li>
        <li><strong>Not suitable for datasets without a baseline:</strong> This method is only applicable to data where a baseline exists. Datasets without a clear baseline do not benefit from this approach.</li>
        <li><strong>Over-correction risk:</strong> There is a risk of over-correcting the signal if the baseline is improperly identified, which could distort the original data.</li>
    </ul>

    <h2>When to Use:</h2>
    <ul>
        <li><strong>Signal-based data:</strong> Use baseline correction when working with data that has an obvious background signal or drift, such as in spectroscopy or chromatography.</li>
        <li><strong>Time-series analysis:</strong> Apply baseline correction to time-series data that has slow trends or background drift that need to be removed for clearer analysis.</li>
        <li><strong>Experiments with drifting conditions:</strong> When working with experimental data affected by changing conditions (e.g., temperature or instrument variations), baseline correction helps remove these effects and highlight the true signal.</li>
    </ul>

    <div class="parameter-section">
        <h2>Parameters:</h2>
        <p>Baseline Correction Normalization utilizes three key parameters: <strong>Lambda (\(\lambda\))</strong>, <strong>Asymmetry (p)</strong>, and <strong>Iterations</strong>. Understanding and appropriately setting these parameters is crucial for effective baseline correction.</p>
        <h3>1. Lambda (\(\lambda\))</h3>
        <p>
            <strong>Description:</strong> Lambda controls the smoothness of the estimated baseline. It determines the penalty for deviations from a smooth baseline. A higher lambda value results in a smoother baseline, while a lower value allows the baseline to follow more closely to the data.
        </p>
        <p>
            <strong>How to Choose:</strong>
        </p>
        <ul>
            <li><strong>High Lambda (e.g., \(1 \times 10^5\) to \(1 \times 10^7\)):</strong> Use when the baseline is expected to be smooth and not follow the minor fluctuations of the data. Ideal for datasets where the baseline drift is gradual.</li>
            <li><strong>Low Lambda (e.g., \(1 \times 10^3\) to \(1 \times 10^5\)):</strong> Choose when the baseline may have sharper features or when you want the baseline to adapt more closely to the data variations.</li>
            <li><strong>Default Value:</strong> A lambda value of \(1 \times 10^6\) is often a good starting point and works well for many datasets.</li>
        </ul>

        <h3>2. Asymmetry (p)</h3>
        <p>
            <strong>Description:</strong> Asymmetry controls the weighting of positive and negative residuals during baseline estimation. It dictates how the algorithm distinguishes between signal peaks and baseline.
        </p>
        <p>
            <strong>How to Choose:</strong>
        </p>
        <ul>
            <li><strong>Low Asymmetry (e.g., 0.001 to 0.01):</strong> Increases sensitivity to peaks, allowing the algorithm to better ignore signal peaks and focus on estimating the baseline.</li>
            <li><strong>High Asymmetry (e.g., 0.05 to 0.1):</strong> Reduces sensitivity to peaks, which may be useful if the signal has overlapping features that shouldn't be overly suppressed.</li>
            <li><strong>Default Value:</strong> An asymmetry value of 0.01 is commonly used and provides a good balance between sensitivity and baseline estimation accuracy.</li>
        </ul>

        <h3>3. Iterations</h3>
        <p>
            <strong>Description:</strong> Iterations determine how many times the algorithm refines the baseline estimation. More iterations can lead to a more accurate and stable baseline.
        </p>
        <p>
            <strong>How to Choose:</strong>
        </p>
        <ul>
            <li><strong>Fewer Iterations (e.g., 5 to 10):</strong> Faster computation but may result in a less accurate baseline, especially in datasets with complex baseline shapes.</li>
            <li><strong>More Iterations (e.g., 15 to 30):</strong> Slower computation but can achieve a more refined and accurate baseline estimation. Useful for high-noise datasets or those with intricate baseline structures.</li>
            <li><strong>Default Value:</strong> Setting iterations to 10 is a standard choice that offers a reasonable trade-off between performance and accuracy.</li>
        </ul>
    </div>
</body>
</html>
"""

SUBTRACTION_NORMALIZATION_HELP = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Subtraction Normalization Help</title>
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
    <h1>Subtraction Normalization</h1>
    <p>
        Subtraction Normalization is a technique where the values of a reference measurement are subtracted from the values of an experimental dataset. This process is useful for isolating the variations that are unique to the experiment by removing any baseline or background influence from the reference measurement.
    </p>
    <h2>Formula:</h2>
    <p>
        Subtraction normalization adjusts a given experimental value \(x\) using the formula:
    </p>
    <p>
        \\[ 
        x' = x - r
        \\]
    </p>
    <p>Where:</p>
    <ul>
        <li>\(x\) is the original experimental value,</li>
        <li>\(r\) is the corresponding reference measurement value,</li>
        <li>\(x'\) is the normalized value after subtraction.</li>
    </ul>
    <h2>Usage:</h2>
    <ul>
        <li><strong>Noise removal:</strong> This method helps eliminate background noise or systematic errors present in both the experimental and reference measurements.</li>
        <li><strong>Comparative analysis:</strong> It allows for a direct comparison between datasets by focusing on the deviations from the reference data.</li>
        <li><strong>Enhanced signal detection:</strong> By subtracting the reference, it helps to highlight significant changes in the experimental data.</li>
    </ul>
    <h2>Advantages:</h2>
    <ul>
        <li><strong>Improves accuracy:</strong> By removing baseline variations, it provides a more accurate representation of the experimental signal.</li>
        <li><strong>Simple implementation:</strong> The subtraction operation is computationally straightforward and effective for many types of data analysis.</li>
        <li><strong>Direct interpretation:</strong> The resulting values represent the deviation from the reference, making it easy to interpret changes in the data.</li>
    </ul>
    <h2>Disadvantages:</h2>
    <ul>
        <li><strong>Reference quality dependency:</strong> The accuracy of the subtraction normalization depends heavily on the quality and relevance of the reference measurement.</li>
        <li><strong>Assumes linear relationship:</strong> This method assumes that the experimental data can be accurately described by a simple linear subtraction, which may not always be the case for complex datasets.</li>
        <li><strong>Outlier sensitivity:</strong> If the reference measurement contains outliers, they may distort the subtraction process.</li>
    </ul>
    <h2>When to use:</h2>
    <ul>
        <li>When you need to eliminate background or systematic errors that are common between the experiment and reference measurement.</li>
        <li>When the primary focus is on analyzing deviations or changes relative to a baseline condition.</li>
    </ul>
</body>
</html>
"""

NOISE_REDUCTION = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Noise Reduction Help</title>
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
        h1, h2, h3, h4 {
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
    <h1>Noise Reduction</h1>
    <p>
        <strong>Noise Reduction</strong> is a data preprocessing technique aimed at removing or minimizing unwanted random variations, known as "noise," from your data. Noise can obscure meaningful patterns and trends, making analysis and interpretation more challenging. By applying noise reduction methods, you enhance the quality and clarity of your data, facilitating more accurate and reliable analyses.
    </p>
    
    <h2>Methods:</h2>
    
    <h3>1. Moving Average Smoothing</h3>
    <p>
        Moving Average Smoothing is one of the simplest and most widely used noise reduction techniques. It involves replacing each data point with the average of its neighboring points within a specified window size. This method effectively smooths out short-term fluctuations, highlighting longer-term trends and patterns.
    </p>
    <h4>Parameters:</h4>
    <ul>
        <li><strong>Window Size:</strong> The number of adjacent data points included in the averaging process. A larger window size results in greater smoothing but may obscure finer details.</li>
    </ul>
    <h4>Why Use Moving Average Smoothing?</h4>
    <ul>
        <li><strong>Simple Implementation:</strong> Easy to understand and implement, making it suitable for quick noise reduction tasks.</li>
        <li><strong>Trend Highlighting:</strong> Helps in identifying and emphasizing underlying trends by reducing minor fluctuations.</li>
    </ul>
    <h4>When to Use Moving Average Smoothing?</h4>
    <ul>
        <li>When you need a quick and straightforward method to smooth out data without preserving specific features.</li>
        <li>In scenarios where the primary interest is in long-term trends rather than short-term variations.</li>
    </ul>
    
    <h3>2. Savitzky-Golay Filter</h3>
    <p>
        The Savitzky-Golay Filter is a more advanced noise reduction technique that fits successive subsets of adjacent data points with a low-degree polynomial. Unlike the Moving Average, it preserves important features such as peaks and sharp transitions while still reducing noise.
    </p>
    <h4>Parameters:</h4>
    <ul>
        <li><strong>Window Size:</strong> The number of data points included in each polynomial fit. Must be an odd integer to ensure symmetry.</li>
        <li><strong>Polynomial Order:</strong> The degree of the polynomial used for fitting. A higher order can better capture complex features but may overfit if too high relative to the window size.</li>
    </ul>
    <h4>Why Use Savitzky-Golay Filter?</h4>
    <ul>
        <li><strong>Feature Preservation:</strong> Maintains critical data features like peaks and edges, which are essential for accurate analysis.</li>
        <li><strong>Enhanced Smoothing:</strong> Provides a balance between smoothing and feature retention, making it suitable for diverse applications.</li>
    </ul>
    <h4>When to Use Savitzky-Golay Filter?</h4>
    <ul>
        <li>When it's crucial to preserve significant data features while reducing noise.</li>
        <li>In applications like spectroscopy or signal processing, where maintaining peak integrity is vital.</li>
    </ul>
    
    <h3>3. Wavelet Denoising</h3>
    <p>
        Wavelet Denoising leverages wavelet transforms to decompose data into different frequency components. By manipulating these components, it's possible to remove noise while retaining essential signal characteristics. This method is particularly effective for data with varying frequency content and can adapt to both smooth and transient noise patterns.
    </p>
    <h4>Parameters:</h4>
    <ul>
        <li><strong>Wavelet Type:</strong> Specifies the family of wavelets used for decomposition (e.g., 'db1', 'sym5'). Different wavelets capture different features of the data.</li>
        <li><strong>Level:</strong> Determines the number of decomposition levels, affecting the granularity of noise removal. Higher levels can capture finer noise details.</li>
    </ul>
    <h4>Why Use Wavelet Denoising?</h4>
    <ul>
        <li><strong>Adaptive Noise Removal:</strong> Capable of handling both smooth and transient noise, making it versatile across various data types.</li>
        <li><strong>Signal Integrity:</strong> Effectively removes noise without distorting important signal components, ensuring data reliability.</li>
    </ul>
    <h4>When to Use Wavelet Denoising?</h4>
    <ul>
        <li>When dealing with complex datasets that contain both low-frequency trends and high-frequency noise.</li>
        <li>In fields like image processing, biomedical signal analysis, and financial data analysis, where maintaining signal integrity is critical.</li>
    </ul>
    
    <h2>Advantages:</h2>
    <ul>
        <li><strong>Improved Data Quality:</strong> Reduces random noise, enhancing the clarity and reliability of data.</li>
        <li><strong>Feature Preservation:</strong> Especially with advanced methods like Savitzky-Golay Filter and Wavelet Denoising, important data features are retained.</li>
        <li><strong>Flexibility:</strong> Multiple methods and adjustable parameters allow for tailored noise reduction based on specific data characteristics and analysis needs.</li>
    </ul>
    
    <h2>Disadvantages:</h2>
    <ul>
        <li><strong>Parameter Sensitivity:</strong> The effectiveness of noise reduction depends heavily on the choice of parameters, which may require careful tuning.</li>
        <li><strong>Computational Complexity:</strong> Advanced methods like Wavelet Denoising can be computationally intensive, especially for large datasets.</li>
        <li><strong>Potential Over-smoothing:</strong> Excessive smoothing can distort or eliminate important data features, leading to loss of critical information.</li>
    </ul>
    
    <h2>Basic Mathematical Descriptions:</h2>
    <h3>Moving Average Smoothing</h3>
    <p>
        For each data point \( y_i \), the Moving Average Smoothing replaces it with the average of its neighboring points within the window size \( w \):
    </p>
    <p>
        \[
        \hat{y}_i = \frac{1}{w} \sum_{j=-k}^{k} y_{i+j}
        \]
    </p>
    <p>
        Where \( k = \frac{w-1}{2} \) and \( w \) is the window size.
    </p>
    
    <h3>Savitzky-Golay Filter</h3>
    <p>
        The Savitzky-Golay Filter fits a polynomial of order \( p \) to each window of \( w \) data points:
    </p>
    <p>
        \[
        \hat{y}_i = \sum_{j=-k}^{k} c_j y_{i+j}
        \]
    </p>
    <p>
        Where \( c_j \) are the filter coefficients derived from the polynomial fit, and \( k = \frac{w-1}{2} \).
    </p>
    
    <h3>Wavelet Denoising</h3>
    <p>
        Wavelet Denoising involves decomposing the data \( y \) into wavelet coefficients \( C \) using a chosen wavelet function \( \psi \) and level \( l \):
    </p>
    <p>
        \[
        C = \text{wavedec}(y, \psi, level=l)
        \]
    </p>
    <p>
        Noise reduction is performed by thresholding the detail coefficients, and the denoised signal \( \hat{y} \) is reconstructed:
    </p>
    <p>
        \[
        \hat{y} = \text{waverec}(C', \psi)
        \]
    </p>
    <p>
        Where \( C' \) are the thresholded coefficients.
    </p>
    
    <h2>When to Use:</h2>
    <ul>
        <li>When your data contains significant random noise that obscures meaningful patterns.</li>
        <li>When preparing data for further analysis, such as peak detection, trend analysis, or statistical modeling.</li>
        <li>In applications where maintaining data integrity and feature preservation is crucial, like biomedical signal processing or financial data analysis.</li>
    </ul>
    
    <h2>Conclusion:</h2>
    <p>
        Noise Reduction is an essential step in data preprocessing, enhancing the quality and interpretability of your data. By choosing the appropriate method and carefully tuning its parameters, you can effectively minimize noise while preserving the vital characteristics of your dataset, leading to more accurate and insightful analyses.
    </p>
</body>
</html>
"""

UNIT_CONVERTER_HELP = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Unit Converter Help</title>
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
        h1, h2, h3 {
            color: #2E8B57;
        }
        p, ul {
            font-size: 16px;
        }
        ul {
            margin-left: 20px;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h1>Unit Converter</h1>
    <p>
        The <strong>Unit Converter</strong> allows you to apply custom mathematical transformations to the X and Y data columns using user-defined formulas. This is useful for converting units, scaling data, or applying any mathematical operation to your data.
    </p>
    <h2>How to Use:</h2>
    <ol>
        <li>Enter a formula for the X-axis in the <strong>X-axis Conversion Formula</strong> field. Use <code>x</code> to represent the original X data.</li>
        <li>Enter a formula for the Y-axis in the <strong>Y-axis Conversion Formula</strong> field. Use <code>y</code> to represent the original Y data.</li>
        <li>If you leave a field empty, no changes will be made to that axis.</li>
        <li>Click <strong>Apply</strong> to perform the unit conversion.</li>
    </ol>
    <h2>Supported Operations:</h2>
    <p>
        You can use any valid mathematical expression, including:
    </p>
    <ul>
        <li>Basic arithmetic: <code>+</code>, <code>-</code>, <code>*</code>, <code>/</code>, <code>**</code> (power)</li>
        <li>Mathematical functions from the <code>numpy</code> and <code>math</code> libraries, such as <code>np.sin(x)</code>, <code>np.log(x)</code>, <code>math.sqrt(x)</code></li>
        <li>Constants like <code>np.pi</code>, <code>math.e</code></li>
    </ul>
    <h2>Examples:</h2>
    <ul>
        <li><strong>Convert nanometers to electronvolts (eV) on X-axis:</strong><br>
            Formula: <code>1239.84193 / x</code>
        </li>
        <li><strong>Convert Celsius to Fahrenheit on Y-axis:</strong><br>
            Formula: <code>(y * 9/5) + 32</code>
        </li>
        <li><strong>Apply logarithmic scale to Y-axis:</strong><br>
            Formula: <code>np.log(y)</code>
        </li>
        <li><strong>Scale Y-axis values by a factor of 1000:</strong><br>
            Formula: <code>y * 1000</code>
        </li>
        <li><strong>Convert energy from eV to Joules on X-axis:</strong><br>
            Formula: <code>x * 1.60218e-19</code>
        </li>
    </ul>
    <h2>Important Notes:</h2>
    <ul>
        <li>Ensure that your formulas are valid Python expressions.</li>
        <li>Use <code>x</code> for the X-axis data and <code>y</code> for the Y-axis data.</li>
        <li>You have access to functions from the <code>numpy</code> and <code>math</code> libraries.</li>
        <li>If an error occurs during the application of the formula, an error message will be displayed.</li>
    </ul>
    <h2>Advantages:</h2>
    <ul>
        <li><strong>Flexibility:</strong> Allows for custom transformations tailored to your specific needs.</li>
        <li><strong>Simplicity:</strong> Easy to use by inputting standard mathematical expressions.</li>
        <li><strong>Efficiency:</strong> Quickly apply unit conversions without the need to modify the original data files.</li>
    </ul>
    <h2>When to Use:</h2>
    <ul>
        <li>When you need to convert data units for consistency or comparison purposes.</li>
        <li>When scaling data for analysis or visualization.</li>
        <li>When applying mathematical transformations to explore different representations of your data.</li>
    </ul>
</body>
</html>
"""

SHIFT_BASELINE_HELP = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Shift Baseline Help</title>
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
        h1, h2, h3 {
            color: #2E8B57;
        }
        p, ul {
            font-size: 16px;
        }
        ul {
            margin-left: 20px;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h1>Shift Baseline</h1>
    <p>
        The <strong>Shift Baseline</strong> feature allows you to adjust the minimum Y-value of your dataset to a desired value. This is particularly useful for normalizing data, aligning datasets for comparison, or preparing data for further analysis.
    </p>
    <h2>How to Use:</h2>
    <ol>
        <li>Enter the desired baseline value in the <strong>Desired Baseline Value</strong> field. The default value is <code>0</code>.</li>
        <li>Select one or more data files from the <strong>Selected Data</strong> panel that you wish to apply the baseline shift to.</li>
        <li>Click the <strong>Apply</strong> button to perform the baseline shift on the selected datasets.</li>
        <li>After applying, you can choose to <strong>Save</strong> the corrected data or <strong>Send to Data Panel</strong> for further processing.</li>
    </ol>
    <h2>Supported Operations:</h2>
    <p>
        The Shift Baseline operation performs a simple translation of the Y-values in your dataset. Specifically, it calculates the difference between the desired baseline and the current minimum Y-value and applies this shift uniformly across all Y-values.
    </p>
    <h2>Example:</h2>
    <ul>
        <li><strong>Setting the Minimum Y-value to Zero:</strong><br>
            - **Desired Baseline Value:** <code>0</code><br>
            - **Operation:** If the current minimum Y-value is <code>5</code>, the shift value is <code>0 - 5 = -5</code>. All Y-values are decreased by <code>5</code>, making the new minimum Y-value <code>0</code>.
        </li>
        <li><strong>Shifting the Baseline to a Specific Value (e.g., -10):</strong><br>
            - **Desired Baseline Value:** <code>-10</code><br>
            - **Operation:** If the current minimum Y-value is <code>2</code>, the shift value is <code>-10 - 2 = -12</code>. All Y-values are decreased by <code>12</code>, setting the new minimum Y-value to <code>-10</code>.
        </li>
    </ul>
    <h2>Important Notes:</h2>
    <ul>
        <li>Ensure that the desired baseline value is appropriate for your dataset and analysis requirements.</li>
        <li>If the desired baseline results in negative Y-values, verify that your subsequent analyses or visualizations can handle them.</li>
        <li>Shifting the baseline does not alter the shape or relative differences in your data; it only translates the data vertically.</li>
        <li>Before applying the shift, it's advisable to review the current minimum Y-value to understand the extent of the shift.</li>
    </ul>
    <h2>Advantages:</h2>
    <ul>
        <li><strong>Data Normalization:</strong> Align datasets to a common baseline, facilitating accurate comparisons.</li>
        <li><strong>Preparation for Analysis:</strong> Ensure that Y-values meet the prerequisites of certain analytical methods or algorithms.</li>
        <li><strong>Visualization Clarity:</strong> Enhance the readability of plots by setting a meaningful baseline.</li>
        <li><strong>Simplicity:</strong> Easy-to-use interface requiring minimal input from the user.</li>
    </ul>
    <h2>When to Use:</h2>
    <ul>
        <li>When comparing multiple datasets that have different baseline levels.</li>
        <li>Preparing data for machine learning models that assume data is centered around a specific value.</li>
        <li>Enhancing the visual appeal of plots by ensuring that all data starts from a consistent baseline.</li>
        <li>Correcting datasets where the baseline has been erroneously offset due to data acquisition issues.</li>
    </ul>
</body>
</html>
"""
