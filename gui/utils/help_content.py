#gui/utils/help_content.py


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



PEAK_FITTING_HELP = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Fitting Functions Help</title>
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
        hr {{
            border: none;
            height: 4px;
            background-color: #2E8B57;
            margin: 40px 0;
        }}
    </style>
</head>
<body>
    <h1>Gaussian Function</h1>
    <p>
        The Gaussian Function, also known as the normal distribution, is fundamental in various branches of science. It describes a bell-shaped curve characterized by its mean and standard deviation, playing a crucial role in modeling natural processes, experimental errors, and distributions in both classical and quantum systems.
    </p>
    <h2>Mathematical Representation:</h2>
    <p>
        The Gaussian Function is defined as:
        <br>
        \\[
        f(x) = A \\exp \\left( -\\frac{{(x - \\mu)^2}}{{2\\sigma^2}} \\right)
        \\]
        where:
        <ul>
            <li><strong>A</strong>: Amplitude, representing the peak height.</li>
            <li><strong>\\( \\mu \\)</strong>: Mean, the center position of the peak, associated with the expectation value.</li>
            <li><strong>\\( \\sigma \\)</strong>: Standard deviation, indicating the spread of the distribution. The Full Width at Half Maximum (FWHM) is related to \\( \\sigma \\) by \\( \\text{{FWHM}} = 2\\sqrt{{2\\ln 2}} \\sigma \\).</li>
        </ul>
    </p>

    <h2>Scientific Significance and Applications:</h2>
    <ul>
        <li><strong>Statistical Mechanics:</strong> Central to the Central Limit Theorem, modeling distributions of measurement errors and thermodynamic fluctuations.</li>
        <li><strong>Quantum Mechanics:</strong> Describes wavefunctions of particles in minimum uncertainty states and is integral in Fourier analysis.</li>
        <li><strong>Optics:</strong> Gaussian beams are fundamental in laser physics, describing light propagation and diffraction.</li>
        <li><strong>Spectroscopy:</strong> Models peak shapes in spectroscopic and chromatographic data, especially for instrumentally broadened lines.</li>
    </ul>

    <h2>Use Cases and Practical Considerations:</h2>
    <h3>Key Considerations:</h3>
    <ul>
        <li><strong>Symmetry Assumption:</strong> The Gaussian function assumes symmetry. Use alternative models for skewed data, such as the Lorentzian or asymmetric profiles.</li>
        <li><strong>Instrumental Effects:</strong> Recognize that observed Gaussian shapes may result from the convolution of intrinsic line shapes with the instrumental response.</li>
        <li><strong>Initial Parameter Guesses:</strong> Proper initial values for \\( \\mu \\) and \\( \\sigma \\) are crucial for convergence in fitting algorithms.</li>
    </ul>

    <h2>Mathematical Properties:</h2>
    <ul>
        <li><strong>Normalization:</strong> The Gaussian function integrates to a finite value:
            \\[
            \\int_{{-\\infty}}^{{\\infty}} \\exp \\left( -\\frac{{(x - \\mu)^2}}{{2\\sigma^2}} \\right) \\mathrm{{d}}x = \\sqrt{{2\\pi \\sigma^2}}
            \\]
            making it a valid probability distribution when normalized.
        </li>
        <li><strong>Fourier Transform:</strong> The Gaussian function's Fourier transform is also a Gaussian, which is fundamental in signal processing and quantum mechanics.</li>
    </ul>

    <h2>Advantages and Limitations:</h2>
    <h3>Advantages:</h3>
    <ul>
        <li><strong>Analytical Simplicity:</strong> The Gaussian function is straightforward to differentiate and integrate, making it analytically tractable.</li>
        <li><strong>Wide Applicability:</strong> Due to the Central Limit Theorem, Gaussian models are ubiquitous, representing various natural and experimental distributions.</li>
    </ul>
    <h3>Limitations:</h3>
    <ul>
        <li><strong>Symmetry Limitation:</strong> The Gaussian model is not suitable for asymmetric or heavy-tailed distributions. Consider models like the Voigt profile for such cases.</li>
        <li><strong>Sensitivity to Outliers:</strong> Outliers can heavily influence the fit. Consider robust fitting methods if outliers are a concern.</li>
    </ul>

    <hr>

    <h1>Lorentzian Function</h1>
    <p>
        The Lorentzian Function, also known as the Cauchy distribution in probability theory, is another fundamental function used to describe resonance phenomena and spectral line shapes. Unlike the Gaussian function, the Lorentzian has heavier tails, making it more suitable for modeling systems with more pronounced outliers or long-range interactions.
    </p>
    <h2>Mathematical Representation:</h2>
    <p>
        The Lorentzian Function is defined as:
        <br>
        \\[
        f(x) = \\frac{{A}}{{\\pi}} \\cdot \\frac{{\\Gamma / 2}}{{(x - x_0)^2 + (\\Gamma / 2)^2}}
        \\]
        where:
        <ul>
            <li><strong>A</strong>: Area under the peak.</li>
            <li><strong>\\( x_0 \\)</strong>: Position of the peak center.</li>
            <li><strong>\\( \\Gamma \\)</strong>: Full Width at Half Maximum (FWHM), representing the width of the peak.</li>
        </ul>
    </p>

    <h2>Scientific Significance and Applications:</h2>
    <ul>
        <li><strong>Resonance Phenomena:</strong> Describes the response of systems at resonance frequencies in physics and engineering.</li>
        <li><strong>Spectroscopy:</strong> Models natural linewidths in atomic and molecular spectra, especially where lifetime broadening is significant.</li>
        <li><strong>Optics:</strong> Utilized in describing the shape of spectral lines in various optical processes.</li>
        <li><strong>Quantum Mechanics:</strong> Appears in the description of certain quantum states and interactions.</li>
    </ul>

    <h2>Use Cases and Practical Considerations:</h2>
    <h3>Key Considerations:</h3>
    <ul>
        <li><strong>Heavy Tails:</strong> The Lorentzian function has heavier tails compared to the Gaussian, making it suitable for data with outliers or long-range dependencies.</li>
        <li><strong>Peak Overlap:</strong> In cases where multiple resonances are close together, Lorentzian profiles can overlap, requiring careful fitting strategies.</li>
        <li><strong>Parameter Interpretation:</strong> Understanding the physical meaning of parameters \\( x_0 \\) and \\( \\Gamma \\) is crucial for accurate modeling.</li>
    </ul>

    <h2>Mathematical Properties:</h2>
    <ul>
        <li><strong>Normalization:</strong> The Lorentzian function is properly normalized over its entire range:
            \\[
            \\int_{{-\\infty}}^{{\\infty}} \\frac{{1}}{{\\pi}} \\cdot \\frac{{\\Gamma / 2}}{{(x - x_0)^2 + (\\Gamma / 2)^2}} \\, \\mathrm{{d}}x = 1
            \\]
        </li>
        <li><strong>Fourier Transform:</strong> The Fourier transform of a Lorentzian function is an exponential decay, which is significant in signal processing and optics.</li>
    </ul>

    <h2>Advantages and Limitations:</h2>
    <h3>Advantages:</h3>
    <ul>
        <li><strong>Heavy Tails:</strong> Better models phenomena with significant outliers or long-range interactions compared to Gaussian functions.</li>
        <li><strong>Simplicity:</strong> The Lorentzian function is mathematically simple and easy to work with in analytical and numerical calculations.</li>
    </ul>
    <h3>Limitations:</h3>
    <ul>
        <li><strong>Non-Normalizable in Probability Theory:</strong> Unlike Gaussian distributions, Lorentzian distributions do not have a finite mean or variance, limiting their use in certain statistical applications.</li>
        <li><strong>Sensitivity to Parameter Estimation:</strong> Accurate fitting requires precise estimation of parameters, especially in the presence of overlapping peaks.</li>
    </ul>

    <hr>

    <h1>Voigt Function</h1>
    <p>
        The Voigt Function is a convolution of a Gaussian and a Lorentzian function. It is widely used to model spectral line shapes in spectroscopy and accounts for both Doppler and pressure broadening effects, making it suitable for more complex line shape modeling.
    </p>
    <h2>Mathematical Representation:</h2>
    <p>
        The Voigt Function does not have a simple closed-form expression and is defined as the convolution:
        <br>
        \\[
        V(x; \\sigma, \\Gamma) = \\int_{{-\\infty}}^{{\\infty}} G(x'; \\sigma) L(x - x'; \\Gamma) \\, \\mathrm{{d}}x'
        \\]
        where:
        <ul>
            <li><strong>G</strong>: Gaussian component with standard deviation \\( \\sigma \\).</li>
            <li><strong>L</strong>: Lorentzian component with width parameter \\( \\Gamma \\).</li>
        </ul>
    </p>

    <h2>Scientific Significance and Applications:</h2>
    <ul>
        <li><strong>Spectroscopy:</strong> The Voigt profile is crucial for accurately modeling spectral lines, especially in the presence of both Doppler and pressure broadening.</li>
        <li><strong>Astrophysics:</strong> Used to model absorption and emission lines in stellar and interstellar spectra.</li>
        <li><strong>Analytical Chemistry:</strong> Essential for interpreting spectroscopic data from complex samples.</li>
    </ul>

    <h2>Use Cases and Practical Considerations:</h2>
    <h3>Key Considerations:</h3>
    <ul>
        <li><strong>Computational Complexity:</strong> Calculating the Voigt profile requires numerical methods, making it more computationally intensive than Gaussian or Lorentzian profiles.</li>
        <li><strong>Parameter Interplay:</strong> The parameters \\( \\sigma \\) and \\( \\Gamma \\) both influence the line shape, requiring careful fitting to accurately represent physical phenomena.</li>
    </ul>

    <h2>Mathematical Properties:</h2>
    <ul>
        <li><strong>Normalization:</strong> The Voigt function is normalized, but the convolution complicates the expression, requiring numerical methods for accurate calculations.</li>
        <li><strong>Asymptotic Behavior:</strong> The Voigt profile behaves like a Lorentzian far from the center and like a Gaussian near the peak.</li>
    </ul>

    <h2>Advantages and Limitations:</h2>
    <h3>Advantages:</h3>
    <ul>
        <li><strong>Comprehensive Modeling:</strong> Captures both Gaussian and Lorentzian broadening effects, making it ideal for complex line shapes.</li>
        <li><strong>Versatility:</strong> Widely used in spectroscopy and astrophysics for accurate data interpretation.</li>
    </ul>
    <h3>Limitations:</h3>
    <ul>
        <li><strong>Computational Demand:</strong> Requires numerical integration, making it less efficient than simpler models.</li>
        <li><strong>Parameter Sensitivity:</strong> Accurate parameter estimation can be challenging due to the interplay between \\( \\sigma \\) and \\( \\Gamma \\).</li>
    </ul>

    <hr>

    <h1>Pseudo-Voigt Function</h1>
    <p>
        The Pseudo-Voigt Function is an approximation of the Voigt profile, expressed as a linear combination of a Gaussian and a Lorentzian function. It provides a simpler and computationally less demanding alternative for modeling spectral line shapes while still capturing the essential features of both broadening mechanisms.
    </p>
    <h2>Mathematical Representation:</h2>
    <p>
        The Pseudo-Voigt Function is given by:
        <br>
        \\[
        PV(x; \\sigma, \\Gamma) = \\eta L(x; \\Gamma) + (1 - \\eta) G(x; \\sigma)
        \\]
        where:
        <ul>
            <li><strong>\\( \\eta \\)</strong>: Mixing parameter (ranging from 0 to 1) that determines the relative contribution of the Lorentzian and Gaussian components.</li>
            <li><strong>L</strong>: Lorentzian component with width \\( \\Gamma \\).</li>
            <li><strong>G</strong>: Gaussian component with standard deviation \\( \\sigma \\).</li>
        </ul>
    </p>

    <h2>Scientific Significance and Applications:</h2>
    <ul>
        <li><strong>Spectroscopy:</strong> The Pseudo-Voigt profile is commonly used for fitting experimental spectra where computational efficiency is essential.</li>
        <li><strong>Material Science:</strong> Useful for analyzing diffraction patterns, particularly in X-ray and neutron diffraction.</li>
        <li><strong>Astrophysics:</strong> Applied to approximate spectral line shapes in stellar and interstellar studies.</li>
    </ul>

    <h2>Use Cases and Practical Considerations:</h2>
    <h3>Key Considerations:</h3>
    <ul>
        <li><strong>Approximation Accuracy:</strong> The Pseudo-Voigt function is an approximation, and its accuracy depends on the chosen value of \\( \\eta \\). While simpler than the Voigt profile, it may not perfectly match all line shapes.</li>
        <li><strong>Parameter Estimation:</strong> Careful estimation of \\( \\sigma \\), \\( \\Gamma \\), and \\( \\eta \\) is necessary to achieve a good fit, especially when distinguishing between Gaussian and Lorentzian contributions.</li>
    </ul>

    <h2>Mathematical Properties:</h2>
    <ul>
        <li><strong>Normalization:</strong> The Pseudo-Voigt function is normalized, but the linear combination introduces slight deviations from the true Voigt profile, depending on \\( \\eta \\).</li>
        <li><strong>Behavior:</strong> The Pseudo-Voigt profile transitions smoothly between a Gaussian and Lorentzian shape as \\( \\eta \\) varies from 0 to 1.</li>
    </ul>

    <h2>Advantages and Limitations:</h2>
    <h3>Advantages:</h3>
    <ul>
        <li><strong>Computational Efficiency:</strong> Easier to compute than the true Voigt profile, making it suitable for real-time data fitting.</li>
        <li><strong>Flexible Approximation:</strong> Provides a reasonable fit for a wide range of spectral lines with fewer computational resources.</li>
    </ul>
    <h3>Limitations:</h3>
    <ul>
        <li><strong>Approximation Limitations:</strong> The Pseudo-Voigt function may not perfectly replicate the Voigt profile, particularly for complex or asymmetric lines.</li>
        <li><strong>Mixing Parameter Dependence:</strong> The accuracy of the approximation depends heavily on the correct choice of \\( \\eta \\), which may require fine-tuning.</li>
    </ul>

    <hr>

    <h1>Exponential Gaussian Function</h1>
    <p>
        The Exponential Gaussian Function is a modification of the Gaussian function that introduces an exponential decay component. It is particularly useful for modeling asymmetric peak shapes that are commonly observed in various types of spectroscopy and chromatography.
    </p>
    <h2>Mathematical Representation:</h2>
    <p>
        The Exponential Gaussian Function is expressed as:
        <br>
        \\[
        f(x) = A \\exp \\left( -\\frac{{(x - \\mu)^2}}{{2\\sigma^2}} \\right) \\times \\exp \\left( -\\lambda (x - \\mu) \\right)
        \\]
        for \\( x \\geq \\mu \\), where:
        <ul>
            <li><strong>A</strong>: Amplitude, representing the peak height.</li>
            <li><strong>\\( \\mu \\)</strong>: Mean or center of the Gaussian component.</li>
            <li><strong>\\( \\sigma \\)</strong>: Standard deviation of the Gaussian component, controlling the peak width.</li>
            <li><strong>\\( \\lambda \\)</strong>: Exponential decay factor, introducing asymmetry into the peak shape.</li>
        </ul>
    </p>

    <h2>Scientific Significance and Applications:</h2>
    <ul>
        <li><strong>Chromatography:</strong> Used to model the tailing of peaks due to interactions between analytes and the stationary phase.</li>
        <li><strong>Fluorescence Spectroscopy:</strong> Applied to describe the emission spectra of fluorescent molecules with asymmetric decay.</li>
        <li><strong>Environmental Analysis:</strong> Useful for fitting data where asymmetric distributions arise from non-uniform physical or chemical processes.</li>
    </ul>

    <h2>Use Cases and Practical Considerations:</h2>
    <h3>Key Considerations:</h3>
    <ul>
        <li><strong>Asymmetry Modeling:</strong> The parameter \\( \\lambda \\) introduces asymmetry to the otherwise symmetric Gaussian profile, making it suitable for skewed peak shapes.</li>
        <li><strong>Parameter Estimation:</strong> Accurate estimation of \\( \\lambda \\), \\( \\mu \\), and \\( \\sigma \\) is crucial to appropriately capture the peak's asymmetry and width.</li>
    </ul>

    <h2>Mathematical Properties:</h2>
    <ul>
        <li><strong>Asymmetry:</strong> The exponential component causes a tailing effect, resulting in a peak that is not symmetric around \\( \\mu \\).</li>
        <li><strong>Combination of Exponential and Gaussian:</strong> The function smoothly transitions from a Gaussian profile near the peak center to an exponentially decaying tail.</li>
    </ul>

    <h2>Advantages and Limitations:</h2>
    <h3>Advantages:</h3>
    <ul>
        <li><strong>Asymmetric Peak Modeling:</strong> Ideal for fitting peaks that exhibit tailing or skewness, commonly seen in experimental data.</li>
        <li><strong>Flexible Parameterization:</strong> Provides more flexibility compared to a standard Gaussian function, allowing for better fits to real-world data.</li>
    </ul>
    <h3>Limitations:</h3>
    <ul>
        <li><strong>Increased Complexity:</strong> The addition of the exponential component introduces more parameters, which may complicate the fitting process.</li>
        <li><strong>Sensitivity to Initial Guesses:</strong> Fitting algorithms may require good initial parameter estimates for convergence, especially for complex data sets.</li>
    </ul>

<hr>

<h1>Split Gaussian Function</h1>
<p>
    The Split Gaussian Function is a variation of the standard Gaussian function, where the standard deviation is different on either side of the peak, allowing for an asymmetric peak shape. This function is particularly useful in modeling skewed distributions where the spread differs on the left and right sides of the mean.
</p>
<h2>Mathematical Representation:</h2>
<p>
    The Split Gaussian Function is defined as:
    <br>
    \\[
    f(x) = \\begin{{cases}} 
    A \\exp \\left( -\\frac{{(x - \\mu)^2}}{{2\\sigma_1^2}} \\right) & \\text{{for }} x < \\mu \\\\
    A \\exp \\left( -\\frac{{(x - \\mu)^2}}{{2\\sigma_2^2}} \\right) & \\text{{for }} x \\geq \\mu
    \\end{{cases}}
    \\]
    where:
    <ul>
        <li><strong>A</strong>: Amplitude, representing the peak height.</li>
        <li><strong>\\( \\mu \\)</strong>: Mean or center of the distribution.</li>
        <li><strong>\\( \\sigma_1 \\)</strong>: Standard deviation for \\( x < \\mu \\), controlling the spread on the left side of the peak.</li>
        <li><strong>\\( \\sigma_2 \\)</strong>: Standard deviation for \\( x \\geq \\mu \\), controlling the spread on the right side of the peak.</li>
    </ul>
</p>

<h2>Scientific Significance and Applications:</h2>
<ul>
    <li><strong>Spectroscopy:</strong> Useful for modeling asymmetric spectral lines that cannot be described by a standard Gaussian profile.</li>
    <li><strong>Geophysical Data:</strong> Applied in analyzing asymmetric geological distributions, such as earthquake magnitudes or sedimentary layers.</li>
    <li><strong>Biostatistics:</strong> Used for data analysis where asymmetric biological distributions are observed.</li>
</ul>

<h2>Use Cases and Practical Considerations:</h2>
<h3>Key Considerations:</h3>
<ul>
    <li><strong>Asymmetry Control:</strong> The parameters \\( \\sigma_1 \\) and \\( \\sigma_2 \\) allow for precise control over the asymmetry of the peak, making it adaptable to various data shapes.</li>
    <li><strong>Parameter Initialization:</strong> Good initial guesses for \\( \\sigma_1 \\) and \\( \\sigma_2 \\) are important to achieve successful and efficient fitting.</li>
</ul>

<h2>Mathematical Properties:</h2>
<ul>
    <li><strong>Piecewise Definition:</strong> The function is defined in two parts, each with a different standard deviation, leading to a smooth but asymmetric peak.</li>
    <li><strong>Continuity:</strong> The Split Gaussian is continuous at \\( \\mu \\), ensuring there are no jumps or discontinuities in the peak.</li>
</ul>

<h2>Advantages and Limitations:</h2>
<h3>Advantages:</h3>
<ul>
    <li><strong>Asymmetric Peak Fitting:</strong> Ideal for data with asymmetry, providing a better fit than a symmetric Gaussian function.</li>
    <li><strong>Flexible Shape Adjustment:</strong> Allows independent control over the spread on both sides of the peak, making it versatile for different applications.</li>
</ul>
<h3>Limitations:</h3>
<ul>
    <li><strong>Increased Parameter Count:</strong> The need for two standard deviations adds complexity, making the fitting process more involved.</li>
    <li><strong>Potential Overfitting:</strong> The flexibility of the model can lead to overfitting if not used with caution, especially on noisy data.</li>
</ul>

      <hr>

<h1>Split Lorentzian Function</h1>
<p>
    The Split Lorentzian Function is a modified version of the standard Lorentzian function, with different width parameters on either side of the peak. This variation allows for the modeling of asymmetric peak shapes where the line width differs on the left and right sides of the peak center.
</p>
<h2>Mathematical Representation:</h2>
<p>
    The Split Lorentzian Function is defined as:
    <br>
    \\[
    f(x) = \\begin{{cases}} 
    \\frac{{A}}{{\\pi}} \\cdot \\frac{{\\Gamma_1 / 2}}{{(x - x_0)^2 + (\\Gamma_1 / 2)^2}} & \\text{{for }} x < x_0 \\\\
    \\frac{{A}}{{\\pi}} \\cdot \\frac{{\\Gamma_2 / 2}}{{(x - x_0)^2 + (\\Gamma_2 / 2)^2}} & \\text{{for }} x \\geq x_0
    \\end{{cases}}
    \\]
    where:
    <ul>
        <li><strong>A</strong>: Amplitude, representing the peak height.</li>
        <li><strong>\\( x_0 \\)</strong>: Center of the peak.</li>
        <li><strong>\\( \\Gamma_1 \\)</strong>: Width parameter for \\( x < x_0 \\), controlling the spread on the left side of the peak.</li>
        <li><strong>\\( \\Gamma_2 \\)</strong>: Width parameter for \\( x \\geq x_0 \\), controlling the spread on the right side of the peak.</li>
    </ul>
</p>

<h2>Scientific Significance and Applications:</h2>
<ul>
    <li><strong>Spectroscopy:</strong> Useful for modeling asymmetric spectral features, such as line shapes influenced by inhomogeneous broadening or environmental factors.</li>
    <li><strong>Seismology:</strong> Applied in modeling asymmetric waveforms generated by geological phenomena.</li>
    <li><strong>Material Science:</strong> Useful for characterizing resonance phenomena in materials with non-uniform properties.</li>
</ul>

<h2>Use Cases and Practical Considerations:</h2>
<h3>Key Considerations:</h3>
<ul>
    <li><strong>Asymmetry Control:</strong> The parameters \\( \\Gamma_1 \\) and \\( \\Gamma_2 \\) provide flexibility in modeling asymmetric line shapes, making the function adaptable to various data sets.</li>
    <li><strong>Initial Parameter Estimation:</strong> Accurate initial values for \\( \\Gamma_1 \\) and \\( \\Gamma_2 \\) can significantly improve the efficiency of fitting algorithms.</li>
</ul>

<h2>Mathematical Properties:</h2>
<ul>
    <li><strong>Piecewise Definition:</strong> The function is defined differently on either side of the peak, allowing for an asymmetric shape while remaining continuous at \\( x_0 \\).</li>
    <li><strong>Continuity:</strong> The Split Lorentzian Function is continuous at \\( x_0 \\), ensuring there are no abrupt changes in the peak.</li>
</ul>

<h2>Advantages and Limitations:</h2>
<h3>Advantages:</h3>
<ul>
    <li><strong>Asymmetric Line Shape Modeling:</strong> Ideal for data sets where the peak shape is asymmetric due to different broadening mechanisms on either side of the peak.</li>
    <li><strong>Versatile Application:</strong> Suitable for various scientific fields, including spectroscopy, seismology, and material characterization.</li>
</ul>
<h3>Limitations:</h3>
<ul>
    <li><strong>Increased Complexity:</strong> The addition of separate width parameters increases the complexity of the fitting process.</li>
    <li><strong>Risk of Overfitting:</strong> The flexibility of the model may lead to overfitting, especially when applied to noisy or insufficiently sampled data.</li>
</ul>
  
</body>
</html>
"""

POLYNOMIAL_FITTING_HELP = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Polynomial Fitting Help</title>
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
        hr {{
            border: none;
            height: 4px;
            background-color: #2E8B57;
            margin: 40px 0;
        }}
    </style>
</head>
<body>
    <h1>Linear Fitting</h1>
    <p>
        Linear fitting, also known as linear regression, is a fundamental statistical method used to model the relationship between two variables by fitting a linear equation to the observed data. It is widely used in various scientific fields to identify trends and make predictions.
    </p>
    <h2>Mathematical Representation:</h2>
    <p>
        The equation of a straight line is given by:
        <br>
        \\[
        y = mx + b
        \\]
        where:
        <ul>
            <li><strong>y</strong>: Dependent variable.</li>
            <li><strong>x</strong>: Independent variable.</li>
            <li><strong>m</strong>: Slope of the line, representing the rate of change of y with respect to x.</li>
            <li><strong>b</strong>: Intercept, the value of y when x = 0.</li>
        </ul>
        The goal of linear fitting is to determine the optimal values of \\( m \\) and \\( b \\) that minimize the difference between the observed data points and the predicted values given by the line. This is typically achieved using the method of least squares.
    </p>

    <h2>Least Squares Method:</h2>
    <p>
        The least squares method minimizes the sum of the squared differences between the observed values \\( y_i \\) and the predicted values \\( \\hat{{y}}_i \\):
        <br>
        \\[
        S = \\sum_{{i=1}}^n (y_i - (mx_i + b))^2
        \\]
        where:
        <ul>
            <li><strong>S</strong>: Sum of squared residuals.</li>
            <li><strong>n</strong>: Number of data points.</li>
            <li><strong>y_i</strong>: Observed value at point i.</li>
            <li><strong>x_i</strong>: Independent variable value at point i.</li>
            <li><strong>\\( \\hat{{y}}_i \\)</strong>: Predicted value at point i using the fitted line.</li>
        </ul>
        By minimizing \\( S \\), we obtain the best-fit parameters \\( m \\) and \\( b \\). The least squares solution can be derived analytically, yielding:
        <br>
        \\[
        m = \\frac{{n \\sum x_i y_i - \\sum x_i \\sum y_i}}{{n \\sum x_i^2 - (\\sum x_i)^2}}
        \\]
        \\[
        b = \\frac{{\\sum y_i - m \\sum x_i}}{{n}}
        \\]
    </p>

    <h2>Scientific Significance and Applications:</h2>
    <ul>
        <li><strong>Physics:</strong> Used to describe relationships between variables, such as velocity and time or force and displacement.</li>
        <li><strong>Economics:</strong> Applied in modeling economic trends, like the relationship between price and demand.</li>
        <li><strong>Biology:</strong> Used to model growth rates and analyze the correlation between biological factors.</li>
    </ul>

    <h2>Advantages and Limitations:</h2>
    <h3>Advantages:</h3>
    <ul>
        <li><strong>Simplicity:</strong> Linear fitting is easy to implement and interpret, making it suitable for initial data analysis.</li>
        <li><strong>Predictive Power:</strong> Useful for making predictions when the relationship between variables is approximately linear.</li>
    </ul>
    <h3>Limitations:</h3>
    <ul>
        <li><strong>Linearity Assumption:</strong> Not suitable for data with nonlinear relationships.</li>
        <li><strong>Sensitivity to Outliers:</strong> Outliers can significantly affect the fitted line, leading to incorrect conclusions.</li>
    </ul>

    <hr>

    <h1>Polynomial Fitting</h1>
    <p>
        Polynomial fitting extends linear fitting by using a polynomial equation to model the relationship between variables. This method is used when data shows a nonlinear trend, and a straight line cannot adequately capture the pattern.
    </p>
    <h2>Mathematical Representation:</h2>
    <p>
        A polynomial of degree \\( n \\) is given by:
        <br>
        \\[
        y = a_0 + a_1x + a_2x^2 + \\dots + a_nx^n
        \\]
        where:
        <ul>
            <li><strong>y</strong>: Dependent variable.</li>
            <li><strong>x</strong>: Independent variable.</li>
            <li><strong>a_0, a_1, \\dots, a_n</strong>: Coefficients of the polynomial, which are determined through fitting.</li>
            <li><strong>n</strong>: Degree of the polynomial, representing the highest power of x.</li>
        </ul>
        The goal is to find the coefficients \\( a_0, a_1, \\dots, a_n \\) that best fit the data using the least squares method, similar to linear fitting but generalized for higher-degree polynomials.
    </p>

    <h2>Least Squares Method for Polynomials:</h2>
    <p>
        The objective is to minimize the sum of squared residuals:
        <br>
        \\[
        S = \\sum_{{i=1}}^n (y_i - (a_0 + a_1x_i + a_2x_i^2 + \\dots + a_nx_i^n))^2
        \\]
        The system of equations obtained from this minimization problem can be solved using numerical techniques, such as matrix algebra or specialized algorithms, to determine the coefficients \\( a_0, a_1, \\dots, a_n \\).
    </p>

    <h2>Scientific Significance and Applications:</h2>
    <ul>
        <li><strong>Physics:</strong> Polynomial fitting is used to model complex phenomena, such as the motion of projectiles or the behavior of materials under stress.</li>
        <li><strong>Astronomy:</strong> Applied in fitting orbits and trajectories of celestial objects.</li>
        <li><strong>Engineering:</strong> Used to approximate curves in structural analysis and control systems.</li>
    </ul>

    <h2>Advantages and Limitations:</h2>
    <h3>Advantages:</h3>
    <ul>
        <li><strong>Flexible Modeling:</strong> Can capture complex, nonlinear relationships in data by adjusting the polynomial degree.</li>
        <li><strong>Improved Fit:</strong> Higher-degree polynomials can provide a better fit for data with curvature or oscillatory behavior.</li>
    </ul>
    <h3>Limitations:</h3>
    <ul>
        <li><strong>Overfitting:</strong> Using a polynomial degree that is too high can lead to overfitting, where the model captures noise rather than the underlying trend.</li>
        <li><strong>Instability:</strong> High-degree polynomials can exhibit large oscillations between data points, making the model sensitive to small changes in data.</li>
        <li><strong>Computational Complexity:</strong> Polynomial fitting can be computationally intensive, especially for large data sets and high-degree polynomials.</li>
    </ul>
</body>
</html>
"""

CUSTOM_FITTING_HELP = f"""

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Custom Fitting Help</title>
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
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        hr {{
            border: none;
            height: 4px;
            background-color: #2E8B57;
            margin: 40px 0;
        }}
    </style>
</head>
<body>
    <h1>Custom Fitting</h1>
    <p>
        Custom fitting allows for flexible modeling of data using user-defined functions and parameters. By specifying an appropriate mathematical model and choosing initial parameter values, users can perform highly customized fits to their data using a variety of optimization techniques.
    </p>
    <h2>Mathematical Model:</h2>
    <p>
        A custom fitting model can be expressed as:
        <br>
        \\[
        y = f(x; a_1, a_2, \\dots, a_n)
        \\]
        where:
        <ul>
            <li><strong>y</strong>: Dependent variable.</li>
            <li><strong>x</strong>: Independent variable.</li>
            <li><strong>f</strong>: User-defined function that describes the relationship between x and y.</li>
            <li><strong>a_1, a_2, \\dots, a_n</strong>: Model parameters to be optimized.</li>
        </ul>
    </p>

    <h2>Parameter Settings:</h2>
    <p>
        For each parameter, users can specify:
    </p>
    <table>
        <thead>
            <tr>
                <th>Parameter</th>
                <th>Initial Guess</th>
                <th>Min</th>
                <th>Max</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>a_1</strong></td>
                <td>Initial value for a_1</td>
                <td>Minimum allowable value</td>
                <td>Maximum allowable value</td>
            </tr>
            <tr>
                <td><strong>a_2</strong></td>
                <td>Initial value for a_2</td>
                <td>Minimum allowable value</td>
                <td>Maximum allowable value</td>
            </tr>
            <!-- Add more rows as needed -->
        </tbody>
    </table>

    <h2>Optimization Methods:</h2>
    <h3>1. Leastsq</h3>
    <p>
        <strong>Leastsq</strong> is based on the Levenberg-Marquardt algorithm, which is an efficient method for minimizing the sum of the squares of nonlinear functions.
    </p>
    <h4>Mathematical Description:</h4>
    <p>
        The algorithm iteratively updates the parameters to minimize the sum of squared residuals:
        <br>
        \\[
        S(\\mathbf{{a}}) = \\sum_{{i=1}}^n \\left( y_i - f(x_i; \\mathbf{{a}}) \\right)^2
        \\]
        The parameter update at each iteration is given by:
        <br>
        \\[
        \\mathbf{{a}}_{{k+1}} = \\mathbf{{a}}_k - (\\mathbf{{J}}^\\mathrm{{T}} \\mathbf{{J}} + \\lambda \\mathbf{{I}})^{{-1}} \\mathbf{{J}}^\\mathrm{{T}} \\mathbf{{r}}
        \\]
        where:
        <ul>
            <li>\\(\\mathbf{{a}}_k\\): Parameter vector at iteration \\(k\\).</li>
            <li>\\(\\mathbf{{J}}\\): Jacobian matrix of partial derivatives \\(J_{{ij}} = \\frac{{\\partial r_i}}{{\\partial a_j}}\\).</li>
            <li>\\(\\mathbf{{r}}\\): Residual vector \\(r_i = y_i - f(x_i; \\mathbf{{a}}_k)\\).</li>
            <li>\\(\\lambda\\): Damping parameter that controls the step size.</li>
            <li>\\(\\mathbf{{I}}\\): Identity matrix.</li>
        </ul>
        <ul>
            <li><strong>When to Use:</strong> Ideal for problems with smooth, continuous functions and well-behaved derivatives.</li>
            <li><strong>Advantages:</strong> Fast convergence and well-suited for least-squares problems.</li>
            <li><strong>Disadvantages:</strong> Sensitive to initial guesses; may converge to local minima if the initial parameters are not chosen carefully.</li>
        </ul>
    </p>

    <h3>2. Least_squares</h3>
    <p>
        <strong>Least_squares</strong> is a more flexible optimization method that supports bounds on parameters and can handle sparse matrices. It can use different algorithms like Trust Region Reflective or Dogleg methods.
    </p>
    <h4>Mathematical Description:</h4>
    <p>
        The objective is to minimize the sum of squared residuals subject to parameter bounds:
        <br>
        \\[
        \\min_{{\\mathbf{{a}}}} \\frac{{1}}{{2}} \\| \\mathbf{{r}}(\\mathbf{{a}}) \\|^2 \\quad \\text{{subject to}} \\quad \\mathbf{{a}}_{{\\text{{min}}}} \\leq \\mathbf{{a}} \\leq \\mathbf{{a}}_{{\\text{{max}}}}
        \\]
        where:
        <ul>
            <li>\\(\\mathbf{{r}}(\\mathbf{{a}}) = [ y_1 - f(x_1; \\mathbf{{a}}), \\dots, y_n - f(x_n; \\mathbf{{a}}) ]^\\mathrm{{T}}\\): Residual vector.</li>
            <li>\\(\\mathbf{{a}}_{{\\text{{min}}}}, \\mathbf{{a}}_{{\\text{{max}}}}\\): Lower and upper bounds on parameters.</li>
        </ul>
        The Trust Region Reflective algorithm solves a subproblem at each iteration:
        <br>
        \\[
        \\min_{{\\mathbf{{p}}}} \\frac{{1}}{{2}} \\| \\mathbf{{J}} \\mathbf{{p}} + \\mathbf{{r}} \\|^2 \\quad \\text{{subject to}} \\quad \\| \\mathbf{{D}} \\mathbf{{p}} \\| \\leq \\Delta
        \\]
        where:
        <ul>
            <li>\\(\\mathbf{{p}}\\): Parameter update vector.</li>
            <li>\\(\\mathbf{{D}}\\): Diagonal scaling matrix.</li>
            <li>\\(\\Delta\\): Trust-region radius.</li>
        </ul>
        <ul>
            <li><strong>When to Use:</strong> Useful when parameter bounds are needed or for problems with additional constraints.</li>
            <li><strong>Advantages:</strong> Robust, with support for bounds and various loss functions.</li>
            <li><strong>Disadvantages:</strong> Slightly slower than leastsq for simple problems; may require more computational resources.</li>
        </ul>
    </p>

    <h3>3. Differential Evolution</h3>
    <p>
        <strong>Differential Evolution</strong> is a stochastic, population-based optimization algorithm. It is useful for global optimization in nonlinear and non-differentiable continuous spaces.
    </p>
    <h4>Mathematical Description:</h4>
    <p>
        Differential Evolution optimizes a population of candidate solutions using operations of mutation, crossover, and selection:
        <ul>
            <li><strong>Mutation:</strong> For each individual \\(\\mathbf{{x}}_i\\), a mutant vector is generated:
                \\[
                \\mathbf{{v}}_i = \\mathbf{{x}}_{{r1}} + F \\cdot (\\mathbf{{x}}_{{r2}} - \\mathbf{{x}}_{{r3}})
                \\]
                where \\(r1, r2, r3\\) are distinct random indices and \\(F\\) is the mutation factor.</li>
            <li><strong>Crossover:</strong> The trial vector \\(\\mathbf{{u}}_i\\) is formed by mixing the mutant vector and the target vector:
                \\[
                u_{{ij}} = \\begin{{cases}}
                    v_{{ij}} & \\text{{if }} rand_j(0,1) \\leq CR \\text{{ or }} j = j_{{\\text{{rand}}}} \\\\
                    x_{{ij}} & \\text{{otherwise}}
                \\end{{cases}}
                \\]
                where \\(CR\\) is the crossover probability and \\(j_{{\\text{{rand}}}}\\) ensures at least one parameter is taken from the mutant vector.</li>
            <li><strong>Selection:</strong> The trial vector replaces the target vector if it yields a better objective function value:
                \\[
                \\mathbf{{x}}_i^{{(t+1)}} = \\begin{{cases}}
                    \\mathbf{{u}}_i & \\text{{if }} S(\\mathbf{{u}}_i) \\leq S(\\mathbf{{x}}_i) \\\\
                    \\mathbf{{x}}_i & \\text{{otherwise}}
                \\end{{cases}}
                \\]
            </li>
        </ul>
        <ul>
            <li><strong>When to Use:</strong> Suitable for problems with many local minima or unknown derivative properties.</li>
            <li><strong>Advantages:</strong> Effective for global optimization; does not require derivatives.</li>
            <li><strong>Disadvantages:</strong> Computationally expensive; slower convergence compared to gradient-based methods.</li>
        </ul>
    </p>

    <h3>4. Brute Force</h3>
    <p>
        <strong>Brute Force</strong> performs a grid search over a specified parameter space, evaluating the objective function at each grid point.
    </p>
    <h4>Mathematical Description:</h4>
    <p>
        The method exhaustively searches over a grid of parameter values:
        <br>
        \\[
        \\mathbf{{a}}_{{\\text{{opt}}}} = \\arg \\min_{{\\mathbf{{a}} \\in \\mathcal{{A}}}} S(\\mathbf{{a}})
        \\]
        where:
        <ul>
            <li>\\(\\mathcal{{A}}\\): Set of all parameter combinations defined by the grid.</li>
            <li>\\(S(\\mathbf{{a}})\\): Objective function, usually the sum of squared residuals.</li>
        </ul>
        <ul>
            <li><strong>When to Use:</strong> Useful when the parameter space is small or when a global search is necessary.</li>
            <li><strong>Advantages:</strong> Simple and easy to implement; guarantees finding the global minimum within the search space.</li>
            <li><strong>Disadvantages:</strong> Highly inefficient for large parameter spaces; computationally expensive.</li>
        </ul>
    </p>

    <h3>5. Basin Hopping</h3>
    <p>
        <strong>Basin Hopping</strong> is a global optimization technique that combines random perturbation with local minimization. It is useful for rugged landscapes with many local minima.
    </p>
    <h4>Mathematical Description:</h4>
    <p>
        Basin Hopping performs the following steps iteratively:
        <ul>
            <li><strong>Perturbation:</strong> Randomly perturb the current parameters:
                \\[
                \\mathbf{{a}}' = \\mathbf{{a}} + \\delta
                \\]
                where \\(\\delta\\) is a random displacement.</li>
            <li><strong>Local Minimization:</strong> Perform a local optimization starting from \\(\\mathbf{{a}}'\\) to find a nearby local minimum \\(\\mathbf{{a}}''\\).</li>
            <li><strong>Acceptance Criterion:</strong> Accept or reject the new point based on the Metropolis criterion:
                \\[
                P = \\begin{{cases}}
                    1 & \\text{{if }} \\Delta S \\leq 0 \\\\
                    \\exp\\left( -\\frac{{\\Delta S}}{{k_B T}} \\right) & \\text{{if }} \\Delta S > 0
                \\end{{cases}}
                \\]
                where \\(\\Delta S = S(\\mathbf{{a}}'') - S(\\mathbf{{a}})\\), \\(k_B\\) is Boltzmann's constant, and \\(T\\) is a temperature parameter.</li>
        </ul>
        <ul>
            <li><strong>When to Use:</strong> Ideal for problems with multiple local minima and a rugged objective function landscape.</li>
            <li><strong>Advantages:</strong> Effective for finding global minima; can escape local traps.</li>
            <li><strong>Disadvantages:</strong> May require careful tuning of parameters; computationally intensive.</li>
        </ul>
    </p>

    <h2>Max Iterations:</h2>
    <p>
        The <strong>Max Iterations</strong> setting specifies the maximum number of iterations an optimization algorithm will perform. This acts as a stopping criterion to prevent the algorithm from running indefinitely.
        <ul>
            <li><strong>Purpose:</strong> To control the computational time and resources used by the fitting process.</li>
            <li><strong>Considerations:</strong> Choosing too low a value may result in an incomplete optimization, while too high a value can lead to unnecessary computation.</li>
        </ul>
    </p>
</body>
</html>
"""

LOG_EXP_POWER_HELP = f"""

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Logarithmic, Exponential, and Power Law Fitting Help</title>
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
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        hr {{
            border: none;
            height: 4px;
            background-color: #2E8B57;
            margin: 40px 0;
        }}
    </style>
</head>
<body>
    <h1>Logarithmic, Exponential, and Power Law Fitting</h1>
    <p>
        This section provides an overview of fitting models commonly used in data analysis: logarithmic, exponential, and power law. Each model is suited to different types of data patterns and offers a mathematical framework for understanding the underlying relationships.
    </p>

    <h2>1. Logarithmic Function</h2>
    <p>
        <strong>Equation:</strong> \\[
        y = a \cdot \ln(x) + b
        \\]
    </p>
    <p>
        <strong>Parameters:</strong>
        <ul>
            <li><strong>a</strong>: Scaling factor.</li>
            <li><strong>b</strong>: Offset.</li>
        </ul>
    </p>
    <h4>When to Use:</h4>
    <p>Appropriate for data that increases rapidly at first and then levels off.</p>
    <h4>Advantages:</h4>
    <p>Useful for modeling phenomena with diminishing returns.</p>
    <h4>Disadvantages:</h4>
    <p>Only applicable for positive x-values and may be sensitive to scaling and offset adjustments.</p>

    <h2>2. Exponential Function</h2>
    <p>
        <strong>Equation:</strong> \\[
        y = a \cdot e^{{b.x}} + c
        \\]
    </p>
    <p>
        <strong>Parameters:</strong>
        <ul>
            <li><strong>a</strong>: Amplitude.</li>
            <li><strong>b</strong>: Growth/decay rate.</li>
            <li><strong>c</strong>: Offset.</li>
        </ul>
    </p>
    <h4>When to Use:</h4>
    <p>Suitable for data exhibiting exponential growth or decay, such as population models or radioactive decay.</p>
    <h4>Advantages:</h4>
    <p>Effective for capturing exponential trends in data.</p>
    <h4>Disadvantages:</h4>
    <p>Sensitive to outliers and can become unstable if parameters are not initialized appropriately.</p>

    <h2>3. Power Law Function</h2>
    <p>
        <strong>Equation:</strong> \\[
        y = a \cdot x^b + c
        \\]
    </p>
    <p>
        <strong>Parameters:</strong>
        <ul>
            <li><strong>a</strong>: Scaling factor.</li>
            <li><strong>b</strong>: Exponent.</li>
            <li><strong>c</strong>: Offset.</li>
        </ul>
    </p>
    <h4>When to Use:</h4>
    <p>Ideal for relationships where one quantity scales as a power of another, such as in physics and economics.</p>
    <h4>Advantages:</h4>
    <p>Useful for modeling non-linear scaling relationships and patterns.</p>
    <h4>Disadvantages:</h4>
    <p>Not suitable for data with zero or negative x-values and may require careful handling of scaling and exponent values.</p>

</body>
</html>
"""
FOURIER_TRANSFORM_HELP = f"""

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Logarithmic, Exponential, and Power Law Fitting Help</title>
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
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        hr {{
            border: none;
            height: 4px;
            background-color: #2E8B57;
            margin: 40px 0;
        }}
    </style>
</head>
<body>
    <h1>Logarithmic, Exponential, and Power Law Fitting</h1>
    <p>
        This section provides an overview of fitting models commonly used in data analysis: logarithmic, exponential, and power law. Each model is suited to different types of data patterns and offers a mathematical framework for understanding the underlying relationships.
    </p>

    <h2>1. Logarithmic Function</h2>
    <p>
        <strong>Equation:</strong> \\[
        y = a \cdot \ln(x) + b
        \\]
    </p>
    <p>
        <strong>Parameters:</strong>
        <ul>
            <li><strong>a</strong>: Scaling factor.</li>
            <li><strong>b</strong>: Offset.</li>
        </ul>
    </p>
    <h4>When to Use:</h4>
    <p>Appropriate for data that increases rapidly at first and then levels off.</p>
    <h4>Advantages:</h4>
    <p>Useful for modeling phenomena with diminishing returns.</p>
    <h4>Disadvantages:</h4>
    <p>Only applicable for positive x-values and may be sensitive to scaling and offset adjustments.</p>

    <h2>2. Exponential Function</h2>
    <p>
        <strong>Equation:</strong> \\[
        y = a \cdot e^{{b.x}} + c
        \\]
    </p>
    <p>
        <strong>Parameters:</strong>
        <ul>
            <li><strong>a</strong>: Amplitude.</li>
            <li><strong>b</strong>: Growth/decay rate.</li>
            <li><strong>c</strong>: Offset.</li>
        </ul>
    </p>
    <h4>When to Use:</h4>
    <p>Suitable for data exhibiting exponential growth or decay, such as population models or radioactive decay.</p>
    <h4>Advantages:</h4>
    <p>Effective for capturing exponential trends in data.</p>
    <h4>Disadvantages:</h4>
    <p>Sensitive to outliers and can become unstable if parameters are not initialized appropriately.</p>

    <h2>3. Power Law Function</h2>
    <p>
        <strong>Equation:</strong> \\[
        y = a \cdot x^b + c
        \\]
    </p>
    <p>
        <strong>Parameters:</strong>
        <ul>
            <li><strong>a</strong>: Scaling factor.</li>
            <li><strong>b</strong>: Exponent.</li>
            <li><strong>c</strong>: Offset.</li>
        </ul>
    </p>
    <h4>When to Use:</h4>
    <p>Ideal for relationships where one quantity scales as a power of another, such as in physics and economics.</p>
    <h4>Advantages:</h4>
    <p>Useful for modeling non-linear scaling relationships and patterns.</p>
    <h4>Disadvantages:</h4>
    <p>Not suitable for data with zero or negative x-values and may require careful handling of scaling and exponent values.</p>

</body>
</html>
"""