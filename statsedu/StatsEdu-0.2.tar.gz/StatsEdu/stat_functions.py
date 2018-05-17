from collections import Counter
import matplotlib.pyplot as plt
from math import floor
from numbers import Number


def _data_check(data_massive):
    """Checks all data in data_massive to be number.

    :param data_massive: massive (1D or 2D) to check
    :type data_massive: list
    :returns: None.
    :raises: ValueError.
    """

    def is_2D(data_massive):
        """Evaluates massive's dimension.

        :param data_massive: list of numbers.
        :return: True if massive is 2D, else False.
        """

        for elem in data_massive:
            if not isinstance(elem, list):
                return False
        return True

    if type(data_massive) == list:
        if not is_2D(data_massive):
            for i in data_massive:
                if not isinstance(i, Number):
                    raise ValueError("Items in data_massive must be numbers")
        else:
            for row in data_massive:
                for element in row:
                    if not isinstance(element, Number):
                        raise ValueError("Items in data_massive must be numbers")
    else:
        raise ValueError("data_massive must be list")


def _dot(x, y):
    """Multiplicates elements in massives.

    :param x: list 1.
    :param y: list 2.
    :returns: sum of multiplicated elements.
    """

    _data_check(x)
    _data_check(y)
    return sum([i * j for i, j in zip(x, y)])


def _make_buckets(data_massive, bucket_size):
    """Splits data into groups.

    :param data_massive: list of numbers.
    :param bucket_size: size of groups.
    :type bucket_size: int.
    :returns: collections.Counter object.

    """
    _data_check(data_massive)
    if type(bucket_size) == int:
        return Counter([bucket_size * floor(i / bucket_size) for i in data_massive])
    else:
        raise TypeError("bucket_size should be integer.")


def box_plot(data_massive):
    """Builds boxplot for data_massive."""

    try:
        plt.show(plt.boxplot(data_massive))
    except Exception as e:
        raise TypeError("It seems there are wrong data types im massive") from e


def correlation(x, y):
    """Counts correlation between x and y.

    :param x: massive of numbers 1
    :type x: list
    :param y: massive of numbers 2
    :type y: list
    :returns: float corellation or 0.
    """
    _data_check(x)
    _data_check(y)
    std_x = std(x)
    std_y = std(y)
    if std_x > 0 and std_y >0:
        return round((covariance(x, y) / std_x / std_y), 2)
    return 0


def covariance(x, y):
    """Calculates covariance between x and y.

    :param x: massive of numbers 1
    :type x: list
    :param y: massive of numbers 2
    :type y: list
    :returns: float covarience.
    """

    _data_check(x)
    _data_check(y)
    m_x = mean(x)
    m_y = mean(y)
    dev_x = [i - m_x for i in x]
    dev_y = [i - m_y for i in y]

    return round((_dot(dev_x, dev_y) / len(x)), 2)


def data_range(data_massive):
    """Finds range in data_massive.

    :param data_massive: massive to find range.
    :type data_massive: list
    :returns range: range in data_massive.
    """

    _data_check(data_massive)
    range = max(data_massive) - min(data_massive)
    return range


def hist(data_massive, bucket_size, title="", xlabel="", ylabel=""):
    """Shows histogram of data massive spitted into groups.

    :param data_massive: list of numbers.
    :param bucket_size: size of groups.
    :param title: title of the histogram (optional).
    :param xlabel: label of x axis (optional).
    :param ylabel: label of y axis (optional).
    :return: None. Shows histogram.
    """

    _data_check(data_massive)
    hist_data = _make_buckets(data_massive, bucket_size)
    plt.bar(hist_data.keys(), hist_data.values(), width=bucket_size)
    plt.xlabel = xlabel
    plt.ylabel = ylabel
    plt.title(title)
    plt.show()


def mean(data_massive):
    """Counts mean value of a massive.

    :param data_massive: massive to calculate mean
    :type data_massive: list
    :returns mean: mean value
    :type mean: float
    """
    _data_check(data_massive)

    mean = sum(data_massive) / len(data_massive)
    return mean


def median(data_massive):
    """Calculates median for data_massive.

    :param data_massive: massive to calculate median.
    :type data_massive: list.
    :returns: median.
    """

    _data_check(data_massive)

    n = len(data_massive)
    sorted_data = sorted(data_massive)
    mid = n // 2
    if n % 2 == 1:
        return sorted_data[mid]
    else:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2


def mode(data_massive):
    """Calculates mode in data_massive.

    :param data_massive: massive to find mode.
    :type data_massive: list.
    :return: massive of modes.
    """

    _data_check(data_massive)
    counts = Counter(data_massive)
    max_val= max(counts.values())
    return [k for k, count in counts.items() if count == max_val]


def quantile(data_massive, p):
    """Calculates quantile.
    :param data_massive: massive to calculate quantile.
    :type data_massive: list.
    :param p: order of the quantile.
    :type p: float.
    :returns: quantile.
    """

    try:
        float(p)
    except ValueError as e:
        raise ValueError("Order of the quantile should be number.") from e

    _data_check(data_massive)
    p_idx = int(p * len(data_massive))
    return sorted(data_massive)[p_idx]


def pplot(data_massive, title="", xlabel="", ylabel=""):
    """

    :param data_massive: list of numbers.
    :param title: title of the plot (optional).
    :param xlabel: label of x axis (optional).
    :param ylabel: label of y axis (optional).
    :return: None. Shows plot.
    """
    _data_check(data_massive)
    plt.plot(data_massive)
    plt.xlabel = xlabel
    plt.ylabel = ylabel
    plt.title(title)
    plt.show()


def std(data_massive):
    """Finds standard deviation.

    :param data_massive: massive to find standard deviation.
    :type data_massive: list.
    :returns: float deviation
    """

    return variance(data_massive) ** 0.5


def variance(data_massive):
    """Calculates variance in data_massive.

    :param data_massive: massive to find range.
    :type data_massive: list.
    :returns: int variance
    """

    _data_check(data_massive)
    m = mean(data_massive)
    return round(sum([(d - m) ** 2 for d in data_massive]) / (len(data_massive)))

