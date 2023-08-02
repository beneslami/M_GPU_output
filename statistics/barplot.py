from bokeh.models import FactorRange
from bokeh.plotting import figure, show


if __name__ == "__main__":
    homo_benchmarks = ["2DConv", "AlexNet", "b+tree", "mri-g", "spmv"]
    data = []
    values = []
    for name in homo_benchmarks:
        data.append((name, "packet"))
        data.append((name, "network"))
        values.append(10)
        values.append(12)

    p = figure(x_range=FactorRange(*data), height=350, toolbar_location=None, tools="")
    p.vbar(x=data, top=values, width=0.9, alpha=0.5)

    p.y_range.start = 0
    p.x_range.range_padding = 0.2
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None

    show(p)