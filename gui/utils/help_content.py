# In gui/help_content.py


import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for PyInstaller and development. """
    try:
        base_path = sys._MEIPASS  # This is where PyInstaller stores the resources.
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



min_max_image_path = resource_path('gui/images/min-max.png')

MIN_MAX_NORMALIZATION_HELP = f"""
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
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }}
        h1, h2 {{
            color: #2E8B57;
        }}
        p, ul {{
            font-size: 16px;
        }}
        ul {{
            margin-left: 20px;
        }}
        img {{
            display: block;
            margin: 20px auto;
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <h1>Min-Max Normalization</h1>
    <p>
        Min-Max Normalization is a feature scaling technique that rescales data to a fixed range, typically between 0 and 1. It is often used as a preprocessing step in machine learning to ensure that different features contribute equally to the analysis.
    </p>
    <h2>Formula:</h2>
    <p>
    </p>
    <p>
        <!-- Image placeholder for the formula screenshot -->
        <img src="{min_max_image_path}" alt="Min-Max Normalization Formula">
    </p>
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

# Dynamically get the path for the robust scaling image
robust_scaling_image_path = resource_path('gui/images/robust_scaling.png')

ROBUST_SCALING_NORMALIZATION_HELP = f"""
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
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }}
        h1, h2 {{
            color: #2E8B57;
        }}
        p, ul {{
            font-size: 16px;
        }}
        ul {{
            margin-left: 20px;
        }}
        img {{
            display: block;
            margin: 20px auto;
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <h1>Robust Scaling Normalization</h1>
    <p>
        Robust Scaling Normalization scales data based on the interquartile range (IQR) instead of the mean and variance, making it less sensitive to outliers. It centers the data around the median and scales it by the IQR, which is the range between the first quartile (25th percentile) and third quartile (75th percentile).
    </p>
    <h2>Formula:</h2>
    <p>
        <!-- Image placeholder for the formula screenshot -->
        <img src="{robust_scaling_image_path}" alt="Robust Scaling Normalization Formula">
    </p>
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


# Dynamically get the path for the AUC image
auc_image_path = resource_path('gui/images/AUC.png')

AUC_NORMALIZATION_HELP = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AUC Normalization Help</title>
    <!-- MathJax Configuration -->
    <script type="text/javascript"
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML">
    </script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }}
        h1, h2 {{
            color: #2E8B57;
        }}
        p, ul {{
            font-size: 16px;
        }}
        ul {{
            margin-left: 20px;
        }}
        img {{
            display: block;
            margin: 20px auto;
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <h1>Area Under the Curve (AUC) Normalization</h1>
    <p>
        Area Under the Curve (AUC) normalization is a technique that normalizes data based on the total area under its curve. This method is frequently used in signal processing, time-series data, and biological assays to account for variations in total magnitude or signal intensity, allowing meaningful comparisons between datasets.
    </p>
    <h2>Formula:</h2>
    <p>
        The area under the curve (AUC) can be approximated using the <strong>Trapezoidal Rule</strong> for discrete data points \( (x_i, y_i) \):
    </p>
    <p>
        <!-- Image placeholder for the formula screenshot -->
        <img src="{auc_image_path}" alt="AUC Normalization Formula">
    </p>
    <h2>Usage:</h2>
    <ul>
        <li><strong>Signal normalization:</strong> AUC normalization is often used to compare signals where the total magnitude varies, but the relative shape is important.</li>
        <li><strong>Comparing time-series data:</strong> In fields like finance, physiology, or engineering, AUC normalization allows the comparison of time-series data by scaling based on the total area under the signal curve.</li>
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


# Dynamically get the path for the Interval AUC image
interval_auc_image_path = resource_path('gui/images/interval_auc.png')

INTERVAL_AUC_NORMALIZATION_HELP = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Interval AUC Normalization Help</title>
    <!-- MathJax Configuration -->
    <script type="text/javascript"
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML">
    </script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }}
        h1, h2 {{
            color: #2E8B57;
        }}
        p, ul {{
            font-size: 16px;
        }}
        ul {{
            margin-left: 20px;
        }}
        img {{
            display: block;
            margin: 20px auto;
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <h1>Interval Area Under the Curve (AUC) Normalization</h1>
    <p>
        Interval AUC Normalization is a technique that rescales data based on the desired area under the curve (AUC) over a specified interval. This method is often used in time series data, signal processing, or experimental data where the total magnitude of the curve needs to be standardized across different datasets.
    </p>
    <h2>Formula:</h2>
    <p>
        <!-- Image placeholder for the formula screenshot -->
        <img src="{interval_auc_image_path}" alt="Interval AUC Normalization Formula">
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


# Dynamically get the path for the Total Intensity image
total_intensity_image_path = resource_path('gui/images/total_intensity.png')

TOTAL_INTENSITY_NORMALIZATION_HELP = f"""
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
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }}
        h1, h2 {{
            color: #2E8B57;
        }}
        p, ul {{
            font-size: 16px;
        }}
        ul {{
            margin-left: 20px;
        }}
        img {{
            display: block;
            margin: 20px auto;
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <h1>Total Intensity Normalization</h1>
    <p>
        Total Intensity Normalization is a technique used to scale data so that the sum (or total intensity) of the data values matches a specific desired total. It is often applied in fields such as spectrometry, bioinformatics, and other experimental data where different datasets may have varying overall magnitudes, but the relative values need to be preserved.
    </p>
    <h2>Formula:</h2>
    <p>
        <!-- Image placeholder for the formula screenshot -->
        <img src="{total_intensity_image_path}" alt="Total Intensity Normalization Formula">
    </p>

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

# Dynamically get the path for the Reference Peak image
reference_peak_image_path = resource_path('gui/images/reference_peak.png')

REFERENCE_PEAK_NORMALIZATION_HELP = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Reference Peak Normalization Help</title>
    <!-- MathJax Configuration -->
    <script type="text/javascript"
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML">
    </script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }}
        h1, h2 {{
            color: #2E8B57;
        }}
        p, ul {{
            font-size: 16px;
        }}
        ul {{
            margin-left: 20px;
        }}
        img {{
            display: block;
            margin: 20px auto;
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <h1>Reference Peak Normalization</h1>
    <p>
        Reference Peak Normalization is a technique used to rescale data by normalizing all values relative to a specific reference peak within the dataset. This method ensures that the intensity of the reference peak is consistent across different datasets, allowing for easier comparison. It is commonly used in fields such as chromatography, mass spectrometry, and spectroscopy.
    </p>
    <h2>Formula:</h2>
    <p>
        <!-- Image placeholder for the formula screenshot -->
        <img src="{reference_peak_image_path}" alt="Reference Peak Normalization Formula">
    </p>

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

# Dynamically get the path for the Baseline Correction image
baseline_correction_image_path = resource_path('gui/images/baseline_correction.png')

BASELINE_CORRECTION_NORMALIZATION_HELP = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Baseline Correction Normalization Help</title>
    <!-- MathJax Configuration -->
    <script type="text/javascript"
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML">
    </script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }}
        h1, h2 {{
            color: #2E8B57;
        }}
        p, ul {{
            font-size: 16px;
        }}
        ul {{
            margin-left: 20px;
        }}
        img {{
            display: block;
            margin: 20px auto;
            max-width: 100%;
            height: auto;
        }}
        .parameter-section {{
            margin-top: 20px;
        }}
        .parameter-section h3 {{
            color: #4682B4;
        }}
        .parameter-section ul {{
            list-style-type: disc;
        }}
    </style>
</head>
<body>
    <h1>Baseline Correction Normalization</h1>
    <p>
        Baseline Correction Normalization is a technique used to remove background noise or drift in data by subtracting the baseline from the data points. This method is commonly applied to datasets where the signal is affected by a non-zero baseline, such as in spectroscopy, chromatography, or time-series data. The goal is to bring the baseline of the data to zero, enabling clearer analysis of the signal or feature of interest.
    </p>
    <h2>Formula:</h2>
    <p>
        <!-- Image placeholder for the formula screenshot -->
        <img src="{baseline_correction_image_path}" alt="Baseline Correction Formula">
    </p>
    
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
# Dynamically get paths for images used in Noise Reduction HTML content
moving_average_image_path = resource_path('gui/images/moving_average.png')
golay_image_path = resource_path('gui/images/golay.png')
wavelet_image_path = resource_path('gui/images/wavelet.png')

NOISE_REDUCTION = f"""
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
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            line-height: 1.6;
        }}
        h1, h2, h3, h4 {{
            color: #2E8B57;
        }}
        p, ul {{
            font-size: 16px;
        }}
        ul {{
            margin-left: 20px;
        }}
    </style>
</head>
<body>
    <h1>Noise Reduction</h1>
    <p>
        <strong>Noise Reduction</strong> refers to methods used to minimize unwanted random variations in data, improving data quality for analysis and interpretation.
    </p>

    <h2>1. Moving Average Smoothing</h2>
    <p>
        Moving Average Smoothing averages each data point with its neighboring points, reducing fluctuations while preserving the overall trend.
    </p>

    <h3>Mathematical Description:</h3>
    <p>
        <img src="{moving_average_image_path}" alt="Moving Average Formula">
    </p>

    <h3>Parameters:</h3>
    <ul>
        <li><strong>Window Size \( w \):</strong> A larger window provides greater smoothing but reduces local variations. A smaller window retains finer details but may not fully reduce noise.</li>
    </ul>

    <h3>Choosing \( w \):</h3>
    <ul>
        <li><strong>Large \( w \):</strong> Good for long-term trend analysis but may obscure short-term features.</li>
        <li><strong>Small \( w \):</strong> Retains local changes but may leave more noise.</li>
    </ul>

    <h3>When to Use:</h3>
    <ul>
        <li>When you want to highlight long-term trends and reduce short-term noise in time-series data.</li>
        <li>Suitable for simple applications where the primary goal is overall trend detection rather than fine-detail preservation.</li>
    </ul>

    <h3>Advantages:</h3>
    <ul>
        <li><strong>Simple to Implement:</strong> Easy to compute, requiring only arithmetic averaging.</li>
        <li><strong>Good for Trend Analysis:</strong> Helps reveal long-term patterns by eliminating short-term variations.</li>
    </ul>

    <h3>Disadvantages:</h3>
    <ul>
        <li><strong>Loss of Detail:</strong> A larger window size may obscure important features such as peaks or abrupt changes in the data.</li>
        <li><strong>Fixed Smoothing:</strong> The same degree of smoothing is applied to all data points, which might not be ideal for varying data densities.</li>
    </ul>

    <h2>2. Savitzky-Golay Filter</h2>
    <p>
        The Savitzky-Golay filter fits a low-degree polynomial to data within a moving window, preserving features such as peaks while reducing noise.
    </p>

    <h3>Mathematical Description:</h3>
    <p>
        <img src="{golay_image_path}" alt="Savitzky-Golay Formula">
    </p>

    <h3>Parameters:</h3>
    <ul>
        <li><strong>Window Size \( w \):</strong> Determines the number of points in the polynomial fit. A larger \( w \) provides more smoothing but may reduce feature sensitivity.</li>
        <li><strong>Polynomial Order \( p \):</strong> The degree of the polynomial. A higher \( p \) captures more complex features but risks overfitting.</li>
    </ul>

    <h3>Choosing \( w \) and \( p \):</h3>
    <ul>
        <li><strong>Window Size \( w \):</strong> Should be large enough to smooth noise but small enough to preserve important features.</li>
        <li><strong>Polynomial Order \( p \):</strong> A typical choice is \( p = 2 \) or \( p = 3 \) to avoid overfitting.</li>
    </ul>

    <h3>When to Use:</h3>
    <ul>
        <li>When it is important to preserve significant features such as peaks while reducing noise.</li>
        <li>Commonly used in signal processing, spectroscopy, or any data where maintaining sharp transitions is critical.</li>
    </ul>

    <h3>Advantages:</h3>
    <ul>
        <li><strong>Feature Preservation:</strong> Preserves key features like sharp peaks and edges while reducing noise.</li>
        <li><strong>Flexibility:</strong> By adjusting the polynomial order, the filter can adapt to both smooth and sharp data trends.</li>
    </ul>

    <h3>Disadvantages:</h3>
    <ul>
        <li><strong>Computationally More Intensive:</strong> Requires polynomial fitting, which is more complex than simple averaging.</li>
        <li><strong>Risk of Overfitting:</strong> A high polynomial order with a small window can lead to overfitting and artificial oscillations.</li>
    </ul>

    <h2>3. Wavelet Denoising</h2>
    <p>
        Wavelet denoising decomposes the data into different frequency components using a wavelet transform. By thresholding the wavelet coefficients, noise can be reduced while preserving important signal details.
    </p>

    <h3>Mathematical Description:</h3>
    <p>
        <img src="{wavelet_image_path}" alt="Wavelet Denoising Formula">
    </p>

    <h3>Parameters:</h3>
    <ul>
        <li><strong>Wavelet Type \( \psi \):</strong> Determines the shape of the wavelets. Common wavelets include:
            <ul>
                <li><strong>db1 (Haar):</strong> Good for detecting sharp transitions.</li>
                <li><strong>db2, db4 (Daubechies):</strong> Suitable for both smooth and sharp features.</li>
                <li><strong>sym5 (Symlets):</strong> Provides symmetry and captures smooth data trends.</li>
                <li><strong>coif1 (Coiflets):</strong> Effective for both sharp transitions and smooth trends.</li>
            </ul>
        </li>
        <li><strong>Decomposition Level \( l \):</strong> The number of levels in the wavelet decomposition. A higher level decomposes the data into coarser approximations.</li>
    </ul>

    <h3>Choosing \( \psi \) and \( l \):</h3>
    <ul>
        <li><strong>Wavelet Type \( \psi \):</strong> Lower-order wavelets (e.g., db1, db2) work well for sharp transitions, while higher-order wavelets (e.g., coif1, sym5) are better for smoother data.</li>
        <li><strong>Decomposition Level \( l \):</strong> A higher level captures larger-scale features, while a lower level focuses on fine details.</li>
    </ul>

    <h3>When to Use:</h3>
    <ul>
        <li>Wavelet denoising is effective when handling both smooth and sharp changes in the data, making it versatile for many applications like signal and image processing.</li>
        <li>Useful when the data contains multi-scale features and noise that needs to be removed across different levels of frequency components.</li>
    </ul>

    <h3>Advantages:</h3>
    <ul>
        <li><strong>Adaptive Denoising:</strong> Wavelet denoising can handle both smooth and abrupt changes in the data, making it versatile for many applications.</li>
        <li><strong>Multiscale Analysis:</strong> By decomposing data into different frequency components, it can target noise at different scales.</li>
    </ul>

    <h3>Disadvantages:</h3>
    <ul>
        <li><strong>Complexity:</strong> More computationally intensive than simpler methods like moving averages or polynomial filters.</li>
        <li><strong>Parameter Sensitivity:</strong> Requires careful selection of wavelet type and decomposition level to avoid over-smoothing or under-smoothing the data.</li>
    </ul>

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

DATA_CUTTING_HELP = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Data Cutting Help</title>
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
    <h1>Data Cutting</h1>
    <p>
        The <strong>Data Cutting</strong> feature allows you to filter your data based on a specific X-axis interval. This is useful for focusing on a particular region of interest within your dataset.
    </p>
    <h2>How to Use:</h2>
    <ol>
        <li>Enter the starting value of the X-axis interval in the <strong>X Start</strong> field.</li>
        <li>Enter the ending value of the X-axis interval in the <strong>X End</strong> field.</li>
        <li>Click the <strong>Apply</strong> button to filter the data. Only data points within the [X Start, X End] range will be retained.</li>
        <li>After applying the cut, you can choose to <strong>Save</strong> the current parameters for future use.</li>
        <li>Click <strong>Send to Data Panel</strong> to send the filtered data to the Selected Data Panel for further processing or plotting.</li>
    </ol>
    <h2>Supported Operations:</h2>
    <p>
        The Data Cutting operation filters out any data points that fall outside of the specified X-axis range. This allows you to isolate the region of the dataset that is most relevant for your analysis.
    </p>
    <h2>Important Notes:</h2>
    <ul>
        <li>Ensure that the <strong>X Start</strong> value is less than or equal to the <strong>X End</strong> value.</li>
        <li>Applying a data cut will update the current plot, displaying only the data within the specified interval.</li>
        <li>You can save multiple cutting configurations and easily switch between them or apply them as needed.</li>
    </ul>
    <h2>Advantages:</h2>
    <ul>
        <li><strong>Focused Analysis:</strong> Allows you to zoom in on specific regions of interest within the data, making it easier to analyze critical sections.</li>
        <li><strong>Streamlined Workflow:</strong> Quickly cut and save specific data intervals for comparison or further analysis.</li>
        <li><strong>Customization:</strong> Easily adjust and save different X-axis intervals without altering the original dataset.</li>
    </ul>
    <h2>When to Use:</h2>
    <ul>
        <li>When you need to focus on a specific range of X-values in your dataset for detailed analysis.</li>
        <li>When preparing data for analysis that is sensitive to certain intervals of the X-axis.</li>
        <li>When comparing specific sections of multiple datasets by cutting them to the same X-axis range.</li>
    </ul>
</body>
</html>
"""
