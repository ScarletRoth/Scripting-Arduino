import argparse
import os
import glob
import matplotlib.pyplot as plt
import datetime

def get_sar_files(path):
    if os.path.isdir(path):
        files = glob.glob(os.path.join(path, 'sa*'))
    else:
        files = [path]
    return [f for f in files if os.path.isfile(f)]

def parse_sar_file(filepath):
    data = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    header_found = False
    idle_index = -1
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if '%idle' in line:
            parts = line.split()
            if '%idle' in parts:
                idle_index = parts.index('%idle')
                header_found = True
            continue
        if header_found and idle_index != -1:
            parts = line.split()
            if len(parts) > idle_index and parts[0].count(':') == 2:
                try:
                    timestamp = parts[0]
                    idle_value = float(parts[idle_index])
                    cpu = parts[1] if len(parts) > 1 else 'unknown'
                    data.append({
                        'timestamp': timestamp,
                        'cpu': cpu,
                        'idle': idle_value
                    })
                except (ValueError, IndexError):
                    continue
    return data

def aggregate_data(files):
    all_data = []
    for file in files:
        data = parse_sar_file(file)
        all_data.extend(data)
    return all_data

def plot_data(data):
    filtered = [d for d in data if d['cpu'] == 'all']
    if not filtered:
        print("No 'all' CPU data found.")
        return
    
    filtered.sort(key=lambda x: x['timestamp'])
    
    today = datetime.date.today()
    times = []
    activities = []
    for entry in filtered:
        try:
            time_obj = datetime.datetime.strptime(entry['timestamp'], '%I:%M:%S %p').time()
            dt = datetime.datetime.combine(today, time_obj)
            times.append(dt)
            activity = 100 - entry['idle']
            activities.append(activity)
        except ValueError:
            continue
    
    plt.figure(figsize=(10, 5))
    plt.plot(times, activities, marker='o')
    plt.title('Server Activity Over Time')
    plt.xlabel('Time')
    plt.ylabel('CPU Usage (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def output_data(data):
    for entry in data:
        print(entry)

def main():
    parser = argparse.ArgumentParser(description='Extract %idle data from SAR files')
    parser.add_argument('path', help='Path to SAR file or directory containing SAR files')
    parser.add_argument('--plot', action='store_true', help='Plot the data instead of printing')
    args = parser.parse_args()
    
    files = get_sar_files(args.path)
    idle_data = aggregate_data(files)
    
    if args.plot:
        plot_data(idle_data)
    else:
        output_data(idle_data)
    
    return idle_data

if __name__ == '__main__':
    main()