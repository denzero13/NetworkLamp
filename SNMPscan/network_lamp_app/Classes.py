import pandas as pd
from network_lamp_app.config import tmp, visual_for_terminal


class PrinterModel:
    def __init__(self, device):
        self.device = device
        self.KYOCERA = dict(location="1.3.6.1.2.1.1.6.0", model="1.3.6.1.2.1.25.3.2.1.3.1",
                            InventoryNumber="1.3.6.1.4.1.1347.40.10.1.1.5.1", TonerModel="1.3.6.1.2.1.43.11.1.1.6.1.1",
                            TonerType="1.3.6.1.2.1.43.12.1.1.4.1.1", TonerLevel="1.3.6.1.2.1.43.11.1.1.9.1.1",
                            CartridgeMaxCapacity="1.3.6.1.2.1.43.11.1.1.8.1.1", PrintsBlack="1.3.6.1.4.1.1347.43.10.1.1.12.1.1",
                            PrintsColor="1.3.6.1.4.1.1347.42.2.1.1.1.8.1.1", ip_host="1.3.6.1.4.1.2699.1.2.1.3.1.1.4.1.3")

        self.Brother = dict(location="1.3.6.1.2.1.1.6.0", model="1.3.6.1.2.1.25.3.2.1.3.1",
                            InventoryNumber="1.3.6.1.4.1.1347.40.10.1.1.5.1", TonerModel="1.3.6.1.2.1.43.11.1.1.6.1.1",
                            TonerType="1.3.6.1.2.1.43.12.1.1.4.1.1", TonerLevel="1.3.6.1.2.1.43.11.1.1.9.1.2",
                            CartridgeMaxCapacity="1.3.6.1.2.1.43.11.1.1.8.1.2", PrintsBlack="1.3.6.1.2.1.43.10.2.1.4.1.1",
                            PrintsColor="1.3.6.1.4.1.1347.42.2.1.1.1.8.1.1", ip_host="1.3.6.1.4.1.2699.1.2.1.3.1.1.4.1.3")

        self.OKI = dict(location="1.3.6.1.2.1.1.6.0", model="1.3.6.1.2.1.25.3.2.1.3.1",
                        InventoryNumber="1.3.6.1.2.1.1.5.0", TonerModel="1.3.6.1.2.1.43.11.1.1.6.1.1",
                        TonerType="1.3.6.1.2.1.43.12.1.1.4.1.1", TonerLevel="1.3.6.1.2.1.43.11.1.1.9.1.1",
                        CartridgeMaxCapacity="1.3.6.1.2.1.43.11.1.1.8.1.1", PrintsBlack="1.3.6.1.4.1.2001.1.1.1.1.11.1.10.130.0",
                        PrintsColor="1.3.6.1.4.1.1347.42.2.1.1.1.8.1.1", ip_host="1.3.6.1.4.1.2699.1.2.1.3.1.1.4.1.3")

        self.HP = dict(location="1.3.6.1.2.1.43.5.1.1.5.1", model="1.3.6.1.2.1.25.3.2.1.3.1",
                       InventoryNumber="1.3.6.1.4.1.1347.40.10.1.1.5.1", TonerModel="1.3.6.1.2.1.43.11.1.1.6.1.1",
                       TonerType="1.3.6.1.2.1.43.12.1.1.4.1.1", TonerLevel="1.3.6.1.2.1.43.11.1.1.9.1.1",
                       CartridgeMaxCapacity="1.3.6.1.2.1.43.11.1.1.8.1.1", PrintsBlack="1.3.6.1.4.1.1347.43.10.1.1.12.1.1",
                       PrintsColor="1.3.6.1.4.1.1347.42.2.1.1.1.8.1.1", ip_host="1.3.6.1.4.1.2699.1.2.1.3.1.1.4.1.3")

    def printer_model(self):
        """
        Filter printers by company
        """
        print(self.device["ip_host"], self.device["snmp"])
        model = False
        if "KYOCERA" in self.device["snmp"]:
            model = self.KYOCERA

        elif "Brother" in self.device["snmp"]:
            model = self.Brother

        elif "OKI" in self.device["snmp"]:
            model = self.OKI

        elif "HP" in self.device["snmp"]:
            model = self.HP

        return model


class DataPreparationForVisual:
    def __init__(self):
        df = pd.read_csv(tmp)

        try:
            df["TonerLevel"] = df["TonerLevel"].fillna(0)
            df["CartridgeMaxCapacity"] = df["CartridgeMaxCapacity"].fillna(0)
            df["Level"] = [int(float(df["TonerLevel"][i]) * 100 / float(df["CartridgeMaxCapacity"][i]))
                           for i in range(len(df))]

            df["Max"] = [100 - df["Level"][i] for i in range(len(df))]
            df["Full Name"] = [str(df["location"][i]) + " -- " + str(df["TonerModel"][i]) +
                               " -- " + str(float(df["Level"][i])) for i in range(len(df))]

            df.set_index("Full Name", inplace=True)
            plot_data = df[["Level", "Max"]].sort_values("Max")
            csv = plot_data.to_csv(visual_for_terminal, header=None)
        except [TypeError, KeyError, ValueError, ZeroDivisionError]:
            print("Host don`t have name")