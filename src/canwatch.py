import can
import csv
import time
import argparse
import sys
import os
from collections import deque
def parse_args():
    parser=argparse.ArgumentParser(description="CANWatch -python-can based logger")
    parser.add_argument("--iface",default="vcan0",help="CAN Interface (default:vcan0)")
    parser.add_argument("--out",default="../data/can_log.csv",help="CSV output file")
    parser.add_argument("--duration",type=int,default=0,help="Duration to capture in seconds(0=until Ctrl+C)")
    parser.add_argument("--count",type=int,default=0,help="Number of frames to capture(0=unlimited)")
    parser.add_argument("--filter-id",default="",help="comma-separated list of CAN IDs to capture(hex like 0x123 ,0x321)")
    parser.add_argument("--filter-payload",default="",help="Substring(hex) to match in payload(e.g., deadbeef)")
    parser.add_argument("--quiet",action="store_true",help="suppress per-frame console output")
    parser.add_argument("--color",action="store_true",help="enable colored output for matching frames")
    return parser.parse_args()

def build_id_set(id_string):
    if not id_string:
        return None
    ids=set()
    for part in id_string.split(","):
        part=part.strip()
        try:
            ids.add(int(part,16))
        except ValueError:
            print(f"Warning:INvalid CAN ID '{part}' in filter")
    return ids

def color_wrap(text,code):
    return f"\033[{code}m{text}\033[0m" if code else text
def matches_filter(msg,id_set,payload_substr):
    if id_set and msg.arbitartion_id not in id_set:
        return False
    if payload_substr and payload_substr not in msg.data.hex():
        return False
    return True
def main():
    args=parse_args()
    id_set=build_id_set(args.filter_id)
    payload_substr=args.filter_payload.lower()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)),exist_ok=True)

    try:
        bus=can.interface.Bus(channel=args.iface,bustype='socketcan')
    except Exception as e:
        print(f"Error:could not open interface {args.iface}:{e}")
        sys.exit(1)
    try:
        with open(args.out,mode='w',newline='') as logfile:
            writer=csv.writer(logfile)
            writer.writerow(["Timestamp","CAN_ID","Data"])
            logfile.flush()
            print(f"Sniffing on {args.iface}... press Ctrl+C to stop")
            start_time=time.time()
            frame_count=0
            matched_count=0
            timestamps=deque(maxlen=100)
            try:
                while True:
                    if args.duration>0 and (time.time() - start_time)>args.duration:
                        break
                    if args.count>0 and frame_count>=args.count:
                        break
                    msg=bus.recv(1.0)
                    if  msg:
                         frame_count+=1
                         if not matches_filter(msg,id_set,payload_substr):
                             continue
                         matched_count+=1
                         timestamp=time.strftime( "%Y-%m-%d %H:%M:%S",time.localtime(msg.timestamp))
                         can_id=hex(msg.arbitration_id)
                         data=msg.data.hex()
                         now=time.time()
                         timestamps.append(now)
                         rate=None
                         if len(timestamps)>=2:
                             elapsed=timestamps[-1]-timestamps[0]
                             if elapsed>0:
                                 rate=len(timestamps)/elapsed
                         if not args.quiet:
                           msg_str=f"[{matched_count}]{timestamp}|ID={can_id}|Data={data}"
                           if rate:
                               msg_str+=f"|rate={rate:.1f}/s"
                           if args.color and id_set and msg.arbitration_id in id_set:
                               msg_str=color_wrap(msg_str,"92")
                           print(msg_str)
                         writer.writerow([matched_count,timestamp,can_id,data])
                         logfile.flush()
            except KeyboardInterrupt:
                print("\nStopped by user.")
            finally:
                total_time=time.time()-start_time
                print(f"Stopped.Log saved to {args.out}")
                if total_time>0:
                    print(f"captured {matched_count} frames in {total_time:.1f}s"
                          f"({(matched_count/total_time):.2f}fps)")
                bus.shutdown()
    except Exception as e:
        print(f"error writing to {args.out}:{e}")
        sys.exit(1)

if __name__=="__main__":
    main()
