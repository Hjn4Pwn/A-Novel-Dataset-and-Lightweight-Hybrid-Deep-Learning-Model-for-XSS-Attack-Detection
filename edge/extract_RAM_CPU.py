import csv


def extract_and_format_data(log_file="backup_log.txt", csv_file="formated_log.csv"):
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()

            data = []
            row = []

            for line in lines:
                if line.startswith("Time"):
                    timecsv = int(line.split("Time: ")[1].split("\n")[0])
                    row.append(timecsv)

                elif line.startswith("RAM"):
                    ramUsed = round(int(line.split("Used: ")[1].split(
                        " bytes, ")[0]) / (1024 * 1024), 0)
                    row.append(ramUsed)

                elif line.startswith("CPU"):
                    cores = line.split("percentages: ")[1]

                    core1 = float(cores.split("1: ")[1].split("%, ")[0])
                    core2 = float(cores.split("2: ")[1].split("%, ")[0])
                    core3 = float(cores.split("3: ")[1].split("%, ")[0])
                    core4 = float(cores.split("4: ")[1].split("%")[0])

                    row.extend([core1, core2, core3, core4])
                    data.append(row)
                    row = []

            with open(csv_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    ["Time (s)", "RAM (MB)", "CPU1 (%)", "CPU2 (%)", "CPU3 (%)", "CPU4 (%)"])
                # Sử dụng writerows để ghi tất cả các dòng dữ liệu
                writer.writerows(data)

            print(
                f"Formatted data extracted from {log_file} and saved to {csv_file}.")

    except FileNotFoundError:
        print(f"File {log_file} not found.")


if __name__ == "__main__":
    extract_and_format_data()
