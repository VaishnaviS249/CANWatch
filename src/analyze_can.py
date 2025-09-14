import pandas as pd
import matplotlib.pyplot as plt
def main():
    df=pd.read_csv("../data/can_log.csv")
    if df.empty:
        print("No data found in csv.")
        return
    df['Data_Length']=df['Data'].apply(lambda x:len(str(x))//2)
    df['Timestamp']=pd.to_datetime(df['Timestamp'],errors='coerce')
    df=df.dropna(subset=['Timestamp'])
    print("\nFirst few rows:")
    print(df.head())

    anomalies=df[df['Data_Length']!=8]
    if not anomalies.empty:
        print("[Anomalies:Non-8 byte payloads]")
        print(anomalies)
    plt.figure() 
    df['CAN_ID'].value_counts().head(10).plot(kind='bar',title="Top 10 CAN IDs Frequency")
    plt.ylabel("Count")
    plt.savefig("../data/can_id_frequency.png",bbox_inches="tight")
    plt.show() 

    df.set_index('Timestamp',inplace=True)
    rate=df.resample("1S").size()
    plt.figure()
    rate.plot(title="Traffic Rate(Messages per second)")
    plt.ylabel("Messages/sec")
    plt.savefig("../data/traffic_rate.png",bbox_inches="tight")
    plt.show()
    df.reset_index(inplace=True)
    df['Cumulative']=range(1,len(df)+1)
    plt.figure()
    plt.title("cumulative Messages Over Time")
    plt.xlabel("Time")
    plt.ylabel("total Messages")
    plt.show()

    counts=df['CAN_ID'].value_counts()
    mean_count=counts.mean()
    suspicious=counts[(counts>3*mean_count)|(counts<0.2*mean_count)]
    if not suspicious.empty:
        print("\n[potential Suspicious IDs based on frequency]")
        print(suspicious)
    
    print("\nMost common payloads:")
    print(df['Data'].value_counts().head(5))

if __name__=="__main__":
    main()
