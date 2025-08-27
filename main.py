import tkinter as tk
import traceback
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog

import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objects import Figure

DIRECTORY = Path(r"\\opdata2\Company\ENGINEERING\HV Feedthru\Epoxy FT HV Tests")


@dataclass
class TestData:
    """
    dataclass to hold test info
    """

    csv_title: str | None
    time: pd.Series | None
    voltage: pd.Series | None
    current: pd.Series | None


class CSVLoader:
    def select_csv(self) -> Path | None:
        """
        Open a file dialog to select a CSV file.

        Returns:
            Path | None: The path to the selected CSV file, or None if no file is selected.
        """
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="Choose CSV File",
            initialdir=DIRECTORY,
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        return Path(filepath) if filepath else None

    def load_test_data(self, filepath: Path) -> TestData:
        """
        Load scan data from a CSV file and return a TestData object.
        """
        try:
            csv_title = filepath.name
            df: pd.DataFrame = pd.read_csv(filepath, skiprows=[1], usecols=[5, 6, 7])
            df.rename(columns={"TIME": "Time"}, inplace=True)
            df.rename(columns={"VOLTAGE": "Voltage (kV)"}, inplace=True)
            df.rename(columns={"AMPERE": "Current (mA)"}, inplace=True)
            df["Time"] = pd.to_datetime(df["Time"], format="%m/%d/%Y %I:%M:%S %p")
            df["Voltage (kV)"] = (
                df["Voltage (kV)"].str.replace("kV", "", regex=True).astype(float)
            )
            df["Current (mA)"] = (
                df["Current (mA)"].str.replace("mA", "", regex=True).astype(float)
            )
            return TestData(
                csv_title=csv_title,
                time=df["Time"],
                voltage=df["Voltage (kV)"],
                current=df["Current (mA)"],
            )
        except Exception as e:
            full_traceback = traceback.format_exc()
            print(f"Error: {e}\n{full_traceback}")
            return TestData(csv_title=None, time=None, voltage=None, current=None)


def plot_test_data(data: TestData) -> Figure:
    fig = go.Figure()

    voltage_color = "blue"
    current_color = "red"
    label_style = dict(size=16, weight="bold")

    if data.time is not None and data.voltage is not None:
        fig.add_trace(
            go.Scatter(
                x=data.time,
                y=data.voltage,
                mode="lines",
                name="Voltage (kV)",
                line=dict(color=voltage_color),
            )
        )

    if data.time is not None and data.current is not None:
        fig.add_trace(
            go.Scatter(
                x=data.time,
                y=data.current,
                mode="lines",
                name="Current (mA)",
                line=dict(color=current_color),
                yaxis="y2",
            )
        )

    fig.update_layout(
        title=data.csv_title,
        xaxis_title="Time",
        yaxis=dict(
            title="Voltage (kV)",
            title_font={**label_style, "color": voltage_color},
            range=[0, 41],
        ),
        yaxis2=dict(
            title="Current (mA)",
            title_font={**label_style, "color": current_color},
            overlaying="y",
            side="right",
            range=[0, 0.061],
        ),
        showlegend=False,
    )

    fig.show()
    return fig


def save_plot(fig: Figure) -> None:
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.asksaveasfilename(
        title="Save Plot As",
        initialdir=DIRECTORY,
        defaultextension=".html",
        filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")],
    )

    if filepath:
        output_path = Path(filepath)
        fig.write_html(output_path)
        print(f"Plot saved as {output_path}")
    else:
        print("Save operation was canceled.")


if __name__ == "__main__":
    csv_loader = CSVLoader()
    filepath = csv_loader.select_csv()
    if filepath:
        test_data = csv_loader.load_test_data(filepath)
        fig = plot_test_data(test_data)
        save_plot(fig)
