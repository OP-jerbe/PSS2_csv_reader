import pandas as pd
import os
import plotly.graph_objects as go
import traceback
from PySide6.QtWidgets import QFileDialog, QApplication
from dataclasses import dataclass

@ dataclass
class TestData:
    csv_title: str | None
    time: pd.Series | None
    voltage: pd.Series | None
    current: pd.Series | None


class CSVLoader:
    def __init__(self):
        ...

    def select_csv(self) -> str:
        """
        Open a file dialog to select a CSV file.

        Returns:
            str: The path to the selected CSV file. If no file is selected, an empty string is returned.

        Notes:
            The file dialog starts in the Production History directory and filters for CSV files.
            If no file is selected, the function will return an empty string.
        """
        dir = r"C:\Users\joshua\Documents\Epoxy FT HV Tests"
        
        caption = 'Choose CSV Files'
        initial_dir = dir
        file_types = 'CSV Files (*.csv);;All Files (*)'
        # Open the file dialog
        filepath, _ = QFileDialog.getOpenFileName(
            None,                      # Parent widget, can be None
            caption,                   # Dialog title
            initial_dir,               # Initial directory
            file_types                 # Filter for file types
        )
        
        return filepath

    def load_test_data(self, filepath: str) -> TestData:
        """
        Load scan data from a CSV file and return a TestData object.

        Args:
            filepath (str): The path to the CSV file containing the test data.

        Returns:
            TestData: An object containing the parsed scan data, including serial number, 
                    scan datetime, step size, resolution, x and y coordinates, cup 
                    current, screen current, total current, polarity, beam voltage, 
                    and extractor voltage.

        Notes:
            The function reads specific metadata from the first few rows of the CSV file
            and uses the rest of the data to populate the scan data. The beam voltage 
            is used to determine the scan polarity ('NEG' or 'POS'), and the step size 
            is used to determine the scan resolution (Ultra, High, or Med).
        """

        try:
            csv_title = os.path.basename(filepath)
            df: pd.DataFrame = pd.read_csv(filepath, skiprows=[1], usecols=[5,6,7])
            df.rename(columns={'TIME':'Time'}, inplace=True)
            df.rename(columns={'VOLTAGE':'Voltage (kV)'}, inplace=True)
            df.rename(columns={'AMPERE':'Current (mA)'}, inplace=True)
            df['Time'] = pd.to_datetime(df['Time'], format='%m/%d/%Y %I:%M:%S %p')
            df['Voltage (kV)'] = df['Voltage (kV)'].str.replace('kV', '', regex=True).astype(float)
            df['Current (mA)'] = df['Current (mA)'].str.replace('mA', '', regex=True).astype(float)
            return TestData(csv_title=csv_title,
                            time=df['Time'],
                            voltage=df['Voltage (kV)'],
                            current=df['Current (mA)'])
        except Exception as e:
            full_traceback = traceback.format_exc()
            print(f'Error: {e}\n{full_traceback}')
            return TestData(csv_title=None,
                            time=None,
                            voltage=None,
                            current=None)

def plot_test_data(data: TestData) -> go.Figure:
    fig = go.Figure()

    voltage_color = 'blue'
    current_color = 'red'
    label_style = dict(size=16, weight="bold")  # Font size and bold style

    # Add voltage trace
    if data.time is not None and data.voltage is not None:
        fig.add_trace(go.Scatter(x=data.time, y=data.voltage, mode='lines', name='Voltage (kV)', line=dict(color=voltage_color)))

    # Add current trace
    if data.time is not None and data.current is not None:
        fig.add_trace(go.Scatter(x=data.time, y=data.current, mode='lines', name='Current (mA)', line=dict(color=current_color), yaxis='y2'))

    # Update layout for secondary y-axis
    fig.update_layout(
        title=data.csv_title,
        xaxis_title="Time",
        yaxis=dict(title="Voltage",
                   title_font={**label_style, "color": voltage_color},
                   range=[0, 41],
        ),
        yaxis2=dict(
            title="Current",
            title_font={**label_style, "color": current_color},
            overlaying="y",
            side="right",
            range=[0, 0.061],
        ),
        showlegend=False
    )

    fig.show()

    return fig

def save_plot(fig: go.Figure) -> None:
    options = QFileDialog.Options() # type:ignore
    options |= QFileDialog.Option.HideNameFilterDetails
    file_path, _ = QFileDialog.getSaveFileName(
        None,
        "Save Plot As",
        "",
        "HTML Files (*.html);;All Files (*)",
        options=options
    )

    if file_path:
        # Save the plot to the chosen file location
        fig.write_html(file_path)
        print(f"Plot saved as {file_path}")
    else:
        print("Save operation was canceled.")

if __name__ == '__main__':
    QApplication([])
    csv_loader: CSVLoader = CSVLoader()
    filepath: str = csv_loader.select_csv()
    test_data: TestData = csv_loader.load_test_data(filepath)
    fig = plot_test_data(test_data)
    save_plot(fig)
