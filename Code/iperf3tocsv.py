import json
import csv
import sys

def convert_iperf3_json_to_csv(json_file, csv_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    intervals = data.get("intervals", [])
    
    if not intervals:
        print("Keine Intervalldaten gefunden.")
        return
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header schreiben
        writer.writerow(["Start", "Ende", "Dauer", "Bytes", "Bitrate (bps)", "Retransmits", "RTT (us)", "RTTVar", "CWnd", "PMTU"])
        
        # Daten schreiben
        for interval in intervals:
            for stream in interval.get("streams", []):
                writer.writerow([
                    stream.get("start", ""),
                    stream.get("end", ""),
                    stream.get("seconds", ""),
                    stream.get("bytes", ""),
                    stream.get("bits_per_second", ""),
                    stream.get("retransmits", ""),
                    stream.get("rtt", ""),
                    stream.get("rttvar", ""),
                    stream.get("snd_cwnd", ""),
                    stream.get("pmtu", "")
                ])
    
    print(f"CSV-Datei wurde erfolgreich erstellt: {csv_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Verwendung: python script.py input.json output.csv")
    else:
        convert_iperf3_json_to_csv(sys.argv[1], sys.argv[2])
